# -*- coding: utf-8 -*-
"""SSO güvenliği (Faz 0.3, G2): TOTP kapısı + auto-provision alan adı izin listesi."""
from types import SimpleNamespace

import pytest
from werkzeug.security import generate_password_hash

from app.models import db
from app.models.core import Role, Tenant, User
from app.routes.sso import email_domain_allowed
from config import TestingConfig


class SsoConfig(TestingConfig):
    GOOGLE_OAUTH_ENABLED = True
    SSO_AUTO_PROVISION = True
    SSO_ALLOWED_DOMAINS = "izinli.com"


@pytest.fixture
def sso_app(monkeypatch):
    from app import create_app

    app = create_app(SsoConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def _fake_google(monkeypatch, email):
    google = SimpleNamespace(
        authorize_access_token=lambda: {"userinfo": {"email": email, "email_verified": True}},
    )
    monkeypatch.setattr("app.routes.sso._oauth_client", lambda: SimpleNamespace(google=google))


def _user(email, totp=False):
    tenant = Tenant(name="T", short_name="t", is_active=True)
    role = Role(name="standard_user")
    db.session.add_all([tenant, role])
    db.session.flush()
    u = User(email=email, password_hash=generate_password_hash("x"), tenant_id=tenant.id,
             role_id=role.id, is_active=True)
    if totp:
        u.totp_enabled = True
        u.totp_secret = "JBSWY3DPEHPK3PXP"
    db.session.add(u)
    db.session.commit()
    return u


def test_domain_allowlist_helper():
    assert email_domain_allowed("a@izinli.com", {"izinli.com"})
    assert not email_domain_allowed("a@kotu.com", {"izinli.com"})
    assert not email_domain_allowed("a@izinli.com", set())  # boş liste = kapalı
    assert not email_domain_allowed("yok", {"izinli.com"})


def test_sso_totp_user_goes_to_challenge(sso_app, monkeypatch):
    u = _user("t@izinli.com", totp=True)
    _fake_google(monkeypatch, "t@izinli.com")
    client = sso_app.test_client()
    r = client.get("/sso/google/callback")
    assert r.status_code == 302 and "/challenge" in r.headers["Location"]
    with client.session_transaction() as sess:
        assert sess.get("_pending_2fa_user_id") == u.id
        assert "_user_id" not in sess  # oturum AÇILMADI


def test_sso_without_totp_logs_in(sso_app, monkeypatch):
    _user("n@izinli.com", totp=False)
    _fake_google(monkeypatch, "n@izinli.com")
    client = sso_app.test_client()
    r = client.get("/sso/google/callback")
    assert r.status_code == 302
    with client.session_transaction() as sess:
        assert "_user_id" in sess


def test_auto_provision_blocked_for_other_domain(sso_app, monkeypatch):
    _fake_google(monkeypatch, "yeni@kotu.com")
    client = sso_app.test_client()
    r = client.get("/sso/google/callback")
    assert r.status_code == 302
    assert User.query.filter_by(email="yeni@kotu.com").first() is None


def test_auto_provision_allowed_for_listed_domain(sso_app, monkeypatch):
    _user("var@izinli.com")  # tenant 1 + standard_user rolü hazır olsun
    _fake_google(monkeypatch, "yeni@izinli.com")
    client = sso_app.test_client()
    client.get("/sso/google/callback")
    assert User.query.filter_by(email="yeni@izinli.com").first() is not None
