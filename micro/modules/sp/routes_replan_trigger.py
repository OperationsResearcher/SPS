"""Replan Trigger routes (Sprint 57 — Ö8)."""
from __future__ import annotations

from flask import render_template, jsonify, request, current_app
from flask_login import login_required, current_user

from platform_core import app_bp
from app.extensions import csrf
from extensions import db
from app.models.replan_trigger import ReplanTrigger, ReplanTriggerEvent
from app.services.replan_trigger_service import evaluate_triggers
from micro.modules.sp.helpers import _check_sp_role


def _can():
    return _check_sp_role(current_user)


@app_bp.route("/sp/replan-triggers")
@login_required
def sp_replan_triggers_page():
    if not _can():
        return render_template("errors/403.html"), 403
    return render_template("platform/sp/replan_triggers.html")


@app_bp.route("/sp/api/replan-triggers")
@login_required
def sp_api_triggers_list():
    if not _can():
        return jsonify({"error": "yetki yok"}), 403
    items = ReplanTrigger.query.filter_by(
        tenant_id=current_user.tenant_id
    ).order_by(ReplanTrigger.id.desc()).all()
    return jsonify({"success": True, "items": [i.to_dict() for i in items]})


@app_bp.route("/sp/api/replan-triggers", methods=["POST"])
@csrf.exempt
@login_required
def sp_api_triggers_create():
    if not _can():
        return jsonify({"error": "yetki yok"}), 403
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    ttype = data.get("trigger_type")
    if not name or not ttype:
        return jsonify({"error": "name ve trigger_type zorunlu"}), 400

    t = ReplanTrigger(
        tenant_id=current_user.tenant_id,
        name=name,
        description=data.get("description"),
        trigger_type=ttype,
        target_kpi_id=data.get("target_kpi_id") or None,
        threshold_value=data.get("threshold_value"),
        threshold_operator=data.get("threshold_operator"),
        consecutive_periods=int(data.get("consecutive_periods") or 1),
        action=data.get("action") or "notify",
        severity=data.get("severity") or "medium",
    )
    db.session.add(t)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    return jsonify({"success": True, "item": t.to_dict()}), 201


@app_bp.route("/sp/api/replan-triggers/<int:tid>", methods=["DELETE"])
@csrf.exempt
@login_required
def sp_api_triggers_delete(tid):
    if not _can():
        return jsonify({"error": "yetki yok"}), 403
    t = ReplanTrigger.query.filter_by(
        id=tid, tenant_id=current_user.tenant_id
    ).first()
    if not t:
        return jsonify({"error": "not found"}), 404
    t.is_active = False
    db.session.commit()
    return jsonify({"success": True})


@app_bp.route("/sp/api/replan-triggers/evaluate", methods=["POST"])
@csrf.exempt
@login_required
def sp_api_triggers_evaluate():
    """Tüm trigger'ları şimdi değerlendir (dry_run opsiyonel)."""
    if not _can():
        return jsonify({"error": "yetki yok"}), 403
    dry = request.args.get("dry_run", "0") in ("1", "true")
    try:
        events = evaluate_triggers(current_user.tenant_id, dry_run=dry)
    except Exception as e:
        current_app.logger.error(f"trigger_eval error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    return jsonify({
        "success": True,
        "fired_count": len(events),
        "events": [e.to_dict() for e in events],
        "dry_run": dry,
    })


@app_bp.route("/sp/api/replan-triggers/events")
@login_required
def sp_api_triggers_events():
    if not _can():
        return jsonify({"error": "yetki yok"}), 403
    rows = ReplanTriggerEvent.query.filter_by(
        tenant_id=current_user.tenant_id
    ).order_by(ReplanTriggerEvent.fired_at.desc()).limit(100).all()
    return jsonify({"success": True, "items": [e.to_dict() for e in rows]})
