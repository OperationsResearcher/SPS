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

from platform_core import app_bp
from app.models import db
from app.models.core import User
from extensions import csrf
from flask_babel import gettext as _


# Giriş: kök `/login` → `public_login` (app factory). Eski micro blueprint giriş view'ı kaldırıldı (URL çakışması).


@app_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profil():
    """Profil sayfası — GET: form, POST: JSON API güncelleme."""
    if request.method == "GET":
        return render_template("platform/auth/profil.html")

    # POST — JSON body
    data = request.get_json() or {}
    try:
        # Şifre değişikliği
        if data.get("current_password") or data.get("new_password"):
            if not data.get("current_password"):
                return jsonify({"success": False, "message": _("Şifre değiştirmek için mevcut şifrenizi girmelisiniz.")}), 400
            if not check_password_hash(current_user.password_hash, data["current_password"]):
                return jsonify({"success": False, "message": _("Mevcut şifre yanlış.")}), 400
            new_pw = data.get("new_password", "")
            # validate_password 8 karakter + karmaşıklık kurallarını uygular
            from app.utils.password_policy import validate_password
            ok, errs = validate_password(new_pw, username=current_user.email)
            if not ok:
                return jsonify({"success": False, "message": " ".join(errs)}), 400
            current_user.password_hash = generate_password_hash(new_pw)

        # E-posta duplicate kontrolü
        new_email = (data.get("email") or "").strip().lower()
        if new_email and new_email != current_user.email:
            if User.query.filter(User.email == new_email, User.id != current_user.id).first():
                return jsonify({"success": False, "message": _("Bu e-posta başka bir kullanıcı tarafından kullanılıyor.")}), 400
            current_user.email = new_email

        # Profil alanları
        current_user.first_name   = data.get("first_name",   current_user.first_name  or "").strip()
        current_user.last_name    = data.get("last_name",    current_user.last_name   or "").strip()
        current_user.phone_number = data.get("phone_number", current_user.phone_number or "").strip() or None
        current_user.job_title    = data.get("job_title",    current_user.job_title   or "").strip() or None
        current_user.department   = data.get("department",   current_user.department  or "").strip() or None
        # profile_picture yalnızca /profil/foto-yukle endpoint'i üzerinden güncellenir.

        db.session.commit()
        return jsonify({"success": True, "message": _("Profil güncellendi.")})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[profil_update] {e}")
        return jsonify({"success": False, "message": _("Profil güncellenirken hata oluştu.")}), 500


@app_bp.route("/profile/photo-upload", methods=["POST"])
@login_required
@csrf.exempt  # multipart/form-data JS fetch ile gönderilir; form body'ye token
              # eklemek için frontend JS'nin FormData'ya csrf_token field eklemesi
              # gerekir (alternatif: X-CSRFToken header). Şimdilik SameSite=Lax
              # cookie + @login_required yeterli koruma sağlar. Frontend'e
              # FormData.append('csrf_token', ...) eklenirse bu decorator kaldırılabilir.
