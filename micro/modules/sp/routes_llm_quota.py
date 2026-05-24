"""LLM kullanım & kota yönetim panel rotaları."""
from __future__ import annotations

from flask import render_template, jsonify, request, current_app
from flask_login import login_required, current_user
from sqlalchemy import func, text

from platform_core import app_bp
from app.extensions import csrf
from extensions import db
from app.models.llm_usage import LLMUsageLog, LLMQuotaOverride
from app.services.llm_quota_service import get_tenant_usage_summary, DEFAULT_LIMITS
from micro.modules.sp.helpers import _check_sp_role


def _can():
    return _check_sp_role(current_user)


@app_bp.route("/sp/llm-usage")
@login_required
def sp_llm_usage_page():
    if not _can():
        return render_template("errors/403.html"), 403
    return render_template("platform/sp/llm_usage.html")


@app_bp.route("/sp/api/llm-usage/summary")
@login_required
def sp_api_llm_summary():
    if not _can():
        return jsonify({"error": "yetki yok"}), 403
    summary = get_tenant_usage_summary(current_user.tenant_id)
    # Son 14 günün günlük breakdown'ı
    daily = db.session.execute(text("""
        SELECT DATE(created_at) as d,
               count(*) FILTER (WHERE status='ok') as ok_calls,
               count(*) FILTER (WHERE status='quota_exceeded') as blocked,
               COALESCE(sum(total_tokens) FILTER (WHERE status='ok'), 0) as tokens,
               COALESCE(sum(cost_usd) FILTER (WHERE status='ok'), 0) as cost
        FROM llm_usage_logs
        WHERE tenant_id=:t AND created_at >= NOW() - INTERVAL '14 days'
        GROUP BY DATE(created_at)
        ORDER BY d DESC
    """), {"t": current_user.tenant_id}).fetchall()
    return jsonify({
        "success": True,
        "summary": summary,
        "limits": DEFAULT_LIMITS,
        "daily": [
            {"date": r.d.isoformat(), "ok_calls": r.ok_calls,
             "blocked": r.blocked, "tokens": int(r.tokens or 0),
             "cost_usd": float(r.cost or 0)}
            for r in daily
        ],
    })


@app_bp.route("/sp/api/llm-usage/recent")
@login_required
def sp_api_llm_recent():
    if not _can():
        return jsonify({"error": "yetki yok"}), 403
    rows = (
        LLMUsageLog.query
        .filter_by(tenant_id=current_user.tenant_id)
        .order_by(LLMUsageLog.created_at.desc())
        .limit(50)
        .all()
    )
    return jsonify({"success": True, "items": [r.to_dict() for r in rows]})
