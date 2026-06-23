"""Stratejik Planlama — Plan yılı API."""

from functools import wraps

from flask import render_template, jsonify, request, current_app, session
from flask_login import login_required, current_user
from sqlalchemy.orm import selectinload

from platform_core import app_bp
from app.extensions import csrf
from app.models import db
from sqlalchemy import or_
from app.models.core import Strategy, SubStrategy, Tenant
from app.models.k_vektor import KVektorStrategyWeight, KVektorSubStrategyWeight
from app.services.k_vektor_config_service import (
    apply_single_strategy_k_vektor_weight,
    apply_single_sub_strategy_k_vektor_weight,
    k_vektor_weights_get_dict,
    save_k_vektor_weights,
)
from app.utils.db_sequence import is_pk_duplicate, sync_pg_sequence_if_needed
from app.models.process import Process, ProcessKpi
from app.models.plan_year import (
    PlanYear, KpiYearConfig,
    StrategyYearConfig, SubStrategyYearConfig, ProcessYearConfig,
)
from app.models.project import PlanProject, PlanProjectTask, PlanProjectActivity
from app.services.score_engine_service import compute_vision_score
from app.services.plan_year_service import (
    list_plan_years,
    get_plan_year,
    get_or_create_plan_year,
    close_plan_year,
    clone_plan_year,
    clone_full_plan_year,
    upsert_kpi_year_config,
    get_active_plan_year_for_user,
)
from app.models.tenant_year import TenantYearIdentity

_SP_ROLES = (
    "Admin",
    "admin",
    "tenant_admin",
    "executive_manager",
    "kurum_yoneticisi",
    "ust_yonetim",
)
from micro.modules.sp.helpers import (
    _check_sp_role,
    sp_manage_required,
    _plan_year_to_dict,
    _plan_project_to_dict,
    _plan_task_to_dict,
)

@app_bp.route("/sp/api/plan-years", methods=["GET"])
@login_required
def sp_api_plan_years_list():
    """Tenant'ın tüm plan yıllarını döner."""
    tid = current_user.tenant_id
    if not tid:
        return jsonify({"success": False, "message": "Tenant bulunamadı."}), 403
    plan_years_list = list_plan_years(tid)
    import datetime as _dt
    active_year = session.get("sp_active_year", _dt.date.today().year)
    return jsonify({
        "success": True,
        "plan_years": [_plan_year_to_dict(py) for py in plan_years_list],
        "active_year": active_year,
    })


@app_bp.route("/sp/api/plan-years", methods=["POST"])
@csrf.exempt
@login_required
@sp_manage_required
def sp_api_plan_years_create():
    """
    Yeni plan yılı oluşturur.
    Body: {year, name (opsiyonel), from_year (opsiyonel — klonlamak için kaynak yıl)}
    """
    tid = current_user.tenant_id
    if not tid:
        return jsonify({"success": False, "message": "Tenant bulunamadı."}), 403

    data = request.get_json() or {}
    new_year = data.get("year")
    if not new_year:
        return jsonify({"success": False, "message": "Yıl zorunludur."}), 400
    try:
        new_year = int(new_year)
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "Geçersiz yıl değeri."}), 400

    if new_year < 2000 or new_year > 2100:
        return jsonify({"success": False, "message": "Yıl 2000-2100 aralığında olmalıdır."}), 400

    # Zaten var mı?
    existing = get_plan_year(tid, new_year)
    if existing:
        return jsonify({
            "success": False,
            "message": f"{new_year} yılı için plan zaten mevcut.",
            "plan_year": _plan_year_to_dict(existing),
        }), 409

    from_year = data.get("from_year")
    name = (data.get("name") or "").strip() or None

    plan_year_feature = bool(getattr(Tenant.query.get(tid), "plan_year_enabled", False))

    try:
        if from_year:
            try:
                from_year = int(from_year)
            except (TypeError, ValueError):
                return jsonify({"success": False, "message": "Geçersiz kaynak yıl."}), 400
            source_py = get_plan_year(tid, from_year)
            if not source_py:
                return jsonify({"success": False, "message": f"{from_year} yılı planı bulunamadı."}), 404
            # Full clone sistemi aktifse tam klon, yoksa eski overlay klon
            if plan_year_feature:
                new_py = clone_full_plan_year(source_py, new_year, name=name)
            else:
                new_py = clone_plan_year(source_py, new_year, name=name)
        else:
            new_py = get_or_create_plan_year(tid, new_year)
            if name:
                new_py.name = name
                db.session.commit()

        session["sp_active_year"] = new_py.year
        return jsonify({
            "success": True,
            "message": f"{new_year} yılı planı oluşturuldu.",
            "plan_year": _plan_year_to_dict(new_py),
        })
    except ValueError as ve:
        return jsonify({"success": False, "message": str(ve)}), 409
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[sp_api_plan_years_create] {e}")
        return jsonify({"success": False, "message": "Plan yılı oluşturulurken hata oluştu."}), 500


