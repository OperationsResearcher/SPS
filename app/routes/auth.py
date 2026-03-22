"""Auth Blueprint - login, logout, profile."""

import os
import uuid

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from app.models import db
from app.models.core import User

auth_bp = Blueprint("auth_bp", __name__, url_prefix="")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Handle login form - GET shows form, POST validates credentials."""
    if current_user.is_authenticated:
        return redirect(url_for("micro_bp.launcher"))

    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        if not email or not password:
            flash("E-posta ve şifre gereklidir.", "danger")
            return render_template("auth/login.html")

        user = User.query.filter_by(email=email, is_active=True).first()
        if not user or not check_password_hash(user.password_hash, password):
            flash("Geçersiz e-posta veya şifre.", "danger")
            return render_template("auth/login.html")

        login_user(user)
        flash("Giriş başarılı.", "success")
        next_url = request.args.get("next") or url_for("micro_bp.launcher")
        return redirect(next_url)

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    """Log out user and redirect to login."""
    logout_user()
    return redirect(url_for("public_login"))


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Profil sayfası - GET gösterir, POST günceller."""
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        first_name = (request.form.get("first_name") or "").strip() or None
        last_name = (request.form.get("last_name") or "").strip() or None
        phone_number = (request.form.get("phone_number") or "").strip() or None
        job_title = (request.form.get("job_title") or "").strip() or None
        department = (request.form.get("department") or "").strip() or None
        profile_picture = (request.form.get("profile_picture") or "").strip() or None
        current_password = request.form.get("current_password") or ""
        new_password = request.form.get("new_password") or ""

        if not email:
            flash("E-posta zorunludur.", "danger")
            return redirect(url_for("auth_bp.profile"))

        existing = User.query.filter_by(email=email).first()
        if existing and existing.id != current_user.id:
            flash("Bu e-posta adresi başka bir kullanıcı tarafından kullanılıyor.", "danger")
            return redirect(url_for("auth_bp.profile"))

        if new_password or current_password:
            if not current_password:
                flash("Şifre değiştirmek için mevcut şifrenizi girmelisiniz.", "danger")
                return redirect(url_for("auth_bp.profile"))
            if not check_password_hash(current_user.password_hash, current_password):
                flash("Mevcut şifre yanlış.", "danger")
                return redirect(url_for("auth_bp.profile"))
            if len(new_password) < 6:
                flash("Yeni şifre en az 6 karakter olmalıdır.", "danger")
                return redirect(url_for("auth_bp.profile"))

        current_user.email = email
        current_user.first_name = first_name
        current_user.last_name = last_name
        current_user.phone_number = phone_number
        current_user.job_title = job_title
        current_user.department = department
        current_user.profile_picture = profile_picture
        if new_password:
            current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        flash("Profil başarıyla güncellendi.", "success")
        return redirect(url_for("auth_bp.profile"))

    return render_template("auth/profile.html")


@auth_bp.route("/profile/upload-photo", methods=["POST"])
@login_required
def upload_profile_photo():
    """Profil fotoğrafı yükle - JSON yanıt."""
    from flask import jsonify

    if "file" not in request.files:
        return jsonify({"success": False, "message": "Dosya seçilmedi."}), 400
    file = request.files["file"]
    if not file or file.filename == "":
        return jsonify({"success": False, "message": "Dosya seçilmedi."}), 400
    allowed = {"png", "jpg", "jpeg", "gif", "svg", "webp"}
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in allowed:
        return jsonify({"success": False, "message": "Geçersiz dosya tipi."}), 400

    filename = secure_filename(file.filename) or "photo"
    unique = f"{uuid.uuid4().hex}_{filename}"
    upload_dir = os.path.join("static", "uploads", "profiles")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, unique)
    file.save(file_path)

    if current_user.profile_picture:
        old = current_user.profile_picture.lstrip("/")
        if os.path.exists(old):
            try:
                os.remove(old)
            except OSError:
                pass

    current_user.profile_picture = f"/static/uploads/profiles/{unique}"
    db.session.commit()
    return jsonify({"success": True, "message": "Fotoğraf yüklendi.", "photo_url": current_user.profile_picture})


def _parse_json_prefs(val, default=None):
    """Parse JSON string from User column."""
    if default is None:
        default = {}
    if not val:
        return default
    try:
        import json
        return json.loads(val) if isinstance(val, str) else (val or default)
    except (ValueError, TypeError):
        return default


@auth_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    """Ayarlar sayfası - GET gösterir, POST günceller."""
    import json as json_module

    if request.method == "POST":
        action = request.form.get("action", "all")

        if action in ("notifications", "all"):
            notify_email = request.form.get("notify_email") in ("on", "1", "true")
            notify_process = request.form.get("notify_process") in ("on", "1", "true")
            notify_task = request.form.get("notify_task") in ("on", "1", "true")
            notify_deadline = request.form.get("notify_deadline") in ("on", "1", "true")
            prefs = _parse_json_prefs(getattr(current_user, "notification_preferences", None))
            prefs.update({
                "email": notify_email,
                "process": notify_process,
                "task": notify_task,
                "deadline": notify_deadline,
            })
            current_user.notification_preferences = json_module.dumps(prefs)

        if action in ("locale", "all"):
            language = request.form.get("language") or "tr"
            timezone = request.form.get("timezone") or "Europe/Istanbul"
            date_format = request.form.get("date_format") or "dd.mm.yyyy"
            prefs = _parse_json_prefs(getattr(current_user, "locale_preferences", None))
            prefs.update({"language": language, "timezone": timezone, "date_format": date_format})
            current_user.locale_preferences = json_module.dumps(prefs)

        if action in ("theme", "all"):
            theme = request.form.get("theme") or "light"
            color = request.form.get("primary_color") or "primary"
            prefs = _parse_json_prefs(getattr(current_user, "theme_preferences", None))
            prefs.update({"theme": theme, "color": color})
            current_user.theme_preferences = json_module.dumps(prefs)

        if action in ("guide", "all"):
            show_guides = request.form.get("show_page_guides") == "on" or request.form.get("show_page_guides") == "1"
            char_style = request.form.get("guide_character_style") or "professional"
            if char_style not in ("professional", "friendly", "minimal"):
                char_style = "professional"
            current_user.show_page_guides = show_guides
            current_user.guide_character_style = char_style

        db.session.commit()
        flash("Ayarlar kaydedildi.", "success")
        return redirect(url_for("auth_bp.settings"))

    # GET - load current values for template
    notif_prefs = _parse_json_prefs(getattr(current_user, "notification_preferences", None), {
        "email": True, "process": True, "task": True, "deadline": True
    })
    locale_prefs = _parse_json_prefs(getattr(current_user, "locale_preferences", None), {
        "language": "tr", "timezone": "Europe/Istanbul", "date_format": "dd.mm.yyyy"
    })
    theme_prefs = _parse_json_prefs(getattr(current_user, "theme_preferences", None), {"theme": "light", "color": "primary"})

    return render_template(
        "auth/settings.html",
        notif_prefs=notif_prefs,
        locale_prefs=locale_prefs,
        theme_prefs=theme_prefs,
        show_page_guides=getattr(current_user, "show_page_guides", True),
        guide_character_style=getattr(current_user, "guide_character_style", "professional"),
    )
