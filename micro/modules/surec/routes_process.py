"""Süreç modülü — Sayfa ve süreç CRUD."""

from __future__ import annotations
from flask_babel import gettext as _

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
# Sayfa Route'ları
# ──────────────────────────────────────────────────

@app_bp.route("/process")
@login_required
def surec():
    """Süreç Yönetimi ana sayfası — hiyerarşik ağaç; erişim rol/atamaya göre filtrelenir."""
    tid = current_user.tenant_id
    active_py = get_active_plan_year_for_user(current_user)
    q = (
        Process.query.options(
            joinedload(Process.leaders),
            joinedload(Process.members),
            joinedload(Process.owners),
            selectinload(Process.kpis),
            selectinload(Process.process_sub_strategy_links),
        )
        .order_by(Process.code)
    )
    _proc_fallback_py_id = None
    if active_py:
        # Aktif dönem + etiketsiz (NULL) süreçler — VM/legacy veride plan_year_id bos olabilir (SP ile ayni mantik).
        q_year = q.filter(
            or_(Process.plan_year_id == active_py.id, Process.plan_year_id.is_(None))
        )
        all_processes = accessible_processes_filter(q_year, current_user, tid).all()
        # Hâlâ yoksa: en çok sürece sahip plan yılına geri dön (ornegin veri baska yila etiketli)
        if not all_processes:
            best = (
                db.session.query(Process.plan_year_id, _sqla_func.count(Process.id))
                .filter(Process.tenant_id == tid, Process.is_active.is_(True),
                        Process.plan_year_id.isnot(None))
                .group_by(Process.plan_year_id)
                .order_by(_sqla_func.count(Process.id).desc())
                .first()
            )
            if best:
                _proc_fallback_py_id = best[0]
                q_fb = q.filter(Process.plan_year_id == best[0])
                all_processes = accessible_processes_filter(q_fb, current_user, tid).all()
    else:
        all_processes = accessible_processes_filter(q, current_user, tid).all()

    all_ids = {p.id for p in all_processes}
    roots = [p for p in all_processes if p.parent_id is None or p.parent_id not in all_ids]

    children_map = {}
    for p in all_processes:
        if p.parent_id and p.parent_id in all_ids:
            children_map.setdefault(p.parent_id, []).append(p)

    users = User.query.filter_by(tenant_id=tid, is_active=True).all()

    _effective_py_id = _proc_fallback_py_id or (active_py.id if active_py else None)
    strat_q = Strategy.query.filter_by(tenant_id=tid, is_active=True)
    if _effective_py_id:
        strat_q = strat_q.filter(
            or_(Strategy.plan_year_id == _effective_py_id, Strategy.plan_year_id.is_(None))
        )
    strategies = strat_q.order_by(Strategy.code).all()
    strategies_json = [
        {
            "id": s.id,
            "code": s.code or "",
            "title": s.title or "",
            "sub_strategies": [
                {"id": ss.id, "code": ss.code or "", "title": ss.title or ""}
                for ss in (s.sub_strategies or [])
                if getattr(ss, "is_active", True)
            ],
        }
        for s in strategies
    ]

    _popts_py = _effective_py_id
    if active_py and _proc_fallback_py_id is None and any(
        p.plan_year_id is None for p in all_processes
    ):
        # Ust süreç seçicide NULL etiketli süreçler de görünsün
        _popts_py = None
    parent_options_with_depth = _parent_options_with_depth(tid, plan_year_id=_popts_py)
    users_pick_json = _users_pick_json(users)

    can_crud = can_crud_process_entity(current_user)
    # Düzenleme modalı: yöneticiler + en az bir süreçte lider/sahip olanlar
    can_open_process_modal = can_crud or any(
        user_can_edit_process_record(current_user, p) for p in all_processes
    )

    t = db.session.get(Tenant, tid)
    k_vektor_enabled = bool(t and getattr(t, "k_vektor_enabled", False))

    try:
        today = date.today()
        _surec_py = get_active_plan_year_for_user(current_user)
        _score_year = _surec_py.year if _surec_py else today.year
        process_scores, _ = compute_process_scores_internal(
            tid, _score_year, today, persist_pg_scores=False, plan_year=_surec_py
        )
    except Exception as _e:
        current_app.logger.error(f"[surec] process_scores hesaplanamadı: {_e}", exc_info=True)
        process_scores = {}

    # Plan dönemi seçici için
    from app.services.plan_year_service import list_plan_years
    plan_years_list = list_plan_years(tid) if tid else []
    _effective_year_val = None
    if _proc_fallback_py_id:
        _fb_py = next((py for py in plan_years_list if py.id == _proc_fallback_py_id), None)
        _effective_year_val = _fb_py.year if _fb_py else None
    elif active_py:
        _effective_year_val = active_py.year

    return render_template(
        "platform/surec/index.html",
        processes=all_processes,
        roots=roots,
        children_map=children_map,
        users=users,
        strategies_json=strategies_json,
        parent_options_with_depth=parent_options_with_depth,
        users_pick_json=users_pick_json,
        can_crud_process=can_crud,
        can_open_process_modal=can_open_process_modal,
        user_can_edit_process_record=user_can_edit_process_record,
        k_vektor_enabled=k_vektor_enabled,
        process_scores=process_scores,
        plan_years=plan_years_list,
        active_plan_year_val=_effective_year_val,
    )


