# -*- coding: utf-8 -*-
"""Demo modu: host adına bağlı + /demo/start yalnız CSRF'li POST (Faz 0.7, G12)."""
import pytest

from app import create_app
from app.models import db
from config import TestingConfig


class DemoConfig(TestingConfig):
    KOKPITIM_DEMO_MODE = True
    DEMO_ALLOWED_HOSTS = "demo.kokpitim.com"
    WTF_CSRF_ENABLED = True


@pytest.fixture
def demo_app():
    app = create_app(DemoConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def test_demo_izinli_host_acik(demo_app):
    r = demo_app.test_client().get("/demo/", base_url="https://demo.kokpitim.com")
    assert r.status_code == 200


@pytest.mark.parametrize("host", ["www.kokpitim.com", "test.kokpitim.com", "localhost"])
def test_demo_baska_host_404(demo_app, host):
    c = demo_app.test_client()
    assert c.get("/demo/", base_url=f"https://{host}").status_code == 404
    assert c.post("/demo/start/tom1", base_url=f"https://{host}").status_code in (400, 404)


def test_demo_start_get_kapali(demo_app):
    r = demo_app.test_client().get("/demo/start/tom1", base_url="https://demo.kokpitim.com")
    assert r.status_code == 405


def test_demo_start_tokensiz_post_400(demo_app):
    r = demo_app.test_client().post("/demo/start/tom1", base_url="https://demo.kokpitim.com")
    assert r.status_code == 400


def test_demo_landing_form_ve_token(demo_app):
    html = demo_app.test_client().get("/demo/", base_url="https://demo.kokpitim.com").get_data(as_text=True)
    assert 'method="post"' in html and 'name="csrf_token"' in html
    assert 'href="/demo/start' not in html
