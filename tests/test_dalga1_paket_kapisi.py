# -*- coding: utf-8 -*-
"""Dalga 1 paket B: paket kapısı tüm metod / XHR / API isteklerinde çalışır."""
import pytest
from werkzeug.security import generate_password_hash

from app.models import db
from app.models.core import User, Tenant, Role


def _login(client, role_name, pkg=False):
    role = Role(name=role_name)
    t = Tenant(name="T", short_name="t", is_active=True)
    if pkg:
        from app.models.saas import SubscriptionPackage
        p = SubscriptionPackage(name="P", code="p")
        db.session.add(p)
        db.session.commit()
        t.package_id = p.id
    db.session.add_all([role, t])
    db.session.commit()
    u = User(email=f"{role_name}@x.com", first_name="a", last_name="b",
             tenant_id=t.id, role_id=role.id, is_active=True,
             password_hash=generate_password_hash("Abcd1234!"))
    db.session.add(u)
    db.session.commit()
    with client.session_transaction() as s:
        s["_user_id"] = str(u.id)
        s["_fresh"] = True


@pytest.fixture
def allowed(monkeypatch):
    box = {"ids": set()}
    import app_platform.core.module_registry as mr
    monkeypatch.setattr(mr, "get_accessible_modules",
                        lambda user: [{"id": i} for i in box["ids"]])
    return box


def test_post_denied_when_module_missing(client, allowed):
    _login(client, "kurum_kullanici", pkg=True)
    r = client.post("/k-plan/individual/api/pi/add", json={})
    assert r.status_code == 403
    assert r.get_json()["success"] is False


def test_xhr_get_denied(client, allowed):
    _login(client, "kurum_kullanici", pkg=True)
    r = client.get("/k-plan/individual/scorecard",
                   headers={"X-Requested-With": "XMLHttpRequest"})
    assert r.status_code == 403


def test_api_prefix_denied(client, allowed):
    _login(client, "kurum_kullanici", pkg=True)
    assert client.post("/api/projeler", json={}).status_code == 403
    assert client.get("/api/surec/1/karne/performans").status_code == 403
    assert client.get("/api/v1/processes").status_code == 403


def test_module_in_package_not_gated(client, allowed):
    allowed["ids"] = {"bireysel"}
    _login(client, "kurum_kullanici", pkg=True)
    r = client.post("/k-plan/individual/api/pi/add", json={})
    assert r.status_code != 403 or "paketinizde" not in (r.get_data(as_text=True))


def test_admin_exempt(client, allowed):
    _login(client, "Admin")
    r = client.post("/k-plan/individual/api/pi/add", json={})
    assert "paketinizde" not in r.get_data(as_text=True)


def test_auth_health_open(client, allowed):
    _login(client, "kurum_kullanici", pkg=True)
    assert client.get("/health").status_code != 403
    assert client.get("/login").status_code != 403