@app_bp.route("/process/<int:process_id>/karne")
@login_required
def surec_karne(process_id):
    """Süreç Karnesi sayfası (PG odaklı)."""
    process = _process_for_user(process_id)
    if not process:
        abort(404)
    if not user_can_access_process(current_user, process):
        abort(403)

    tid = current_user.tenant_id
    active_py = get_active_plan_year_for_user(current_user)
    # Sprint 1.2: merkezi plan_year filter helper
    from app.utils.plan_year_filter import filter_by_plan_year
    ap_q = Process.query.filter_by(tenant_id=tid, is_active=True)
    if active_py:
        # Karne dropdown'u: aktif yıl + plan yılına bağlanmamış (NULL legacy) süreçler.
        # include_null=False yapılırsa KMF gibi tüm süreçleri plan_year_id=NULL olan
        # kurumlarda dropdown TAMAMEN boşalır (görüntülenen süreç bile listelenmez).
        ap_q = filter_by_plan_year(ap_q, Process, active_py.id, include_null=True)
    ap_q = ap_q.order_by(Process.code)
    all_processes = accessible_processes_filter(ap_q, current_user, tid).all()

    parent_process = None
    if process.parent_id:
        pq = (
            Process.query.filter_by(id=process.parent_id, tenant_id=tid, is_active=True)
            .options(joinedload(Process.leaders))
        )
        parent_process = accessible_processes_filter(pq, current_user, tid).first()

    child_q = (
        Process.query.filter_by(parent_id=process.id, tenant_id=tid, is_active=True)
        .order_by(Process.code)
        .options(joinedload(Process.leaders))
    )
    child_processes = accessible_processes_filter(child_q, current_user, tid).all()

    links_ss = (
        ProcessSubStrategyLink.query.filter_by(process_id=process.id)
        .options(joinedload(ProcessSubStrategyLink.sub_strategy))
        .all()
    )
    substrategy_options = []
    for link in links_ss:
        ss = link.sub_strategy
        if not ss:
            continue
        code = (ss.code or "·").strip()
        tit = (ss.title or "").strip()
        label = f"{code} — {tit}".strip(" —") if tit else code
        substrategy_options.append({"id": ss.id, "label": label})

    # Sürecin kendi plan yılı varsa onu kullan — kullanıcı session'ındaki aktif yıl
    # farklı olsa bile (örn. user aktif=2025, sayfa=2026 SR10) sayfa kendi yılını
    # gösterir. Aksi halde dropdown yıl değiştirildiğinde sonsuz reset döngüsüne girer.
    process_py_year = None
    if process.plan_year_id:
        from app.models import PlanYear
        _py = PlanYear.query.get(process.plan_year_id)
        process_py_year = _py.year if _py else None
    current_year = process_py_year or (active_py.year if active_py else datetime.now().year)
    initial_tab = (request.args.get("tab") or "kpi").strip().lower()
    if initial_tab not in {"kpi", "activities"}:
        initial_tab = "kpi"
    flags = {
        "can_crud_pg": user_can_crud_pg_and_activity(current_user, process),
        "can_enter_pgv": user_can_enter_pgv(current_user, process),
    }

    tenant_row = Tenant.query.get(tid) if tid else None
    k_vektor_enabled = bool(tenant_row and getattr(tenant_row, "k_vektor_enabled", False))
    plan_year_enabled = bool(tenant_row and getattr(tenant_row, "plan_year_enabled", False))

    # Plan year aktifse tüm dönemleri karne year selector'a ver
    plan_years_for_karne = []
    if plan_year_enabled and tid:
        plan_years_for_karne = list_plan_years(tid)

    return render_template(
        "platform/surec/karne.html",
        process=process,
        all_processes=all_processes,
        parent_process=parent_process,
        child_processes=child_processes,
        substrategy_options=substrategy_options,
        current_year=current_year,
        page_flags=flags,
        initial_tab=initial_tab,
        k_vektor_enabled=k_vektor_enabled,
        plan_year_enabled=plan_year_enabled,
        plan_years_for_karne=plan_years_for_karne,
    )


