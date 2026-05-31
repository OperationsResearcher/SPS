"""Süreç modülü — ortak yardımcılar ve importlar."""

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


def _parent_options_with_depth(tenant_id: int, plan_year_id: int | None = None):
    """Üst süreç seçici — tenant’taki tüm aktif süreçler (hiyerarşi ile)."""
    q = Process.query.filter_by(tenant_id=tenant_id, is_active=True)
    if plan_year_id is not None:
        q = q.filter(Process.plan_year_id == plan_year_id)
    all_p = q.order_by(Process.code).all()
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
