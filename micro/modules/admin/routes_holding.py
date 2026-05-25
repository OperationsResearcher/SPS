"""Holding konsolide dashboard (Sprint D).

Yetki: Holding tenant'ına bağlı tenant_admin/executive_manager veya Platform Admin.
"""
from __future__ import annotations

from flask import render_template, jsonify, request, current_app
from flask_login import login_required, current_user

from platform_core import app_bp
from app.models.core import Tenant
from app.services.holding_consolidated_service import build_holding_snapshot
from app.utils.tenant_scope import is_holding_admin, is_platform_admin


def _403():
    return jsonify({"success": False, "message": "Yetkiniz yok."}), 403


@app_bp.route("/holding/dashboard")
@login_required
def holding_dashboard_page():
    if not (is_holding_admin(current_user) or is_platform_admin(current_user)):
        return render_template("platform/errors/403.html"), 403

    # Platform Admin için ?tenant_id=X ile farklı holding bakabilsin
    holding = current_user.tenant
    if is_platform_admin(current_user):
        tid = request.args.get("tenant_id", type=int)
        if tid:
            holding = Tenant.query.get_or_404(tid)
            if holding.tenant_type != "holding":
                return render_template("platform/errors/403.html"), 403

    return render_template("platform/admin/holding_dashboard.html", holding=holding)


@app_bp.route("/holding/api/snapshot")
@login_required
def holding_api_snapshot():
    if not (is_holding_admin(current_user) or is_platform_admin(current_user)):
        return _403()

    holding_id = current_user.tenant_id
    if is_platform_admin(current_user):
        tid = request.args.get("tenant_id", type=int)
        if tid:
            holding_id = tid

    try:
        snap = build_holding_snapshot(holding_id)
        if "error" in snap:
            return jsonify({"success": False, "message": snap["error"]}), 400
        return jsonify({"success": True, **snap})
    except Exception as e:
        current_app.logger.error(f"[holding_api_snapshot] {e}", exc_info=True)
        return jsonify({"success": False, "message": str(e)}), 500