@app_bp.route("/process/<int:process_id>/faaliyetler")
@login_required
def surec_faaliyetler(process_id):
    """Geriye dönük URL: faaliyet görünümünü karne sayfasında açar."""
    process = _process_for_user(process_id)
    if not process:
        abort(404)
    if not user_can_access_process(current_user, process):
        abort(403)
    return redirect(url_for("app_bp.surec_karne", process_id=process_id, tab="activities"))


# ──────────────────────────────────────────────────
# API — Süreç CRUD
# ──────────────────────────────────────────────────

@app_bp.route("/process/api/add", methods=["POST"])
@login_required
def surec_api_add():
    if not can_crud_process_entity(current_user):
        return jsonify({"success": False, "message": _("Süreç oluşturma yetkiniz yok.")}), 403
    data = request.get_json() or {}
    try:
        parent_id_raw = data.get("parent_id") or None
        parent_id = validate_process_parent_id(None, parent_id_raw, current_user.tenant_id)
        active_py = get_active_plan_year_for_user(current_user)
        p = Process(
            tenant_id=current_user.tenant_id,
            parent_id=parent_id,
            plan_year_id=active_py.id if active_py else None,
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

        links_in = data.get("sub_strategy_links")
        if links_in is None and data.get("sub_strategy_ids"):
            links_in = [{"sub_strategy_id": int(x)} for x in data["sub_strategy_ids"]]
        _apply_sub_strategy_links(p, links_in, current_user.tenant_id)

        # Lider+üye kullanıcılarını tek sorguda topla (N+1 önlemi)
        _all_uids = [int(x) for x in (data.get("leader_ids") or [])] + [int(x) for x in (data.get("member_ids") or [])]
        _users_map = {u.id: u for u in User.query.filter(
            User.id.in_(_all_uids), User.tenant_id == current_user.tenant_id
        ).all()} if _all_uids else {}

        new_leaders = []
        for uid in (data.get("leader_ids") or []):
            u = _users_map.get(int(uid))
            if u:
                p.leaders.append(u)
                new_leaders.append(u)

        new_members = []
        for uid in (data.get("member_ids") or []):
            u = _users_map.get(int(uid))
            if u:
                p.members.append(u)
                new_members.append(u)

        # Bildirim tetikleyicileri
        try:
            from app_platform.services.notification_triggers import notify_process_assignment
            for u in new_leaders:
                notify_process_assignment(p, u, "lider", actor=current_user)
            for u in new_members:
                notify_process_assignment(p, u, "üye", actor=current_user)
        except Exception as notif_err:
            current_app.logger.warning(f"[surec_api_add] notification: {notif_err}")

        db.session.commit()
        try:
            AuditLogger.log_create("Süreç Yönetimi", p.id, {"name": p.name, "code": p.code})
        except Exception as e:
            current_app.logger.error(f"Audit log hatası: {e}")
        return jsonify({"success": True, "message": _("Süreç başarıyla oluşturuldu."), "id": p.id})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[surec_api_add] {e}")
        return jsonify({"success": False, "message": _("İşlem tamamlanamadı.")}), 400


@app_bp.route("/process/api/get/<int:process_id>", methods=["GET"])
@login_required
def surec_api_get(process_id):
    p = (
        Process.query.options(
            selectinload(Process.process_sub_strategy_links),
            joinedload(Process.leaders),
            joinedload(Process.members),
            joinedload(Process.owners),
        )
        .filter_by(id=process_id, tenant_id=current_user.tenant_id, is_active=True)
        .first()
    )
    if not p:
        abort(404)
    if not user_can_access_process(current_user, p):
        abort(403)
    sub_strategy_links = [
        {"sub_strategy_id": link.sub_strategy_id, "contribution_pct": link.contribution_pct}
        for link in p.process_sub_strategy_links
    ]
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
            "sub_strategy_links": sub_strategy_links,
        },
    })


