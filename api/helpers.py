# -*- coding: utf-8 -*-
"""
API Routes - Süreç Karnesi Endpoint'leri
"""
from flask import Blueprint, jsonify, request, current_app, send_file
from werkzeug.utils import secure_filename
import os
import uuid
from flask_login import login_required, current_user
from extensions import csrf
from app.utils.project_rbac import project_access_required, project_manager_required, project_member_required, project_observer_allowed, role_required


def _invalidate_executive_dashboard_cache(kurum_id: int | None = None):
    """Executive dashboard cache invalidation placeholder.

    Not all deployments use a cache layer; this prevents runtime errors where
    the function is referenced.
    """
    try:
        # If a caching layer is introduced later, invalidate here.
        return
    except Exception:
        return
from extensions import db
from app.models.portfolio_project import (
    Project,
    Task,
    TaskImpact,
    TaskComment,
    TaskMention,
    ProjectFile,
    Tag,
    TaskSubtask,
    TimeEntry,
    TaskActivity,
    ProjectTemplate,
    TaskTemplate,
    Sprint,
    TaskSprint,
    ProjectRisk,
    TaskDependency,
    IntegrationHook,
    RuleDefinition,
    SLA,
    RecurringTask,
    WorkingDay,
    CapacityPlan,
    RaidItem,
    TaskBaseline,
    project_leaders,
    task_predecessors,
)
from app.models.legacy_bridge import (
    User, Kurum, Surec, AnaStrateji, AltStrateji,
    BireyselFaaliyet, BireyselPerformansGostergesi,
    PerformansGostergeVeri, PerformansGostergeVeriAudit, SurecPerformansGostergesi, SurecFaaliyet,
    FaaliyetTakip, surec_liderleri, surec_uyeleri,
    Notification, UserActivityLog, FavoriKPI, DashboardLayout,
    KullaniciYetki,
)
from sqlalchemy import or_, and_, text, delete, insert
from sqlalchemy.orm import joinedload


def _resolve_project_leader_ids_api(data: dict, kurum_id: int) -> list:
    """JSON: manager_ids (liste) veya geriye dönük manager_id (tek)."""
    out: list = []
    raw = data.get("manager_ids")
    if isinstance(raw, list):
        for x in raw:
            try:
                out.append(int(x))
            except (TypeError, ValueError):
                continue
    elif data.get("manager_id") is not None:
        try:
            out.append(int(data["manager_id"]))
        except (TypeError, ValueError):
            pass
    seen_ids = set()
    result: list = []
    for uid in out:
        if uid in seen_ids:
            continue
        u = User.query.get(uid)
        if u and getattr(u, "kurum_id", None) == kurum_id:
            seen_ids.add(uid)
            result.append(uid)
    return result


def _sync_project_leaders_api(project: Project, kurum_id: int, leader_ids: list) -> None:
    if not leader_ids:
        return
    db.session.execute(delete(project_leaders).where(project_leaders.c.project_id == project.id))
    for uid in leader_ids:
        u = User.query.get(uid)
        if u and getattr(u, "kurum_id", None) == kurum_id:
            db.session.execute(insert(project_leaders).values(project_id=project.id, user_id=uid))
    project.manager_id = leader_ids[0]


from services.performance_service import (
    generatePeriyotVerileri, calculateHedefDeger, hesapla_durum,
    get_ceyrek_aylari, get_ay_ceyreği, get_ay_haftalari, get_ay_gunleri
)
from services.cpm_service import compute_cpm
from services.burn_service import burn_charts
from services.rule_engine_service import list_rules, save_rule, evaluate_rules
from services.digest_service import project_digest
from utils.karne_hesaplamalar import (
    hesapla_basari_puani, hesapla_agirlikli_basari_puani,
    hesapla_onceki_yil_ortalamasi, parse_basari_puani_araliklari
)
from datetime import datetime, timedelta, date
from utils.telemetry import log_event
from werkzeug.security import generate_password_hash
from io import BytesIO
from werkzeug.utils import secure_filename
import os
import uuid
import mimetypes
import json
import re


def _notify_project_team_changes_api(
    project: Project,
    kurum_id: int,
    old_leader_ids: set,
    old_member_ids: set,
) -> None:
    """Yeni atanan proje liderleri ve üyelerine uygulama içi + e-posta bildirimi."""
    try:
        from app.models.core import User as CoreUser
        from app_platform.services.notification_triggers import (
            notify_project_leaders_added,
            notify_project_members_added,
        )
    except Exception:
        return
    actor = CoreUser.query.get(current_user.id)
    if not actor:
        return
    new_l = set(project.leader_user_ids())
    new_m = set(project.member_user_ids())
    notify_project_leaders_added(project, list(new_l - old_leader_ids), actor, kurum_id)
    notify_project_members_added(project, list(new_m - old_member_ids), actor, kurum_id)


def _parse_date_safe(val):
    if not val:
        return None
    if isinstance(val, date) and not isinstance(val, datetime):
        return val
    if isinstance(val, datetime):
        return val.date()
    try:
        return datetime.strptime(str(val), '%Y-%m-%d').date()
    except Exception:
        return None

