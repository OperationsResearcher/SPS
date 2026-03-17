"""Strategy Blueprint - SWOT Analysis, Strategic Planning Flow."""

from flask import Blueprint, jsonify, render_template, request, url_for
from flask_login import current_user, login_required

from app.models import db
from app.models.strategy import SwotAnalysis
from app.models.core import Strategy, SubStrategy, Tenant
from app.models.process import Process, ProcessKpi, ProcessSubStrategyLink
from app.utils.decorators import require_component
from app.services.score_engine_service import compute_vision_score

strategy_bp = Blueprint("strategy_bp", __name__, url_prefix="/strategy")


@strategy_bp.route("/swot", methods=["GET", "POST"])
@login_required
@require_component("swot_analizi")
def swot():
    """SWOT Analysis - GET lists items, POST adds/deletes via AJAX or form."""
    tenant_id = current_user.tenant_id
    if not tenant_id:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"success": False, "error": "Kurum bulunamadı."}), 400
        return render_template("strategy/swot.html", strengths=[], weaknesses=[], opportunities=[], threats=[])

    if request.method == "POST":
        action = request.form.get("action") or (request.get_json() or {}).get("action")
        if action == "add":
            category = (request.form.get("category") or (request.get_json() or {}).get("category") or "").strip()
            content = (request.form.get("content") or (request.get_json() or {}).get("content") or "").strip()
            if category and content and category in ("strength", "weakness", "opportunity", "threat"):
                item = SwotAnalysis(tenant_id=tenant_id, category=category, content=content, is_active=True)
                db.session.add(item)
                db.session.commit()
                if _is_ajax():
                    return jsonify({"success": True, "id": item.id, "category": category, "content": content})
                from flask import flash, redirect, url_for

                flash("SWOT maddesi eklendi.", "success")
                return redirect(url_for("strategy_bp.swot"))
            if _is_ajax():
                return jsonify({"success": False, "error": "Geçersiz veri."}), 400
        elif action == "delete":
            item_id = request.form.get("id") or (request.get_json() or {}).get("id")
            item = SwotAnalysis.query.filter_by(id=item_id, tenant_id=tenant_id, is_active=True).first()
            if item:
                item.is_active = False
                db.session.commit()
                if _is_ajax():
                    return jsonify({"success": True})
                from flask import flash, redirect, url_for

                flash("SWOT maddesi silindi.", "success")
                return redirect(url_for("strategy_bp.swot"))
            if _is_ajax():
                return jsonify({"success": False, "error": "Kayıt bulunamadı."}), 404

    items = SwotAnalysis.query.filter_by(tenant_id=tenant_id, is_active=True).order_by(SwotAnalysis.created_at).all()
    strengths = [i for i in items if i.category == "strength"]
    weaknesses = [i for i in items if i.category == "weakness"]
    opportunities = [i for i in items if i.category == "opportunity"]
    threats = [i for i in items if i.category == "threat"]
    return render_template(
        "strategy/swot.html",
        strengths=strengths,
        weaknesses=weaknesses,
        opportunities=opportunities,
        threats=threats,
    )


def _is_ajax():
    return request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json


def _resolve_tenant_id_for_flow():
    """Admin can pass tenant_id; others use their own."""
    if current_user.role and current_user.role.name == "Admin":
        tid = request.args.get("tenant_id", type=int)
        if tid:
            return tid
    return current_user.tenant_id


@strategy_bp.route("/strategic-planning-flow")
@login_required
@require_component("dinamik_stratejik_planlama")
def strategic_planning_flow():
    """Stratejik planlama akışı - statik akış sayfası (Değerler, Amaç, Vizyon, SWOT, BSC, Stratejiler, Süreçler)."""
    tenant_id = _resolve_tenant_id_for_flow()
    if not tenant_id:
        return render_template("strategy/strategic_planning_flow.html", tenant=None, error="Kurum bulunamadı.")
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        return render_template("strategy/strategic_planning_flow.html", tenant=None, error="Kurum bulunamadı.")
    swot_count = SwotAnalysis.query.filter_by(tenant_id=tenant_id, is_active=True).count()
    strategies_count = Strategy.query.filter_by(tenant_id=tenant_id, is_active=True).count()
    processes_count = Process.query.filter_by(tenant_id=tenant_id, is_active=True).count()
    return render_template(
        "strategy/strategic_planning_flow.html",
        tenant=tenant,
        swot_count=swot_count,
        strategies_count=strategies_count,
        processes_count=processes_count,
    )


@strategy_bp.route("/strategic-planning-flow/dynamic")
@login_required
@require_component("dinamik_stratejik_planlama")
def strategic_planning_dynamic():
    """Dinamik stratejik planlama akışı - graf görünümü."""
    tenant_id = _resolve_tenant_id_for_flow()
    if not tenant_id:
        return render_template("strategy/dynamic_flow.html", tenant=None, error="Kurum bulunamadı.")
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        return render_template("strategy/dynamic_flow.html", tenant=None, error="Kurum bulunamadı.")
    return render_template("strategy/dynamic_flow.html", tenant=tenant)


