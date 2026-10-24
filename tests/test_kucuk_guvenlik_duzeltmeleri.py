# -*- coding: utf-8 -*-
"""Faz 0.8 küçük güvenlik düzeltmeleri (G7, G14-G16)."""
from pathlib import Path

import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.models import db
from app.models.core import Role, Tenant, User
from config import TestingConfig

KOK = Path(__file__).resolve().parent.parent


@pytest.fixture
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def _set_lang(client, referrer):
    return client.get("/set-language/en", headers={"Referer": referrer}) if referrer else client.get("/set-language/en")


def _lang_url(app):
    for r in app.url_map.iter_rules():
        if "language" in r.rule or "lang" in r.endpoint:
            return r.rule
    return None


def test_open_redirect_dis_referrer_kok_e_doner(app):
    url = _lang_url(app)
    assert url, "dil değiştirme route'u bulunamadı"
    url = url.replace("<lang>", "en").replace("<string:lang>", "en").replace("<code>", "en")
    c = app.test_client()
    r = c.get(url, headers={"Referer": "https://evil.example/x"})
    assert r.status_code == 302 and "evil.example" not in r.headers["Location"]
    r = c.get(url, headers={"Referer": "http://localhost/sayfa"})
    assert r.headers["Location"].endswith("/sayfa")


def test_swagger_ui_yalniz_admin(app):
    c = app.test_client()
    assert c.get("/api/docs/").status_code == 403  # anonim


def test_ham_x_real_ip_okunmuyor():
    for f in ("app/routes/auth.py", "app/routes/totp.py"):
        assert 'headers.get("X-Real-IP")' not in (KOK / f).read_text("utf-8")


def test_yedek_hata_mesaji_ayrinti_sizdirmiyor():
    src = (KOK / "micro/modules/admin/routes_admin_tools.py").read_text("utf-8")
    assert 'alınamadı: {e}' not in src


def test_app_debug_acik_bayraga_bagli():
    src = (KOK / "app.py").read_text("utf-8")
    assert "debug=True" not in src and "KOKPITIM_ENV" in src
