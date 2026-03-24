"""Auth sayfaları — micro platform için profil ve ayarlar.

Klasik giriş kökta `public_login` (`/login`); çıkış `public_logout` (`/logout`).
"""

import json
import os
import uuid

from flask import render_template, redirect, url_for, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from micro import micro_bp
from app.models import db
from app.models.core import User
from extensions import csrf


# Giriş: kök `/login` → `public_login` (app factory). Eski `micro_bp.micro_login` kaldırıldı (URL çakışması).


@micro_bp.route("/profil", methods=["GET", "POST"])
@login_required
def profil():
    """Profil sayfası — GET: form, POST: JSON API güncelleme."""
    if request.method == "GET":
        return render_template("micro/auth/profil.html")

    # POST — JSON body
    data = request.get_json() or {}
    try:
        # Şifre değişikliği
        if data.get("current_password") or data.get("new_password"):
            if not data.get("current_password"):
                return jsonify({"success": False, "message": "Şifre değiştirmek için mevcut şifrenizi girmelisiniz."}), 400
            if not check_password_hash(current_user.password_hash, data["current_password"]):
                return jsonify({"success": False, "message": "Mevcut şifre yanlış."}), 400
            new_pw = data.get("new_password", "")
            if len(new_pw) < 6:
                return jsonify({"success": False, "message": "Yeni şifre en az 6 karakter olmalıdır."}), 400
            current_user.password_hash = generate_password_hash(new_pw)

        # E-posta duplicate kontrolü
        new_email = (data.get("email") or "").strip().lower()
        if new_email and new_email != current_user.email:
            if User.query.filter(User.email == new_email, User.id != current_user.id).first():
                return jsonify({"success": False, "message": "Bu e-posta başka bir kullanıcı tarafından kullanılıyor."}), 400
            current_user.email = new_email

        # Profil alanları
        current_user.first_name   = data.get("first_name",   current_user.first_name  or "").strip()
        current_user.last_name    = data.get("last_name",    current_user.last_name   or "").strip()
        current_user.phone_number = data.get("phone_number", current_user.phone_number or "").strip() or None
        current_user.job_title    = data.get("job_title",    current_user.job_title   or "").strip() or None
        current_user.department   = data.get("department",   current_user.department  or "").strip() or None
        if "profile_picture" in data:
            current_user.profile_picture = data["profile_picture"] or None

        db.session.commit()
        return jsonify({"success": True, "message": "Profil güncellendi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[profil_update] {e}")
        return jsonify({"success": False, "message": "Profil güncellenirken hata oluştu."}), 500


@micro_bp.route("/profil/foto-yukle", methods=["POST"])
@csrf.exempt
@login_required
def profil_foto_yukle():
    """Profil fotoğrafı yükleme — fiziksel silme yok, sadece DB güncellenir."""
    if "file" not in request.files:
        return jsonify({"success": False, "message": "Dosya seçilmedi."}), 400
    file = request.files["file"]
    if not file or file.filename == "":
        return jsonify({"success": False, "message": "Dosya seçilmedi."}), 400

    allowed_ext   = {"png", "jpg", "jpeg", "gif", "webp"}
    allowed_mime  = {"image/png", "image/jpeg", "image/jpg", "image/gif", "image/webp"}
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in allowed_ext:
        return jsonify({"success": False, "message": f"Geçersiz dosya tipi. İzin verilenler: {', '.join(allowed_ext)}"}), 400
    if file.mimetype and file.mimetype not in allowed_mime:
        return jsonify({"success": False, "message": "Geçersiz dosya içeriği. Yalnızca resim dosyaları kabul edilir."}), 400

    # Dosya boyutu kontrolü — 5MB
    file_content = file.read()
    file_size = len(file_content)
    file.seek(0)
    if file_size > 5 * 1024 * 1024:
        return jsonify({"success": False, "message": "Dosya boyutu çok büyük. Maksimum 5MB yükleyebilirsiniz."}), 400

    try:
        filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        upload_folder = os.path.join(current_app.static_folder, "uploads", "profiles")
        os.makedirs(upload_folder, exist_ok=True)
        file.save(os.path.join(upload_folder, filename))

        current_user.profile_picture = f"/static/uploads/profiles/{filename}"
        db.session.commit()
        return jsonify({"success": True, "message": "Fotoğraf yüklendi.", "photo_url": current_user.profile_picture})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[profil_foto_yukle] {e}")
        return jsonify({"success": False, "message": f"Fotoğraf yüklenirken hata oluştu: {str(e)}"}), 500


@micro_bp.route("/ayarlar")
@login_required
def ayarlar():
    """Ayarlar hub sayfası."""
    return render_template("micro/ayarlar/index.html")


@micro_bp.route("/ayarlar/hesap", methods=["GET", "POST"])
@login_required
def ayarlar_hesap():
    """Kişisel hesap ayarları — mevcut auth_bp.settings ile aynı mantık, micro UI."""
    if request.method == "POST":
        return redirect(url_for("auth_bp.settings"), code=307)

    # GET — mevcut ayarları yükle
    def _parse_json(val, default=None):
        if default is None:
            default = {}
        if not val:
            return default
        try:
            return json.loads(val) if isinstance(val, str) else (val or default)
        except (ValueError, TypeError):
            return default

    notif_prefs = _parse_json(getattr(current_user, "notification_preferences", None), {
        "email": True, "process": True, "task": True, "deadline": True
    })
    locale_prefs = _parse_json(getattr(current_user, "locale_preferences", None), {
        "language": "tr", "timezone": "Europe/Istanbul", "date_format": "dd.mm.yyyy"
    })
    theme_prefs = _parse_json(getattr(current_user, "theme_preferences", None), {
        "theme": "light", "color": "primary"
    })

    return render_template(
        "micro/auth/ayarlar.html",
        notif_prefs=notif_prefs,
        locale_prefs=locale_prefs,
        theme_prefs=theme_prefs,
        show_page_guides=getattr(current_user, "show_page_guides", True),
        guide_character_style=getattr(current_user, "guide_character_style", "professional"),
    )
