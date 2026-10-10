"""GUV-25 — demo oturumlarında tehlikeli uçlar kapalı; /demo/end yalnız POST sıfırlar."""
from datetime import datetime, timedelta, timezone

import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.models import db
from app.models.core import Role, Tenant, User
from config import TestingConfig


class _DemoCfg(TestingConfig):
    KOKPITIM_DEMO_MODE = True


@pytest.fixture
def demo_app():
    app = create_app(_DemoCfg)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def uid(demo_app):
    t = Tenant(name="Tomofil", short_name="tomofil", is_active=True)
    r = Role(name="tenant_admin", description="ta")
    db.session.add_all([t, r])
    db.session.flush()
    u = User(email="demo@t.local", first_name="d", last_name="e", tenant_id=t.id, role_id=r.id,
             password_hash=generate_password_hash("x"), is_active=True)
    db.session.add(u)
    db.session.commit()
    return u.id


def _login(client, uid, demo=True, expires_in=3600):
    with client.session_transaction() as s:
        s["_user_id"] = str(uid)
        s["_fresh"] = True
        s["sv"] = 0
        if demo:
            s["demo_session_active"] = True
            s["demo_expires_at"] = (datetime.now(timezone.utc) + timedelta(seconds=expires_in)).isoformat()


def _fresh(client):
    from flask import g
    g.pop("_login_user", None)


@pytest.mark.parametrize("method,path", [
    ("post", "/admin/users/add"),
    ("post", "/settings/email/api/test"),
    ("post", "/settings/email/api/save"),
    ("post", "/k-report/api/webhook/test"),
    ("post", "/k-report/api/anomalies/notify-slack"),
    ("post", "/admin/araclar/yedekleme/indir/db"),
    ("get", "/admin/araclar"),
    ("post", "/profile"),
])
def test_demo_oturumunda_tehlikeli_uclar_kapali(demo_app, uid, method, path):
    c = demo_app.test_client()
    _login(c, uid)
    _fresh(c)
    rv = getattr(c, method)(path, json={})
    assert rv.status_code == 403
    assert rv.get_json()["success"] is False


def test_demo_disi_oturumda_kapatilmaz(demo_app, uid):
    c = demo_app.test_client()
    _login(c, uid, demo=False)
    _fresh(c)
    rv = c.post("/admin/users/add", json={})
    assert rv.status_code != 403 or "demo" not in (rv.get_json() or {}).get("message", "").lower()


def test_demo_oturumunda_okuma_serbest(demo_app, uid):
    c = demo_app.test_client()
    _login(c, uid)
    _fresh(c)
    assert c.get("/admin/users").status_code == 200


def test_sure_dolunca_oturum_dusurulur(demo_app, uid, monkeypatch):
    from app.services import demo_reset_service as drs
    calls = []
    monkeypatch.setattr(drs, "trigger_async_reset", lambda: calls.append(1))
    c = demo_app.test_client()
    _login(c, uid, expires_in=-5)
    _fresh(c)
    rv = c.get("/masaustu", headers={"Accept": "application/json"})
    assert rv.status_code == 401 and rv.get_json()["expired"] is True
    assert calls == [1]
    with c.session_transaction() as s:
        assert "demo_session_active" not in s


def test_demo_end_get_sifirlama_tetiklemez_post_tetikler(demo_app, uid, monkeypatch):
    from app.services import demo_reset_service as drs
    calls = []
    monkeypatch.setattr(drs, "trigger_async_reset", lambda: calls.append(1))
    c = demo_app.test_client()
    _login(c, uid)
    _fresh(c)
    assert c.get("/demo/end").status_code in (301, 302)
    assert calls == []
    with c.session_transaction() as s:
        assert s.get("demo_session_active") is True  # GET oturumu da bitirmez
    _fresh(c)
    rv = c.post("/demo/end")
    assert rv.status_code == 200 and calls == [1]