def profil_foto_yukle():
    """Profil fotoğrafı yükleme — fiziksel silme yok, sadece DB güncellenir."""
    if "file" not in request.files:
        return jsonify({"success": False, "message": _("Dosya seçilmedi.")}), 400
    file = request.files["file"]
    if not file or file.filename == "":
        return jsonify({"success": False, "message": _("Dosya seçilmedi.")}), 400

    allowed_ext   = {"png", "jpg", "jpeg", "gif", "webp"}
    allowed_mime  = {"image/png", "image/jpeg", "image/jpg", "image/gif", "image/webp"}
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in allowed_ext:
        return jsonify({"success": False, "message": f"Geçersiz dosya tipi. İzin verilenler: {', '.join(allowed_ext)}"}), 400
    if file.mimetype and file.mimetype not in allowed_mime:
        return jsonify({"success": False, "message": _("Geçersiz dosya içeriği. Yalnızca resim dosyaları kabul edilir.")}), 400

    # Dosya boyutu — 15MB üst sınır (büyükse de resize edeceğiz, bu sadece güvenlik)
    file_content = file.read()
    file_size = len(file_content)
    file.seek(0)
    if file_size > 15 * 1024 * 1024:
        return jsonify({"success": False, "message": _("Dosya boyutu çok büyük (max 15 MB).")}), 400

    try:
        upload_folder = os.path.join(current_app.static_folder, "uploads", "profiles")
        os.makedirs(upload_folder, exist_ok=True)

        # ── Pillow ile resize + optimize ────────────────────────────────────
        # Profil fotoğrafı için 512×512 yeter (retina ekranda bile kaliteli)
        MAX_DIM = 512
        JPEG_QUALITY = 85
        out_filename = f"{uuid.uuid4().hex}.jpg"   # her zaman JPEG'e çevir
        out_path = os.path.join(upload_folder, out_filename)

        try:
            from PIL import Image, ImageOps
            import io as _io
            img = Image.open(_io.BytesIO(file_content))
            # EXIF orientation düzeltmesi (telefondan dik çekilen fotoğraflar)
            img = ImageOps.exif_transpose(img)
            # RGBA / palette → RGB (JPEG için)
            if img.mode in ("RGBA", "LA", "P"):
                bg = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode in ("RGBA", "LA"):
                    bg.paste(img, mask=img.split()[-1])
                else:
                    bg.paste(img.convert("RGBA"), mask=img.convert("RGBA").split()[-1])
                img = bg
            elif img.mode != "RGB":
                img = img.convert("RGB")
            # Aspect-ratio koruyarak resize
            img.thumbnail((MAX_DIM, MAX_DIM), Image.LANCZOS)
            img.save(out_path, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
            current_app.logger.info(
                f"[profil_foto] {current_user.email}: "
                f"orijinal {file_size//1024} KB → resize {os.path.getsize(out_path)//1024} KB "
                f"({img.width}×{img.height})"
            )
        except ImportError:
            # Pillow yoksa: orijinali kaydet (eski davranış)
            current_app.logger.warning("[profil_foto] Pillow kurulu degil, resize yapilamadi")
            out_filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
            out_path = os.path.join(upload_folder, out_filename)
            file.save(out_path)

        current_user.profile_picture = f"/static/uploads/profiles/{out_filename}"
        db.session.commit()
        return jsonify({
            "success": True,
            "message": _("Fotoğraf yüklendi ve optimize edildi."),
            "photo_url": current_user.profile_picture,
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[profil_foto_yukle] {e}", exc_info=True)
        return jsonify({"success": False, "message": _("Fotoğraf yüklenirken bir hata oluştu.")}), 500


@app_bp.route("/settings")
@login_required
def ayarlar():
    """Ayarlar hub sayfası."""
    return render_template("platform/ayarlar/index.html")


@app_bp.route("/settings/account", methods=["GET", "POST"])
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
        "platform/auth/ayarlar.html",
        notif_prefs=notif_prefs,
        locale_prefs=locale_prefs,
        theme_prefs=theme_prefs,
        show_page_guides=getattr(current_user, "show_page_guides", True),
        guide_character_style=getattr(current_user, "guide_character_style", "professional"),
    )


# ── Hızlı tema güncelleme (dark mode toggle) ─────────────────────────────────
@app_bp.route("/api/profile/theme", methods=["GET", "POST"])
@login_required
@csrf.exempt  # JS fetch ile AJAX çağrısı — SameSite=Lax cookie koruması yeterli
def api_profile_theme():
    """Kullanıcının tema tercihini sunucuya kaydeder/okur (çoklu cihaz senkronu)."""
    raw = getattr(current_user, "theme_preferences", None) or "{}"
    try:
        prefs = json.loads(raw) if isinstance(raw, str) else (raw or {})
    except Exception:
        prefs = {}

    if request.method == "GET":
        return jsonify({
            "success": True,
            "theme": prefs.get("theme") or "light",
            "color": prefs.get("color") or "primary",
        })

    data = request.get_json(silent=True) or {}
    theme = (data.get("theme") or "").lower().strip()
    if theme not in ("light", "dark"):
        return jsonify({"success": False, "message": _("theme alanı 'light' veya 'dark' olmalı.")}), 400
    prefs["theme"] = theme
    if data.get("color"):
        prefs["color"] = data.get("color")
    try:
        current_user.theme_preferences = json.dumps(prefs)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[api_profile_theme] {e}")
        return jsonify({"success": False, "message": "Kaydedilemedi."}), 500
    return jsonify({"success": True, "theme": prefs["theme"], "color": prefs.get("color", "primary")})
