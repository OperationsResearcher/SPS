"""Süreç Yönetimi modülü."""

from datetime import datetime, timezone, date

from flask import render_template, jsonify, request, current_app
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload, selectinload

from micro import micro_bp
from app.models import db
from app.models.process import (
    Process,
    ProcessSubStrategyLink,
    ProcessKpi,
    ProcessActivity,
    ActivityTrack,
    KpiData,
    KpiDataAudit,
    FavoriteKpi,
)
from app.models.core import User
from app.utils.process_utils import (
    validate_process_parent_id,
    last_day_of_period,
    data_date_to_period_keys,
)


# ──────────────────────────────────────────────────
# Sayfa Route'ları
# ──────────────────────────────────────────────────

@micro_bp.route("/surec")
@login_required
def surec():
    """Süreç Yönetimi ana sayfası — hiyerarşik ağaç, N+1 önlendi."""
    all_processes = (
        Process.query
        .options(
            joinedload(Process.leaders),
            joinedload(Process.members),
            selectinload(Process.kpis),
        )
        .filter_by(tenant_id=current_user.tenant_id, is_active=True)
        .order_by(Process.code)
        .all()
    )

    all_ids = {p.id for p in all_processes}
    roots = [p for p in all_processes if p.parent_id is None or p.parent_id not in all_ids]

    children_map = {}
    for p in all_processes:
        if p.parent_id and p.parent_id in all_ids:
            children_map.setdefault(p.parent_id, []).append(p)

    users = User.query.filter_by(tenant_id=current_user.tenant_id, is_active=True).all()

    return render_template(
        "micro/surec/index.html",
        processes=all_processes,
        roots=roots,
        children_map=children_map,
        users=users,
    )


@micro_bp.route("/surec/<int:process_id>/karne")
@login_required
def surec_karne(process_id):
    """Süreç Karnesi sayfası."""
    process = Process.query.filter_by(
        id=process_id,
        tenant_id=current_user.tenant_id,
        is_active=True,
    ).first_or_404()

    all_processes = (
        Process.query
        .filter_by(tenant_id=current_user.tenant_id, is_active=True)
        .order_by(Process.code)
        .all()
    )

    current_year = datetime.now().year

    return render_template(
        "micro/surec/karne.html",
        process=process,
        all_processes=all_processes,
        current_year=current_year,
    )


# ──────────────────────────────────────────────────
# API — Süreç CRUD
# ──────────────────────────────────────────────────

@micro_bp.route("/surec/api/add", methods=["POST"])
@login_required
def surec_api_add():
    data = request.get_json() or {}
    try:
        parent_id_raw = data.get("parent_id") or None
        parent_id = validate_process_parent_id(None, parent_id_raw, current_user.tenant_id)
        p = Process(
            tenant_id=current_user.tenant_id,
            parent_id=parent_id,
            code=data.get("code"),
            name=data.get("name"),
            english_name=data.get("english_name"),
            description=data.get("description"),
            document_no=data.get("document_no"),
            revision_no=data.get("revision_no"),
            status=data.get("status", "Aktif"),
            progress=int(data.get("progress") or 0),
            start_boundary=data.get("start_boundary"),
            end_boundary=data.get("end_boundary"),
        )
        for field in ("revision_date", "first_publish_date", "start_date", "end_date"):
            if data.get(field):
                setattr(p, field, datetime.strptime(data[field], "%Y-%m-%d").date())

        db.session.add(p)
        db.session.flush()

        new_leaders = []
        for uid in (data.get("leader_ids") or []):
            u = User.query.get(int(uid))
            if u:
                p.leaders.append(u)
                new_leaders.append(u)

        new_members = []
        for uid in (data.get("member_ids") or []):
            u = User.query.get(int(uid))
            if u:
                p.members.append(u)
                new_members.append(u)

        # Bildirim tetikleyicileri
        try:
            from micro.services.notification_triggers import notify_process_assignment
            for u in new_leaders:
                notify_process_assignment(p, u, "lider", actor=current_user)
            for u in new_members:
                notify_process_assignment(p, u, "üye", actor=current_user)
        except Exception as notif_err:
            current_app.logger.warning(f"[surec_api_add] notification: {notif_err}")

        db.session.commit()
        return jsonify({"success": True, "message": "Süreç başarıyla oluşturuldu.", "id": p.id})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[surec_api_add] {e}")
        return jsonify({"success": False, "message": str(e)}), 400


