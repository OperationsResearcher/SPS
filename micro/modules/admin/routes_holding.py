"""Holding konsolide dashboard (Sprint D).

Yetki: Holding tenant'ına bağlı tenant_admin/executive_manager veya Platform Admin.
"""
from __future__ import annotations

from flask import render_template, jsonify, request, current_app
from flask_login import login_required, current_user

from platform_core import app_bp
from app.models.core import Tenant
from app.services.holding_consolidated_service import (
    build_holding_snapshot, build_sub_tenant_drilldown,
)
from app.utils.tenant_scope import is_holding_admin, is_platform_admin, is_holding_user


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
        return jsonify({"success": False, "message": "Sunucu hatası oluştu."}), 500


# ─── Sprint E: Read-Only Drill-Down ──────────────────────────────────────────

def _validate_holding_access(sub_tenant_id: int):
    """Holding yetkili kullanıcı bu alt-tenant'a erişebilir mi? (tenant, err_response)"""
    if not (is_holding_user(current_user) or is_platform_admin(current_user)):
        return None, (_403(), 403)
    sub = Tenant.query.get(sub_tenant_id)
    if not sub:
        return None, (jsonify({"success": False, "message": "Alt kurum bulunamadı."}), 404)
    if not sub.parent_tenant_id:
        return None, (jsonify({"success": False, "message": "Bu kurum bir alt kurum değil."}), 400)
    # Platform Admin → tümüne erişebilir
    # Holding user → sadece kendi children'ı
    if is_holding_user(current_user) and sub.parent_tenant_id != current_user.tenant_id:
        return None, (_403(), 403)
    return sub, None


@app_bp.route("/holding/tenant/<int:sub_tenant_id>/view")
@login_required
def holding_sub_tenant_view_page(sub_tenant_id):
    sub, err = _validate_holding_access(sub_tenant_id)
    if err:
        return render_template("platform/errors/403.html"), 403
    holding_id = sub.parent_tenant_id

    # Audit: holding bu alt-tenant'a baktı
    try:
        from app.utils.audit_logger import AuditLogger
        AuditLogger.log(
            action="HOLDING_VIEW_TENANT", resource_type="HOLDING",
            resource_id=sub.id,
            description=f"{current_user.email} (holding={holding_id}) → drill-down: {sub.name}",
        )
    except Exception:
        pass

    return render_template(
        "platform/admin/holding_drilldown.html",
        sub_tenant=sub,
        holding_id=holding_id,
    )


@app_bp.route("/holding/api/tenant/<int:sub_tenant_id>/drilldown")
@login_required
def holding_api_drilldown(sub_tenant_id):
    sub, err = _validate_holding_access(sub_tenant_id)
    if err:
        return err[0], err[1]
    try:
        data = build_sub_tenant_drilldown(sub.parent_tenant_id, sub.id)
        if "error" in data:
            return jsonify({"success": False, "message": data["error"]}), 400
        return jsonify({"success": True, **data})
    except Exception as e:
        current_app.logger.error(f"[holding_api_drilldown] {e}", exc_info=True)
        return jsonify({"success": False, "message": "Sunucu hatası oluştu."}), 500
