from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
import os
from werkzeug.utils import secure_filename
from app.models import db
from app.models.core import Ticket

core_bp = Blueprint("core_bp", __name__)


@core_bp.route("/offline.html")
def offline():
    """PWA offline fallback page."""
    return render_template("offline.html")


@core_bp.route("/kule/send", methods=["POST"])
@login_required
def kule_send():
    """Kullanıcıların Kuleye bilet (ticket) gönderme rotası."""
    try:
        subject = request.form.get("subject")
        message = request.form.get("message")
        page_url = request.form.get("page_url")

        if not subject or not message:
            return jsonify({"success": False, "message": "Konu ve mesaj zorunludur."}), 400

        # Create new ticket
        ticket = Ticket(
            user_id=current_user.id,
            tenant_id=current_user.tenant_id,
            page_url=page_url[:500] if page_url else None,
            subject=subject[:50],
            message=message,
            status="Bekliyor"
        )
        
        # Handle screenshot upload if any
        if 'screenshot' in request.files:
            file = request.files['screenshot']
            if file and file.filename:
                # Basic security block
                if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    return jsonify({"success": False, "message": "Geçersiz dosya formatı. Sadece resimler kabul edilir."}), 400
                    
                filename = secure_filename(f"ticket_{current_user.id}_{file.filename}")
                upload_dir = os.path.join("static", "uploads", "tickets")
                os.makedirs(upload_dir, exist_ok=True)
                filepath = os.path.join(upload_dir, filename)
                file.save(filepath)
                ticket.screenshot_path = f"uploads/tickets/{filename}"

        db.session.add(ticket)
        db.session.commit()

        return jsonify({"success": True, "message": "Bilet başarıyla gönderildi."})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Kule bağlantı hatası: {str(e)}"}), 500
