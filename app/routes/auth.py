"""Auth Blueprint - login, logout, profile."""

import os
import uuid

from flask import Blueprint, flash, redirect, render_template, request, url_for, current_app
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from app.models import db
from app.models.core import User
from app.utils.audit_logger import AuditLogger
from app.utils.security import limiter

auth_bp = Blueprint("auth_bp", __name__, url_prefix="")


def _write_auth_audit(action, user=None):
    """Login/Logout audit kaydı (hata olsa da akışı bozmaz)."""
    try:
        AuditLogger.log(
            action=action,
            resource_type="GÜVENLİK",
            resource_id=(user.id if user else None),
            description=f"Auth event: {action}",
        )
    except Exception as e:
        current_app.logger.error(f"[auth_audit:{action}] {e}")


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit(lambda: current_app.config.get("RATELIMIT_LOGIN", "15 per minute; 100 per hour") or "15 per minute", methods=["POST"])
def login():
    """Handle login form - GET shows form, POST validates credentials."""
    if current_user.is_authenticated:
        return redirect(url_for("app_bp.launcher"))

    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        ip = request.remote_addr or "unknown"

        if not email or not password:
            flash("E-posta ve şifre gereklidir.", "danger")
            return render_template("auth/login.html")

        # Sprint 19.2: brute force koruması
        from app.utils.login_throttle import is_locked, record_failure, clear_failures
        locked, remaining = is_locked(email, ip)
        if locked:
            _write_auth_audit("LOGIN_BLOCKED_LOCKED", None)
            mins = max(1, remaining // 60)
            flash(f"Çok fazla başarısız deneme. Hesap {mins} dakika boyunca kilitli.", "danger")
            return render_template("auth/login.html"), 429

        user = User.query.filter_by(email=email, is_active=True).first()
        if not user or not check_password_hash(user.password_hash, password):
            _write_auth_audit("LOGIN_FAILED", None)
            now_locked, attempts = record_failure(email, ip)
            if now_locked:
                flash(
                    "Çok fazla başarısız deneme. Hesabınız 15 dakika boyunca kilitlendi.",
                    "danger"
                )
                _write_auth_audit("ACCOUNT_LOCKED", None)
            else:
                remaining_attempts = max(0, 5 - attempts)
                flash(
                    f"Geçersiz e-posta veya şifre. ({remaining_attempts} deneme hakkı kaldı)",
                    "danger"
                )
            return render_template("auth/login.html")

        login_user(user)
        clear_failures(email)  # başarılı login → sayaç sıfır
        _write_auth_audit("OTURUM AÇMA", user)
        flash("Giriş başarılı.", "success")
        next_url = request.args.get("next") or url_for("app_bp.launcher")
        return redirect(next_url)

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    """Log out user and redirect to login."""
    user = current_user if current_user.is_authenticated else None
    if user:
        _write_auth_audit("OTURUM KAPATMA", user)
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
        password_changed = False
        if new_password:
            # Sprint 22: password complexity policy
            from app.utils.password_policy import validate_password
            ok, errs = validate_password(new_password, username=current_user.email)
            if not ok:
                for e in errs:
                    flash(e, "danger")
                return redirect(url_for("auth_bp.profile"))
            current_user.password_hash = generate_password_hash(new_password)
            password_changed = True
        db.session.commit()
        # Sprint 12.3 — password change audit log
        if password_changed:
            try:
                AuditLogger.log(
                    action="PASSWORD_CHANGED",
                    resource_type="GÜVENLİK",
                    resource_id=current_user.id,
                    description=f"User {current_user.email} kendi şifresini değiştirdi",
                )
            except Exception as e:
                current_app.logger.error(f"[password_audit] {e}")
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

# ── KVKK / GDPR uyumu — Sprint 12 ─────────────────────────────────────────────

@auth_bp.route("/api/user/export-my-data")
@login_required
def kvkk_user_data_export():
    """KVKK Madde 11 (veri taşınabilirliği): kullanıcı kendi verisini JSON olarak alır.

    Not: Sadece kullanıcının doğrudan sahip olduğu veri. Tenant-genelinde paylaşılan
    veriler (process_kpi tanımları vb.) tenant_admin yetkisi gerektirir.
    """
    from flask import jsonify
    import datetime as _dt

    try:
        # Bireysel veriler
        from app.models.process import (
            IndividualPerformanceIndicator, IndividualActivity,
            IndividualKpiData, KpiData,
        )
        from app.models.audit import AuditLog

        ipgs = IndividualPerformanceIndicator.query.filter_by(user_id=current_user.id).all()
        iacts = IndividualActivity.query.filter_by(user_id=current_user.id).all()
        ikpidata = IndividualKpiData.query.filter_by(user_id=current_user.id).all()

        # Kullanıcının girdiği KpiData kayıtları
        user_kpi_data = KpiData.query.filter_by(user_id=current_user.id).limit(1000).all()

        # Audit log (son 100)
        my_audits = (
            AuditLog.query.filter_by(user_id=current_user.id)
            .order_by(AuditLog.created_at.desc())
            .limit(100).all()
        )

        data = {
            "_kvkk_madde": "Veri Taşınabilirliği (Madde 11)",
            "_export_date": _dt.datetime.utcnow().isoformat() + "Z",
            "user": {
                "id": current_user.id,
                "email": current_user.email,
                "first_name": current_user.first_name,
                "last_name": current_user.last_name,
                "phone_number": current_user.phone_number,
                "job_title": current_user.job_title,
                "department": current_user.department,
                "tenant_id": current_user.tenant_id,
                "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
            },
            "individual_performance_indicators": [
                {"id": p.id, "code": p.code, "name": p.name, "target_value": p.target_value, "unit": p.unit, "weight": p.weight}
                for p in ipgs
            ],
            "individual_activities": [
                {"id": a.id, "name": getattr(a, "name", None), "status": getattr(a, "status", None)}
                for a in iacts
            ],
            "individual_kpi_data_count": len(ikpidata),
            "kpi_data_entries_count": len(user_kpi_data),
            "audit_log_recent": [
                {"id": a.id, "action": a.action, "resource_type": a.resource_type, "created_at": a.created_at.isoformat() if a.created_at else None}
                for a in my_audits
            ],
        }

        # Audit log: data exported
        try:
            AuditLogger.log(
                action="KVKK_DATA_EXPORT",
                resource_type="GÜVENLİK",
                resource_id=current_user.id,
                description="Kullanıcı kendi verisini export etti",
            )
        except Exception:
            pass

        return jsonify(data)
    except Exception as e:
        current_app.logger.error(f"[kvkk_export] {e}", exc_info=True)
        return jsonify({"success": False, "message": "Veri export edilemedi."}), 500


@auth_bp.route("/api/user/delete-my-account", methods=["POST"])
@login_required
def kvkk_user_delete():
    """KVKK Madde 7 (silinme hakkı): kullanıcı kendi hesabını anonimleştirir.

    Soft delete + PII anonymization (audit log için id kalıyor ama email/isim hashlenir).
    Aktif tenant admin/sahibi kendini silemez (tenant bütünlüğü).
    """
    from flask import jsonify
    from werkzeug.security import check_password_hash
    import hashlib

    try:
        # Password confirmation
        password = (request.form.get("password") or request.json.get("password", "") if request.is_json else request.form.get("password", "")) or ""
        if not check_password_hash(current_user.password_hash, password):
            return jsonify({"success": False, "message": "Şifre yanlış."}), 401

        # Tenant admin koruması
        if current_user.role and (current_user.role.name or "").lower() in ("admin", "tenant_admin"):
            # Son tenant_admin mı?
            from app.models.core import User, Role
            ta_role = Role.query.filter(Role.name.ilike("tenant_admin")).first()
            if ta_role:
                other_admins = User.query.filter(
                    User.tenant_id == current_user.tenant_id,
                    User.id != current_user.id,
                    User.role_id == ta_role.id,
                    User.is_active == True,
                ).count()
                if other_admins == 0:
                    return jsonify({
                        "success": False,
                        "message": "Son tenant yöneticisi silinemez. Önce başka bir yönetici atayın."
                    }), 403

        # Audit log (silinmeden önce)
        original_email = current_user.email
        try:
            AuditLogger.log(
                action="KVKK_USER_DELETE",
                resource_type="GÜVENLİK",
                resource_id=current_user.id,
                description=f"User self-delete: {original_email}",
            )
        except Exception:
            pass

        # Anonymize (PII clear, id korunur)
        h = hashlib.sha256(str(current_user.id).encode()).hexdigest()[:8]
        current_user.email = f"deleted_{h}@anonim.local"
        current_user.first_name = "Silindi"
        current_user.last_name = "Kullanıcı"
        current_user.phone_number = None
        current_user.job_title = None
        current_user.department = None
        current_user.profile_picture = None
        current_user.password_hash = "!"  # invalidate (login imkansız)
        current_user.is_active = False
        db.session.commit()

        from flask_login import logout_user
        logout_user()
        return jsonify({"success": True, "message": "Hesabınız silindi. Veriler anonimleştirildi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[kvkk_delete] {e}", exc_info=True)
        return jsonify({"success": False, "message": "Silme işlemi başarısız."}), 500

