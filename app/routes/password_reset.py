"""Password reset ("Şifremi unuttum") flow.

Token: itsdangerous URLSafeTimedSerializer (SECRET_KEY + salt, 1 hour).
Single use: token embeds a fingerprint of the current password hash, so
it becomes invalid as soon as the password changes.
"""
import hashlib

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_babel import gettext as _
from itsdangerous import BadData, URLSafeTimedSerializer
from werkzeug.security import generate_password_hash

from app.models import db
from app.models.core import User
from app.utils.password_policy import validate_password
from extensions import limiter

password_reset_bp = Blueprint("password_reset_bp", __name__, url_prefix="")

_SALT = "kokpitim-password-reset"
TOKEN_MAX_AGE = 3600


def _serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt=_SALT)


def _fingerprint(user):
    return hashlib.sha256((user.password_hash or "").encode("utf-8")).hexdigest()[:16]


def generate_reset_token(user):
    return _serializer().dumps({"uid": user.id, "fp": _fingerprint(user)})


def load_user_from_token(token, max_age=None):
    """Return the active user for a valid, unused token, else None."""
    if max_age is None:
        max_age = TOKEN_MAX_AGE
    try:
        data = _serializer().loads(token, max_age=max_age)
        user = db.session.get(User, int(data["uid"]))
    except (BadData, KeyError, TypeError, ValueError):
        return None
    if not user or not user.is_active or data.get("fp") != _fingerprint(user):
        return None
    return user


def _send_reset_email(user):
    from micro.services.email_service import send_notification_email

    link = url_for("password_reset_bp.reset_password", token=generate_reset_token(user), _external=True)
    html = render_template("auth/reset_email.html", reset_link=link, user=user)
    ok, err = send_notification_email(
        user.email, _("Kokpitim şifre sıfırlama"), html,
        tenant_id=getattr(user, "tenant_id", None),
    )
    if not ok:
        current_app.logger.error("Password reset email failed: %s", err)


@password_reset_bp.route("/forgot-password", methods=["GET", "POST"])
@limiter.limit("5 per hour; 20 per day", methods=["POST"])
def forgot_password():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        if email:
            try:
                user = User.query.filter_by(email=email, is_active=True).first()
                if user:
                    _send_reset_email(user)
            except Exception as e:
                current_app.logger.error("Password reset request failed: %s", e)
        flash(_("Bu e-posta adresi kayıtlıysa şifre sıfırlama bağlantısı gönderildi."), "info")
        return redirect(url_for("password_reset_bp.forgot_password"))
    return render_template("auth/forgot_password.html")


@password_reset_bp.route("/reset-password/<token>", methods=["GET", "POST"])
@limiter.limit("10 per hour", methods=["POST"])
def reset_password(token):
    user = load_user_from_token(token)
    if user is None:
        flash(_("Şifre sıfırlama bağlantısı geçersiz veya süresi dolmuş."), "danger")
        return redirect(url_for("password_reset_bp.forgot_password"))
    if request.method == "POST":
        pwd = request.form.get("password") or ""
        if pwd != (request.form.get("password_confirm") or ""):
            flash(_("Şifreler eşleşmiyor."), "danger")
        else:
            ok, errors = validate_password(pwd, user.email)
            if not ok:
                flash(", ".join(errors), "danger")
            else:
                try:
                    user.password_hash = generate_password_hash(pwd)
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    current_app.logger.error("Password reset commit failed: %s", e)
                    flash(_("Bir hata oluştu. Lütfen tekrar deneyin."), "danger")
                    return render_template("auth/reset_password.html", token=token)
                flash(_("Şifreniz güncellendi. Giriş yapabilirsiniz."), "success")
                return redirect(url_for("public_login"))
    return render_template("auth/reset_password.html", token=token)
