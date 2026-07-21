"""Hoshin X-Matrix, Blue Ocean, VRIO, EVM, Digest routes (S59-S63)."""
from __future__ import annotations

import json

from flask import render_template, jsonify, request, current_app, Response
from flask_login import login_required, current_user

from platform_core import app_bp
from app.extensions import csrf
from extensions import db
from app.models.strategy_frameworks import (
    BlueOceanCanvas, BlueOceanFactor, BlueOceanERRC, VRIOResource,
)
from app.services.hoshin_xmatrix_service import build_xmatrix
from app.services.project_evm_service import compute_project_evm
from app.services.weekly_digest_service import render_digest_html, render_digest_pdf
from app.services.plan_year_service import get_active_plan_year_for_user
from app.utils.db_sequence import add_and_commit_with_retry
from micro.modules.sp.helpers import _check_sp_role
from flask_babel import gettext as _


def _to_float(v, default: float = 0.0) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _to_int(v, default: int = 0) -> int:
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def _can():
    return _check_sp_role(current_user)


# ─── S59: Hoshin X-Matrix ────────────────────────────────────────────────────

@app_bp.route("/k-plan/strategy/xmatrix")
@login_required
def sp_xmatrix_page():
    if not _can():
        return render_template("errors/403.html"), 403
    return render_template("platform/sp/xmatrix.html")


@app_bp.route("/k-plan/strategy/api/xmatrix")
@login_required
def sp_api_xmatrix():
    if not _can():
        return jsonify({"error": "yetki yok"}), 403
    try:
        py = get_active_plan_year_for_user(current_user)
    except Exception:
        py = None
    try:
        data = build_xmatrix(current_user.tenant_id, py.id if py else None)
        return jsonify({"success": True, **data})
    except Exception as e:
        current_app.logger.error(f"xmatrix error: {e}", exc_info=True)
        return jsonify({"success": False, "message": _("İşlem tamamlanamadı.")}), 500


# ─── S60: Blue Ocean ─────────────────────────────────────────────────────────

@app_bp.route("/k-plan/strategy/blue-ocean")
@login_required
def sp_blue_ocean_page():
    if not _can():
        return render_template("errors/403.html"), 403
    return render_template("platform/sp/blue_ocean.html")


@app_bp.route("/k-plan/strategy/api/blue-ocean/canvases")
@login_required
def sp_api_bo_canvases():
    if not _can():
        return jsonify({"error": "yetki yok"}), 403
    items = BlueOceanCanvas.query.filter_by(
        tenant_id=current_user.tenant_id, is_active=True
    ).order_by(BlueOceanCanvas.id.desc()).all()
    return jsonify({"success": True, "items": [c.to_dict() for c in items]})


