"""Exec Dashboard + AI Pivot Advisor + Template Marketplace routes.

Önerilen Hamleler #2, #4, #5.
"""
from __future__ import annotations

from flask import render_template, jsonify, request, current_app
from flask_login import login_required, current_user

from platform_core import app_bp
from app.services.exec_dashboard_service import build_exec_snapshot
from app.services.ai_pivot_advisor_service import generate_pivot_recommendations
from app.services.plan_year_template_service import (
    list_templates, get_template, apply_template_to_tenant,
)
from micro.modules.sp.helpers import _check_sp_role


def _can():
    return _check_sp_role(current_user)


# ─── Exec Dashboard ──────────────────────────────────────────────────────────

@app_bp.route("/sp/exec-dashboard")
@login_required
def sp_exec_dashboard():
    if not _can():
        return render_template("errors/403.html"), 403
    return render_template("platform/sp/exec_dashboard.html")


@app_bp.route("/sp/api/exec-snapshot")
@login_required
def sp_api_exec_snapshot():
    if not _can():
        return jsonify({"error": "yetki yok"}), 403
    try:
        snap = build_exec_snapshot(current_user.tenant_id)
        return jsonify({"success": True, "snapshot": snap})
    except Exception as e:
        current_app.logger.error(f"exec_snapshot error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


# ─── AI Pivot Advisor ────────────────────────────────────────────────────────

@app_bp.route("/sp/api/ai-pivot", methods=["POST"])
@login_required
def sp_api_ai_pivot():
    if not _can():
        return jsonify({"error": "yetki yok"}), 403
    use_llm = (request.args.get("use_llm", "1") in ("1", "true"))
    try:
        result = generate_pivot_recommendations(current_user.tenant_id, use_llm=use_llm)
        return jsonify({"success": True, **result})
    except Exception as e:
        current_app.logger.error(f"ai_pivot error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


# ─── Template Marketplace ────────────────────────────────────────────────────

@app_bp.route("/sp/templates")
@login_required
def sp_templates_page():
    if not _can():
        return render_template("errors/403.html"), 403
    return render_template("platform/sp/templates.html")


@app_bp.route("/sp/api/templates")
@login_required
def sp_api_templates_list():
    if not _can():
        return jsonify({"error": "yetki yok"}), 403
    return jsonify({"success": True, "items": list_templates()})


@app_bp.route("/sp/api/templates/<code>")
@login_required
def sp_api_template_get(code):
    if not _can():
        return jsonify({"error": "yetki yok"}), 403
    t = get_template(code)
    if not t:
        return jsonify({"error": "not found"}), 404
    return jsonify({"success": True, "template": t})


@app_bp.route("/sp/api/templates/<code>/apply", methods=["POST"])
@login_required
def sp_api_template_apply(code):
    if not _can():
        return jsonify({"error": "yetki yok"}), 403
    data = request.get_json(silent=True) or {}
    try:
        target_year = int(data.get("target_year"))
    except (TypeError, ValueError):
        return jsonify({"error": "target_year zorunlu"}), 400
    overwrite = bool(data.get("overwrite_identity", False))
    try:
        py = apply_template_to_tenant(
            current_user.tenant_id, code, target_year, overwrite_identity=overwrite
        )
        return jsonify({
            "success": True,
            "plan_year": {"id": py.id, "year": py.year, "name": py.name, "status": py.status},
        }), 201
    except Exception as e:
        current_app.logger.error(f"template_apply error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
