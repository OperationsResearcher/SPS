"""Süreç Yönetimi modülü."""

from __future__ import annotations

from datetime import datetime, timezone, date, timedelta
from io import BytesIO

from flask import render_template, jsonify, request, current_app, redirect, abort, send_file, url_for
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, selectinload

from platform_core import app_bp
from app.models import db
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
from app.utils.audit_logger import AuditLogger
from app.utils.db_sequence import is_pk_duplicate, sync_kpi_data_related_sequences, sync_pg_sequence_if_needed
from app.utils.process_utils import (
    validate_process_parent_id,
    last_day_of_period,
    data_date_to_period_keys,
    validate_same_tenant_sub_strategies,
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

def _user_display_name(user: User | None) -> str:
    if not user:
        return "—"
    fn = (getattr(user, "first_name", None) or "").strip()
    ln = (getattr(user, "last_name", None) or "").strip()
    if fn or ln:
        return f"{fn} {ln}".strip()
    em = getattr(user, "email", None) or ""
    return em.strip() or f"#{user.id}"


def _user_can_manage_activity(user: User, proc: Process, act: ProcessActivity) -> bool:
    """Faaliyet yönetimi: süreç lideri/sahibi veya faaliyete atanmış kişi."""
    if not user or not proc or not act:
        return False
    if user_can_crud_pg_and_activity(user, proc):
        return True
    return any(int(link.user_id) == int(user.id) for link in (act.assignment_links or []))


def _user_can_add_activity(user: User, proc: Process) -> bool:
    """Faaliyet ekleme: süreçte atanan herkes + üst roller."""
    return user_can_access_process(user, proc)


def _is_process_activity_pk_duplicate(err: Exception) -> bool:
    return is_pk_duplicate(err, "process_activities")


def _is_notification_pk_duplicate(err: Exception) -> bool:
    return is_pk_duplicate(err, "notifications")


def _is_kpi_data_audit_pk_duplicate(err: Exception) -> bool:
    return is_pk_duplicate(err, "kpi_data_audits")


def _latest_delete_audit_by_kpi_data_ids(data_ids: list[int]) -> dict[int, KpiDataAudit]:
    if not data_ids:
        return {}
    rows = (
        KpiDataAudit.query.filter(
            KpiDataAudit.kpi_data_id.in_(data_ids),
            KpiDataAudit.action_type == "DELETE",
        )
        .order_by(KpiDataAudit.created_at.desc())
        .all()
    )
    by_id: dict[int, KpiDataAudit] = {}
    for a in rows:
        if a.kpi_data_id not in by_id:
            by_id[a.kpi_data_id] = a
    return by_id


def _latest_update_audit_by_kpi_data_ids(data_ids: list[int]) -> dict[int, KpiDataAudit]:
    """Her kpi_data satırı için en son UPDATE audit kaydı (kim / ne zaman)."""
    if not data_ids:
        return {}
    rows = (
        KpiDataAudit.query.filter(
            KpiDataAudit.kpi_data_id.in_(data_ids),
            KpiDataAudit.action_type == "UPDATE",
        )
        .order_by(KpiDataAudit.created_at.desc())
        .all()
    )
    by_id: dict[int, KpiDataAudit] = {}
    for a in rows:
        if a.kpi_data_id not in by_id:
            by_id[a.kpi_data_id] = a
    return by_id


def _apply_sub_strategy_links(process: Process, links_raw, tenant_id: int) -> None:
    """Sürece en az bir alt strateji bağlar. links_raw: [{sub_strategy_id, contribution_pct?}] veya [id, ...]."""
    tenant = db.session.get(Tenant, tenant_id)
    kv = bool(tenant and getattr(tenant, "k_vektor_enabled", False))

    for link in list(process.process_sub_strategy_links):
        db.session.delete(link)

    items = []
    if not links_raw:
        links_raw = []
    for item in links_raw:
        if isinstance(item, dict):
            sid = item.get("sub_strategy_id")
            if not sid:
                continue
            pct = item.get("contribution_pct")
            pct_f = float(pct) if pct is not None and str(pct).strip() != "" else None
            items.append((int(sid), pct_f))
        else:
            if item is None:
                continue
            items.append((int(item), None))

    if not items:
        raise ValueError("Süreç en az bir alt stratejiye bağlanmalıdır.")

    if kv:
        pcts = [t[1] for t in items]
        if any(x is None for x in pcts):
            raise ValueError("K-Vektör açıkken her seçili alt strateji için katkı yüzdesi (%) girilmelidir.")
        total = sum(float(x) for x in pcts)
        if total > 100.0001:
            raise ValueError("Alt strateji katkı yüzdelerinin toplamı 100'ü aşamaz.")
        if any(float(x) < 0 for x in pcts):
            raise ValueError("Katkı yüzdeleri negatif olamaz.")

    validate_same_tenant_sub_strategies(tenant_id, [t[0] for t in items])
    for sid, pct_f in items:
        db.session.add(
            ProcessSubStrategyLink(
                process_id=process.id,
                sub_strategy_id=sid,
                contribution_pct=pct_f,
            )
        )


def _process_for_user(process_id: int) -> Process | None:
    return (
        Process.query.options(
            joinedload(Process.leaders),
            joinedload(Process.members),
            joinedload(Process.owners),
        )
        .filter_by(id=process_id, tenant_id=current_user.tenant_id, is_active=True)
        .first()
    )


def _parent_options_with_depth(tenant_id: int):
    """Üst süreç seçici — tenant’taki tüm aktif süreçler (hiyerarşi ile)."""
    all_p = (
        Process.query.filter_by(tenant_id=tenant_id, is_active=True)
        .order_by(Process.code)
        .all()
    )
    all_ids = {p.id for p in all_p}
    roots_all = [p for p in all_p if p.parent_id is None or p.parent_id not in all_ids]
    ch_map = {}
    for p in all_p:
        if p.parent_id and p.parent_id in all_ids:
            ch_map.setdefault(p.parent_id, []).append(p)

    def _collect(node_list, depth=0):
        out = []
        for p in node_list:
            out.append((p, depth))
            kids = ch_map.get(p.id, [])
            out.extend(_collect(kids, depth + 1))
        return out

    return _collect(roots_all)


def _users_pick_json(users):
    def _label(u):
        name = f"{u.first_name or ''} {u.last_name or ''}".strip()
        if not name:
            name = u.email or f"Kullanıcı #{u.id}"
        return f"{name} ({u.email})"

    return [{"id": u.id, "label": _label(u)} for u in users]


# ──────────────────────────────────────────────────
# Sayfa Route'ları
# ──────────────────────────────────────────────────

@app_bp.route("/process")
@login_required
def surec():
    """Süreç Yönetimi ana sayfası — hiyerarşik ağaç; erişim rol/atamaya göre filtrelenir."""
    tid = current_user.tenant_id
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
    all_processes = accessible_processes_filter(q, current_user, tid).all()

    all_ids = {p.id for p in all_processes}
    roots = [p for p in all_processes if p.parent_id is None or p.parent_id not in all_ids]

    children_map = {}
    for p in all_processes:
        if p.parent_id and p.parent_id in all_ids:
            children_map.setdefault(p.parent_id, []).append(p)

    users = User.query.filter_by(tenant_id=tid, is_active=True).all()

    strategies = Strategy.query.filter_by(tenant_id=tid, is_active=True).order_by(Strategy.code).all()
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

    parent_options_with_depth = _parent_options_with_depth(tid)
    users_pick_json = _users_pick_json(users)

    can_crud = can_crud_process_entity(current_user)
    # Düzenleme modalı: yöneticiler + en az bir süreçte lider/sahip olanlar
    can_open_process_modal = can_crud or any(
        user_can_edit_process_record(current_user, p) for p in all_processes
    )

    t = db.session.get(Tenant, tid)
    k_vektor_enabled = bool(t and getattr(t, "k_vektor_enabled", False))

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
    ap_q = Process.query.filter_by(tenant_id=tid, is_active=True).order_by(Process.code)
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

    current_year = datetime.now().year
    initial_tab = (request.args.get("tab") or "kpi").strip().lower()
    if initial_tab not in {"kpi", "activities"}:
        initial_tab = "kpi"
    flags = {
        "can_crud_pg": user_can_crud_pg_and_activity(current_user, process),
        "can_enter_pgv": user_can_enter_pgv(current_user, process),
    }

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
        return jsonify({"success": False, "message": "Süreç oluşturma yetkiniz yok."}), 403
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

        links_in = data.get("sub_strategy_links")
        if links_in is None and data.get("sub_strategy_ids"):
            links_in = [{"sub_strategy_id": int(x)} for x in data["sub_strategy_ids"]]
        _apply_sub_strategy_links(p, links_in, current_user.tenant_id)

        new_leaders = []
        for uid in (data.get("leader_ids") or []):
            u = User.query.get(int(uid))
            if u and u.tenant_id == current_user.tenant_id:
                p.leaders.append(u)
                new_leaders.append(u)

        new_members = []
        for uid in (data.get("member_ids") or []):
            u = User.query.get(int(uid))
            if u and u.tenant_id == current_user.tenant_id:
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
        return jsonify({"success": True, "message": "Süreç başarıyla oluşturuldu.", "id": p.id})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[surec_api_add] {e}")
        return jsonify({"success": False, "message": str(e)}), 400


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
        return jsonify({"success": False, "message": "Bu süreci güncelleme yetkiniz yok."}), 403
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
        if "leader_ids" in data:
            p.leaders = [
                u for uid in data["leader_ids"]
                if (u := User.query.get(int(uid))) and u.tenant_id == tid
            ]
        if "member_ids" in data:
            p.members = [
                u for uid in data["member_ids"]
                if (u := User.query.get(int(uid))) and u.tenant_id == tid
            ]

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
        return jsonify({"success": True, "message": "Süreç güncellendi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[surec_api_update] {e}")
        return jsonify({"success": False, "message": str(e)}), 400


@app_bp.route("/process/api/delete/<int:process_id>", methods=["POST"])
@login_required
def surec_api_delete(process_id):
    if not can_crud_process_entity(current_user):
        return jsonify({"success": False, "message": "Süreç silme yetkiniz yok."}), 403
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
        return jsonify({"success": False, "message": str(e)}), 400


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
        return jsonify({"success": False, "message": str(e)}), 400


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
        kpi.is_active = False
        db.session.commit()
        return jsonify({"success": True, "message": "Performans göstergesi silindi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[surec_api_kpi_delete] {e}")
        return jsonify({"success": False, "message": str(e)}), 400


@app_bp.route("/process/api/kpi/list/<int:process_id>", methods=["GET"])
@login_required
def surec_api_kpi_list(process_id):
    p = _process_for_user(process_id)
    if not p or not user_can_access_process(current_user, p):
        abort(403)
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

@app_bp.route("/process/api/kpi-data/add", methods=["POST"])
@login_required
def surec_api_kpi_data_add():
    data = request.get_json() or {}
    kpi_id = data.get("kpi_id")
    kpi = ProcessKpi.query.join(Process).filter(
        ProcessKpi.id == kpi_id,
        Process.tenant_id == current_user.tenant_id,
        Process.is_active.is_(True),
    ).first_or_404()
    proc = _process_for_user(kpi.process_id)
    if not proc or not user_can_enter_pgv(current_user, proc):
        return jsonify({"success": False, "message": "PG verisi girme yetkiniz yok."}), 403
    try:
        year_val = int(data.get("year", datetime.now().year))
        pt = (data.get("period_type") or "yillik").lower().strip()
        pn = int(data.get("period_no") or 1)
        pm = data.get("period_month")
        period_month = int(pm) if pm is not None and str(pm).strip() else None

        # Açık data_date verilmişse öncelikli (VGS / özel dönem); yoksa periyot son günü
        data_date_val = None
        if data.get("data_date"):
            data_date_val = datetime.strptime(data["data_date"], "%Y-%m-%d").date()
        else:
            last_day = last_day_of_period(year_val, pt, pn, period_month)
            if last_day is not None:
                data_date_val = last_day
        if data_date_val is None:
            data_date_val = date.today()

        entry = None
        for attempt in (1, 2):
            try:
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
                break
            except Exception as e:
                db.session.rollback()
                if attempt == 1 and (
                    is_pk_duplicate(e, "kpi_data") or _is_kpi_data_audit_pk_duplicate(e)
                ):
                    sync_kpi_data_related_sequences()
                    db.session.commit()
                    continue
                raise

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

        try:
            AuditLogger.log_create(
                "PG Veri Girişi",
                entry.id,
                {"kpi_id": kpi.id, "year": entry.year, "period_type": entry.period_type, "period_no": entry.period_no},
            )
        except Exception as e:
            current_app.logger.error(f"Audit log hatası: {e}")
        return jsonify({"success": True, "message": "Veri kaydedildi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[surec_api_kpi_data_add] {e}")
        return jsonify({"success": False, "message": str(e)}), 400


@app_bp.route("/process/api/kpi-data/list/<int:kpi_id>", methods=["GET"])
@login_required
def surec_api_kpi_data_list(kpi_id):
    kpi = ProcessKpi.query.join(Process).filter(
        ProcessKpi.id == kpi_id,
        Process.tenant_id == current_user.tenant_id,
        Process.is_active.is_(True),
    ).first_or_404()
    proc = _process_for_user(kpi.process_id)
    if not proc or not user_can_access_process(current_user, proc):
        abort(403)
    year = request.args.get("year", datetime.now().year, type=int)
    q = (
        KpiData.query.filter_by(process_kpi_id=kpi.id, year=year, is_active=True)
        .order_by(KpiData.data_date)
    )
    if not user_can_crud_pg_and_activity(current_user, proc):
        q = q.filter_by(user_id=current_user.id)
    entries = q.all()
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
                "user_id": e.user_id,
            }
            for e in entries
        ],
    })


