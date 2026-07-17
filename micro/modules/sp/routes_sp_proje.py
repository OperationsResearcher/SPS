"""Stratejik Planlama — SP proje ve görev API."""

from flask_babel import gettext as _


def _try_int(val):
    try:
        return int(val)
    except (TypeError, ValueError):
        return None
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
    _require_plan_year,
    _plan_year_to_dict,
    _plan_project_to_dict,
    _plan_task_to_dict,
)

@app_bp.route("/k-plan/strategy/api/project", methods=["GET"])
@login_required
def sp_api_proje_list():
    """Aktif dönemin projelerini listeler."""
    py, err = _require_plan_year()
    if err:
        return err
    items = PlanProject.query.filter_by(
        tenant_id=current_user.tenant_id,
        plan_year_id=py.id,
        is_active=True,
    ).order_by(PlanProject.id).all()
    return jsonify({"success": True, "items": [_plan_project_to_dict(p) for p in items]})


@app_bp.route("/k-plan/strategy/api/project", methods=["POST"])
@csrf.exempt
@login_required
@sp_manage_required
def sp_api_proje_save():
    """Proje ekle veya güncelle."""
    py, err = _require_plan_year()
    if err:
        return err
    data = request.get_json() or {}
    item_id = data.get("id")
    try:
        if item_id:
            obj = PlanProject.query.filter_by(
                id=item_id, tenant_id=current_user.tenant_id
            ).first_or_404()
        else:
            obj = PlanProject(tenant_id=current_user.tenant_id, plan_year_id=py.id)
            db.session.add(obj)
        name = (data.get("name") or "").strip()
        if not name:
            return jsonify({"success": False, "message": _("Proje adı zorunludur.")}), 400
        obj.name        = name
        obj.description = data.get("description", obj.description)
        obj.status      = data.get("status", obj.status) or "Planlandı"
        obj.progress    = _try_int(data.get("progress")) if data.get("progress") is not None else obj.progress
        if data.get("start_date"):
            from datetime import datetime as _dt
            obj.start_date = _dt.strptime(data["start_date"], "%Y-%m-%d").date()
        if data.get("end_date"):
            from datetime import datetime as _dt
            obj.end_date = _dt.strptime(data["end_date"], "%Y-%m-%d").date()
        db.session.commit()
        return jsonify({"success": True, "message": "Proje kaydedildi.", "id": obj.id})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[sp_api_proje_save] {e}")
        return jsonify({"success": False, "message": _("Kayıt sırasında hata oluştu.")}), 500


@app_bp.route("/k-plan/strategy/api/project/<int:item_id>", methods=["DELETE"])
@csrf.exempt
@login_required
@sp_manage_required
def sp_api_proje_delete(item_id):
    obj = PlanProject.query.filter_by(
        id=item_id, tenant_id=current_user.tenant_id
    ).first_or_404()
    try:
        obj.is_active = False
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[sp_api_proje_delete] {e}")
        return jsonify({"success": False, "message": _("Silme hatası.")}), 500


# ── Proje Görevleri ────────────────────────────────────────────────────────────

@app_bp.route("/k-plan/strategy/api/project/<int:project_id>/task", methods=["GET"])
@login_required
def sp_api_proje_gorev_list(project_id):
    proj = PlanProject.query.filter_by(
        id=project_id, tenant_id=current_user.tenant_id, is_active=True
    ).first_or_404()
    items = PlanProjectTask.query.filter_by(
        project_id=proj.id, is_active=True
    ).order_by(PlanProjectTask.id).all()
    return jsonify({"success": True, "items": [_plan_task_to_dict(t) for t in items]})


@app_bp.route("/k-plan/strategy/api/project/<int:project_id>/task", methods=["POST"])
@csrf.exempt
@login_required
@sp_manage_required
def sp_api_proje_gorev_save(project_id):
    proj = PlanProject.query.filter_by(
        id=project_id, tenant_id=current_user.tenant_id, is_active=True
    ).first_or_404()
    data = request.get_json() or {}
    item_id = data.get("id")
    try:
        if item_id:
            obj = PlanProjectTask.query.filter_by(
                id=item_id, project_id=proj.id
            ).first_or_404()
        else:
            obj = PlanProjectTask(
                project_id=proj.id,
                plan_year_id=proj.plan_year_id,
            )
            db.session.add(obj)
        name = (data.get("name") or "").strip()
        if not name:
            return jsonify({"success": False, "message": _("Görev adı zorunludur.")}), 400
        obj.name        = name
        obj.description = data.get("description", obj.description)
        obj.status      = data.get("status", obj.status) or "Planlandı"
        obj.assignee_id = data.get("assignee_id") or obj.assignee_id
        if data.get("start_date"):
            from datetime import datetime as _dt
            obj.start_date = _dt.strptime(data["start_date"], "%Y-%m-%d").date()
        if data.get("end_date"):
            from datetime import datetime as _dt
            obj.end_date = _dt.strptime(data["end_date"], "%Y-%m-%d").date()
        db.session.commit()
        return jsonify({"success": True, "message": _("Görev kaydedildi."), "id": obj.id})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[sp_api_proje_gorev_save] {e}")
        return jsonify({"success": False, "message": _("Kayıt hatası.")}), 500


@app_bp.route("/k-plan/strategy/api/project/task/<int:task_id>", methods=["DELETE"])
@csrf.exempt
@login_required
@sp_manage_required
def sp_api_proje_gorev_delete(task_id):
    obj = PlanProjectTask.query.filter_by(id=task_id).first_or_404()
    proj = PlanProject.query.filter_by(
        id=obj.project_id, tenant_id=current_user.tenant_id
    ).first_or_404()
    try:
        obj.is_active = False
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[sp_api_proje_gorev_delete] {e}")
        return jsonify({"success": False, "message": _("Silme hatası.")}), 500
