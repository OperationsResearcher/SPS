"""Tenant ayarları — AI/LLM yapılandırması (BYOK)."""
from __future__ import annotations

from flask import render_template, jsonify, request, current_app
from flask_login import login_required, current_user

from platform_core import app_bp
from app.extensions import csrf
from extensions import db
from app.models.tenant_llm_config import TenantLLMConfig
from app.services.llm_gateway import test_tenant_config, PROVIDERS
from micro.modules.sp.helpers import _check_sp_role


def _can():
    return _check_sp_role(current_user)


@app_bp.route("/sp/ayarlar/ai")
@login_required
def sp_ai_settings_page():
    if not _can():
        return render_template("errors/403.html"), 403
    return render_template("platform/sp/ai_settings.html")


@app_bp.route("/sp/api/ai-config")
@login_required
def sp_api_ai_config_get():
    if not _can():
        return jsonify({"error": "yetki yok"}), 403
    cfg = TenantLLMConfig.query.filter_by(tenant_id=current_user.tenant_id).first()
    if not cfg:
        return jsonify({
            "success": True,
            "config": None,
            "providers": list(PROVIDERS.keys()),
            "default_models": {p: d["default_model"] for p, d in PROVIDERS.items()},
        })
    return jsonify({
        "success": True,
        "config": cfg.to_dict(reveal_key=False),
        "providers": list(PROVIDERS.keys()),
        "default_models": {p: d["default_model"] for p, d in PROVIDERS.items()},
    })


@app_bp.route("/sp/api/ai-config", methods=["POST"])
@csrf.exempt
@login_required
def sp_api_ai_config_save():
    if not _can():
        return jsonify({"error": "yetki yok"}), 403
    d = request.get_json(silent=True) or {}
    cfg = TenantLLMConfig.query.filter_by(tenant_id=current_user.tenant_id).first()
    if not cfg:
        cfg = TenantLLMConfig(tenant_id=current_user.tenant_id)
        db.session.add(cfg)

    provider = (d.get("provider") or "gemini").lower()
    if provider not in PROVIDERS:
        return jsonify({"error": f"Desteklenmeyen provider: {provider}"}), 400

    cfg.provider = provider
    cfg.model = (d.get("model") or "").strip() or PROVIDERS[provider]["default_model"]
    cfg.base_url = (d.get("base_url") or "").strip() or None
    cfg.is_active = bool(d.get("is_active"))
    cfg.pii_mask_enabled = bool(d.get("pii_mask_enabled", True))

    new_key = (d.get("api_key") or "").strip()
    if new_key:
        cfg.set_api_key(new_key)

    db.session.commit()
    return jsonify({"success": True, "config": cfg.to_dict()})


@app_bp.route("/sp/api/ai-config/test", methods=["POST"])
@csrf.exempt
@login_required
def sp_api_ai_config_test():
    if not _can():
        return jsonify({"error": "yetki yok"}), 403
    try:
        result = test_tenant_config(current_user.tenant_id)
        return jsonify({"success": result["success"], **result})
    except Exception as e:
        current_app.logger.error(f"ai_config_test error: {e}", exc_info=True)
        return jsonify({"success": False, "message": "Sunucu hatası oluştu."}), 500


@app_bp.route("/sp/api/ai-config", methods=["DELETE"])
@csrf.exempt
@login_required
def sp_api_ai_config_delete():
    if not _can():
        return jsonify({"error": "yetki yok"}), 403
    cfg = TenantLLMConfig.query.filter_by(tenant_id=current_user.tenant_id).first()
    if cfg:
        cfg.api_key_encrypted = None
        cfg.is_active = False
        db.session.commit()
    return jsonify({"success": True})