@app_bp.route("/process/api/kpi-data/history/<int:kpi_id>", methods=["GET"])
@login_required
def surec_api_kpi_data_history(kpi_id):
    """
    PG’ye ait tüm yıllar + silinmiş kayıtlar (salt okuma listesi).
    Üye: herkesin geçmişini görür; düzenle/sil yalnız yetkili satırlarda.
    """
    kpi = ProcessKpi.query.join(Process).filter(
        ProcessKpi.id == kpi_id,
        Process.tenant_id == current_user.tenant_id,
        Process.is_active.is_(True),
    ).first_or_404()
    proc = _process_for_user(kpi.process_id)
    if not proc or not user_can_access_process(current_user, proc):
        abort(403)

    entries = (
        KpiData.query.filter_by(process_kpi_id=kpi.id)
        .options(joinedload(KpiData.user))
        .order_by(KpiData.data_date.desc(), KpiData.id.desc())
        .all()
    )
    del_audits = _latest_delete_audit_by_kpi_data_ids([e.id for e in entries])
    upd_audits = _latest_update_audit_by_kpi_data_ids([e.id for e in entries])
    user_ids = {e.user_id for e in entries}
    for e in entries:
        if e.deleted_by_id:
            user_ids.add(e.deleted_by_id)
        au = del_audits.get(e.id)
        if au and au.user_id:
            user_ids.add(au.user_id)
        uau = upd_audits.get(e.id)
        if uau and uau.user_id:
            user_ids.add(uau.user_id)
    users_map = {u.id: u for u in User.query.filter(User.id.in_(user_ids)).all()} if user_ids else {}

    out = []
    for e in entries:
        del_audit = del_audits.get(e.id)
        upd_audit = upd_audits.get(e.id)
        del_at = e.deleted_at
        del_by_id = e.deleted_by_id
        if not e.is_active and del_at is None and del_audit:
            del_at = del_audit.created_at
            del_by_id = del_audit.user_id
        del_user = users_map.get(del_by_id) if del_by_id else None
        upd_user = users_map.get(upd_audit.user_id) if upd_audit and upd_audit.user_id else None
        can_edit = bool(e.is_active and user_can_edit_kpi_data_row(current_user, e, proc))
        can_delete = can_edit
        out.append({
            "id": e.id,
            "year": e.year,
            "data_date": str(e.data_date),
            "period_type": e.period_type,
            "period_no": e.period_no,
            "period_month": e.period_month,
            "actual_value": e.actual_value,
            "target_value": e.target_value,
            "description": e.description or "",
            "user_id": e.user_id,
            "entered_by_name": _user_display_name(users_map.get(e.user_id) or e.user),
            "recorded_at": e.created_at.isoformat() if getattr(e, "created_at", None) else None,
            "last_updated_at": upd_audit.created_at.isoformat() if upd_audit else None,
            "last_updated_by_name": _user_display_name(upd_user) if upd_user else None,
            "is_active": e.is_active,
            "deleted_at": del_at.isoformat() if del_at else None,
            "deleted_by_id": del_by_id,
            "deleted_by_name": _user_display_name(del_user) if del_user else None,
            "can_edit": can_edit,
            "can_delete": can_delete,
        })

    return jsonify({
        "success": True,
        "current_user_id": current_user.id,
        "data": out,
    })


