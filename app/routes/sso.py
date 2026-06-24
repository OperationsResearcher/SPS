"""SSO entegrasyonu (Sprint 25).

Authlib kütüphanesi ile Google OAuth 2.0 + OIDC akışı.

Konfigürasyon (.env):
    GOOGLE_CLIENT_ID=...
    GOOGLE_CLIENT_SECRET=...
    GOOGLE_OAUTH_ENABLED=true
    SSO_AUTO_PROVISION=true   # mevcut olmayan kullanıcıyı oto oluştur

Akış:
    1. /sso/google → Google OAuth redirect
    2. /sso/google/callback → token al, profile çek, kullanıcıyı login et
    3. Mevcut user varsa login_user, yoksa SSO_AUTO_PROVISION=true ise yarat

Güvenlik notları:
- State parameter ile CSRF koruma
- Email verified=True kontrolü zorunlu
- Yeni provisioned user'lar standard_user role'üne atanır
"""
from __future__ import annotations

from flask import Blueprint, redirect, url_for, session, request, flash, current_app
from flask_login import login_user

from extensions import db
from app.models.core import User, Role, Tenant
from flask_babel import gettext as _

sso_bp = Blueprint("sso_bp", __name__, url_prefix="/sso")


def _oauth_client():
    """Lazy authlib client init."""
    try:
        from authlib.integrations.flask_client import OAuth
    except ImportError:
        return None

    # Bir tane OAuth instance app'e attach edilir
    app = current_app._get_current_object()
    oauth = getattr(app, "_oauth", None)
    if oauth is None:
        oauth = OAuth(app)
        app._oauth = oauth
        # Google provider
        if app.config.get("GOOGLE_OAUTH_ENABLED"):
            oauth.register(
                name="google",
                client_id=app.config.get("GOOGLE_CLIENT_ID"),
                client_secret=app.config.get("GOOGLE_CLIENT_SECRET"),
                server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
                client_kwargs={"scope": "openid email profile"},
            )
    return oauth


@sso_bp.route("/google")
def sso_google():
    """Google OAuth akışını başlat."""
    if not current_app.config.get("GOOGLE_OAUTH_ENABLED"):
        flash(_("Google SSO bu ortamda devre dışı."), "warning")
        return redirect(url_for("auth_bp.login"))

    oauth = _oauth_client()
    if oauth is None or not hasattr(oauth, "google"):
        flash(_("Google SSO yapılandırılmamış."), "danger")
        return redirect(url_for("auth_bp.login"))

    redirect_uri = url_for("sso_bp.sso_google_callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@sso_bp.route("/google/callback")
def sso_google_callback():
    """Google OAuth callback — token al, kullanıcıyı login et."""
    if not current_app.config.get("GOOGLE_OAUTH_ENABLED"):
        return redirect(url_for("auth_bp.login"))

    oauth = _oauth_client()
    try:
        token = oauth.google.authorize_access_token()
    except Exception as e:
        current_app.logger.error(f"[sso_google] token alımı: {e}")
        flash(_("Google girişi başarısız."), "danger")
        return redirect(url_for("auth_bp.login"))

    user_info = token.get("userinfo") or oauth.google.parse_id_token(token, None)
    if not user_info:
        flash(_("Google profil alınamadı."), "danger")
        return redirect(url_for("auth_bp.login"))

    email = (user_info.get("email") or "").strip().lower()
    email_verified = user_info.get("email_verified", False)

    if not email:
        flash(_("E-posta alınamadı."), "danger")
        return redirect(url_for("auth_bp.login"))

    if not email_verified:
        current_app.logger.warning(f"[sso_google] verified=False email={email}")
        flash(_("E-posta doğrulanmamış — Google hesabınızı doğrulayın."), "danger")
        return redirect(url_for("auth_bp.login"))

    # Kullanıcıyı bul
    user = User.query.filter_by(email=email, is_active=True).first()

    if not user:
        if not current_app.config.get("SSO_AUTO_PROVISION", False):
            flash(f"Bu hesap ({email}) Kokpitim'de tanımlı değil. Yöneticinizden erişim talep edin.", "warning")
            return redirect(url_for("auth_bp.login"))

        # Auto-provision (default tenant'a ata — config ile değiştirilebilir)
        default_tenant_id = current_app.config.get("SSO_DEFAULT_TENANT_ID", 1)
        std_role = Role.query.filter_by(name="standard_user").first()
        user = User(
            email=email,
            password_hash="!",  # SSO-only, password login imkansız
            first_name=user_info.get("given_name") or "",
            last_name=user_info.get("family_name") or "",
            is_active=True,
            tenant_id=default_tenant_id,
            role_id=std_role.id if std_role else None,
        )
        db.session.add(user)
        db.session.commit()
        current_app.logger.info(f"[sso_google] auto-provisioned: {email}")

    login_user(user)

    # Audit log
    try:
        from app.utils.audit_logger import AuditLogger
        AuditLogger.log(
            action="SSO_GOOGLE_LOGIN",
            resource_type="GÜVENLİK",
            resource_id=user.id,
            description=f"User {email} Google SSO ile giriş yaptı",
        )
    except Exception:
        pass

    flash(_("Google ile giriş başarılı."), "success")
    return redirect(url_for("app_bp.launcher"))
