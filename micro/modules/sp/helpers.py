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
    """Strateji haritası vis-network düğüm/kenar listesi.

    Hiyerarşi (level):
      0 — Vizyon
      1 — Ana Strateji
      2 — Alt Strateji
      3 — Süreç  |  Stratejik Girişim
      4 — PG     |  Proje
    """
    import app.models.process  # noqa: F401
    from app.models.process import ProcessSubStrategyLink

    nodes: list[dict] = []
    edges: list[dict] = []
    seen_proc: set[str] = set()
    seen_pg:   set[str] = set()

    # ── 0. Vizyon düğümü ──────────────────────────────────────────────────────
    vizyon_text = "Vizyon"
    try:
        py = PlanYear.query.filter_by(tenant_id=tenant_id, is_active=True).order_by(PlanYear.id.desc()).first()
        if py:
            tyi = TenantYearIdentity.query.filter_by(plan_year_id=py.id, tenant_id=tenant_id).first()
            if tyi and tyi.vision:
                vizyon_text = tyi.vision
    except Exception:
        pass

    nodes.append({
        "id": "vizyon",
        "label": _harita_short_label(vizyon_text, 44),
        "group": "vizyon",
        "level": 0,
        "title": vizyon_text,
    })

    # ── 1-3. Strateji → Alt Strateji → Süreç → PG ────────────────────────────
    for s in strategies:
        s_id = f"s_{s.id}"
        full = f"{s.code or ''} {s.title or ''}".strip() or f"Strateji #{s.id}"
        label = _harita_short_label(full, 38)
        if s.code and s.title:
            label = f"{s.code}\n{_harita_short_label(s.title, 30)}"
        nodes.append({"id": s_id, "label": label, "group": "strategy", "level": 1, "title": full})
        edges.append({"from": "vizyon", "to": s_id})

        for ss in (s.sub_strategies or []):
            if not getattr(ss, "is_active", True):
                continue
            ss_id = f"ss_{ss.id}"
            ss_full = f"{ss.code or ''} {ss.title or ''}".strip() or f"Alt #{ss.id}"
            nodes.append({
                "id": ss_id,
                "label": _harita_short_label(ss_full, 32),
                "group": "sub_strategy",
                "level": 2,
                "title": ss_full,
            })
            edges.append({"from": s_id, "to": ss_id})

            processes = (
                Process.query.filter_by(is_active=True, tenant_id=tenant_id)
                .join(ProcessSubStrategyLink, ProcessSubStrategyLink.process_id == Process.id)
                .filter(ProcessSubStrategyLink.sub_strategy_id == ss.id)
                .limit(12)
                .all()
            )
            for proc in processes:
                p_id = f"p_{proc.id}"
                edges.append({"from": ss_id, "to": p_id})
                if p_id in seen_proc:
                    continue  # süreç düğümü + PG'ler zaten eklendi
                seen_proc.add(p_id)
                proc_full = f"{proc.code or ''} {proc.name or ''}".strip() or proc.name
                nodes.append({
                    "id": p_id,
                    "label": _harita_short_label(proc_full, 26),
                    "group": "process",
                    "level": 3,
                    "title": proc_full,
                })

                # Bireysel PG'ler (max 7 adet, süreç başına bir kez)
                pgs = ProcessKpi.query.filter_by(process_id=proc.id, is_active=True).limit(7).all()
                for pg in pgs:
                    pg_id = f"pg_{pg.id}"
                    if pg_id not in seen_pg:
                        seen_pg.add(pg_id)
                        pg_label = pg.code or _harita_short_label(pg.name or "", 20)
                        nodes.append({
                            "id": pg_id,
                            "label": pg_label,
                            "group": "pg",
                            "level": 4,
                            "title": f"{pg.code or ''} {pg.name or ''}".strip(),
                        })
                    edges.append({"from": p_id, "to": pg_id})

                # Fazla PG özet düğümü (süreç başına bir kez)
                total_pg = ProcessKpi.query.filter_by(process_id=proc.id, is_active=True).count()
                if total_pg > 7:
                    more_id = f"pg_more_{proc.id}"
                    nodes.append({
                        "id": more_id,
                        "label": f"+{total_pg - 7} PG",
                        "group": "pg_more",
                        "level": 4,
                        "title": f"{proc.name}: toplam {total_pg} PG",
                    })
                    edges.append({"from": p_id, "to": more_id})

    # ── Stratejik Girişimler (level 3) ────────────────────────────────────────
    init_ids: list[int] = []
    try:
        from app.models.initiative import Initiative
        inits = Initiative.query.filter_by(tenant_id=tenant_id, is_active=True).all()
        for init in inits:
            i_id = f"init_{init.id}"
            init_ids.append(init.id)
            i_label = _harita_short_label(init.name or f"Girişim #{init.id}", 28)
            nodes.append({
                "id": i_id,
                "label": f"⚡ {i_label}",
                "group": "initiative",
                "level": 3,
                "title": f"{init.name} ({init.start_year}–{init.end_year}) • %{int(init.progress_pct or 0)}",
            })
            if init.sub_strategy_id:
                edges.append({"from": f"ss_{init.sub_strategy_id}", "to": i_id, "dashes": True})
            elif init.strategy_id:
                edges.append({"from": f"s_{init.strategy_id}", "to": i_id, "dashes": True})
    except Exception:
        pass

    # ── Projeler (level 4, Girişime bağlı) ───────────────────────────────────
    if init_ids:
        try:
            from app.models.portfolio_project import Project as PortfolioProject
            projs = (
                PortfolioProject.query
                .filter(
                    PortfolioProject.tenant_id == tenant_id,
                    PortfolioProject.is_active == True,
                    PortfolioProject.initiative_id.in_(init_ids),
                )
                .limit(60)
                .all()
            )
            for proj in projs:
                pj_id = f"proj_{proj.id}"
                nodes.append({
                    "id": pj_id,
                    "label": _harita_short_label(proj.name or f"Proje #{proj.id}", 26),
                    "group": "proje",
                    "level": 4,
                    "title": proj.name or f"Proje #{proj.id}",
                })
                edges.append({"from": f"init_{proj.initiative_id}", "to": pj_id, "dashes": True})
        except Exception:
            pass

    meta = {
        "sub":        sum(1 for n in nodes if n["group"] == "sub_strategy"),
        "process":    sum(1 for n in nodes if n["group"] == "process"),
        "pg":         sum(1 for n in nodes if n["group"] == "pg"),
        "initiative": sum(1 for n in nodes if n["group"] == "initiative"),
        "proje":      sum(1 for n in nodes if n["group"] == "proje"),
    }
    return {"success": True, "nodes": nodes, "edges": edges, "meta": meta}
