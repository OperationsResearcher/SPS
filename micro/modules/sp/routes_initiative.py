"""Multi-Year Initiative routes (Sprint 55 — Ö4)."""
from __future__ import annotations

import datetime as _dt

from flask import render_template, jsonify, request, current_app
from flask_login import login_required, current_user

from platform_core import app_bp
from extensions import db
from app.models.initiative import Initiative, InitiativeMilestone
from micro.modules.sp.helpers import _check_sp_role


def _can_manage():
    return _check_sp_role(current_user)


@app_bp.route("/sp/initiatives")
@login_required
def sp_initiatives_page():
    if not _can_manage():
        return render_template("errors/403.html"), 403
    return render_template("platform/sp/initiatives.html")


@app_bp.route("/sp/api/initiatives", methods=["GET"])
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


@app_bp.route("/sp/api/initiatives", methods=["POST"])
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
        return jsonify({"error": str(e)}), 500
    return jsonify({"success": True, "item": init.to_dict()}), 201


@app_bp.route("/sp/api/initiatives/<int:iid>", methods=["PATCH"])
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
    for f in ("name", "code", "description", "status", "priority",
              "strategy_id", "sub_strategy_id", "start_year", "end_year",
              "budget_total", "budget_spent", "progress_pct", "owner_user_id"):
        if f in data:
            setattr(init, f, data[f])
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    return jsonify({"success": True, "item": init.to_dict()})


@app_bp.route("/sp/api/initiatives/<int:iid>", methods=["DELETE"])
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


@app_bp.route("/sp/api/initiatives/<int:iid>/milestones", methods=["POST"])
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