@app_bp.route("/process/api/update/<int:process_id>", methods=["POST"])
@login_required
def surec_api_update(process_id):
    p = _process_for_user(process_id)
    if not p:
        abort(404)
    if not user_can_edit_process_record(current_user, p):
        return jsonify({"success": False, "message": _("Bu süreci güncelleme yetkiniz yok.")}), 403
    p = (
        Process.query.options(selectinload(Process.process_sub_strategy_links))
        .filter_by(id=process_id, tenant_id=current_user.tenant_id, is_active=True)
        .first_or_404()
    )
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

        links_from_payload = False
        if "sub_strategy_links" in data:
            _apply_sub_strategy_links(p, data.get("sub_strategy_links"), current_user.tenant_id)
            links_from_payload = True
        elif data.get("sub_strategy_ids") is not None:
            _apply_sub_strategy_links(
                p,
                [{"sub_strategy_id": int(x)} for x in data["sub_strategy_ids"]],
                current_user.tenant_id,
            )
            links_from_payload = True
        # Payload ile bağlantı gönderildiyse _apply zaten boş listeyi reddeder; yeni linkler
        # flush öncesi `p.process_sub_strategy_links` koleksiyonunda görünmeyebilir — burada kontrol etme.
        if not links_from_payload and not p.process_sub_strategy_links:
            raise ValueError("Süreç en az bir alt stratejiye bağlı olmalıdır.")

        old_leader_ids = {u.id for u in p.leaders}
        old_member_ids = {u.id for u in p.members}

        tid = current_user.tenant_id
        leader_ids = [int(x) for x in (data.get("leader_ids") or [])] if "leader_ids" in data else []
        member_ids = [int(x) for x in (data.get("member_ids") or [])] if "member_ids" in data else []
        all_uids = list(set(leader_ids + member_ids))
        users_map = {u.id: u for u in User.query.filter(User.id.in_(all_uids), User.tenant_id == tid).all()} if all_uids else {}

        if "leader_ids" in data:
            p.leaders = [u for uid in leader_ids if (u := users_map.get(uid))]
        if "member_ids" in data:
            p.members = [u for uid in member_ids if (u := users_map.get(uid))]

        # Yeni eklenen lider/üyelere bildirim gönder
        try:
            from app_platform.services.notification_triggers import notify_process_assignment
            for u in p.leaders:
                if u.id not in old_leader_ids:
                    notify_process_assignment(p, u, "lider", actor=current_user)
            for u in p.members:
                if u.id not in old_member_ids:
                    notify_process_assignment(p, u, "üye", actor=current_user)
        except Exception as notif_err:
            current_app.logger.warning(f"[surec_api_update] notification: {notif_err}")

        db.session.commit()
        try:
            AuditLogger.log_update("Süreç Yönetimi", p.id, {}, {"name": p.name, "code": p.code, "status": p.status})
        except Exception as e:
            current_app.logger.error(f"Audit log hatası: {e}")
        return jsonify({"success": True, "message": _("Süreç güncellendi.")})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[surec_api_update] {e}")
        return jsonify({"success": False, "message": _("İşlem tamamlanamadı.")}), 400


