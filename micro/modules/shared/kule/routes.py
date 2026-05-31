"""Kule yardımcı sistemi — tur API route'ları."""

from flask import jsonify, request, abort
from flask_login import login_required, current_user

from platform_core import app_bp
from app.extensions import csrf
from app.services.kule_service import (
    load_tour,
    get_or_create_progress,
    mark_seen,
    mark_complete,
    mark_dismiss,
    restart_tour,
    is_audience_allowed,
)


@app_bp.route("/api/kule/tour/<tour_key>", methods=["GET"])
@login_required
def kule_get_tour(tour_key: str):
    """Tur tanımını + kullanıcı durumunu döner."""
    tour = load_tour(tour_key)
    if not tour:
        return jsonify({"success": False, "message": "Tur bulunamadı"}), 404

    user_role = current_user.role.name if current_user.role else None
    if not is_audience_allowed(tour, user_role):
        return jsonify({"success": False, "message": "Bu tur senin için değil"}), 403

    progress = get_or_create_progress(current_user.id, tour_key)

    # Welcome metninde {{ first_name }} placeholder'ını doldur
    welcome = tour.get("welcome") or {}
    if welcome.get("body"):
        welcome["body"] = welcome["body"].replace(
            "{{ first_name }}", current_user.first_name or current_user.email
        )

    return jsonify({
        "success": True,
        "tour": {
            "key": tour["key"],
            "title": tour.get("title"),
            "auto_show": bool(tour.get("auto_show", True)),
            "welcome": welcome,
            "steps": tour.get("steps") or [],
            "finale": tour.get("finale") or {},
        },
        "progress": progress.to_dict(),
    })


@app_bp.route("/api/kule/tour/<tour_key>/seen", methods=["POST"])
@login_required
@csrf.exempt
def kule_mark_seen(tour_key: str):
    """Kullanıcı turu görüntüledi (seen_count artar)."""
    row = mark_seen(current_user.id, tour_key)
    return jsonify({"success": True, "progress": row.to_dict()})


@app_bp.route("/api/kule/tour/<tour_key>/complete", methods=["POST"])
@login_required
@csrf.exempt
def kule_mark_complete(tour_key: str):
    """Tur tamamlandı."""
    row = mark_complete(current_user.id, tour_key)
    return jsonify({"success": True, "progress": row.to_dict()})


@app_bp.route("/api/kule/tour/<tour_key>/dismiss", methods=["POST"])
@login_required
@csrf.exempt
def kule_mark_dismiss(tour_key: str):
    """Kullanıcı turu atladı."""
    row = mark_dismiss(current_user.id, tour_key)
    return jsonify({"success": True, "progress": row.to_dict()})


@app_bp.route("/api/kule/tour/<tour_key>/restart", methods=["POST"])
@login_required
@csrf.exempt
def kule_restart(tour_key: str):
    """Tur durumunu sıfırla, tekrar gösterilebilir hale gelsin."""
    row = restart_tour(current_user.id, tour_key)
    return jsonify({"success": True, "progress": row.to_dict()})
