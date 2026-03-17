"""Bildirim Merkezi modülü."""

from datetime import datetime, timezone

from flask import render_template, jsonify, request
from flask_login import login_required, current_user

from micro import micro_bp
from app.models import db
from app.models.core import Notification


@micro_bp.route("/bildirim")
@login_required
def bildirim():
    """Bildirim Merkezi ana sayfası — okunmamışlar önce."""
    bildirimler = (
        Notification.query
        .filter_by(user_id=current_user.id)
        .order_by(Notification.is_read.asc(), Notification.created_at.desc())
        .limit(50)
        .all()
    )
    return render_template("micro/bildirim/index.html", bildirimler=bildirimler)


@micro_bp.route("/bildirim/api/unread-count")
@login_required
def bildirim_api_unread_count():
    """Okunmamış bildirim sayısı — topbar badge için."""
    count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({"count": count})


@micro_bp.route("/bildirim/api/mark-read/<int:notif_id>", methods=["POST"])
@login_required
def bildirim_api_mark_read(notif_id):
    """Tekil bildirimi okundu işaretle."""
    notif = Notification.query.filter_by(id=notif_id, user_id=current_user.id).first_or_404()
    try:
        notif.is_read = True
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        from flask import current_app
        current_app.logger.error(f"[bildirim_api_mark_read] {e}")
        return jsonify({"success": False, "message": str(e)}), 400


@micro_bp.route("/bildirim/api/mark-all-read", methods=["POST"])
@login_required
def bildirim_api_mark_all_read():
    """Tüm bildirimleri okundu işaretle."""
    try:
        Notification.query.filter_by(
            user_id=current_user.id, is_read=False
        ).update({"is_read": True})
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        from flask import current_app
        current_app.logger.error(f"[bildirim_api_mark_all_read] {e}")
        return jsonify({"success": False, "message": str(e)}), 400
