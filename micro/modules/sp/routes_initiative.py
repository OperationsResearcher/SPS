"""Multi-Year Initiative routes (Sprint 55 — Ö4)."""
from __future__ import annotations

import datetime as _dt

from flask import render_template, jsonify, request, current_app
from flask_login import login_required, current_user

from platform_core import app_bp
from app.extensions import csrf
from extensions import db
from app.models.initiative import Initiative, InitiativeMilestone
from micro.modules.sp.helpers import _check_sp_role
from flask_babel import gettext as _


def _can_manage():
    return _check_sp_role(current_user)


@app_bp.route("/k-plan/strategy/initiatives")
@login_required
def sp_initiatives_page():
    if not _can_manage():
        return render_template("errors/403.html"), 403
    return render_template("platform/sp/initiatives.html")


@app_bp.route("/k-plan/strategy/api/initiatives", methods=["GET"])
@login_required
def sp_api_initiatives_list():
    if not _can_manage():
        return jsonify({"error": "yetki yok"}), 403
    q = Initiative.query.filter_by(tenant_id=current_user.tenant_id, is_active=True)
    year = request.args.get("year", type=int)
    if year:
        q = q.filter(Initiative.start_year <= year, Initiative.end_year >= year)
    items = q.order_by(Initiative.start_year.desc(), Initiative.id.desc()).all()
    return jsonify({"success": True, "items": [i.to_dict() for i in items]})


@app_bp.route("/k-plan/strategy/api/initiatives", methods=["POST"])
@csrf.exempt
@login_required
def sp_api_initiatives_create():
    if not _can_manage():
        return jsonify({"error": "yetki yok"}), 403
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name zorunlu"}), 400
    try:
        start_year = int(data.get("start_year"))
        end_year = int(data.get("end_year"))
    except (TypeError, ValueError):
        return jsonify({"error": "start_year/end_year sayı olmalı"}), 400
    if end_year < start_year:
        return jsonify({"error": "end_year >= start_year olmalı"}), 400

    init = Initiative(
        tenant_id=current_user.tenant_id,
        code=(data.get("code") or "").strip() or None,
        name=name,
        description=data.get("description"),
        strategy_id=data.get("strategy_id") or None,
        sub_strategy_id=data.get("sub_strategy_id") or None,
        start_year=start_year,
        end_year=end_year,
        status=data.get("status") or "planned",
        priority=data.get("priority") or "medium",
        budget_total=data.get("budget_total") or None,
        owner_user_id=data.get("owner_user_id") or current_user.id,
    )
    db.session.add(init)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"initiative_create error: {e}", exc_info=True)
        return jsonify({"success": False, "message": _("İşlem tamamlanamadı.")}), 500
    return jsonify({"success": True, "item": init.to_dict()}), 201


@app_bp.route("/k-plan/strategy/api/initiatives/<int:iid>", methods=["PATCH"])
@csrf.exempt
@login_required
def sp_api_initiatives_update(iid):
    if not _can_manage():
        return jsonify({"error": "yetki yok"}), 403
    init = Initiative.query.filter_by(
        id=iid, tenant_id=current_user.tenant_id, is_active=True
    ).first()
    if not init:
        return jsonify({"error": "not found"}), 404
    data = request.get_json(silent=True) or {}
    tid = current_user.tenant_id
    # Basit alanlar doğrudan atanabilir
    for f in ("name", "code", "description", "status", "priority",
              "start_year", "end_year", "budget_total", "budget_spent", "progress_pct"):
        if f in data:
            setattr(init, f, data[f])
    # Tenant-scoped FK'lar — sahiplik doğrulaması gerekir
    if "strategy_id" in data and data["strategy_id"]:
        from app.models.core import Strategy
        s = Strategy.query.filter_by(id=data["strategy_id"], tenant_id=tid).first()
        if not s:
            return jsonify({"success": False, "message": _("Geçersiz strateji.")}), 400
        init.strategy_id = s.id
    elif "strategy_id" in data:
        init.strategy_id = None
    if "sub_strategy_id" in data and data["sub_strategy_id"]:
        from app.models.core import SubStrategy
        ss = SubStrategy.query.filter_by(id=data["sub_strategy_id"]).join(
            __import__('app.models.core', fromlist=['Strategy']).Strategy
        ).filter_by(tenant_id=tid).first()
        init.sub_strategy_id = ss.id if ss else None
    elif "sub_strategy_id" in data:
        init.sub_strategy_id = None
    if "owner_user_id" in data and data["owner_user_id"]:
        from app.models.core import User
        u = User.query.filter_by(id=data["owner_user_id"], tenant_id=tid, is_active=True).first()
        init.owner_user_id = u.id if u else None
    elif "owner_user_id" in data:
        init.owner_user_id = None
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": _("İşlem tamamlanamadı.")}), 500
    return jsonify({"success": True, "item": init.to_dict()})


