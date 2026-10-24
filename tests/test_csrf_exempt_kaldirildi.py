# -*- coding: utf-8 -*-
"""Eski @csrf.exempt uçları artık CSRF ister (Faz 0.5, G4)."""
import re
from pathlib import Path

import pytest

from app import create_app
from app.models import db
from config import TestingConfig

KORUNAN = [
    "/k-plan/strategy/api/ai-config",
    "/admin/araclar/hata-kontrolu/tarama-baslat",
    "/admin/araclar/yedekleme/otomatik-calistir",
]


class CsrfConfig(TestingConfig):
    WTF_CSRF_ENABLED = True


@pytest.fixture
def csrf_app():
    app = create_app(CsrfConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.mark.parametrize("url", KORUNAN)
def test_tokensiz_post_400(csrf_app, url):
    assert csrf_app.test_client().post(url, json={}).status_code == 400


@pytest.mark.parametrize("url", KORUNAN)
def test_tokenli_post_csrf_asamasini_gecer(csrf_app, url):
    client = csrf_app.test_client()
    html = client.get("/login").get_data(as_text=True)
    token = re.search(r'name="csrf-token" content="([^"]+)"', html) or re.search(r'name="csrf_token"[^>]*value="([^"]+)"', html)
    assert token, "login sayfasında CSRF token yok"
    r = client.post(url, json={}, headers={"X-CSRFToken": token.group(1)})
    assert r.status_code != 400  # login yönlendirmesi/403 olabilir; CSRF reddi değil


def test_kaynakta_exempt_kalmadi():
    kok = Path(__file__).resolve().parent.parent
    kalan = [str(p.relative_to(kok)) for d in ("micro", "app")
             for p in (kok / d).rglob("*.py") if re.search(r"^@csrf\.exempt", p.read_text("utf-8", "ignore"), re.M)]
    assert kalan == []


def test_fetch_sarmalayici_base_de_yuklenir():
    kok = Path(__file__).resolve().parent.parent
    base = (kok / "ui/templates/platform/base.html").read_text("utf-8")
    assert "platform/js/csrf_fetch.js" in base
    assert (kok / "ui/static/platform/js/csrf_fetch.js").exists()
