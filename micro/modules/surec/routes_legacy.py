"""Süreç modülü — Eski /surec URL yönlendirmeleri."""

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

