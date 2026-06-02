"""K-Radar Risk Yönetim modülü (Sprint 34).

RAID (Risk/Assumption/Issue/Decision) + K-Radar Risk Heatmap birleşik view.
- /k-radar/risk: ana sayfa
- /k-radar/api/risk/list: tüm aktif riskler (filter: severity, status, source)
- /k-radar/api/risk/add/update/delete: CRUD
- /k-radar/api/risk/matrix: probability × impact heatmap data
"""
from __future__ import annotations

import datetime as _dt
import json

from flask import render_template, jsonify, request, current_app
from flask_login import login_required, current_user

from platform_core import app_bp
from micro.modules.k_radar.routes_common import _required_tenant_id as _rtid
from extensions import db
from app.models.k_radar_domain import RiskHeatmapItem


def _is_manager() -> bool:
    return current_user.role and (current_user.role.name or "").lower() in (
        "admin", "tenant_admin", "executive_manager"
    )


@app_bp.route("/k-radar/risk")
@login_required
def k_radar_risk_page():
    """Risk Yönetim ana sayfası."""
    return render_template("platform/k_radar/risk_management.html")


@app_bp.route("/k-radar/api/risk/list")
@login_required
def k_radar_api_risk_list():
    """Aktif riskler listesi + filter."""
    try:
        tid = _rtid()
    except ValueError:
        return jsonify({"success": False, "message": "Tenant bağlamı yok."}), 400
    severity = request.args.get("severity")  # "low"/"medium"/"high"/"critical"
    status = request.args.get("status")  # "Open"/"Mitigating"/"Closed"
    source = request.args.get("source")  # process/pestel/swot/project

    q = RiskHeatmapItem.query.filter_by(tenant_id=tid, is_active=True)
    if status:
        q = q.filter(RiskHeatmapItem.status == status)
    if source:
        q = q.filter(RiskHeatmapItem.source_type == source)

    risks = q.order_by(RiskHeatmapItem.rpn.desc().nullslast()).all()

    def _severity(rpn):
        if rpn is None:
            return "low"
        if rpn >= 16:
            return "critical"
        if rpn >= 10:
            return "high"
        if rpn >= 5:
            return "medium"
        return "low"

    rows = []
    for r in risks:
        rpn = (r.probability or 0) * (r.impact or 0)
        sev = _severity(rpn)
        if severity and sev != severity.lower():
            continue
        rows.append({
            "id": r.id,
            "title": r.title,
            "probability": r.probability,
            "impact": r.impact,
            "rpn": rpn,
            "severity": sev,
            "owner_id": r.owner_id,
            "status": r.status,
            "source_type": r.source_type,
            "plan_year_id": r.plan_year_id,
        })
    return jsonify({"success": True, "count": len(rows), "data": rows})


@app_bp.route("/k-radar/api/risk/matrix")
@login_required
def k_radar_api_risk_matrix():
    """5×5 probability × impact heatmap için count grid."""
    try:
        tid = _rtid()
    except ValueError:
        return jsonify({"success": False, "message": "Tenant bağlamı yok."}), 400
    risks = RiskHeatmapItem.query.filter_by(tenant_id=tid, is_active=True).all()
    # 5x5 matrix [probability-1][impact-1] = count
    grid = [[0] * 5 for _ in range(5)]
    for r in risks:
        p = max(1, min(5, r.probability or 1))
        i = max(1, min(5, r.impact or 1))
        grid[p - 1][i - 1] += 1
    return jsonify({"success": True, "matrix": grid, "total": len(risks)})


@app_bp.route("/k-radar/api/risk/add", methods=["POST"])
@login_required
def k_radar_api_risk_add():
    """Yeni risk ekle."""
    if not _is_manager():
        return jsonify({"success": False, "message": "Yetkisiz"}), 403

    payload = request.get_json(silent=True) or {}
    title = (payload.get("title") or "").strip()
    if not title:
        return jsonify({"success": False, "message": "Başlık zorunludur."}), 400

    try:
        prob = max(1, min(5, int(payload.get("probability", 3))))
        imp = max(1, min(5, int(payload.get("impact", 3))))
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "probability/impact 1-5 arası olmalı."}), 400

    risk = RiskHeatmapItem(
        tenant_id=current_user.tenant_id,
        plan_year_id=payload.get("plan_year_id") or None,
        title=title,
        probability=prob,
        impact=imp,
        rpn=prob * imp,
        owner_id=payload.get("owner_id") or None,
        status=payload.get("status") or "Open",
        source_type=payload.get("source_type") or "manual",
    )
    db.session.add(risk)
    db.session.commit()
    return jsonify({"success": True, "data": {"id": risk.id}})


@app_bp.route("/k-radar/api/risk/<int:risk_id>", methods=["PUT", "DELETE"])
@login_required
def k_radar_api_risk_modify(risk_id):
    if not _is_manager():
        return jsonify({"success": False, "message": "Yetkisiz"}), 403

    risk = RiskHeatmapItem.query.filter_by(
        id=risk_id, tenant_id=current_user.tenant_id
    ).first_or_404()

    if request.method == "DELETE":
        risk.is_active = False
        db.session.commit()
        return jsonify({"success": True})

    payload = request.get_json(silent=True) or {}
    if "title" in payload:
        title = (payload["title"] or "").strip()
        if title:
            risk.title = title
    if "probability" in payload:
        try:
            risk.probability = max(1, min(5, int(payload["probability"])))
        except (ValueError, TypeError):
            pass
    if "impact" in payload:
        try:
            risk.impact = max(1, min(5, int(payload["impact"])))
        except (ValueError, TypeError):
            pass
    if "status" in payload:
        risk.status = payload["status"]
    risk.rpn = (risk.probability or 0) * (risk.impact or 0)
    db.session.commit()
    return jsonify({"success": True})