@app_bp.route("/sp/api/plan-years/set-active", methods=["POST"])
@csrf.exempt
@login_required
@sp_manage_required
def sp_api_plan_years_set_active():
    """Aktif plan yılını session'a yazar."""
    data = request.get_json() or {}
    year = data.get("year")
    try:
        year = int(year)
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "Geçersiz yıl."}), 400

    tid = current_user.tenant_id
    if tid:
        py = get_plan_year(tid, year)
        if not py:
            # Plan yoksa oluştur (yeni tenant için kolay başlangıç)
            py = get_or_create_plan_year(tid, year)
    session["sp_active_year"] = year
    return jsonify({"success": True, "active_year": year})


@app_bp.route("/sp/api/plan-years/<int:year_id>/close", methods=["POST"])
@csrf.exempt
@login_required
@sp_manage_required
def sp_api_plan_year_close(year_id):
    """Plan yılını kapatır (status=closed)."""
    tid = current_user.tenant_id
    py = PlanYear.query.filter_by(id=year_id, tenant_id=tid).first_or_404()
    if py.status == "closed":
        return jsonify({"success": False, "message": "Bu yıl zaten kapalı."}), 400
    try:
        close_plan_year(py, actor_id=current_user.id)
        return jsonify({
            "success": True,
            "message": f"{py.year} yılı kapatıldı.",
            "plan_year": _plan_year_to_dict(py),
        })
    except Exception as e:
        current_app.logger.error(f"[sp_api_plan_year_close] {e}")
        return jsonify({"success": False, "message": "Yıl kapatılırken hata oluştu."}), 500


@app_bp.route("/sp/api/plan-years/<int:year_id>/kpi-configs", methods=["GET"])
@login_required
def sp_api_plan_year_kpi_configs(year_id):
    """Bir plan yılına ait tüm KPI konfigürasyonlarını döner."""
    tid = current_user.tenant_id
    py = PlanYear.query.filter_by(id=year_id, tenant_id=tid).first_or_404()
    cfgs = KpiYearConfig.query.filter_by(plan_year_id=py.id).all()
    return jsonify({
        "success": True,
        "year": py.year,
        "kpi_configs": [
            {
                "id": c.id,
                "process_kpi_id": c.process_kpi_id,
                "target_value": c.target_value,
                "unit": c.unit,
                "period": c.period,
                "direction": c.direction,
                "target_method": c.target_method,
                "calculation_method": c.calculation_method,
                "basari_puani_araliklari": c.basari_puani_araliklari,
                "onceki_yil_ortalamasi": c.onceki_yil_ortalamasi,
                "weight": c.weight,
                "is_included": c.is_included,
            }
            for c in cfgs
        ],
    })


@app_bp.route("/sp/api/plan-years/<int:year_id>/kpi-configs/<int:kpi_id>", methods=["POST"])
@csrf.exempt
@login_required
@sp_manage_required
def sp_api_plan_year_kpi_config_upsert(year_id, kpi_id):
    """Tek KPI için yıllık config güncelle/oluştur."""
    tid = current_user.tenant_id
    py = PlanYear.query.filter_by(id=year_id, tenant_id=tid).first_or_404()
    if py.status == "closed":
        return jsonify({"success": False, "message": "Kapalı plan yılı düzenlenemez."}), 400

    # H-16: cross-tenant doğrulama
    kpi_owner = ProcessKpi.query.join(Process).filter(
        ProcessKpi.id == kpi_id, Process.tenant_id == tid
    ).first()
    if not kpi_owner:
        return jsonify({"success": False, "message": "Geçersiz KPI."}), 400

    data = request.get_json() or {}
    try:
        cfg = upsert_kpi_year_config(py, kpi_id, data)
        return jsonify({"success": True, "id": cfg.id, "message": "KPI yıllık hedef güncellendi."})
    except ValueError:
        return jsonify({"success": False, "message": "Geçersiz KPI."}), 404
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[sp_api_plan_year_kpi_config_upsert] {e}")
        return jsonify({"success": False, "message": "Kayıt sırasında hata oluştu."}), 500