@app_bp.route("/process/api/kpi-data/update/<int:data_id>", methods=["POST", "PUT"])
@login_required
def surec_api_kpi_data_update(data_id):
    entry = KpiData.query.join(ProcessKpi).join(Process).filter(
        KpiData.id == data_id,
        Process.tenant_id == current_user.tenant_id,
        Process.is_active.is_(True),
    ).first_or_404()
    if not entry.is_active:
        return jsonify({"success": False, "message": "Silinmiş veri düzenlenemez."}), 400
    proc = _process_for_user(entry.process_kpi.process_id)
    if not proc or not user_can_edit_kpi_data_row(current_user, entry, proc):
        return jsonify({"success": False, "message": "Bu veriyi güncelleme yetkiniz yok."}), 403
    data = request.get_json() or {}
    old_actual = entry.actual_value or ""
    old_desc = entry.description or ""
    old_target = entry.target_value or ""

    if "actual_value" in data:
        entry.actual_value = str(data["actual_value"]) if data.get("actual_value") is not None else ""
    if "description" in data:
        entry.description = data["description"]
    if "target_value" in data:
        entry.target_value = data["target_value"]

    new_actual = entry.actual_value or ""
    new_desc = entry.description or ""
    new_target = entry.target_value or ""

    changed_labels = []
    if "actual_value" in data and str(old_actual) != str(new_actual):
        changed_labels.append("gerçekleşen")
    if "description" in data and str(old_desc) != str(new_desc):
        changed_labels.append("açıklama")
    if "target_value" in data and str(old_target) != str(new_target):
        changed_labels.append("hedef")

    try:
        for attempt in (1, 2):
            try:
                if changed_labels:
                    db.session.add(KpiDataAudit(
                        kpi_data_id=entry.id,
                        action_type="UPDATE",
                        old_value=old_actual,
                        new_value=new_actual,
                        action_detail="Micro platform PGV güncelleme: " + ", ".join(changed_labels),
                        user_id=current_user.id,
                    ))
                db.session.commit()
                break
            except Exception as e:
                db.session.rollback()
                if attempt == 1 and (
                    is_pk_duplicate(e, "kpi_data") or _is_kpi_data_audit_pk_duplicate(e)
                ):
                    sync_kpi_data_related_sequences()
                    db.session.commit()
                    continue
                raise
        try:
            from app.services.score_engine_service import recalc_on_pg_data_change
            recalc_on_pg_data_change(current_user.tenant_id, entry.year)
        except Exception as svc_err:
            current_app.logger.warning(f"[surec_api_kpi_data_update] score_engine: {svc_err}")
        try:
            from app.services.process_deviation_service import check_pg_performance_deviation
            check_pg_performance_deviation(data_id)
        except Exception as svc_err:
            current_app.logger.warning(f"[surec_api_kpi_data_update] deviation: {svc_err}")
        try:
            AuditLogger.log_update(
                "PG Veri Girişi",
                entry.id,
                {},
                {"actual_value": entry.actual_value, "target_value": entry.target_value, "description": entry.description},
            )
        except Exception as e:
            current_app.logger.error(f"Audit log hatası: {e}")
        return jsonify({"success": True, "message": "Veri güncellendi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[surec_api_kpi_data_update] {e}")
        return jsonify({"success": False, "message": str(e)}), 400


@app_bp.route("/process/api/kpi-data/delete/<int:data_id>", methods=["POST", "DELETE"])
@login_required
def surec_api_kpi_data_delete(data_id):
    entry = KpiData.query.join(ProcessKpi).join(Process).filter(
        KpiData.id == data_id,
        Process.tenant_id == current_user.tenant_id,
        Process.is_active.is_(True),
    ).first_or_404()
    if not entry.is_active:
        return jsonify({"success": False, "message": "Veri zaten silinmiş."}), 400
    proc = _process_for_user(entry.process_kpi.process_id)
    if not proc or not user_can_edit_kpi_data_row(current_user, entry, proc):
        return jsonify({"success": False, "message": "Bu veriyi silme yetkiniz yok."}), 403
    try:
        now = datetime.now(timezone.utc)
        for attempt in (1, 2):
            try:
                db.session.add(KpiDataAudit(
                    kpi_data_id=entry.id,
                    action_type="DELETE",
                    old_value=entry.actual_value,
                    new_value=None,
                    action_detail="Micro platform PGV silme (soft)",
                    user_id=current_user.id,
                ))
                entry.is_active = False
                entry.deleted_at = now
                entry.deleted_by_id = current_user.id
                db.session.commit()
                break
            except Exception as e:
                db.session.rollback()
                if attempt == 1 and (
                    is_pk_duplicate(e, "kpi_data") or _is_kpi_data_audit_pk_duplicate(e)
                ):
                    sync_kpi_data_related_sequences()
                    db.session.commit()
                    continue
                raise
        try:
            from app.services.score_engine_service import recalc_on_pg_data_change
            recalc_on_pg_data_change(current_user.tenant_id, entry.year)
        except Exception as svc_err:
            current_app.logger.warning(f"[surec_api_kpi_data_delete] score_engine: {svc_err}")
        return jsonify({"success": True, "message": "Veri silindi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[surec_api_kpi_data_delete] {e}")
        return jsonify({"success": False, "message": str(e)}), 400


@app_bp.route("/process/api/kpi-data/detail", methods=["GET"])
@login_required
def surec_api_kpi_data_detail():
    """Kök karne «veri detay» modalı ile uyumlu: periyot bazlı kayıtlar + audit."""
    kpi_id = request.args.get("kpi_id", type=int)
    period_key = request.args.get("period_key", "")
    year = request.args.get("year", datetime.now().year, type=int)
    if kpi_id is None:
        return jsonify({"success": False, "message": "kpi_id gerekli."}), 400
    if not period_key:
        return jsonify({"success": False, "message": "period_key gerekli."}), 400

    kpi = ProcessKpi.query.join(Process).filter(
        ProcessKpi.id == kpi_id,
        Process.tenant_id == current_user.tenant_id,
        Process.is_active.is_(True),
    ).first_or_404()
    proc = _process_for_user(kpi.process_id)
    if not proc or not user_can_access_process(current_user, proc):
        abort(403)

    entries_raw = (
        KpiData.query.filter_by(process_kpi_id=kpi.id, year=year)
        .order_by(KpiData.data_date.desc())
        .all()
    )
    rows = []
    entry_ids = []
    for e in entries_raw:
        keys = data_date_to_period_keys(e.data_date, year)
        if period_key not in keys:
            continue
        entry_ids.append(e.id)
        if not e.is_active:
            continue
        u = e.user
        user_name = _user_display_name(u) if u else "Bilinmiyor"
        rows.append({
            "id": e.id,
            "data_date": str(e.data_date),
            "created_at": e.created_at.isoformat() if e.created_at else None,
            "actual_value": e.actual_value,
            "target_value": e.target_value,
            "description": e.description,
            "user": user_name,
        })

    audits = []
    if entry_ids:
        audit_rows = (
            KpiDataAudit.query.filter(KpiDataAudit.kpi_data_id.in_(entry_ids))
            .order_by(KpiDataAudit.created_at.desc())
            .all()
        )
        for a in audit_rows:
            u = a.user
            user_name = _user_display_name(u) if u else "Bilinmiyor"
            action_label = {"CREATE": "Ekleme", "UPDATE": "Değiştirme", "DELETE": "Silme"}.get(
                a.action_type, a.action_type
            )
            audits.append({
                "id": a.id,
                "kpi_data_id": a.kpi_data_id,
                "action_type": a.action_type,
                "action_label": action_label,
                "old_value": a.old_value,
                "new_value": a.new_value,
                "action_detail": a.action_detail,
                "user": user_name,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            })

    return jsonify({
        "success": True,
        "kpi_name": kpi.name,
        "period_key": period_key,
        "year": year,
        "entries": rows,
        "audits": audits,
    })


@app_bp.route("/process/api/kpi-data/proje-gorevleri", methods=["GET"])
@login_required
def surec_api_kpi_data_proje_gorevleri():
    """Kök API ile uyumlu; proje modülü entegrasyonu yoksa boş liste."""
    _ = request.args.get("kpi_id")
    return jsonify({"success": True, "gorevler": []})


# ──────────────────────────────────────────────────
# API — Faaliyet CRUD ve Aylık Takip
# ──────────────────────────────────────────────────

@app_bp.route("/process/api/activity/add", methods=["POST"])
@login_required
def surec_api_activity_add():
    data = request.get_json() or {}
    process_id = data.get("process_id")
    p = _process_for_user(int(process_id)) if process_id else None
    if not p:
        abort(404)
    if not _user_can_add_activity(current_user, p):
        return jsonify({"success": False, "message": "Faaliyet ekleme yetkiniz yok."}), 403
    try:
        def _parse_dt(v):
            if not v:
                return None
            txt = str(v).strip()
            for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S"):
                try:
                    return datetime.strptime(txt, fmt)
                except ValueError:
                    continue
            return None

        start_at = _parse_dt(data.get("start_at")) or _parse_dt(data.get("start_date"))
        end_at = _parse_dt(data.get("end_at")) or _parse_dt(data.get("end_date"))
        if not start_at and data.get("start_date"):
            start_at = datetime.strptime(data["start_date"], "%Y-%m-%d")
        if not end_at and data.get("end_date"):
            end_at = datetime.strptime(data["end_date"], "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        if not start_at or not end_at:
            return jsonify({"success": False, "message": "Başlangıç ve bitiş zamanı zorunludur."}), 400
        if end_at <= start_at:
            return jsonify({"success": False, "message": "Bitiş başlangıçtan sonra olmalıdır."}), 400

        can_multi = False
        try:
            can_multi = (
                (current_user.role and current_user.role.name in ("tenant_admin", "executive_manager", "Admin"))
                or any(int(u.id) == int(current_user.id) for u in (p.leaders or []))
            )
        except Exception:
            can_multi = False

        raw_assignees = data.get("assignee_ids") if data.get("assignee_ids") is not None else data.get("assigned_user_ids")
        if not isinstance(raw_assignees, list):
            raw_assignees = [raw_assignees] if raw_assignees is not None else []
        assignee_ids = []
        seen = set()
        allowed_ids = {int(u.id) for u in (p.leaders + p.members + p.owners) if u and u.is_active}
        for rid in raw_assignees:
            try:
                uid = int(rid)
            except (TypeError, ValueError):
                continue
            if uid in seen:
                continue
            seen.add(uid)
            if uid in allowed_ids:
                assignee_ids.append(uid)
        if not assignee_ids:
            assignee_ids = [int(current_user.id)]
        if not can_multi:
            assignee_ids = [int(current_user.id)]

        raw_offsets = data.get("reminder_offsets")
        if not isinstance(raw_offsets, list):
            raw_offsets = [raw_offsets] if raw_offsets is not None else []
        reminder_offsets = []
        r_seen = set()
        for rv in raw_offsets:
            try:
                m = int(rv)
            except (TypeError, ValueError):
                continue
            if m < 0 or m > 60 * 24 * 60 or m in r_seen:
                continue
            r_seen.add(m)
            reminder_offsets.append(m)

        act = None
        for attempt in (1, 2):
            act = ProcessActivity(
                process_id=p.id,
                process_kpi_id=data.get("process_kpi_id") or None,
                name=data.get("name"),
                description=data.get("description"),
                status=data.get("status", "Planlandı"),
                progress=int(data.get("progress") or 0),
                start_at=start_at,
                end_at=end_at,
                start_date=start_at.date(),
                end_date=end_at.date(),
                notify_email=bool(data.get("notify_email", False)),
            )
            db.session.add(act)
            try:
                db.session.flush()
                break
            except IntegrityError as ie:
                db.session.rollback()
                if attempt == 1 and _is_process_activity_pk_duplicate(ie):
                    sync_pg_sequence_if_needed("process_activities", "id")
                    continue
                raise

        ProcessActivityAssignee.query.filter_by(activity_id=act.id).delete(synchronize_session=False)
        for idx, uid in enumerate(assignee_ids, start=1):
            db.session.add(ProcessActivityAssignee(
                activity_id=act.id,
                user_id=int(uid),
                order_no=idx,
                assigned_by=current_user.id,
                assigned_at=datetime.now(timezone.utc),
            ))

        ProcessActivityReminder.query.filter_by(activity_id=act.id).delete(synchronize_session=False)
        # PostgreSQL sequence kayması varsa reminder insert'i patlamasın.
        sync_pg_sequence_if_needed("process_activity_reminders", "id")
        for off in reminder_offsets:
            remind_at = start_at - timedelta(minutes=int(off))
            db.session.add(ProcessActivityReminder(
                activity_id=act.id,
                minutes_before=int(off),
                remind_at=remind_at,
                channel_email=bool(act.notify_email),
            ))
        db.session.commit()

        # Faaliyet ekleme bildirimi
        from sqlalchemy.orm import joinedload as _joinedload
        from app_platform.services.notification_triggers import notify_activity_assignment
        for n_attempt in (1, 2):
            try:
                p_with_users = Process.query.options(
                    _joinedload(Process.leaders), _joinedload(Process.members)
                ).get(p.id)
                notify_activity_assignment(act, p_with_users, actor=current_user)
                db.session.commit()
                break
            except Exception as notif_err:
                db.session.rollback()
                if n_attempt == 1 and _is_notification_pk_duplicate(notif_err):
                    sync_pg_sequence_if_needed("notifications", "id")
                    continue
                current_app.logger.warning(f"[surec_api_activity_add] notification: {notif_err}")
                break

        try:
            AuditLogger.log_create(
                "Süreç Faaliyeti",
                act.id,
                {"name": act.name, "process_id": act.process_id, "status": act.status},
            )
        except Exception as e:
            current_app.logger.error(f"Audit log hatası: {e}")
        return jsonify({"success": True, "message": "Faaliyet eklendi.", "id": act.id})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[surec_api_activity_add] {e}")
        return jsonify({"success": False, "message": str(e)}), 400


@app_bp.route("/process/api/activity/get/<int:act_id>", methods=["GET"])
@login_required
def surec_api_activity_get(act_id):
    act = ProcessActivity.query.join(Process).filter(
        ProcessActivity.id == act_id,
        Process.tenant_id == current_user.tenant_id,
        Process.is_active.is_(True),
    ).first_or_404()
    proc = _process_for_user(act.process_id)
    if not proc or not user_can_access_process(current_user, proc):
        abort(403)
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
            "start_at": act.start_at.strftime("%Y-%m-%dT%H:%M") if act.start_at else "",
            "end_at": act.end_at.strftime("%Y-%m-%dT%H:%M") if act.end_at else "",
            "notify_email": bool(act.notify_email),
            "assignee_ids": [int(x.user_id) for x in sorted(act.assignment_links, key=lambda z: z.order_no or 0)],
            "reminder_offsets": [int(r.minutes_before) for r in sorted(act.reminders, key=lambda z: z.minutes_before, reverse=True)],
            "process_kpi_id": act.process_kpi_id,
        },
    })


