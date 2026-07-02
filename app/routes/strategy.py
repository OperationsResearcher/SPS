"""Strategy Blueprint - SWOT Analysis."""

from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required

from app.models import db
from app.models.strategy import SwotAnalysis
from app.utils.decorators import require_component

strategy_bp = Blueprint("strategy_bp", __name__, url_prefix="/strategy")


@strategy_bp.route("/swot", methods=["GET", "POST"])
@login_required
@require_component("swot_analizi")
def swot():
    """SWOT Analysis - GET lists items, POST adds/deletes via AJAX or form."""
    tenant_id = current_user.tenant_id
    if not tenant_id:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"success": False, "error": "Kurum bulunamadı."}), 400
        return render_template("strategy/swot.html", strengths=[], weaknesses=[], opportunities=[], threats=[])

    if request.method == "POST":
        action = request.form.get("action") or (request.get_json() or {}).get("action")
        if action == "add":
            category = (request.form.get("category") or (request.get_json() or {}).get("category") or "").strip()
            content = (request.form.get("content") or (request.get_json() or {}).get("content") or "").strip()
            if category and content and category in ("strength", "weakness", "opportunity", "threat"):
                item = SwotAnalysis(tenant_id=tenant_id, category=category, content=content, is_active=True)
                db.session.add(item)
                db.session.commit()
                if _is_ajax():
                    return jsonify({"success": True, "id": item.id, "category": category, "content": content})
                from flask import flash, redirect, url_for

                flash("SWOT maddesi eklendi.", "success")
                return redirect(url_for("strategy_bp.swot"))
            if _is_ajax():
                return jsonify({"success": False, "error": "Geçersiz veri."}), 400
        elif action == "delete":
            item_id = request.form.get("id") or (request.get_json() or {}).get("id")
            item = SwotAnalysis.query.filter_by(id=item_id, tenant_id=tenant_id, is_active=True).first()
            if item:
                item.is_active = False
                db.session.commit()
                if _is_ajax():
                    return jsonify({"success": True})
                from flask import flash, redirect, url_for

                flash("SWOT maddesi silindi.", "success")
                return redirect(url_for("strategy_bp.swot"))
            if _is_ajax():
                return jsonify({"success": False, "error": "Kayıt bulunamadı."}), 404

    items = SwotAnalysis.query.filter_by(tenant_id=tenant_id, is_active=True).order_by(SwotAnalysis.created_at).all()
    strengths = [i for i in items if i.category == "strength"]
    weaknesses = [i for i in items if i.category == "weakness"]
    opportunities = [i for i in items if i.category == "opportunity"]
    threats = [i for i in items if i.category == "threat"]
    return render_template(
        "strategy/swot.html",
        strengths=strengths,
        weaknesses=weaknesses,
        opportunities=opportunities,
        threats=threats,
    )


def _is_ajax():
    return request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json