@strategy_bp.route("/api/strategic-planning-graph")
@login_required
@require_component("dinamik_stratejik_planlama")
def api_strategic_planning_graph():
    """Dinamik akış için graf verisi (nodes/edges + Score Engine skorları)."""
    tenant_id = _resolve_tenant_id_for_flow()
    if not tenant_id:
        return jsonify({"success": False, "message": "Kurum bulunamadı."}), 400
    try:
        score_result = compute_vision_score(
            tenant_id,
            persist_pg_scores=False
        )
        process_scores = score_result.get("process_scores", {})
        sub_strategy_scores = score_result.get("sub_strategy_scores", {})
        strategy_scores = score_result.get("strategy_scores", {})
        pg_scores = score_result.get("pg_scores", {})

        tenant = Tenant.query.get(tenant_id)
        strategies = Strategy.query.filter_by(tenant_id=tenant_id, is_active=True).order_by(Strategy.code).all()
        sub_strategies = (
            SubStrategy.query.join(Strategy)
            .filter(Strategy.tenant_id == tenant_id, Strategy.is_active == True, SubStrategy.is_active == True)
            .order_by(SubStrategy.code)
            .all()
        )
        processes = Process.query.filter_by(tenant_id=tenant_id, is_active=True).order_by(Process.code).all()
        kpis = (
            ProcessKpi.query.join(Process)
            .filter(Process.tenant_id == tenant_id, Process.is_active == True, ProcessKpi.is_active == True)
            .all()
        )

        nodes = []
        edges = []
        kurum_panel_url = url_for("dashboard_bp.tenant_dashboard")

        def _label_with_score(prefix: str, name: str, score: float) -> str:
            sc = int(round(score)) if score is not None else 0
            return f"{prefix} {name}".strip() + f"\n({sc}%)"

        if tenant and tenant.vision:
            nodes.append({
                "id": "vision", "group": "vision", "shape": "box", "color": "#8b5cf6",
                "label": f"VİZYON\n{tenant.vision[:80]}..." if len(tenant.vision) > 80 else f"VİZYON\n{tenant.vision}",
                "title": f"<b>Vizyon</b><br/>{tenant.vision}",
                "url": kurum_panel_url, "level": 0,
            })

        for st in strategies:
            score = strategy_scores.get(st.id, 0.0)
            code = (st.code or "").strip()
            prefix = code if code else "ANA"
            nodes.append({
                "id": f"main_{st.id}", "group": "main_strategy", "shape": "box", "color": "#f97316",
                "label": _label_with_score(prefix, st.title, score),
                "title": f"<b>{st.title}</b><br/>Skor: <b>{int(round(score))}%</b>",
                "url": kurum_panel_url, "level": 1, "score": score,
            })

        for ss in sub_strategies:
            score = sub_strategy_scores.get(ss.id, 0.0)
            code = (ss.code or "").strip()
            prefix = code if code else "ALT"
            nodes.append({
                "id": f"sub_{ss.id}", "group": "sub_strategy", "shape": "box", "color": "#0891b2",
                "label": _label_with_score(prefix, ss.title, score),
                "title": f"<b>{ss.title}</b><br/>Skor: <b>{int(round(score))}%</b>",
                "url": kurum_panel_url, "level": 2, "score": score,
            })
            edges.append({
                "from": f"main_{ss.strategy_id}", "to": f"sub_{ss.id}",
                "arrows": "to", "color": {"color": "#94a3b8"}, "width": 1, "dashes": True,
            })

        if tenant and tenant.vision:
            for st in strategies:
                edges.append({
                    "from": "vision", "to": f"main_{st.id}",
                    "arrows": "to", "color": {"color": "#c084fc"}, "width": 3, "dashes": False,
                })

        for proc in processes:
            score = process_scores.get(proc.id, 0.0)
            code = (proc.code or "").strip()
            prefix = code if code else "SR"
            nodes.append({
                "id": f"proc_{proc.id}", "group": "process", "shape": "ellipse", "color": "#059669",
                "label": _label_with_score(prefix, proc.name, score),
                "title": f"<b>{proc.name}</b><br/>Skor: <b>{int(round(score))}%</b>",
                "url": kurum_panel_url, "level": 3, "score": score,
            })

        links = ProcessSubStrategyLink.query.filter(
            ProcessSubStrategyLink.process_id.in_([p.id for p in processes]),
            ProcessSubStrategyLink.sub_strategy_id.in_([s.id for s in sub_strategies]),
        ).all()
        for link in links:
            edges.append({
                "from": f"sub_{link.sub_strategy_id}", "to": f"proc_{link.process_id}",
                "arrows": "to", "label": f"{int(link.contribution_pct or 0)}%",
                "color": {"color": "#16a34a"},
                "width": 2,
            })

        for kpi in kpis:
            score = pg_scores.get(kpi.id)
            score_txt = f" ({int(round(score))}%)" if score is not None else ""
            label = (kpi.code or "").strip()
            label = f"{label}: {kpi.name}{score_txt}" if label else f"PG: {kpi.name}{score_txt}"
            nodes.append({
                "id": f"kpi_{kpi.id}", "group": "kpi", "shape": "box", "color": "#7c3aed",
                "label": label,
                "title": f"<b>{kpi.name}</b><br/>Skor: <b>{(str(int(round(score))) + '%' if score is not None else '-')}</b>",
                "url": kurum_panel_url, "level": 4, "score": score,
            })
            edges.append({
                "from": f"proc_{kpi.process_id}", "to": f"kpi_{kpi.id}",
                "arrows": "to", "color": {"color": "#c4b5fd"}, "width": 1,
            })

        return jsonify({
            "success": True,
            "nodes": nodes,
            "edges": edges,
            "meta": {
                "tenant_id": tenant_id,
                "main_strategies": len(strategies),
                "sub_strategies": len(sub_strategies),
                "processes": len(processes),
                "projects": 0,
                "kpis": len(kpis),
            },
        })
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"Strategic planning graph API error: {e}", exc_info=True)
        return jsonify({"success": False, "message": str(e)}), 500