@app_bp.route("/process/api/activity/update/<int:act_id>", methods=["POST"])
@login_required
def surec_api_activity_update(act_id):
    act = ProcessActivity.query.join(Process).filter(
        ProcessActivity.id == act_id,
        Process.tenant_id == current_user.tenant_id,
        Process.is_active.is_(True),
    ).first_or_404()
    proc = _process_for_user(act.process_id)
    if not proc or not _user_can_manage_activity(current_user, proc, act):
        return jsonify({"success": False, "message": "Faaliyet güncelleme yetkiniz yok."}), 403
    data = request.get_json() or {}
    try:
        def _parse_dt(v):
            if not v:
                return None
            txt = str(v).strip()
            for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S"):
                try:
                    return datetime.strptime(txt, fmt)
                except ValueError:
                    continue
            return None

        act.name = data.get("name", act.name)
        act.description = data.get("description", act.description)
        act.status = data.get("status", act.status)
        act.progress = int(data.get("progress", act.progress) or 0)
        if "notify_email" in data:
            act.notify_email = bool(data.get("notify_email"))
        if "process_kpi_id" in data:
            act.process_kpi_id = data.get("process_kpi_id") or None

        parsed_start = _parse_dt(data.get("start_at")) or _parse_dt(data.get("start_date"))
        parsed_end = _parse_dt(data.get("end_at")) or _parse_dt(data.get("end_date"))
        if data.get("start_date") and not parsed_start:
            parsed_start = datetime.strptime(data["start_date"], "%Y-%m-%d")
        if data.get("end_date") and not parsed_end:
            parsed_end = datetime.strptime(data["end_date"], "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        if parsed_start:
            act.start_at = parsed_start
            act.start_date = parsed_start.date()
        if parsed_end:
            act.end_at = parsed_end
            act.end_date = parsed_end.date()
        if act.start_at and act.end_at and act.end_at <= act.start_at:
            return jsonify({"success": False, "message": "Bitiş başlangıçtan sonra olmalıdır."}), 400

        if data.get("assignee_ids") is not None or data.get("assigned_user_ids") is not None:
            can_multi = (
                (current_user.role and current_user.role.name in ("tenant_admin", "executive_manager", "Admin"))
                or any(int(u.id) == int(current_user.id) for u in (proc.leaders or []))
            )
            raw_assignees = data.get("assignee_ids") if data.get("assignee_ids") is not None else data.get("assigned_user_ids")
            if not isinstance(raw_assignees, list):
                raw_assignees = [raw_assignees] if raw_assignees is not None else []
            allowed_ids = {int(u.id) for u in (proc.leaders + proc.members + proc.owners) if u and u.is_active}
            cleaned = []
            seen = set()
            for rid in raw_assignees:
                try:
                    uid = int(rid)
                except (TypeError, ValueError):
                    continue
                if uid in seen:
                    continue
                seen.add(uid)
                if uid in allowed_ids:
                    cleaned.append(uid)
            if not cleaned:
                cleaned = [int(current_user.id)]
            if not can_multi:
                cleaned = [int(current_user.id)]
            ProcessActivityAssignee.query.filter_by(activity_id=act.id).delete(synchronize_session=False)
            for idx, uid in enumerate(cleaned, start=1):
                db.session.add(ProcessActivityAssignee(
                    activity_id=act.id,
                    user_id=int(uid),
                    order_no=idx,
                    assigned_by=current_user.id,
                    assigned_at=datetime.now(timezone.utc),
                ))

        if "reminder_offsets" in data:
            raw_offsets = data.get("reminder_offsets")
            if not isinstance(raw_offsets, list):
                raw_offsets = [raw_offsets] if raw_offsets is not None else []
            offsets = []
            seen_r = set()
            for rv in raw_offsets:
                try:
                    mm = int(rv)
                except (TypeError, ValueError):
                    continue
                if mm < 0 or mm > 60 * 24 * 60 or mm in seen_r:
                    continue
                seen_r.add(mm)
                offsets.append(mm)
            ProcessActivityReminder.query.filter_by(activity_id=act.id).delete(synchronize_session=False)
            base_start = act.start_at or datetime.combine(act.start_date, datetime.min.time()) if act.start_date else None
            if base_start:
                for mm in offsets:
                    db.session.add(ProcessActivityReminder(
                        activity_id=act.id,
                        minutes_before=int(mm),
                        remind_at=base_start - timedelta(minutes=int(mm)),
                        channel_email=bool(act.notify_email),
                    ))
        db.session.commit()
        try:
            AuditLogger.log_update(
                "Süreç Faaliyeti",
                act.id,
                {},
                {"name": act.name, "process_id": act.process_id, "status": act.status, "progress": act.progress},
            )
        except Exception as e:
            current_app.logger.error(f"Audit log hatası: {e}")
        return jsonify({"success": True, "message": "Faaliyet güncellendi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[surec_api_activity_update] {e}")
        return jsonify({"success": False, "message": str(e)}), 400


@app_bp.route("/process/api/activity/delete/<int:act_id>", methods=["POST"])
@login_required
def surec_api_activity_delete(act_id):
    act = ProcessActivity.query.join(Process).filter(
        ProcessActivity.id == act_id,
        Process.tenant_id == current_user.tenant_id,
        Process.is_active.is_(True),
    ).first_or_404()
    proc = _process_for_user(act.process_id)
    if not proc or not _user_can_manage_activity(current_user, proc, act):
        return jsonify({"success": False, "message": "Faaliyet silme yetkiniz yok."}), 403
    try:
        act.is_active = False
        db.session.commit()
        return jsonify({"success": True, "message": "Faaliyet silindi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[surec_api_activity_delete] {e}")
        return jsonify({"success": False, "message": str(e)}), 400


@app_bp.route("/process/api/activity/complete/<int:act_id>", methods=["POST"])
@login_required
def surec_api_activity_complete(act_id):
    act = ProcessActivity.query.join(Process).filter(
        ProcessActivity.id == act_id,
        Process.tenant_id == current_user.tenant_id,
        Process.is_active.is_(True),
    ).first_or_404()
    proc = _process_for_user(act.process_id)
    if not proc or not _user_can_manage_activity(current_user, proc, act):
        return jsonify({"success": False, "message": "Faaliyet tamamlama yetkiniz yok."}), 403
    try:
        act.status = "Tamamlandı"
        act.progress = 100
        act.completed_at = datetime.now(timezone.utc)
        db.session.commit()
        return jsonify({"success": True, "message": "Faaliyet tamamlandı."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[surec_api_activity_complete] {e}")
        return jsonify({"success": False, "message": str(e)}), 400


@app_bp.route("/process/api/activity/track/<int:act_id>", methods=["POST"])
@login_required
def surec_api_activity_track(act_id):
    """Faaliyet aylık tamamlanma toggle (upsert)."""
    act = ProcessActivity.query.join(Process).filter(
        ProcessActivity.id == act_id,
        Process.tenant_id == current_user.tenant_id,
        Process.is_active.is_(True),
    ).first_or_404()
    proc = _process_for_user(act.process_id)
    if not proc or not _user_can_manage_activity(current_user, proc, act):
        return jsonify({"success": False, "message": "Faaliyet takibi için yetkiniz yok."}), 403
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

@app_bp.route("/process/api/karne/<int:process_id>", methods=["GET"])
@login_required
def surec_api_karne(process_id):
    """Karne sayfasının yıl bazlı KPI + faaliyet aylık takip verisini döner."""
    p = _process_for_user(process_id)
    if not p:
        abort(404)
    if not user_can_access_process(current_user, p):
        abort(403)
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

    def _rollup_year_actual(method: str | None, raw_rows: list) -> float | None:
        """Yıl içindeki ham PGV satırlarından tek özet değer (PGV yoksa None)."""
        m = (method or "").lower()
        raw_nums = [_parse_float(e.actual_value) for e in raw_rows]
        raw_nums = [x for x in raw_nums if x is not None]
        if m in ("toplama", "toplam"):
            return float(sum(raw_nums)) if raw_nums else None
        if m == "ortalama":
            return round(sum(raw_nums) / len(raw_nums), 6) if raw_nums else None
        if raw_rows:
            last_e = max(raw_rows, key=lambda e: e.data_date or date(1900, 1, 1))
            return _parse_float(last_e.actual_value)
        return None

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

        prev_y = int(year) - 1
        prev_rows = (
            KpiData.query.filter_by(process_kpi_id=k.id, year=prev_y, is_active=True)
            .order_by(KpiData.data_date)
            .all()
        )
        year_rollup = _rollup_year_actual(k.data_collection_method, entries)
        prev_rollup = _rollup_year_actual(k.data_collection_method, prev_rows)
        prev_from_pgv = prev_rollup is not None

        strategy_title = ""
        if k.sub_strategy and k.sub_strategy.strategy:
            strategy_title = k.sub_strategy.strategy.title

        sub_st = k.sub_strategy
        oy = getattr(k, "onceki_yil_ortalamasi", None)
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
            "sub_strategy_title": sub_st.title if sub_st else "-",
            "sub_strategy_code": (sub_st.code or "").strip() if sub_st else "",
            "basari_puani_araliklari": k.basari_puani_araliklari,
            "is_favorite": k.id in favorite_kpi_ids,
            "entries": entries_by_period,
            "year_rollup": round(float(year_rollup), 6) if year_rollup is not None else None,
            "onceki_yil_ortalamasi": round(float(oy), 6) if oy is not None else None,
            "prev_year_from_pgv": prev_from_pgv,
            "prev_year_rollup": round(float(prev_rollup), 6) if prev_rollup is not None else None,
        })

    act_list = []
    for a in activities:
        tracks = ActivityTrack.query.filter_by(activity_id=a.id, year=year).all()
        tracks_map = {t.month: t.completed for t in tracks}
        assignee_links = sorted(a.assignment_links, key=lambda z: z.order_no or 0)
        assignees = []
        for link in assignee_links:
            u = link.user
            if not u:
                continue
            full_name = (f"{(u.first_name or '').strip()} {(u.last_name or '').strip()}").strip() or (u.email or "")
            assignees.append({
                "id": int(u.id),
                "full_name": full_name,
                "email": u.email,
                "order_no": link.order_no,
            })
        can_manage = user_can_crud_pg_and_activity(current_user, p) or any(
            int(x["id"]) == int(current_user.id) for x in assignees
        )
        act_list.append({
            "id": a.id,
            "name": a.name,
            "description": a.description,
            "status": a.status,
            "progress": a.progress,
            "start_date": str(a.start_date) if a.start_date else None,
            "end_date": str(a.end_date) if a.end_date else None,
            "start_at": a.start_at.isoformat(timespec="minutes") if a.start_at else None,
            "end_at": a.end_at.isoformat(timespec="minutes") if a.end_at else None,
            "notify_email": bool(a.notify_email),
            "process_kpi_id": a.process_kpi_id,
            "process_kpi_name": a.process_kpi.name if a.process_kpi else None,
            "assignee_ids": [x["id"] for x in assignees],
            "assignees": assignees,
            "first_assignee_id": a.first_assignee_id,
            "reminder_offsets": [int(r.minutes_before) for r in sorted(a.reminders, key=lambda z: z.minutes_before, reverse=True)],
            "monthly_tracks": tracks_map,
            "can_manage": bool(can_manage),
        })

    process_users = []
    seen_uids = set()
    for u in (p.leaders + p.members + p.owners):
        if not u or not u.is_active or int(u.id) in seen_uids:
            continue
        seen_uids.add(int(u.id))
        full_name = (f"{(u.first_name or '').strip()} {(u.last_name or '').strip()}").strip() or (u.email or "")
        process_users.append({"id": int(u.id), "full_name": full_name, "email": u.email})

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
        "process_users": process_users,
        "favorite_kpi_ids": list(favorite_kpi_ids),
        "permissions": {
            "can_crud_pg": user_can_crud_pg_and_activity(current_user, p),
            "can_enter_pgv": user_can_enter_pgv(current_user, p),
            "can_crud_activity": _user_can_add_activity(current_user, p),
            "can_track_activity": user_can_access_process(current_user, p),
        },
    })


@app_bp.route("/process/api/karne/<int:process_id>/export-xlsx", methods=["POST"])
@login_required
def surec_api_karne_export_xlsx(process_id):
    """Karne tablosunu istemcinin ürettiği başlık/satırlarla gerçek .xlsx olarak döner."""
    p = _process_for_user(process_id)
    if not p or not user_can_access_process(current_user, p):
        abort(403)
    payload = request.get_json() or {}
    headers = payload.get("headers")
    rows = payload.get("rows")
    year = payload.get("year", "")
    if not isinstance(headers, list) or not isinstance(rows, list):
        return jsonify({"success": False, "message": "Geçersiz istek gövdesi."}), 400
    if len(headers) > 200 or len(rows) > 2000:
        return jsonify({"success": False, "message": "Çok fazla sütun veya satır."}), 400
    try:
        from openpyxl import Workbook
    except ImportError:
        current_app.logger.error("[surec_api_karne_export_xlsx] openpyxl yok")
        return jsonify({"success": False, "message": "Sunucuda Excel dışa aktarma kullanılamıyor."}), 500

    wb = Workbook()
    ws = wb.active
    ws.title = "Karne"

    def _cell(v):
        if v is None:
            return ""
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            return v
        return str(v)

    ws.append([_cell(h) for h in headers])
    nh = len(headers)
    for raw in rows:
        if not isinstance(raw, list):
            continue
        line = [_cell(raw[i]) if i < len(raw) else "" for i in range(nh)]
        ws.append(line)

    bio = BytesIO()
    wb.save(bio)
    bio.seek(0)
    base = f"surec_karne_{p.id}_{year}"
    try:
        from werkzeug.utils import secure_filename

        fname = secure_filename(base) or base
    except Exception:
        fname = base
    if not fname.endswith(".xlsx"):
        fname = f"{fname}.xlsx"
    return send_file(
        bio,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=fname,
    )


# ── Eski URL uyumluluğu: /surec → /process (307: POST gövdesi korunur) ──


@app_bp.route("/surec")
@app_bp.route("/surec/")
def surec_legacy_index_redirect():
    target = "/process"
    qs = request.query_string.decode() if request.query_string else ""
    if qs:
        target = f"{target}?{qs}"
    return redirect(target, code=307)


@app_bp.route("/surec/<path:subpath>")
def surec_legacy_path_redirect(subpath):
    target = f"/process/{subpath}"
    qs = request.query_string.decode() if request.query_string else ""
    if qs:
        target = f"{target}?{qs}"
    return redirect(target, code=307)

