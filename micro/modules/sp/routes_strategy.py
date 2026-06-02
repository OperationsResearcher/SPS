"""Stratejik Planlama — Strateji ve alt strateji API."""

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
from app.constants.roles import PRIVILEGED_ROLES as _PRIVILEGED_ROLES_SET

# Legacy sistem rolleri de dahil (sistem_rol dönüşümü)
_SP_ROLES = _PRIVILEGED_ROLES_SET | {"admin", "kurum_yoneticisi", "ust_yonetim"}
from micro.modules.sp.helpers import (
    _check_sp_role,
    sp_manage_required,
    _plan_year_to_dict,
    _plan_project_to_dict,
    _plan_task_to_dict,
)

@app_bp.route("/sp/api/strategy/add", methods=["POST"])
@csrf.exempt
@login_required
@sp_manage_required
def sp_add_strategy():
    """Ana strateji ekle."""
    data = request.get_json() or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"success": False, "message": "Strateji adı zorunludur."}), 400

    tenant_id = current_user.tenant_id
    if not tenant_id:
        return jsonify({"success": False, "message": "Kurum (tenant) bilgisi eksik."}), 400

    active_py = get_active_plan_year_for_user(current_user)

    def _make_strategy():
        return Strategy(
            tenant_id=tenant_id,
            title=title,
            code=(data.get("code") or "").strip() or None,
            description=(data.get("description") or "").strip() or None,
            plan_year_id=active_py.id if active_py else None,
        )

    try:
        new_strategy = _make_strategy()
        db.session.add(new_strategy)
        db.session.commit()
        return jsonify({"success": True, "message": "Strateji eklendi.", "id": new_strategy.id})
    except Exception as e:
        db.session.rollback()
        if is_pk_duplicate(e, "strategies"):
            try:
                sync_pg_sequence_if_needed("strategies", "id")
                new_strategy = _make_strategy()
                db.session.add(new_strategy)
                db.session.commit()
                return jsonify({"success": True, "message": "Strateji eklendi.", "id": new_strategy.id})
            except Exception as e2:
                db.session.rollback()
                current_app.logger.error(f"[sp_add_strategy/retry] {e2}")
        current_app.logger.error(f"[sp_add_strategy] {e}")
        return jsonify({"success": False, "message": "Kayıt sırasında hata oluştu."}), 500


