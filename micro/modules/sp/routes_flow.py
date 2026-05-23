"""Stratejik Planlama — Strateji akışı sayfaları ve graf."""

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

@app_bp.route("/sp/flow")
@login_required
def sp_flow():
    """Stratejik planlama akış özet sayfası."""
    tid = current_user.tenant_id
    active_py = get_active_plan_year_for_user(current_user)
    strat_base = Strategy.query.filter_by(tenant_id=tid, is_active=True)
    proc_base = Process.query.filter_by(tenant_id=tid, is_active=True)
    if active_py:
        strat_base = strat_base.filter(
            or_(Strategy.plan_year_id == active_py.id, Strategy.plan_year_id == None))
        proc_base = proc_base.filter(
            or_(Process.plan_year_id == active_py.id, Process.plan_year_id == None))
    strategy_count = strat_base.count()
    process_count = proc_base.count()
    sub_strategy_count = (
        SubStrategy.query
        .join(Strategy)
        .filter(Strategy.tenant_id == tid, SubStrategy.is_active == True,
                *([or_(Strategy.plan_year_id == active_py.id, Strategy.plan_year_id == None)]
                  if active_py else []))
        .count()
    )
    tenant = current_user.tenant
    return render_template(
        "platform/sp/flow.html",
        tenant=tenant,
        strategy_count=strategy_count,
        sub_strategy_count=sub_strategy_count,
        process_count=process_count,
    )


@app_bp.route("/sp/flow/dynamic")
@login_required
def sp_flow_dynamic():
    """İnteraktif node-edge görselleştirme sayfası."""
    return render_template("platform/sp/dynamic_flow.html")


# ── API: Graf verisi ──────────────────────────────────────────────────────────

@app_bp.route("/sp/api/graph")
@login_required
def sp_api_graph():
    """Vizyon/strateji/alt-strateji/süreç/KPI node ve edge'lerini JSON döndür.

    Sprint 6: Performans koruması — büyük tenant'larda (Tomofil gibi multi-year
    clone'lu) limit zorunlu. Default 500 node, max 2000.
    """
    # Admin başka tenant'ı sorgulayabilir
    if current_user.role and current_user.role.name == "Admin":
        tid = request.args.get("tenant_id", current_user.tenant_id, type=int)
    else:
        tid = current_user.tenant_id

    # Performans limit
    node_limit = request.args.get("limit", 500, type=int)
    node_limit = max(50, min(node_limit, 2000))  # clamp [50, 2000]

    tenant = Tenant.query.get_or_404(tid)

    active_py = get_active_plan_year_for_user(current_user)

    # Sprint 1.5 plan_year filter helper kullanımı
    from app.utils.plan_year_filter import filter_by_plan_year

    strat_q = (
        Strategy.query
        .options(selectinload(Strategy.sub_strategies))
        .filter_by(tenant_id=tid, is_active=True)
    )
    if active_py:
        strat_q = filter_by_plan_year(strat_q, Strategy, active_py.id, include_null=True)
    strategies = strat_q.all()
    proc_q = Process.query.filter_by(tenant_id=tid, is_active=True)
    if active_py:
        proc_q = filter_by_plan_year(proc_q, Process, active_py.id, include_null=True)
    processes = proc_q.limit(node_limit).all()

    nodes = []
    edges = []

    # Vizyon node
    nodes.append({"id": "vision", "label": tenant.vision or tenant.name, "type": "vision"})

    for st in strategies:
        st_node_id = f"st_{st.id}"
        nodes.append({"id": st_node_id, "label": f"{st.code or ''} {st.title}".strip(), "type": "strategy"})
        edges.append({"from": "vision", "to": st_node_id})

        for ss in st.sub_strategies:
            if not ss.is_active:
                continue
            ss_node_id = f"ss_{ss.id}"
            nodes.append({"id": ss_node_id, "label": f"{ss.code or ''} {ss.title}".strip(), "type": "sub_strategy"})
            edges.append({"from": st_node_id, "to": ss_node_id})

    for proc in processes:
        p_node_id = f"proc_{proc.id}"
        nodes.append({"id": p_node_id, "label": f"{proc.code or ''} {proc.name}".strip(), "type": "process"})
        # Süreci bağlı alt stratejilere bağla
        for link in proc.process_sub_strategy_links:
            ss_node_id = f"ss_{link.sub_strategy_id}"
            edges.append({"from": ss_node_id, "to": p_node_id})

        kpis = ProcessKpi.query.filter_by(process_id=proc.id, is_active=True).all()
        for k in kpis:
            k_node_id = f"kpi_{k.id}"
            nodes.append({"id": k_node_id, "label": k.name, "type": "kpi"})
            edges.append({"from": p_node_id, "to": k_node_id})

    try:
        from app.services.score_engine_service import compute_vision_score
        _graph_py = get_active_plan_year_for_user(current_user)
        vision_score = compute_vision_score(tid, plan_year=_graph_py)
    except Exception as e:
        current_app.logger.warning(f"[sp_api_graph] score_engine: {e}")
        vision_score = None

    return jsonify({
        "success": True,
        "nodes": nodes,
        "edges": edges,
        "vision_score": vision_score,
    })


# ═══════════════════════════════════════════════════════════════════════════════
# PLAN YEAR API — Yıllık Stratejik Plan Dönem Yönetimi
# ═══════════════════════════════════════════════════════════════════════════════