@app_bp.route("/sp/api/plan-years/<int:year_id>/kpi-configs/bulk", methods=["POST"])
@csrf.exempt
@login_required
@sp_manage_required
def sp_api_plan_year_kpi_configs_bulk(year_id):
    """
    Birden fazla KPI için yıllık config toplu güncelle.
    Body: {"configs": [{"kpi_id": 1, "target_value": "30", ...}, ...]}
    """
    tid = current_user.tenant_id
    py = PlanYear.query.filter_by(id=year_id, tenant_id=tid).first_or_404()
    if py.status == "closed":
        return jsonify({"success": False, "message": "Kapalı plan yılı düzenlenemez."}), 400

    data = request.get_json() or {}
    configs = data.get("configs", [])
    if not configs:
        return jsonify({"success": False, "message": "Konfigürasyon listesi boş."}), 400

    # H-16: cross-tenant doğrulama — tüm kpi_id'lerin tenant'a ait olduğunu doğrula
    requested_ids = [int(item["kpi_id"]) for item in configs if item.get("kpi_id")]
    if requested_ids:
        valid_ids = {
            row.id for row in ProcessKpi.query.join(Process).filter(
                ProcessKpi.id.in_(requested_ids), Process.tenant_id == tid
            ).all()
        }
        if len(valid_ids) < len(set(requested_ids)):
            return jsonify({"success": False, "message": "Geçersiz KPI."}), 400

    updated = 0
    errors = []
    for item in configs:
        kpi_id = item.get("kpi_id")
        if not kpi_id:
            continue
        try:
            upsert_kpi_year_config(py, int(kpi_id), item)
            updated += 1
        except Exception:
            errors.append({"kpi_id": kpi_id, "error": "Geçersiz KPI."})

    if errors:
        db.session.rollback()
        return jsonify({"success": False, "message": "Bazı kayıtlarda hata oluştu.", "errors": errors}), 400

    return jsonify({"success": True, "message": f"{updated} KPI hedefi güncellendi.", "updated": updated})


# ── SP Projeler ───────────────────────────────────────────────────────────────


# ── Plan Yılı Geçiş Sihirbazı ─────────────────────────────────────────────────

@app_bp.route("/sp/wizard/new-year")
@login_required
@sp_manage_required
def sp_sihirbaz_yeni_yil():
    """Plan yılı geçiş sihirbazı sayfası."""
    tid = current_user.tenant_id
    plan_years = list_plan_years(tid)
    return render_template(
        "platform/sp/sihirbaz_yeni_yil.html",
        plan_years=plan_years,
    )


@app_bp.route("/sp/api/wizard/new-year/preview", methods=["POST"])
@login_required
@sp_manage_required
def sp_api_sihirbaz_preview():
    """Sihirbaz adım 1: yeni yıl ön izleme (mevcut KPI sayısı, süreç sayısı)."""
    payload = request.get_json(silent=True) or {}
    source_year_id = payload.get("source_year_id")
    new_year = payload.get("new_year")

    if not source_year_id or not new_year:
        return jsonify({"success": False, "message": "source_year_id ve new_year zorunludur."}), 400

    tid = current_user.tenant_id
    source = PlanYear.query.filter_by(id=source_year_id, tenant_id=tid).first()
    if not source:
        return jsonify({"success": False, "message": "Kaynak yıl bulunamadı."}), 404

    process_count = Process.query.filter_by(tenant_id=tid, plan_year_id=source.id, is_active=True).count()
    kpi_count = (
        ProcessKpi.query
        .join(Process, Process.id == ProcessKpi.process_id)
        .filter(Process.plan_year_id == source.id, ProcessKpi.is_active.is_(True))
        .count()
    )

    return jsonify({
        "success": True,
        "preview": {
            "source_year": source.year,
            "new_year": new_year,
            "process_count": process_count,
            "kpi_count": kpi_count,
            "message": (
                f"{source.year} yılından {new_year} yılına geçiş yapılacak. "
                f"{process_count} süreç ve {kpi_count} KPI taşınacak."
            ),
        },
    })


@app_bp.route("/sp/api/wizard/new-year/apply", methods=["POST"])
@login_required
@sp_manage_required
def sp_api_sihirbaz_uygula():
    """Sihirbaz adım 3: plan yılı klonlama işlemini uygular."""
    payload = request.get_json(silent=True) or {}
    source_year_id = payload.get("source_year_id")
    new_year       = payload.get("new_year")
    new_name       = (payload.get("name") or f"Plan {new_year}").strip()

    if not source_year_id or not new_year:
        return jsonify({"success": False, "message": "source_year_id ve new_year zorunludur."}), 400

    tid = current_user.tenant_id
    source = PlanYear.query.filter_by(id=source_year_id, tenant_id=tid).first()
    if not source:
        return jsonify({"success": False, "message": "Kaynak yıl bulunamadı."}), 404

    existing = get_plan_year(tid, new_year)
    if existing:
        return jsonify({"success": False, "message": f"{new_year} yılı zaten mevcut."}), 409

    try:
        new_py = clone_full_plan_year(source, new_year, new_name)
        db.session.commit()
        return jsonify({
            "success": True,
            "plan_year": _plan_year_to_dict(new_py),
            "message": f"{new_year} yılına başarıyla geçildi.",
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[sp_sihirbaz_uygula] {e}", exc_info=True)
        return jsonify({"success": False, "message": "Geçiş sırasında hata oluştu."}), 500