@app_bp.route("/sp/api/strategy/update/<int:strategy_id>", methods=["POST"])
@csrf.exempt
@login_required
@sp_manage_required
def sp_update_strategy(strategy_id):
    """Ana strateji güncelle."""
    st = Strategy.query.filter_by(
        id=strategy_id, tenant_id=current_user.tenant_id, is_active=True
    ).first_or_404()
    data = request.get_json() or {}
    tid = current_user.tenant_id
    tenant = Tenant.query.get(tid) if tid else None
    try:
        if "title" in data:
            t = (data.get("title") or "").strip()
            if not t:
                return jsonify({"success": False, "message": "Başlık boş olamaz."}), 400
            st.title = t
        if "code" in data:
            st.code = (data.get("code") or "").strip() or None
        if "description" in data:
            st.description = (data.get("description") or "").strip() or None
        if tenant and tenant.k_vektor_enabled and "k_vektor_weight_raw" in data:
            err = apply_single_strategy_k_vektor_weight(
                tid, current_user.id, strategy_id, data.get("k_vektor_weight_raw")
            )
            if err:
                db.session.rollback()
                return jsonify({"success": False, "message": err}), 400
        db.session.commit()
        return jsonify({"success": True, "message": "Ana strateji güncellendi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[sp_update_strategy] {e}")
        return jsonify({"success": False, "message": "Güncelleme sırasında hata oluştu."}), 500


@app_bp.route("/sp/api/strategy/delete/<int:strategy_id>", methods=["POST"])
@csrf.exempt
@login_required
@sp_manage_required
def sp_delete_strategy(strategy_id):
    """Ana strateji sil (soft delete)."""
    st = Strategy.query.filter_by(
        id=strategy_id, tenant_id=current_user.tenant_id
    ).first_or_404()
    try:
        st.is_active = False
        db.session.commit()
        return jsonify({"success": True, "message": "Strateji silindi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[sp_delete_strategy] {e}")
        return jsonify({"success": False, "message": "Silme sırasında hata oluştu."}), 500


# ── API: Alt Strateji CRUD ────────────────────────────────────────────────────

@app_bp.route("/sp/api/sub-strategy/add", methods=["POST"])
@csrf.exempt
@login_required
@sp_manage_required
def sp_add_sub_strategy():
    """Alt strateji ekle."""
    data = request.get_json() or {}
    raw_sid = data.get("strategy_id")
    title = (data.get("title") or "").strip()
    if not raw_sid or not title:
        return jsonify({"success": False, "message": "Strateji ve başlık zorunludur."}), 400

    try:
        strategy_id = int(raw_sid)
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "Geçersiz strateji numarası."}), 400

    parent = Strategy.query.filter_by(
        id=strategy_id, tenant_id=current_user.tenant_id, is_active=True
    ).first_or_404()

    active_py = get_active_plan_year_for_user(current_user)

    def _make_sub():
        return SubStrategy(
            strategy_id=parent.id,
            title=title,
            code=(data.get("code") or "").strip() or None,
            description=(data.get("description") or "").strip() or None,
            plan_year_id=active_py.id if active_py else None,
        )

    try:
        sub = _make_sub()
        db.session.add(sub)
        db.session.commit()
        return jsonify({"success": True, "message": "Alt strateji eklendi.", "id": sub.id})
    except Exception as e:
        db.session.rollback()
        if is_pk_duplicate(e, "sub_strategies"):
            try:
                sync_pg_sequence_if_needed("sub_strategies", "id")
                sub = _make_sub()
                db.session.add(sub)
                db.session.commit()
                return jsonify({"success": True, "message": "Alt strateji eklendi.", "id": sub.id})
            except Exception as e2:
                db.session.rollback()
                current_app.logger.error(f"[sp_add_sub_strategy/retry] {e2}")
        current_app.logger.error(f"[sp_add_sub_strategy] {e}")
        return jsonify({"success": False, "message": "Kayıt sırasında hata oluştu."}), 500


@app_bp.route("/sp/api/sub-strategy/update/<int:sub_id>", methods=["POST"])
@csrf.exempt
@login_required
@sp_manage_required
def sp_update_sub_strategy(sub_id):
    """Alt strateji güncelle."""
    sub = SubStrategy.query.join(Strategy).filter(
        SubStrategy.id == sub_id,
        Strategy.tenant_id == current_user.tenant_id,
        SubStrategy.is_active.is_(True),
    ).first_or_404()

    data = request.get_json() or {}
    tid = current_user.tenant_id
    tenant = Tenant.query.get(tid) if tid else None
    try:
        sub.title = (data.get("title") or sub.title).strip()
        sub.code = (data.get("code") or "").strip() or sub.code
        sub.description = data.get("description", sub.description)
        if tenant and tenant.k_vektor_enabled and "k_vektor_weight_raw" in data:
            err = apply_single_sub_strategy_k_vektor_weight(
                tid, current_user.id, sub_id, data.get("k_vektor_weight_raw")
            )
            if err:
                db.session.rollback()
                return jsonify({"success": False, "message": err}), 400
        db.session.commit()
        return jsonify({"success": True, "message": "Alt strateji güncellendi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[sp_update_sub_strategy] {e}")
        return jsonify({"success": False, "message": "Güncelleme sırasında hata oluştu."}), 500


@app_bp.route("/sp/api/sub-strategy/delete/<int:sub_id>", methods=["POST"])
@csrf.exempt
@login_required
@sp_manage_required
def sp_delete_sub_strategy(sub_id):
    """Alt strateji soft delete."""
    sub = SubStrategy.query.join(Strategy).filter(
        SubStrategy.id == sub_id,
        Strategy.tenant_id == current_user.tenant_id,
    ).first_or_404()
    try:
        sub.is_active = False
        db.session.commit()
        return jsonify({"success": True, "message": "Alt strateji silindi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[sp_delete_sub_strategy] {e}")
        return jsonify({"success": False, "message": "Silme sırasında hata oluştu."}), 500


# ── Akış Sayfaları ────────────────────────────────────────────────────────────
