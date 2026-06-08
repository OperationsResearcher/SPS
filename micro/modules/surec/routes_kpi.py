"""Süreç modülü — KPI CRUD API."""

from __future__ import annotations

from datetime import datetime, timezone, date, timedelta
from io import BytesIO

from flask import render_template, jsonify, request, current_app, redirect, abort, send_file, url_for
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, selectinload

from platform_core import app_bp
from app.models import db
from sqlalchemy import or_, func as _sqla_func
from app.models.process import (
    Process,
    ProcessSubStrategyLink,
    ProcessKpi,
    ProcessActivity,
    ProcessActivityAssignee,
    ProcessActivityReminder,
    ActivityTrack,
    KpiData,
    KpiDataAudit,
    FavoriteKpi,
)
from app.models.core import User, Strategy, Tenant
from app.services.plan_year_service import (
    get_plan_year, get_kpi_configs_bulk, get_active_plan_year_for_user, list_plan_years,
    upsert_kpi_year_config,
)
from app.services.score_engine_service import compute_process_scores_internal
from app.utils.audit_logger import AuditLogger
from app.utils.db_sequence import is_pk_duplicate, sync_kpi_data_related_sequences, sync_pg_sequence_if_needed
from app.utils.process_utils import (
    validate_process_parent_id,
    last_day_of_period,
    data_date_to_period_keys,
    validate_same_tenant_sub_strategies,
)
from utils.karne_hesaplamalar import (
    hesapla_basari_puani as _hesapla_basari_puani,
    parse_basari_puani_araliklari as _parse_bpa,
)

from app_platform.modules.surec.permissions import (
    accessible_processes_filter,
    can_crud_process_entity,
    user_can_access_process,
    user_can_crud_pg_and_activity,
    user_can_edit_kpi_data_row,
    user_can_edit_process_record,
    user_can_enter_pgv,
)
from micro.modules.surec.helpers import (
    _apply_sub_strategy_links,
    _is_kpi_data_audit_pk_duplicate,
    _is_notification_pk_duplicate,
    _is_process_activity_pk_duplicate,
    _latest_delete_audit_by_kpi_data_ids,
    _latest_update_audit_by_kpi_data_ids,
    _parent_options_with_depth,
    _process_for_user,
    _user_can_add_activity,
    _user_can_manage_activity,
    _user_display_name,
    _users_pick_json,
)


# ──────────────────────────────────────────────────
# API — KPI CRUD
# ──────────────────────────────────────────────────

@app_bp.route("/process/api/kpi/add", methods=["POST"])
@login_required
def surec_api_kpi_add():
    data = request.get_json() or {}
    process_id = data.get("process_id")
    p = _process_for_user(int(process_id)) if process_id else None
    if not p:
        abort(404)
    if not user_can_crud_pg_and_activity(current_user, p):
        return jsonify({"success": False, "message": "PG ekleme yetkiniz yok."}), 403
    try:
        active_py = get_active_plan_year_for_user(current_user)
        kpi_plan_year_id = active_py.id if active_py else p.plan_year_id
        kpi = ProcessKpi(
            process_id=p.id,
            plan_year_id=kpi_plan_year_id,
            name=data.get("name"),
            code=data.get("code"),
            description=data.get("description"),
            target_value=data.get("target_value"),
            unit=data.get("unit"),
            period=data.get("period", "Aylık"),
            direction=data.get("direction", "Increasing"),
            weight=float(data.get("weight") or 0),
            data_collection_method=data.get("data_collection_method", "Ortalama"),
            is_important=bool(data.get("is_important", False)),
            gosterge_turu=data.get("gosterge_turu") or None,
            target_method=data.get("target_method") or None,
            basari_puani_araliklari=data.get("basari_puani_araliklari") or None,
            onceki_yil_ortalamasi=float(data["onceki_yil_ortalamasi"]) if data.get("onceki_yil_ortalamasi") else None,
        )
        if data.get("sub_strategy_id"):
            tid = current_user.tenant_id
            if not validate_same_tenant_sub_strategies(tid, [int(data["sub_strategy_id"])]):
                return jsonify({"success": False, "message": "Geçersiz alt strateji."}), 400
            kpi.sub_strategy_id = int(data["sub_strategy_id"])
        if data.get("start_date"):
            kpi.start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
        if data.get("end_date"):
            kpi.end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
        db.session.add(kpi)
        db.session.commit()

        # PG ekleme bildirimi
        try:
            from sqlalchemy.orm import joinedload
            from app_platform.services.notification_triggers import notify_kpi_change
            p_with_users = Process.query.options(
                joinedload(Process.leaders), joinedload(Process.members)
            ).get(p.id)
            notify_kpi_change(kpi, p_with_users, change_type="eklendi", actor=current_user)
            db.session.commit()
        except Exception as notif_err:
            current_app.logger.warning(f"[surec_api_kpi_add] notification: {notif_err}")

        try:
            AuditLogger.log_create("PG Yönetimi", kpi.id, {"name": kpi.name, "code": kpi.code, "process_id": p.id})
        except Exception as e:
            current_app.logger.error(f"Audit log hatası: {e}")
        return jsonify({"success": True, "message": "Performans göstergesi eklendi.", "id": kpi.id})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[surec_api_kpi_add] {e}")
        return jsonify({"success": False, "message": "İşlem tamamlanamadı."}), 400


