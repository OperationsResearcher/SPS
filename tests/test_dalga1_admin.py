# -*- coding: utf-8 -*-
"""Dalga 1 paket A — C-005, F-001, F-005/F-015, F-006, F-008 regresyon testleri."""
import io
import os

import pytest
from werkzeug.security import generate_password_hash

from app.models import db
from app.models.core import Role, Tenant, User


def _login(client, user_id):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


@pytest.fixture
def ctx(app):
    t1 = Tenant(name="T1", short_name="t1", is_active=True)
    t2 = Tenant(name="T2", short_name="t2", is_active=True)
    db.session.add_all([t1, t2])
    roles = {}
    for n in ("Admin", "tenant_admin", "executive_manager", "standard_user"):
        r = Role(name=n, description=n)
        db.session.add(r)
        roles[n] = r
    db.session.flush()

    def mk(email, role, tenant=t1):
        u = User(email=email, first_name="A", last_name="B", tenant_id=tenant.id,
                 role_id=roles[role].id, password_hash=generate_password_hash("x"),
                 is_active=True)
        db.session.add(u)
        db.session.flush()
        return u

    c = {
        "admin": mk("adm@t.l", "Admin"),
        "ta": mk("ta@t.l", "tenant_admin"),
        "ta2": mk("ta2@t.l", "tenant_admin"),
        "em": mk("em@t.l", "executive_manager"),
        "em2": mk("em2@t.l", "executive_manager"),
        "std": mk("std@t.l", "standard_user"),
        "t1": t1.id,
    }
    db.session.commit()
    return {k: (v.id if isinstance(v, User) else v) for k, v in c.items()}


# ── C-005 ────────────────────────────────────────────────────────────────────

def test_logo_update_requires_role(client, ctx):
    _login(client, ctx["std"])
    rv = client.post("/api/kurum/update-logo", json={"logo_url": "https://x.com/a.png"})
    assert rv.status_code == 403


@pytest.mark.parametrize("bad", ["static/../.env", "/static/../.env", "javascript:alert(1)",
                                 "/static/uploads/logos/../../x"])
def test_logo_update_rejects_bad_url(client, ctx, bad):
    _login(client, ctx["ta"])
    rv = client.post("/api/kurum/update-logo", json={"logo_url": bad})
    assert rv.status_code == 400


def test_logo_upload_requires_role(client, ctx):
    _login(client, ctx["std"])
    rv = client.post("/api/kurum/upload-logo",
                     data={"file": (io.BytesIO(b"x"), "a.png")},
                     content_type="multipart/form-data")
    assert rv.status_code == 403


def test_safe_remove_old_logo_blocks_traversal(app, tmp_path, monkeypatch):
    from api import routes_admin as ra
    monkeypatch.chdir(tmp_path)
    (tmp_path / "static" / "uploads" / "logos").mkdir(parents=True)
    victim = tmp_path / ".env"
    victim.write_text("secret")
    ok = tmp_path / "static" / "uploads" / "logos" / "a.png"
    ok.write_text("x")
    ra._safe_remove_old_logo("static/../.env")
    assert victim.exists()
    ra._safe_remove_old_logo("/static/uploads/logos/a.png")
    assert not ok.exists()


# ── F-001 ────────────────────────────────────────────────────────────────────

def test_tenant_edit_commercial_fields_ignored_for_non_admin(client, ctx):
    _login(client, ctx["ta"])
    rv = client.post(f"/admin/tenants/edit/{ctx['t1']}",
                     json={"name": "Yeni", "max_user_count": 999,
                           "license_end_date": "2099-01-01", "package_id": 1})
    assert rv.status_code == 200
    t = db.session.get(Tenant, ctx["t1"])
    assert t.name == "Yeni"
    assert t.max_user_count != 999
    assert t.package_id != 1 or t.package_id is None
    assert t.license_end_date is None or str(t.license_end_date) != "2099-01-01"


def test_tenant_edit_commercial_fields_applied_for_admin(client, ctx):
    _login(client, ctx["admin"])
    rv = client.post(f"/admin/tenants/edit/{ctx['t1']}",
                     json={"max_user_count": 77, "license_end_date": "2099-01-01"})
    assert rv.status_code == 200
    t = db.session.get(Tenant, ctx["t1"])
    assert t.max_user_count == 77
    assert str(t.license_end_date) == "2099-01-01"


# ── F-005 / F-015 ────────────────────────────────────────────────────────────

def test_equal_role_cannot_edit_or_reset_2fa(client, ctx):
    _login(client, ctx["em"])
    rv = client.post(f"/admin/users/edit/{ctx['em2']}", json={"password": "Hack1234!"})
    assert rv.status_code == 403
    rv = client.post(f"/admin/users/{ctx['em2']}/2fa-reset")
    assert rv.status_code == 403
    rv = client.post(f"/admin/users/toggle/{ctx['em2']}")
    assert rv.status_code == 403


def test_tenant_admin_cannot_touch_admin_or_peer(client, ctx):
    _login(client, ctx["ta"])
    for target in (ctx["admin"], ctx["ta2"]):
        assert client.post(f"/admin/users/edit/{target}", json={"password": "Hack1234!"}).status_code == 403
        assert client.post(f"/admin/users/{target}/2fa-reset").status_code == 403


def test_tenant_admin_can_edit_lower_and_self(client, ctx):
    _login(client, ctx["ta"])
    assert client.post(f"/admin/users/edit/{ctx['std']}", json={"first_name": "Z"}).status_code == 200
    assert client.post(f"/admin/users/edit/{ctx['em']}", json={"first_name": "Z"}).status_code == 200
    _login(client, ctx["em"])
    assert client.post(f"/admin/users/edit/{ctx['em']}", json={"first_name": "Q"}).status_code == 200


def test_admin_can_edit_admin(client, ctx):
    _login(client, ctx["admin"])
    assert client.post(f"/admin/users/edit/{ctx['ta']}", json={"first_name": "Z"}).status_code == 200


# ── F-006 ────────────────────────────────────────────────────────────────────

def test_db_restore_locked_in_production(client, ctx, monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "production")
    _login(client, ctx["admin"])
    rv = client.post("/admin/araclar/yedekleme/geri-yukle/db", data={})
    assert rv.status_code == 403
    assert "kilitli" in rv.get_json()["error"]


def test_db_restore_not_locked_locally(client, ctx, monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "development")
    _login(client, ctx["admin"])
    rv = client.post("/admin/araclar/yedekleme/geri-yukle/db", data={})
    assert rv.status_code == 400  # onay metni hatali: kilide takilmadi


# ── F-008 ────────────────────────────────────────────────────────────────────

def test_executive_manager_cannot_manage_sub_tenants(client, ctx):
    _login(client, ctx["em"])
    rv = client.post("/admin/api/sub-tenants", json={"name": "X", "admin_email": "x@y.zz"})
    assert rv.status_code == 403
    rv = client.post("/admin/api/sub-tenants/1/admin/reset-password")
    assert rv.status_code == 403