@app_bp.route("/k-plan/strategy/api/initiatives/<int:iid>", methods=["DELETE"])
@csrf.exempt
@login_required
def sp_api_initiatives_delete(iid):
    if not _can_manage():
        return jsonify({"error": "yetki yok"}), 403
    init = Initiative.query.filter_by(
        id=iid, tenant_id=current_user.tenant_id
    ).first()
    if not init:
        return jsonify({"error": "not found"}), 404
    init.is_active = False
    db.session.commit()
    return jsonify({"success": True})


@app_bp.route("/k-plan/strategy/api/initiatives/<int:iid>/milestones", methods=["POST"])
@csrf.exempt
@login_required
def sp_api_milestone_create(iid):
    if not _can_manage():
        return jsonify({"error": "yetki yok"}), 403
    init = Initiative.query.filter_by(
        id=iid, tenant_id=current_user.tenant_id, is_active=True
    ).first()
    if not init:
        return jsonify({"error": "not found"}), 404
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name zorunlu"}), 400
    td = data.get("target_date")
    try:
        td_parsed = _dt.date.fromisoformat(td) if td else None
    except ValueError:
        td_parsed = None
    ms = InitiativeMilestone(
        initiative_id=iid,
        name=name,
        target_date=td_parsed,
        status=data.get("status") or "pending",
        note=data.get("note"),
        order_index=data.get("order_index") or 0,
    )
    db.session.add(ms)
    db.session.commit()
    return jsonify({"success": True, "item": ms.to_dict()}), 201


# ── Stratejik Girişim ↔ Proje bağlantısı ──────────────────────────────────
@app_bp.route("/k-plan/strategy/api/initiatives/<int:iid>/projects", methods=["GET"])
@login_required
def sp_api_initiative_projects(iid):
    """Bir stratejik girişimin altındaki projeleri döner."""
    from app.models.portfolio_project import Project
    tid = current_user.tenant_id
    rows = (Project.query
            .filter_by(initiative_id=iid, tenant_id=tid)
            .filter(Project.is_archived.is_(False))
            .order_by(Project.name).all())
    return jsonify({"success": True, "items": [{
        "id": p.id,
        "name": p.name,
        "manager_id": p.manager_id,
        "manager_name": ((p.manager.first_name or '') + ' ' + (p.manager.last_name or '')).strip() if p.manager else '',
        "health_score": p.health_score,
        "health_status": p.health_status,
        "priority": p.priority,
        "start_date": p.start_date.isoformat() if p.start_date else None,
        "end_date": p.end_date.isoformat() if p.end_date else None,
    } for p in rows]})


@app_bp.route("/k-plan/strategy/api/projects/<int:pid>/initiative", methods=["POST"])
@csrf.exempt
@login_required
def sp_api_project_set_initiative(pid):
    """Bir projeyi bir stratejik girişime bağlar (veya bağı keser: initiative_id=null)."""
    from app.models.portfolio_project import Project
    from app.models.initiative import Initiative
    tid = current_user.tenant_id
    p = Project.query.filter_by(id=pid, tenant_id=tid).first_or_404()
    data = request.get_json(silent=True) or {}
    new_iid = data.get("initiative_id")
    if new_iid is not None:
        try: new_iid = int(new_iid)
        except (TypeError, ValueError): return jsonify({"success": False, "message": _("Geçersiz initiative_id")}), 400
        Initiative.query.filter_by(id=new_iid, tenant_id=tid).first_or_404()
    p.initiative_id = new_iid
    db.session.commit()
    return jsonify({"success": True, "project_id": p.id, "initiative_id": new_iid})
