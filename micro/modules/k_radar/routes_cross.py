"""K-Radar — Cross (KS×KP×KPR) ve Paydaş route'ları."""

from datetime import datetime, timezone
from flask import jsonify, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required

from platform_core import app_bp
from app.models import db
from app.models.k_radar_domain import StakeholderMap
from micro.modules.k_radar.routes_common import (
    _can_manage_k_radar, _required_tenant_id, _safe_json, _forbidden_json,
)


@app_bp.route("/k-radar/cross")
@login_required
def k_radar_cross():
    return render_template("platform/k_radar/cross.html", can_manage_k_radar=_can_manage_k_radar())


@app_bp.route("/k-radar/cross/paydas")
@login_required
def k_radar_cross_paydas():
    tenant_id = _required_tenant_id()
    rows = (
        StakeholderMap.query.filter_by(tenant_id=tenant_id, is_active=True)
        .order_by(StakeholderMap.updated_at.desc())
        .limit(200)
        .all()
    )
    return render_template(
        "platform/k_radar/cross_paydas.html",
        can_manage_k_radar=_can_manage_k_radar(),
        rows=rows,
    )


@app_bp.route("/k-radar/cross/rekabet")
@login_required
def k_radar_cross_rekabet():
    return render_template("platform/k_radar/cross_rekabet.html", can_manage_k_radar=_can_manage_k_radar())


@app_bp.route("/k-radar/cross/a3")
@login_required
def k_radar_cross_a3():
    return render_template("platform/k_radar/cross_a3.html", can_manage_k_radar=_can_manage_k_radar())


@app_bp.route("/k-radar/cross/anket")
@login_required
def k_radar_cross_anket():
    return render_template("platform/k_radar/cross_anket.html", can_manage_k_radar=_can_manage_k_radar())


@app_bp.route("/k-radar/cross/paydas/ekle", methods=["POST"])
@login_required
def k_radar_cross_paydas_ekle():
    if not _can_manage_k_radar():
        return render_template("platform/errors/403.html"), 403
    tenant_id = _required_tenant_id()
    name = (request.form.get("name") or "").strip()
    role = (request.form.get("role") or "").strip() or None
    strategy = (request.form.get("strategy") or "").strip() or None
    influence = request.form.get("influence", type=int)
    interest = request.form.get("interest", type=int)
    if not name:
        flash("Paydaş adı zorunludur.", "danger")
        return redirect(url_for("app_bp.k_radar_cross_paydas"))
    row = StakeholderMap(
        tenant_id=tenant_id,
        name=name,
        role=role,
        strategy=strategy,
        influence=max(1, min(5, influence or 3)),
        interest=max(1, min(5, interest or 3)),
        is_active=True,
    )
    db.session.add(row)
    db.session.commit()
    flash("Paydaş kaydı eklendi.", "success")
    return redirect(url_for("app_bp.k_radar_cross_paydas"))


@app_bp.route("/k-radar/api/cross/risk-heatmap")
@login_required
def k_radar_api_cross_risk_heatmap():
    from services.k_radar_service import get_cross_heatmap_data
    return _safe_json(
        lambda: jsonify({"success": True, "data": get_cross_heatmap_data(_required_tenant_id())})
    )


@app_bp.route("/k-radar/api/cross/paydas")
@login_required
def k_radar_api_cross_paydas():
    def _build():
        rows = (
            StakeholderMap.query.filter_by(tenant_id=_required_tenant_id(), is_active=True)
            .order_by(StakeholderMap.updated_at.desc())
            .limit(300)
            .all()
        )
        return jsonify({
            "success": True,
            "data": {
                "rows": [
                    {
                        "id": r.id,
                        "name": r.name,
                        "role": r.role,
                        "influence": r.influence,
                        "interest": r.interest,
                        "strategy": r.strategy,
                    }
                    for r in rows
                ]
            },
        })
    return _safe_json(_build)


@app_bp.route("/k-radar/api/cross/paydas", methods=["POST"])
@login_required
def k_radar_api_cross_paydas_create():
    if not _can_manage_k_radar():
        return _forbidden_json()
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    if not name:
        return jsonify({"success": False, "message": "name zorunlu"}), 400
    role = (payload.get("role") or "").strip() or None
    strategy = (payload.get("strategy") or "").strip() or None
    influence = int(payload.get("influence") or 3)
    interest = int(payload.get("interest") or 3)
    def _create():
        row = StakeholderMap(
            tenant_id=_required_tenant_id(),
            name=name,
            role=role,
            strategy=strategy,
            influence=max(1, min(5, influence)),
            interest=max(1, min(5, interest)),
            is_active=True,
        )
        db.session.add(row)
        db.session.commit()
        return jsonify({"success": True, "data": {"id": row.id}})
    return _safe_json(_create)


@app_bp.route("/k-radar/api/cross/paydas/<int:row_id>", methods=["PUT"])
@login_required
def k_radar_api_cross_paydas_update(row_id: int):
    if not _can_manage_k_radar():
        return _forbidden_json()
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    if not name:
        return jsonify({"success": False, "message": "name zorunlu"}), 400
    role = (payload.get("role") or "").strip() or None
    strategy = (payload.get("strategy") or "").strip() or None
    influence = int(payload.get("influence") or 3)
    interest = int(payload.get("interest") or 3)

    def _update():
        row = StakeholderMap.query.filter_by(id=row_id, tenant_id=_required_tenant_id(), is_active=True).first()
        if not row:
            return jsonify({"success": False, "message": "Kayıt bulunamadı"}), 404
        row.name = name
        row.role = role
        row.strategy = strategy
        row.influence = max(1, min(5, influence))
        row.interest = max(1, min(5, interest))
        db.session.commit()
        return jsonify({"success": True, "data": {"id": row.id}})

    return _safe_json(_update)


@app_bp.route("/k-radar/api/cross/paydas/<int:row_id>", methods=["DELETE"])
@login_required
def k_radar_api_cross_paydas_delete(row_id: int):
    if not _can_manage_k_radar():
        return _forbidden_json()

    def _delete():
        row = StakeholderMap.query.filter_by(id=row_id, tenant_id=_required_tenant_id(), is_active=True).first()
        if not row:
            return jsonify({"success": False, "message": "Kayıt bulunamadı"}), 404
        row.is_active = False
        db.session.commit()
        return jsonify({"success": True, "data": {"id": row.id}})

    return _safe_json(_delete)


@app_bp.route("/k-radar/api/cross/rekabet")
@login_required
def k_radar_api_cross_rekabet():
    from services.k_radar_service import get_cross_extended_data
    return _safe_json(lambda: jsonify({"success": True, "data": get_cross_extended_data(_required_tenant_id()).get("rekabet", {})}))


@app_bp.route("/k-radar/api/cross/a3")
@login_required
def k_radar_api_cross_a3():
    from services.k_radar_service import get_cross_extended_data
    return _safe_json(lambda: jsonify({"success": True, "data": get_cross_extended_data(_required_tenant_id()).get("a3_5neden", {})}))


@app_bp.route("/k-radar/api/cross/anket")
@login_required
def k_radar_api_cross_anket():
    from services.k_radar_service import get_cross_extended_data
    return _safe_json(lambda: jsonify({"success": True, "data": get_cross_extended_data(_required_tenant_id()).get("anket", {})}))