@app_bp.route("/k-plan/strategy/api/blue-ocean/canvases", methods=["POST"])
@csrf.exempt
@login_required
def sp_api_bo_canvas_create():
    if not _can():
        return jsonify({"error": "yetki yok"}), 403
    d = request.get_json(silent=True) or {}
    name = (d.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name zorunlu"}), 400
    c = BlueOceanCanvas(
        tenant_id=current_user.tenant_id,
        name=name,
        industry=d.get("industry"),
        description=d.get("description"),
        competitor_names=d.get("competitor_names"),
    )
    add_and_commit_with_retry(c, "blue_ocean_canvases")
    return jsonify({"success": True, "item": c.to_dict()}), 201


@app_bp.route("/k-plan/strategy/api/blue-ocean/canvases/<int:cid>")
@login_required
def sp_api_bo_canvas_detail(cid):
    if not _can():
        return jsonify({"error": "yetki yok"}), 403
    c = BlueOceanCanvas.query.filter_by(
        id=cid, tenant_id=current_user.tenant_id
    ).first()
    if not c:
        return jsonify({"error": "not found"}), 404
    return jsonify({
        "success": True,
        "canvas": c.to_dict(),
        "factors": [f.to_dict() for f in sorted(c.factors, key=lambda x: x.order_index)],
        "errc": [e.to_dict() for e in sorted(c.errc_items, key=lambda x: x.order_index)],
    })


@app_bp.route("/k-plan/strategy/api/blue-ocean/canvases/<int:cid>/factors", methods=["POST"])
@csrf.exempt
@login_required
def sp_api_bo_factor_add(cid):
    if not _can():
        return jsonify({"error": "yetki yok"}), 403
    c = BlueOceanCanvas.query.filter_by(id=cid, tenant_id=current_user.tenant_id).first()
    if not c:
        return jsonify({"error": "not found"}), 404
    d = request.get_json(silent=True) or {}
    f = BlueOceanFactor(
        canvas_id=cid,
        name=d.get("name", "").strip(),
        self_score=_to_float(d.get("self_score"), 5),
        order_index=_to_int(d.get("order_index"), 0),
        competitor_scores=json.dumps(d.get("competitor_scores") or {}, ensure_ascii=False),
    )
    if not f.name:
        return jsonify({"error": "name zorunlu"}), 400
    add_and_commit_with_retry(f, "blue_ocean_factors")
    return jsonify({"success": True, "item": f.to_dict()}), 201


@app_bp.route("/k-plan/strategy/api/blue-ocean/canvases/<int:cid>/errc", methods=["POST"])
@csrf.exempt
@login_required
def sp_api_bo_errc_add(cid):
    if not _can():
        return jsonify({"error": "yetki yok"}), 403
    c = BlueOceanCanvas.query.filter_by(id=cid, tenant_id=current_user.tenant_id).first()
    if not c:
        return jsonify({"error": "not found"}), 404
    d = request.get_json(silent=True) or {}
    action = (d.get("action") or "").strip().lower()
    if action not in ("eliminate", "reduce", "raise", "create"):
        return jsonify({"error": "action: eliminate/reduce/raise/create"}), 400
    text_v = (d.get("text") or "").strip()
    if not text_v:
        return jsonify({"error": "text zorunlu"}), 400
    item = BlueOceanERRC(
        canvas_id=cid,
        action=action,
        text=text_v,
        rationale=d.get("rationale"),
        impact=d.get("impact"),
    )
    add_and_commit_with_retry(item, "blue_ocean_errc_items")
    return jsonify({"success": True, "item": item.to_dict()}), 201


# ─── S61: VRIO ───────────────────────────────────────────────────────────────

@app_bp.route("/k-plan/strategy/vrio")
@login_required
def sp_vrio_page():
    if not _can():
        return render_template("errors/403.html"), 403
    return render_template("platform/sp/vrio.html")


@app_bp.route("/k-plan/strategy/api/vrio")
@login_required
def sp_api_vrio_list():
    if not _can():
        return jsonify({"error": "yetki yok"}), 403
    items = VRIOResource.query.filter_by(
        tenant_id=current_user.tenant_id, is_active=True
    ).order_by(VRIOResource.id.desc()).all()
    return jsonify({"success": True, "items": [r.to_dict() for r in items]})


@app_bp.route("/k-plan/strategy/api/vrio", methods=["POST"])
@csrf.exempt
@login_required
def sp_api_vrio_create():
    if not _can():
        return jsonify({"error": "yetki yok"}), 403
    d = request.get_json(silent=True) or {}
    name = (d.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name zorunlu"}), 400
    r = VRIOResource(
        tenant_id=current_user.tenant_id,
        name=name,
        category=d.get("category"),
        description=d.get("description"),
        is_valuable=bool(d.get("is_valuable")),
        is_rare=bool(d.get("is_rare")),
        is_inimitable=bool(d.get("is_inimitable")),
        is_organized=bool(d.get("is_organized")),
        note=d.get("note"),
    )
    add_and_commit_with_retry(r, "vrio_resources")
    return jsonify({"success": True, "item": r.to_dict()}), 201


@app_bp.route("/k-plan/strategy/api/vrio/<int:rid>", methods=["PATCH"])
@csrf.exempt
@login_required
def sp_api_vrio_update(rid):
    if not _can():
        return jsonify({"error": "yetki yok"}), 403
    r = VRIOResource.query.filter_by(
        id=rid, tenant_id=current_user.tenant_id
    ).first()
    if not r:
        return jsonify({"error": "not found"}), 404
    d = request.get_json(silent=True) or {}
    for f in ("name", "category", "description", "note",
              "is_valuable", "is_rare", "is_inimitable", "is_organized"):
        if f in d:
            setattr(r, f, d[f])
    db.session.commit()
    return jsonify({"success": True, "item": r.to_dict()})


@app_bp.route("/k-plan/strategy/api/vrio/<int:rid>", methods=["DELETE"])
@csrf.exempt
@login_required
def sp_api_vrio_delete(rid):
    if not _can():
        return jsonify({"error": "yetki yok"}), 403
    r = VRIOResource.query.filter_by(
        id=rid, tenant_id=current_user.tenant_id
    ).first()
    if not r:
        return jsonify({"error": "not found"}), 404
    db.session.delete(r)
    db.session.commit()
    return jsonify({"success": True})


# ─── S62: Project EVM ────────────────────────────────────────────────────────

@app_bp.route("/k-plan/strategy/api/projects/<int:pid>/evm")
@login_required
def sp_api_project_evm(pid):
    if not _can():
        return jsonify({"error": "yetki yok"}), 403
    try:
        # S3: tenant_id ZORUNLU geçilir — `_can()` yalnız rol kontrolüdür,
        # sahiplik değil. Bu satır olmadan başka kurumun proje bütçesi okunuyordu.
        data = compute_project_evm(pid, tenant_id=current_user.tenant_id)
        return jsonify({"success": True, **data})
    except ValueError:
        return jsonify({"success": False, "message": _("Proje bulunamadı.")}), 404
    except Exception as e:
        current_app.logger.error(f"evm error: {e}", exc_info=True)
        return jsonify({"success": False, "message": _("İşlem tamamlanamadı.")}), 500


# ─── S63: Weekly Digest ──────────────────────────────────────────────────────

@app_bp.route("/k-plan/strategy/digest/weekly.html")
@login_required
def sp_digest_html():
    # Haftalık digest okuma raporu — tüm giriş yapmış kullanıcılar görebilir.
    tenant = getattr(current_user, "tenant", None)
    tenant_name = getattr(tenant, "name", None)
    html = render_digest_html(current_user.tenant_id, tenant_name)
    return Response(html, mimetype="text/html")


@app_bp.route("/k-plan/strategy/digest/weekly.pdf")
@login_required
def sp_digest_pdf():
    # Haftalık digest okuma raporu — tüm giriş yapmış kullanıcılar görebilir.
    tenant = getattr(current_user, "tenant", None)
    tenant_name = getattr(tenant, "name", None)
    content, mime = render_digest_pdf(current_user.tenant_id, tenant_name, tenant=tenant)
    ext = "pdf" if mime == "application/pdf" else "html"
    headers = {
        "Content-Disposition": f'attachment; filename="kokpitim_haftalik_rapor.{ext}"'
    }
    return Response(content, mimetype=mime, headers=headers)
