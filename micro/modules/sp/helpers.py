"""SP modülü — ortak yardımcılar."""

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
def _check_sp_role(user=None):
    """SP sayfasında düzenleme / silme yetkisi olan roller."""
    u = user or current_user
    return u.role and u.role.name in _SP_ROLES


def sp_manage_required(f):
    """SP CRUD API uçları için merkezi yetki kontrolü (403 JSON)."""

    @wraps(f)
    def decorated(*args, **kwargs):
        if not _check_sp_role():
            return jsonify({"success": False, "message": "Yetkisiz işlem."}), 403
        return f(*args, **kwargs)

    return decorated


def _plan_year_to_dict(py: PlanYear) -> dict:
    return {
        "id": py.id,
        "year": py.year,
        "name": py.name or f"{py.year} Stratejik Planı",
        "status": py.status,
        "template_source_id": py.template_source_id,
        "created_at": py.created_at.isoformat() if py.created_at else None,
        "closed_at": py.closed_at.isoformat() if py.closed_at else None,
    }


def _plan_project_to_dict(p):
    return {
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "status": p.status,
        "progress": p.progress,
        "start_date": str(p.start_date) if p.start_date else None,
        "end_date": str(p.end_date) if p.end_date else None,
        "plan_year_id": p.plan_year_id,
    }


def _plan_task_to_dict(t):
    return {
        "id": t.id,
        "name": t.name,
        "description": t.description,
        "status": t.status,
        "assignee_id": t.assignee_id,
        "start_date": str(t.start_date) if t.start_date else None,
        "end_date": str(t.end_date) if t.end_date else None,
    }


def load_sp_strategies_for_user(user):
    """SP ana sayfa ile aynı strateji listesi (aktif plan yılı + geri dönüş)."""
    tenant_id = getattr(user, "tenant_id", None) or getattr(user, "kurum_id", None)
    if not tenant_id:
        return []

    active_py = get_active_plan_year_for_user(user)
    strat_q = (
        Strategy.query.options(selectinload(Strategy.sub_strategies))
        .filter_by(tenant_id=tenant_id, is_active=True)
        .order_by(Strategy.code)
    )

    if active_py:
        try:
            strat_q_year = strat_q.filter(
                or_(Strategy.plan_year_id == active_py.id, Strategy.plan_year_id.is_(None))
            )
            strategies = strat_q_year.all()
        except Exception:
            db.session.rollback()
            strategies = strat_q.all()

        if not strategies:
            from sqlalchemy import func as _func

            try:
                best = (
                    db.session.query(Strategy.plan_year_id, _func.count(Strategy.id).label("cnt"))
                    .filter(
                        Strategy.tenant_id == tenant_id,
                        Strategy.is_active.is_(True),
                        Strategy.plan_year_id.isnot(None),
                    )
                    .group_by(Strategy.plan_year_id)
                    .order_by(_func.count(Strategy.id).desc())
                    .first()
                )
                if best:
                    strategies = strat_q.filter(Strategy.plan_year_id == best[0]).all()
            except Exception:
                db.session.rollback()
                strategies = strat_q.all()
    else:
        strategies = strat_q.all()

    return strategies


def _harita_short_label(text: str, max_len: int = 36) -> str:
    """Graf düğüm etiketlerini okunaklı kısalt."""
    t = " ".join((text or "").split())
    if len(t) <= max_len:
        return t
    return t[: max_len - 1].rstrip() + "…"


def build_strateji_harita_graph(tenant_id: int, strategies: list) -> dict:
    """Strateji haritası vis-network düğüm/kenar listesi."""
    import app.models.process  # noqa: F401 — SubStrategy.processes proxy
    from app.models.process import ProcessSubStrategyLink

    nodes, edges = [], []
    seen_process_nodes: set[str] = set()

    for s in strategies:
        s_id = f"s_{s.id}"
        full = f"{s.code or ''} {s.title or ''}".strip() or (s.title or f"Strateji #{s.id}")
        label = _harita_short_label(full, 40)
        if s.code and s.title and len(f"{s.code}\n{s.title}") <= 48:
            label = f"{s.code}\n{_harita_short_label(s.title, 32)}"
        nodes.append({
            "id": s_id,
            "label": label,
            "group": "strategy",
            "title": full,
        })
        for ss in (s.sub_strategies or []):
            if not getattr(ss, "is_active", True):
                continue
            ss_id = f"ss_{ss.id}"
            ss_full = f"{ss.code or ''} {ss.title or ''}".strip() or (ss.title or f"Alt #{ss.id}")
            ss_label = _harita_short_label(ss_full, 34)
            nodes.append({
                "id": ss_id,
                "label": ss_label,
                "group": "sub_strategy",
                "title": ss_full,
            })
            edges.append({"from": s_id, "to": ss_id})

            processes = (
                Process.query.filter_by(is_active=True, tenant_id=tenant_id)
                .join(
                    ProcessSubStrategyLink,
                    ProcessSubStrategyLink.process_id == Process.id,
                )
                .filter(ProcessSubStrategyLink.sub_strategy_id == ss.id)
                .limit(15)
                .all()
            )
            for proc in processes:
                p_id = f"p_{proc.id}"
                if p_id not in seen_process_nodes:
                    seen_process_nodes.add(p_id)
                    proc_full = f"{proc.code or ''} {proc.name or ''}".strip() or proc.name
                    proc_label = _harita_short_label(proc_full, 28)
                    nodes.append({
                        "id": p_id,
                        "label": proc_label,
                        "group": "process",
                        "title": proc_full,
                    })
                edges.append({"from": ss_id, "to": p_id})

                kpi_count = ProcessKpi.query.filter_by(process_id=proc.id, is_active=True).count()
                if kpi_count:
                    k_id = f"kpi_{proc.id}"
                    if not any(n["id"] == k_id for n in nodes):
                        nodes.append({
                            "id": k_id,
                            "label": f"{kpi_count} KPI",
                            "group": "kpi",
                            "title": f"{proc.name}: {kpi_count} gösterge",
                        })
                    edges.append({"from": p_id, "to": k_id})

    # Initiative node'ları (Hamle #3): strategy_id veya sub_strategy_id ile bağlı initiative'leri ekle
    try:
        from app.models.initiative import Initiative
        inits = Initiative.query.filter_by(tenant_id=tenant_id, is_active=True).all()
        for init in inits:
            i_id = f"init_{init.id}"
            i_label = _harita_short_label(init.name or f"Init #{init.id}", 30)
            nodes.append({
                "id": i_id,
                "label": f"🚀 {i_label}",
                "group": "initiative",
                "title": f"{init.name} ({init.start_year}-{init.end_year}) • %{int(init.progress_pct)}",
            })
            if init.sub_strategy_id:
                edges.append({"from": f"ss_{init.sub_strategy_id}", "to": i_id, "dashes": True})
            elif init.strategy_id:
                edges.append({"from": f"s_{init.strategy_id}", "to": i_id, "dashes": True})
    except Exception:
        pass

    meta = {
        "sub": sum(1 for n in nodes if n["group"] == "sub_strategy"),
        "process": sum(1 for n in nodes if n["group"] == "process"),
        "kpi": sum(1 for n in nodes if n["group"] == "kpi"),
        "initiative": sum(1 for n in nodes if n["group"] == "initiative"),
    }
    return {"success": True, "nodes": nodes, "edges": edges, "meta": meta}