@micro_bp.route("/surec/api/get/<int:process_id>", methods=["GET"])
@login_required
def surec_api_get(process_id):
    p = Process.query.filter_by(id=process_id, tenant_id=current_user.tenant_id).first_or_404()
    return jsonify({
        "success": True,
        "process": {
            "id": p.id,
            "code": p.code,
            "name": p.name,
            "english_name": p.english_name,
            "description": p.description,
            "document_no": p.document_no,
            "revision_no": p.revision_no,
            "revision_date": str(p.revision_date) if p.revision_date else "",
            "first_publish_date": str(p.first_publish_date) if p.first_publish_date else "",
            "start_date": str(p.start_date) if p.start_date else "",
            "end_date": str(p.end_date) if p.end_date else "",
            "status": p.status,
            "progress": p.progress,
            "parent_id": p.parent_id,
            "start_boundary": p.start_boundary,
            "end_boundary": p.end_boundary,
            "leader_ids": [u.id for u in p.leaders],
            "member_ids": [u.id for u in p.members],
        },
    })


@micro_bp.route("/surec/api/update/<int:process_id>", methods=["POST"])
@login_required
def surec_api_update(process_id):
    p = Process.query.filter_by(id=process_id, tenant_id=current_user.tenant_id).first_or_404()
    data = request.get_json() or {}
    try:
        p.code = data.get("code", p.code)
        p.name = data.get("name", p.name)
        p.english_name = data.get("english_name", p.english_name)
        p.description = data.get("description", p.description)
        p.document_no = data.get("document_no", p.document_no)
        p.revision_no = data.get("revision_no", p.revision_no)
        p.status = data.get("status", p.status)
        p.progress = int(data.get("progress", p.progress) or 0)
        p.start_boundary = data.get("start_boundary", p.start_boundary)
        p.end_boundary = data.get("end_boundary", p.end_boundary)
        p.parent_id = validate_process_parent_id(p.id, data.get("parent_id"), current_user.tenant_id)

        for field in ("revision_date", "first_publish_date", "start_date", "end_date"):
            if data.get(field):
                setattr(p, field, datetime.strptime(data[field], "%Y-%m-%d").date())

        old_leader_ids = {u.id for u in p.leaders}
        old_member_ids = {u.id for u in p.members}

        if "leader_ids" in data:
            p.leaders = [u for uid in data["leader_ids"] if (u := User.query.get(int(uid)))]
        if "member_ids" in data:
            p.members = [u for uid in data["member_ids"] if (u := User.query.get(int(uid)))]

        # Yeni eklenen lider/üyelere bildirim gönder
        try:
            from micro.services.notification_triggers import notify_process_assignment
            for u in p.leaders:
                if u.id not in old_leader_ids:
                    notify_process_assignment(p, u, "lider", actor=current_user)
            for u in p.members:
                if u.id not in old_member_ids:
                    notify_process_assignment(p, u, "üye", actor=current_user)
        except Exception as notif_err:
            current_app.logger.warning(f"[surec_api_update] notification: {notif_err}")

        db.session.commit()
        return jsonify({"success": True, "message": "Süreç güncellendi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[surec_api_update] {e}")
        return jsonify({"success": False, "message": str(e)}), 400


@micro_bp.route("/surec/api/delete/<int:process_id>", methods=["POST"])
@login_required
def surec_api_delete(process_id):
    p = Process.query.filter_by(id=process_id, tenant_id=current_user.tenant_id).first_or_404()
    try:
        p.is_active = False
        p.deleted_at = datetime.now(timezone.utc)
        p.deleted_by = current_user.id
        db.session.commit()
        return jsonify({"success": True, "message": "Süreç silindi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[surec_api_delete] {e}")
        return jsonify({"success": False, "message": str(e)}), 400


# ──────────────────────────────────────────────────
# API — KPI CRUD
# ──────────────────────────────────────────────────

@micro_bp.route("/surec/api/kpi/add", methods=["POST"])
@login_required
def surec_api_kpi_add():
    data = request.get_json() or {}
    process_id = data.get("process_id")
    p = Process.query.filter_by(id=process_id, tenant_id=current_user.tenant_id).first_or_404()
    try:
        kpi = ProcessKpi(
            process_id=p.id,
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
            from micro.services.notification_triggers import notify_kpi_change
            p_with_users = Process.query.options(
                joinedload(Process.leaders), joinedload(Process.members)
            ).get(p.id)
            notify_kpi_change(kpi, p_with_users, change_type="eklendi", actor=current_user)
            db.session.commit()
        except Exception as notif_err:
            current_app.logger.warning(f"[surec_api_kpi_add] notification: {notif_err}")

        return jsonify({"success": True, "message": "Performans göstergesi eklendi.", "id": kpi.id})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[surec_api_kpi_add] {e}")
        return jsonify({"success": False, "message": str(e)}), 400


@micro_bp.route("/surec/api/kpi/get/<int:kpi_id>", methods=["GET"])
@login_required
def surec_api_kpi_get(kpi_id):
    kpi = ProcessKpi.query.join(Process).filter(
        ProcessKpi.id == kpi_id,
        Process.tenant_id == current_user.tenant_id,
    ).first_or_404()
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


@micro_bp.route("/surec/api/kpi/update/<int:kpi_id>", methods=["POST"])
@login_required
def surec_api_kpi_update(kpi_id):
    kpi = ProcessKpi.query.join(Process).filter(
        ProcessKpi.id == kpi_id,
        Process.tenant_id == current_user.tenant_id,
    ).first_or_404()
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
            kpi.sub_strategy_id = int(data["sub_strategy_id"])
        elif "sub_strategy_id" in data and not data["sub_strategy_id"]:
            kpi.sub_strategy_id = None
        db.session.commit()

        # PG güncelleme bildirimi
        try:
            from sqlalchemy.orm import joinedload as _joinedload
            from micro.services.notification_triggers import notify_kpi_change
            p_with_users = Process.query.options(
                _joinedload(Process.leaders), _joinedload(Process.members)
            ).get(kpi.process_id)
            notify_kpi_change(kpi, p_with_users, change_type="güncellendi", actor=current_user)
            db.session.commit()
        except Exception as notif_err:
            current_app.logger.warning(f"[surec_api_kpi_update] notification: {notif_err}")

        return jsonify({"success": True, "message": "Performans göstergesi güncellendi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[surec_api_kpi_update] {e}")
        return jsonify({"success": False, "message": str(e)}), 400


@micro_bp.route("/surec/api/kpi/delete/<int:kpi_id>", methods=["POST"])
@login_required
def surec_api_kpi_delete(kpi_id):
    kpi = ProcessKpi.query.join(Process).filter(
        ProcessKpi.id == kpi_id,
        Process.tenant_id == current_user.tenant_id,
    ).first_or_404()
    try:
        kpi.is_active = False
        db.session.commit()
        return jsonify({"success": True, "message": "Performans göstergesi silindi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[surec_api_kpi_delete] {e}")
        return jsonify({"success": False, "message": str(e)}), 400


@micro_bp.route("/surec/api/kpi/list/<int:process_id>", methods=["GET"])
@login_required
def surec_api_kpi_list(process_id):
    p = Process.query.filter_by(id=process_id, tenant_id=current_user.tenant_id).first_or_404()
    kpis = ProcessKpi.query.filter_by(process_id=p.id, is_active=True).all()
    return jsonify({
        "success": True,
        "kpis": [
            {
                "id": k.id,
                "name": k.name,
                "code": k.code,
                "target_value": k.target_value,
                "unit": k.unit,
                "period": k.period,
                "direction": k.direction,
                "weight": k.weight,
                "sub_strategy_id": k.sub_strategy_id,
                "sub_strategy_title": k.sub_strategy.title if k.sub_strategy else None,
            }
            for k in kpis
        ],
    })


# ──────────────────────────────────────────────────
# API — KPI Veri Girişi
# ──────────────────────────────────────────────────

@micro_bp.route("/surec/api/kpi-data/add", methods=["POST"])
@login_required
def surec_api_kpi_data_add():
    data = request.get_json() or {}
    kpi_id = data.get("kpi_id")
    kpi = ProcessKpi.query.join(Process).filter(
        ProcessKpi.id == kpi_id,
        Process.tenant_id == current_user.tenant_id,
    ).first_or_404()
    try:
        year_val = int(data.get("year", datetime.now().year))
        pt = (data.get("period_type") or "yillik").lower().strip()
        pn = int(data.get("period_no") or 1)
        pm = data.get("period_month")
        period_month = int(pm) if pm is not None and str(pm).strip() else None

        data_date_val = None
        if data.get("data_date"):
            data_date_val = datetime.strptime(data["data_date"], "%Y-%m-%d").date()
        last_day = last_day_of_period(year_val, pt, pn, period_month)
        if last_day is not None:
            data_date_val = last_day
        if data_date_val is None:
            data_date_val = date.today()

        entry = KpiData(
            process_kpi_id=kpi.id,
            year=year_val,
            data_date=data_date_val,
            period_type=pt,
            period_no=pn,
            period_month=period_month,
            target_value=data.get("target_value"),
            actual_value=data.get("actual_value", ""),
            description=data.get("description"),
            user_id=current_user.id,
        )
        db.session.add(entry)
        db.session.flush()
        db.session.add(KpiDataAudit(
            kpi_data_id=entry.id,
            action_type="CREATE",
            new_value=entry.actual_value,
            action_detail="Micro platform veri girişi",
            user_id=current_user.id,
        ))
        db.session.commit()

        try:
            from app.services.score_engine_service import recalc_on_pg_data_change
            recalc_on_pg_data_change(current_user.tenant_id, year_val)
        except Exception as svc_err:
            current_app.logger.warning(f"[surec_api_kpi_data_add] score_engine: {svc_err}")

        try:
            from app.services.process_deviation_service import check_pg_performance_deviation
            check_pg_performance_deviation(entry.id)
        except Exception as svc_err:
            current_app.logger.warning(f"[surec_api_kpi_data_add] deviation_service: {svc_err}")

        return jsonify({"success": True, "message": "Veri kaydedildi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[surec_api_kpi_data_add] {e}")
        return jsonify({"success": False, "message": str(e)}), 400


@micro_bp.route("/surec/api/kpi-data/list/<int:kpi_id>", methods=["GET"])
@login_required
def surec_api_kpi_data_list(kpi_id):
    kpi = ProcessKpi.query.join(Process).filter(
        ProcessKpi.id == kpi_id,
        Process.tenant_id == current_user.tenant_id,
    ).first_or_404()
    year = request.args.get("year", datetime.now().year, type=int)
    entries = (
        KpiData.query
        .filter_by(process_kpi_id=kpi.id, year=year, is_active=True)
        .order_by(KpiData.data_date)
        .all()
    )
    return jsonify({
        "success": True,
        "data": [
            {
                "id": e.id,
                "year": e.year,
                "data_date": str(e.data_date),
                "period_type": e.period_type,
                "period_no": e.period_no,
                "actual_value": e.actual_value,
                "target_value": e.target_value,
                "description": e.description,
            }
            for e in entries
        ],
    })


# ──────────────────────────────────────────────────
# API — Faaliyet CRUD ve Aylık Takip
# ──────────────────────────────────────────────────

@micro_bp.route("/surec/api/activity/add", methods=["POST"])
@login_required
def surec_api_activity_add():
    data = request.get_json() or {}
    process_id = data.get("process_id")
    p = Process.query.filter_by(id=process_id, tenant_id=current_user.tenant_id).first_or_404()
    try:
        act = ProcessActivity(
            process_id=p.id,
            process_kpi_id=data.get("process_kpi_id") or None,
            name=data.get("name"),
            description=data.get("description"),
            status=data.get("status", "Planlandı"),
            progress=int(data.get("progress") or 0),
        )
        if data.get("start_date"):
            act.start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
        if data.get("end_date"):
            act.end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
        db.session.add(act)
        db.session.commit()

        # Faaliyet ekleme bildirimi
        try:
            from sqlalchemy.orm import joinedload as _joinedload
            from micro.services.notification_triggers import notify_activity_assignment
            p_with_users = Process.query.options(
                _joinedload(Process.leaders), _joinedload(Process.members)
            ).get(p.id)
            notify_activity_assignment(act, p_with_users, actor=current_user)
            db.session.commit()
        except Exception as notif_err:
            current_app.logger.warning(f"[surec_api_activity_add] notification: {notif_err}")

        return jsonify({"success": True, "message": "Faaliyet eklendi.", "id": act.id})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[surec_api_activity_add] {e}")
        return jsonify({"success": False, "message": str(e)}), 400


@micro_bp.route("/surec/api/activity/get/<int:act_id>", methods=["GET"])
@login_required
def surec_api_activity_get(act_id):
    act = ProcessActivity.query.join(Process).filter(
        ProcessActivity.id == act_id,
        Process.tenant_id == current_user.tenant_id,
    ).first_or_404()
    return jsonify({
        "success": True,
        "activity": {
            "id": act.id,
            "name": act.name,
            "description": act.description,
            "status": act.status,
            "progress": act.progress,
            "start_date": str(act.start_date) if act.start_date else "",
            "end_date": str(act.end_date) if act.end_date else "",
            "process_kpi_id": act.process_kpi_id,
        },
    })


@micro_bp.route("/surec/api/activity/update/<int:act_id>", methods=["POST"])
@login_required
def surec_api_activity_update(act_id):
    act = ProcessActivity.query.join(Process).filter(
        ProcessActivity.id == act_id,
        Process.tenant_id == current_user.tenant_id,
    ).first_or_404()
    data = request.get_json() or {}
    try:
        act.name = data.get("name", act.name)
        act.description = data.get("description", act.description)
        act.status = data.get("status", act.status)
        act.progress = int(data.get("progress", act.progress) or 0)
        if data.get("start_date"):
            act.start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
        if data.get("end_date"):
            act.end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
        db.session.commit()
        return jsonify({"success": True, "message": "Faaliyet güncellendi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[surec_api_activity_update] {e}")
        return jsonify({"success": False, "message": str(e)}), 400


@micro_bp.route("/surec/api/activity/delete/<int:act_id>", methods=["POST"])
@login_required
def surec_api_activity_delete(act_id):
    act = ProcessActivity.query.join(Process).filter(
        ProcessActivity.id == act_id,
        Process.tenant_id == current_user.tenant_id,
    ).first_or_404()
    try:
        act.is_active = False
        db.session.commit()
        return jsonify({"success": True, "message": "Faaliyet silindi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[surec_api_activity_delete] {e}")
        return jsonify({"success": False, "message": str(e)}), 400


@micro_bp.route("/surec/api/activity/track/<int:act_id>", methods=["POST"])
@login_required
def surec_api_activity_track(act_id):
    """Faaliyet aylık tamamlanma toggle (upsert)."""
    act = ProcessActivity.query.join(Process).filter(
        ProcessActivity.id == act_id,
        Process.tenant_id == current_user.tenant_id,
    ).first_or_404()
    data = request.get_json() or {}
    year = int(data.get("year", datetime.now().year))
    month = int(data.get("month", 1))
    completed = bool(data.get("completed", False))
    try:
        track = ActivityTrack.query.filter_by(
            activity_id=act.id, year=year, month=month
        ).first()
        if track:
            track.completed = completed
            track.user_id = current_user.id
        else:
            track = ActivityTrack(
                activity_id=act.id,
                year=year,
                month=month,
                completed=completed,
                user_id=current_user.id,
            )
            db.session.add(track)
        db.session.commit()
        return jsonify({"success": True, "completed": track.completed})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[surec_api_activity_track] {e}")
        return jsonify({"success": False, "message": str(e)}), 400


# ──────────────────────────────────────────────────
# API — Karne AJAX verisi
# ──────────────────────────────────────────────────

@micro_bp.route("/surec/api/karne/<int:process_id>", methods=["GET"])
@login_required
def surec_api_karne(process_id):
    """Karne sayfasının yıl bazlı KPI + faaliyet aylık takip verisini döner."""
    p = Process.query.filter_by(
        id=process_id, tenant_id=current_user.tenant_id, is_active=True
    ).first_or_404()
    year = request.args.get("year", datetime.now().year, type=int)

    kpis = ProcessKpi.query.filter_by(process_id=p.id, is_active=True).all()
    activities = ProcessActivity.query.filter_by(process_id=p.id, is_active=True).all()
    favorite_kpi_ids = {
        f.process_kpi_id
        for f in FavoriteKpi.query.filter_by(user_id=current_user.id).all()
    }

    def _parse_float(v):
        try:
            return float(v) if v not in (None, "") else None
        except (ValueError, TypeError):
            return None

    def _aggregate(entries_with_keys, method):
        by_key = {}
        for key, val_str, dt in entries_with_keys:
            by_key.setdefault(key, []).append((val_str, _parse_float(val_str), dt))
        result = {}
        for key, items in by_key.items():
            m = (method or "").lower()
            numeric = [(v, d) for _, v, d in items if v is not None]
            if m in ("toplama", "toplam") and numeric:
                result[key] = str(sum(v for v, _ in numeric))
            elif m == "ortalama" and numeric:
                result[key] = str(round(sum(v for v, _ in numeric) / len(numeric), 2))
            else:
                last = max(items, key=lambda x: x[2] or date(1900, 1, 1))
                result[key] = last[0]
        return result

    kpi_list = []
    for k in kpis:
        entries = (
            KpiData.query
            .filter_by(process_kpi_id=k.id, year=year, is_active=True)
            .order_by(KpiData.data_date)
            .all()
        )
        entries_with_keys = []
        for e in entries:
            for key in data_date_to_period_keys(e.data_date, year):
                entries_with_keys.append((key, e.actual_value, e.data_date))
        entries_by_period = _aggregate(entries_with_keys, k.data_collection_method)

        strategy_title = ""
        if k.sub_strategy and k.sub_strategy.strategy:
            strategy_title = k.sub_strategy.strategy.title

        kpi_list.append({
            "id": k.id,
            "name": k.name,
            "code": k.code,
            "target_value": k.target_value,
            "unit": k.unit,
            "period": k.period,
            "data_collection_method": k.data_collection_method or "Ortalama",
            "direction": k.direction or "Increasing",
            "weight": k.weight,
            "sub_strategy_id": k.sub_strategy_id,
            "strategy_title": strategy_title or "-",
            "sub_strategy_title": k.sub_strategy.title if k.sub_strategy else "-",
            "basari_puani_araliklari": k.basari_puani_araliklari,
            "is_favorite": k.id in favorite_kpi_ids,
            "entries": entries_by_period,
        })

    act_list = []
    for a in activities:
        tracks = ActivityTrack.query.filter_by(activity_id=a.id, year=year).all()
        tracks_map = {t.month: t.completed for t in tracks}
        act_list.append({
            "id": a.id,
            "name": a.name,
            "description": a.description,
            "status": a.status,
            "progress": a.progress,
            "start_date": str(a.start_date) if a.start_date else None,
            "end_date": str(a.end_date) if a.end_date else None,
            "monthly_tracks": tracks_map,
        })

    return jsonify({
        "success": True,
        "process": {
            "id": p.id,
            "name": p.name,
            "document_no": p.document_no,
            "revision_no": p.revision_no,
        },
        "year": year,
        "kpis": kpi_list,
        "activities": act_list,
        "favorite_kpi_ids": list(favorite_kpi_ids),
    })
