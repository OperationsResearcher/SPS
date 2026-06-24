"""Scenario Branching routes (Sprint 56 — Ö5)."""
from __future__ import annotations

from flask import render_template, jsonify, request, current_app
from flask_login import login_required, current_user

from platform_core import app_bp
from app.extensions import csrf
from extensions import db
from app.models.plan_year import PlanYear
from app.services.plan_year_service import clone_full_plan_year
from micro.modules.sp.helpers import _check_sp_role
from flask_babel import gettext as _


def _can():
    return _check_sp_role(current_user)


@app_bp.route("/sp/scenarios")
@login_required
def sp_scenarios_page():
    if not _can():
        return render_template("errors/403.html"), 403
    return render_template("platform/sp/scenarios.html")


@app_bp.route("/sp/api/scenarios")
@login_required
def sp_api_scenarios_list():
    """Tenant'a ait tüm plan yılları + senaryo ağacı."""
    if not _can():
        return jsonify({"error": "yetki yok"}), 403
    tid = current_user.tenant_id
    rows = PlanYear.query.filter_by(tenant_id=tid).order_by(
        PlanYear.year.desc(), PlanYear.id
    ).all()

    items = []
    for py in rows:
        items.append({
            "id": py.id,
            "year": py.year,
            "name": py.name,
            "status": py.status,
            "scenario_of_id": py.scenario_of_id,
            "scenario_label": py.scenario_label,
            "is_scenario": py.scenario_of_id is not None,
            "created_at": py.created_at.isoformat() if py.created_at else None,
        })
    return jsonify({"success": True, "items": items})


@app_bp.route("/sp/api/scenarios", methods=["POST"])
@csrf.exempt
@login_required
def sp_api_scenario_create():
    """Bir plan yılından senaryo dalı oluştur."""
    if not _can():
        return jsonify({"error": "yetki yok"}), 403
    data = request.get_json(silent=True) or {}
    base_id = data.get("base_plan_year_id")
    label = (data.get("scenario_label") or "").strip().lower()
    if not base_id or not label:
        return jsonify({"error": "base_plan_year_id ve scenario_label zorunlu"}), 400
    if label not in ("baseline", "optimistic", "pessimistic") and len(label) > 50:
        return jsonify({"error": "scenario_label geçersiz"}), 400

    base = PlanYear.query.filter_by(
        id=base_id, tenant_id=current_user.tenant_id
    ).first()
    if not base:
        return jsonify({"error": "base plan year bulunamadı"}), 404

    # Aynı senaryo label zaten varsa engelle
    dup = PlanYear.query.filter_by(
        tenant_id=current_user.tenant_id,
        year=base.year,
        scenario_of_id=base.id,
        scenario_label=label,
    ).first()
    if dup:
        return jsonify({"error": f"'{label}' senaryosu zaten var (id={dup.id})"}), 409

    try:
        new_py = clone_full_plan_year(base, base.year, as_scenario_label=label)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"scenario_create error: {e}", exc_info=True)
        return jsonify({"success": False, "message": _("İşlem tamamlanamadı.")}), 500

    return jsonify({
        "success": True,
        "scenario": {
            "id": new_py.id, "year": new_py.year,
            "name": new_py.name, "scenario_label": new_py.scenario_label,
            "scenario_of_id": new_py.scenario_of_id,
        },
    }), 201


@app_bp.route("/sp/api/scenarios/<int:py_id>", methods=["DELETE"])
@csrf.exempt
@login_required
def sp_api_scenario_delete(py_id):
    if not _can():
        return jsonify({"error": "yetki yok"}), 403
    py = PlanYear.query.filter_by(
        id=py_id, tenant_id=current_user.tenant_id
    ).first()
    if not py:
        return jsonify({"error": "not found"}), 404
    if py.scenario_of_id is None:
        return jsonify({"error": "yalnızca senaryolar silinebilir"}), 400
    try:
        db.session.delete(py)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": _("İşlem tamamlanamadı.")}), 500
    return jsonify({"success": True})


# ── Senaryo / What-if Kıyas ───────────────────────────────────────────────────

@app_bp.route("/sp/scenarios/compare")
@login_required
def sp_scenarios_compare_page():
    """Baseline ⟷ senaryo yan yana kıyas ekranı."""
    if not _can():
        return render_template("errors/403.html"), 403
    return render_template("platform/sp/scenarios_kiyas.html")


@app_bp.route("/sp/api/scenarios/compare")
@login_required
def sp_api_scenarios_compare():
    """Seçilen plan yılları/senaryoları için vizyon skorlarını salt-okunur hesaplar.

    Veriyi DEĞİŞTİRMEZ (persist_pg_scores=False).
    """
    if not _can():
        return jsonify({"error": "yetki yok"}), 403
    raw = request.args.get("ids", "")
    ids = [int(x) for x in raw.split(",") if x.strip().isdigit()][:6]
    if not ids:
        return jsonify({"success": False, "message": "ids gerekli"}), 400

    from app.services.score_engine_service import compute_vision_score
    tid = current_user.tenant_id
    out = []
    for pid in ids:
        py = PlanYear.query.filter_by(id=pid, tenant_id=tid).first()
        if not py:
            continue
        vs = None
        try:
            res = compute_vision_score(
                tid, year=py.year, plan_year=py, persist_pg_scores=False
            )
            vs = res.get("vision_score") if isinstance(res, dict) else None
        except Exception as e:
            current_app.logger.info(f"[scenario-compare] {pid} skor hatası: {e}")
        out.append({
            "id": py.id,
            "year": py.year,
            "name": py.name,
            "label": py.scenario_label or ("baseline" if py.scenario_of_id is None else "senaryo"),
            "is_scenario": py.scenario_of_id is not None,
            "vision_score": round(vs, 1) if isinstance(vs, (int, float)) else None,
        })
    return jsonify({"success": True, "items": out})