@app_bp.route("/process/api/delete/<int:process_id>", methods=["POST"])
@login_required
def surec_api_delete(process_id):
    if not can_crud_process_entity(current_user):
        return jsonify({"success": False, "message": _("Süreç silme yetkiniz yok.")}), 403
    p = Process.query.filter_by(id=process_id, tenant_id=current_user.tenant_id).first_or_404()
    try:
        # Soft-delete cascade: torun süreçleri de pasif yap
        to_delete = [p.id]
        stack = [p.id]
        while stack:
            children = [c.id for c in Process.query.filter_by(
                parent_id=stack.pop(), tenant_id=current_user.tenant_id, is_active=True
            ).all()]
            to_delete.extend(children)
            stack.extend(children)
        now = datetime.now(timezone.utc)
        Process.query.filter(
            Process.id.in_(to_delete), Process.tenant_id == current_user.tenant_id
        ).update({"is_active": False, "deleted_at": now, "deleted_by": current_user.id},
                 synchronize_session="fetch")
        db.session.commit()
        return jsonify({"success": True, "message": _("Süreç silindi."), "cascade_count": len(to_delete)})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[surec_api_delete] {e}")
        return jsonify({"success": False, "message": _("İşlem tamamlanamadı.")}), 400


# ── PG Mini Sparkline (C2) — Süreç başına son 3 ay PG hedef üstü % ─────────
@app_bp.route("/process/api/sparklines")
@login_required
def surec_api_sparklines():
    """Tenant'ın tüm süreçleri için son 3 ay aylık PG hedef-üstü oranı.
    Dönüş: {process_id: [v1, v2, v3]}  — None'lar veri yok demek.
    """
    from sqlalchemy import text as _t, inspect as _sqlinspect
    tid = current_user.tenant_id
    if not tid:
        return jsonify({"success": True, "data": {}})
    # M-18 fix: generate_series() PostgreSQL-only → SQLite (Yerel) ortamında boş dön
    if _sqlinspect(db.engine).dialect.name != 'postgresql':
        return jsonify({"success": True, "data": {}, "labels": []})
    try:
        rows = db.session.execute(_t(r"""
            WITH months AS (
              SELECT generate_series(
                date_trunc('month', CURRENT_DATE) - INTERVAL '2 months',
                date_trunc('month', CURRENT_DATE),
                INTERVAL '1 month'
              )::date AS m
            ),
            agg AS (
              SELECT
                p.id AS pid,
                date_trunc('month', kd.data_date)::date AS m,
                sum(CASE
                     WHEN kd.actual_value ~ '^-?[0-9]+\.?[0-9]*$'
                      AND kd.target_value ~ '^-?[0-9]+\.?[0-9]*$'
                      AND kd.actual_value::float >= kd.target_value::float
                    THEN 1 ELSE 0 END) AS on_target,
                sum(CASE
                     WHEN kd.actual_value ~ '^-?[0-9]+\.?[0-9]*$'
                      AND kd.target_value ~ '^-?[0-9]+\.?[0-9]*$'
                    THEN 1 ELSE 0 END) AS comparable
              FROM processes p
              JOIN process_kpis k ON k.process_id = p.id AND k.is_active = true
              JOIN kpi_data kd ON kd.process_kpi_id = k.id AND kd.is_active = true
              WHERE p.tenant_id = :t AND p.is_active = true
                AND kd.data_date >= (date_trunc('month', CURRENT_DATE) - INTERVAL '2 months')
              GROUP BY p.id, date_trunc('month', kd.data_date)
            )
            SELECT pid, m, on_target, comparable FROM agg
        """), {"t": tid}).fetchall()

        # 3 ay etiket listesi (eski → yeni)
        from datetime import date as _date
        today = _date.today()
        labels = []
        cur_y, cur_m = today.year, today.month
        for off in (2, 1, 0):
            yr = cur_y; mo = cur_m - off
            while mo <= 0: mo += 12; yr -= 1
            labels.append(f"{yr:04d}-{mo:02d}")

        data = {}
        for r in rows:
            mkey = r.m.strftime("%Y-%m")
            data.setdefault(r.pid, {})
            if r.comparable and r.comparable > 0:
                data[r.pid][mkey] = round((r.on_target / r.comparable) * 100, 1)
            else:
                data[r.pid][mkey] = None

        result = {}
        for pid, mvals in data.items():
            result[pid] = [mvals.get(lbl) for lbl in labels]

        return jsonify({"success": True, "data": result, "labels": labels})
    except Exception as e:
        current_app.logger.error(f"[surec_api_sparklines] {e}", exc_info=True)
        return jsonify({"success": False, "message": _("Sparkline verisi alınamadı.")}), 500