@app_bp.route("/process/api/kpi/get/<int:kpi_id>", methods=["GET"])
@login_required
def surec_api_kpi_get(kpi_id):
    kpi = ProcessKpi.query.join(Process).filter(
        ProcessKpi.id == kpi_id,
        Process.tenant_id == current_user.tenant_id,
        Process.is_active.is_(True),
    ).first_or_404()
    proc = _process_for_user(kpi.process_id)
    if not proc or not user_can_access_process(current_user, proc):
        abort(403)
    return jsonify({
        "success": True,
        "kpi": {
            "id": kpi.id,
            "name": kpi.name,
            "code": kpi.code,
            "description": kpi.description,
            "target_value": kpi.target_value,
            "unit": kpi.unit,
            "period": kpi.period,
            "direction": kpi.direction,
            "weight": kpi.weight,
            "data_collection_method": kpi.data_collection_method,
            "gosterge_turu": kpi.gosterge_turu,
            "target_method": kpi.target_method,
            "basari_puani_araliklari": kpi.basari_puani_araliklari,
            "onceki_yil_ortalamasi": kpi.onceki_yil_ortalamasi,
            "sub_strategy_id": kpi.sub_strategy_id,
        },
    })


@app_bp.route("/process/api/kpi/update/<int:kpi_id>", methods=["POST"])
@login_required
def surec_api_kpi_update(kpi_id):
    kpi = ProcessKpi.query.join(Process).filter(
        ProcessKpi.id == kpi_id,
        Process.tenant_id == current_user.tenant_id,
        Process.is_active.is_(True),
    ).first_or_404()
    proc = _process_for_user(kpi.process_id)
    if not proc or not user_can_crud_pg_and_activity(current_user, proc):
        return jsonify({"success": False, "message": "PG güncelleme yetkiniz yok."}), 403
    data = request.get_json() or {}
    try:
        kpi.name = data.get("name", kpi.name)
        kpi.code = data.get("code", kpi.code)
        kpi.description = data.get("description", kpi.description)
        kpi.target_value = data.get("target_value", kpi.target_value)
        kpi.unit = data.get("unit", kpi.unit)
        kpi.period = data.get("period", kpi.period)
        kpi.direction = data.get("direction", kpi.direction)
        kpi.weight = float(data.get("weight") or kpi.weight or 0)
        kpi.data_collection_method = data.get("data_collection_method", kpi.data_collection_method)
        kpi.gosterge_turu = data.get("gosterge_turu", kpi.gosterge_turu)
        kpi.target_method = data.get("target_method", kpi.target_method)
        kpi.basari_puani_araliklari = data.get("basari_puani_araliklari", kpi.basari_puani_araliklari)
        if "onceki_yil_ortalamasi" in data:
            v = data["onceki_yil_ortalamasi"]
            kpi.onceki_yil_ortalamasi = float(v) if v not in (None, "") else None
        if data.get("sub_strategy_id"):
            tid = current_user.tenant_id
            if not validate_same_tenant_sub_strategies(tid, [int(data["sub_strategy_id"])]):
                return jsonify({"success": False, "message": "Geçersiz alt strateji."}), 400
            kpi.sub_strategy_id = int(data["sub_strategy_id"])
        elif "sub_strategy_id" in data and not data["sub_strategy_id"]:
            kpi.sub_strategy_id = None
        db.session.commit()

        # PG güncelleme bildirimi
        try:
            from sqlalchemy.orm import joinedload as _joinedload
            from app_platform.services.notification_triggers import notify_kpi_change
            p_with_users = Process.query.options(
                _joinedload(Process.leaders), _joinedload(Process.members)
            ).get(kpi.process_id)
            notify_kpi_change(kpi, p_with_users, change_type="güncellendi", actor=current_user)
            db.session.commit()
        except Exception as notif_err:
            current_app.logger.warning(f"[surec_api_kpi_update] notification: {notif_err}")

        try:
            AuditLogger.log_update("PG Yönetimi", kpi.id, {}, {"name": kpi.name, "code": kpi.code, "weight": kpi.weight})
        except Exception as e:
            current_app.logger.error(f"Audit log hatası: {e}")
        return jsonify({"success": True, "message": "Performans göstergesi güncellendi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[surec_api_kpi_update] {e}")
        return jsonify({"success": False, "message": "İşlem tamamlanamadı."}), 400


@app_bp.route("/process/api/kpi/delete/<int:kpi_id>", methods=["POST"])
@login_required
def surec_api_kpi_delete(kpi_id):
    kpi = ProcessKpi.query.join(Process).filter(
        ProcessKpi.id == kpi_id,
        Process.tenant_id == current_user.tenant_id,
        Process.is_active.is_(True),
    ).first_or_404()
    proc = _process_for_user(kpi.process_id)
    if not proc or not user_can_crud_pg_and_activity(current_user, proc):
        return jsonify({"success": False, "message": "PG silme yetkiniz yok."}), 403
    try:
        data = request.get_json(silent=True) or {}
        tenant = current_user.tenant
        plan_year_enabled = bool(tenant and getattr(tenant, "plan_year_enabled", False))
        try:
            target_year = int(data.get("year")) if data.get("year") is not None else None
        except (TypeError, ValueError):
            target_year = None

        if plan_year_enabled:
            py = get_plan_year(current_user.tenant_id, target_year) if target_year else get_active_plan_year_for_user(current_user)
            if py:
                # Plan-year modunda silme, sadece seçili yıla özel hariç bırakma yapar.
                upsert_kpi_year_config(py, kpi.id, {"is_included": False})
                return jsonify({
                    "success": True,
                    "message": f"Performans göstergesi {py.year} yılı için kaldırıldı.",
                    "scope": "year",
                    "year": py.year,
                })

        kpi.is_active = False
        db.session.commit()
        return jsonify({"success": True, "message": "Performans göstergesi silindi.", "scope": "global"})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[surec_api_kpi_delete] {e}")
        return jsonify({"success": False, "message": "İşlem tamamlanamadı."}), 400


@app_bp.route("/process/api/kpi/list/<int:process_id>", methods=["GET"])
@login_required
def surec_api_kpi_list(process_id):
    p = _process_for_user(process_id)
    if not p or not user_can_access_process(current_user, p):
        abort(403)
    kpis = (
        ProcessKpi.query.options(joinedload(ProcessKpi.sub_strategy))
        .filter_by(process_id=p.id, is_active=True).all()
    )

    # Opsiyonel yıl parametresi: yıllık config varsa override değerler döner
    year_param = request.args.get("year", type=int)
    _py_enabled = year_param and current_user.tenant_id and getattr(current_user.tenant, "plan_year_enabled", False)
    _py_obj = get_plan_year(current_user.tenant_id, year_param) if _py_enabled else None
    _cfg_map = get_kpi_configs_bulk(kpis, _py_obj) if kpis else {}

    kpi_items = []
    for k in kpis:
        cfg = _cfg_map.get(k.id, {})
        if cfg.get("is_included", True) is False:
            continue
        kpi_items.append({
            "id": k.id,
            "name": k.name,
            "code": k.code,
            "target_value": cfg.get("target_value", k.target_value),
            "unit": cfg.get("unit", k.unit),
            "period": cfg.get("period", k.period),
            "direction": cfg.get("direction", k.direction),
            "weight": cfg.get("weight", k.weight),
            "sub_strategy_id": k.sub_strategy_id,
            "sub_strategy_title": k.sub_strategy.title if k.sub_strategy else None,
        })

    return jsonify({"success": True, "kpis": kpi_items})


@app_bp.route("/process/api/favorite-kpi/toggle", methods=["POST"])
@login_required
def surec_api_favorite_kpi_toggle():
    """Favori KPI ekle/kaldır (legacy process_bp.favorite_kpi_toggle yerine)."""
    data = request.get_json() or {}
    kpi_id = data.get("process_kpi_id") or data.get("kpi_id")
    if not kpi_id:
        return jsonify({"success": False, "message": "process_kpi_id gerekli."}), 400

    kpi = ProcessKpi.query.join(Process).filter(
        ProcessKpi.id == int(kpi_id),
        Process.tenant_id == current_user.tenant_id,
        Process.is_active.is_(True),
    ).first_or_404()
    proc = _process_for_user(kpi.process_id)
    if not proc or not user_can_access_process(current_user, proc):
        abort(403)

    existing = FavoriteKpi.query.filter_by(
        user_id=current_user.id,
        process_kpi_id=kpi.id,
        is_active=True,
    ).first()
    if existing:
        existing.is_active = False
        db.session.commit()
        return jsonify({"success": True, "favorite": False, "message": "Favorilerden kaldırıldı."})

    archived = FavoriteKpi.query.filter_by(
        user_id=current_user.id,
        process_kpi_id=kpi.id,
        is_active=False,
    ).first()
    if archived:
        archived.is_active = True
        db.session.commit()
    else:
        db.session.add(FavoriteKpi(user_id=current_user.id, process_kpi_id=kpi.id))
        db.session.commit()
    return jsonify({"success": True, "favorite": True, "message": "Favorilere eklendi."})


# ──────────────────────────────────────────────────
# API — KPI Veri Girişi
# ──────────────────────────────────────────────────
