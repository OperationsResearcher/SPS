"""2FA TOTP route'ları (Sprint 26).

Setup flow + verify flow + disable.
"""
from __future__ import annotations

import json

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session, current_app
from flask_login import login_required, current_user, login_user

from extensions import db
from app.models.core import User
from app.services.totp_service import (
    generate_totp_secret, get_qr_code_base64,
    verify_totp_code, generate_backup_codes, consume_backup_code,
)

totp_bp = Blueprint("totp_bp", __name__, url_prefix="/2fa")


@totp_bp.route("/setup", methods=["GET"])
@login_required
def totp_setup():
    """Setup başlat — secret üret + QR göster."""
    if current_user.totp_enabled:
        flash("2FA zaten etkin. Önce devre dışı bırakın.", "info")
        return redirect(url_for("auth_bp.settings"))

    # Geçici secret session'da tut (kullanıcı doğrulayana kadar DB'ye yazma)
    secret = generate_totp_secret()
    session["_pending_totp_secret"] = secret

    qr = get_qr_code_base64(secret, current_user.email)
    return render_template("auth/totp_setup.html", secret=secret, qr_code=qr)


@totp_bp.route("/verify-setup", methods=["POST"])
@login_required
def totp_verify_setup():
    """Setup doğrulama — kullanıcı authenticator'dan gelen kodu girer."""
    secret = session.get("_pending_totp_secret")
    if not secret:
        return jsonify({"success": False, "message": "Setup oturumu bulunamadı."}), 400

    code = (request.form.get("code") or "").strip()
    if not verify_totp_code(secret, code):
        return jsonify({"success": False, "message": "Doğrulama kodu hatalı."}), 400

    # Backup codes üret + DB'ye yaz
    backup = generate_backup_codes(10)
    current_user.totp_secret = secret
    current_user.totp_enabled = True
    current_user.totp_backup_codes_json = json.dumps(backup)
    db.session.commit()
    session.pop("_pending_totp_secret", None)

    # Audit
    try:
        from app.utils.audit_logger import AuditLogger
        AuditLogger.log(
            action="2FA_ENABLED", resource_type="GÜVENLİK",
            resource_id=current_user.id,
            description=f"User {current_user.email} 2FA etkinleştirdi",
        )
    except Exception:
        pass

    return jsonify({
        "success": True,
        "message": "2FA etkinleştirildi. Backup kodlarınızı güvenli bir yere kaydedin.",
        "backup_codes": backup,
    })


@totp_bp.route("/disable", methods=["POST"])
@login_required
def totp_disable():
    """2FA devre dışı bırak — şifre confirm zorunlu."""
    from werkzeug.security import check_password_hash
    password = request.form.get("password") or ""
    if not check_password_hash(current_user.password_hash, password):
        return jsonify({"success": False, "message": "Şifre hatalı."}), 401

    current_user.totp_secret = None
    current_user.totp_enabled = False
    current_user.totp_backup_codes_json = None
    db.session.commit()

    try:
        from app.utils.audit_logger import AuditLogger
        AuditLogger.log(
            action="2FA_DISABLED", resource_type="GÜVENLİK",
            resource_id=current_user.id,
            description=f"User {current_user.email} 2FA devre dışı bıraktı",
        )
    except Exception:
        pass

    return jsonify({"success": True, "message": "2FA devre dışı bırakıldı."})


# Login flow için ek endpoint — auth_bp.login içinden çağrılır
@totp_bp.route("/challenge", methods=["GET", "POST"])
def totp_challenge():
    """Login sırasında 2FA enabled kullanıcı için ek doğrulama."""
    pending_user_id = session.get("_pending_2fa_user_id")
    if not pending_user_id:
        return redirect(url_for("auth_bp.login"))

    user = User.query.get(pending_user_id)
    if not user or not user.totp_enabled:
        session.pop("_pending_2fa_user_id", None)
        return redirect(url_for("auth_bp.login"))

    if request.method == "POST":
        code = (request.form.get("code") or "").strip()
        is_backup = (request.form.get("is_backup") or "").lower() in ("1", "true", "on")

        ok = False
        if is_backup:
            ok = consume_backup_code(user, code)
            if ok:
                db.session.commit()
        else:
            ok = verify_totp_code(user.totp_secret, code)

        if not ok:
            flash("Doğrulama kodu hatalı.", "danger")
            return render_template("auth/totp_challenge.html")

        # Login complete
        session.pop("_pending_2fa_user_id", None)
        login_user(user)
        try:
            from app.utils.audit_logger import AuditLogger
            AuditLogger.log(
                action="2FA_LOGIN_SUCCESS", resource_type="GÜVENLİK",
                resource_id=user.id, description=f"User {user.email} 2FA doğrulamayla giriş",
            )
        except Exception:
            pass
        return redirect(url_for("app_bp.launcher"))

    return render_template("auth/totp_challenge.html")
