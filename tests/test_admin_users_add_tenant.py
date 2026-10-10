"""GUV-01 — /admin/users/add başka kuruma kullanıcı açtırmamalı."""
import pytest
from werkzeug.security import generate_password_hash

from app.models import db
from app.models.core import Role, Tenant, User


def _login(client, user_id: int):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


def _mk_user(email, tenant_id, role_id):
    u = User(
        email=email, first_name="T", last_name="U", tenant_id=tenant_id,
        role_id=role_id, password_hash=generate_password_hash("x"), is_active=True,
    )
    db.session.add(u)
    db.session.flush()
    return u


@pytest.fixture
def ctx(app):
    t1 = Tenant(name="T1", short_name="t1", is_active=True)
    t2 = Tenant(name="T2", short_name="t2", is_active=True)
    db.session.add_all([t1, t2])
    r_admin = Role(name="Admin", description="a")
    r_ta = Role(name="tenant_admin", description="ta")
    r_std = Role(name="standard_user", description="s")
    db.session.add_all([r_admin, r_ta, r_std])
    db.session.flush()
    admin = _mk_user("admin@t.local", t1.id, r_admin.id)
    ta = _mk_user("ta@t.local", t1.id, r_ta.id)
    db.session.commit()
    return {
        "t1": t1.id, "t2": t2.id, "std": r_std.id,
        "admin": admin.id, "ta": ta.id,
    }


def _post(client, c, email, tenant_id, role_id=None):
    body = {"email": email, "password": "Abcdef1!x", "tenant_id": tenant_id}
    if role_id is not None:
        body["role_id"] = role_id
    return client.post("/admin/users/add", json=body)


def test_tenant_admin_cannot_target_other_tenant(client, app, ctx):
    _login(client, ctx["ta"])
    rv = _post(client, ctx, "victim@t.local", ctx["t2"], ctx["std"])
    assert rv.status_code in (200, 403)
    u = User.query.filter_by(email="victim@t.local").first()
    # Ya reddedilir ya da kendi kurumuna açılır; başka kuruma ASLA.
    assert u is None or u.tenant_id == ctx["t1"]


def test_tenant_admin_without_tenant_id_uses_own(client, app, ctx):
    _login(client, ctx["ta"])
    rv = client.post("/admin/users/add", json={
        "email": "own@t.local", "password": "Abcdef1!x", "role_id": ctx["std"],
    })
    assert rv.status_code == 200
    assert User.query.filter_by(email="own@t.local").one().tenant_id == ctx["t1"]


def test_platform_admin_can_target_other_tenant(client, app, ctx):
    _login(client, ctx["admin"])
    rv = _post(client, ctx, "ok@t.local", ctx["t2"], ctx["std"])
    assert rv.status_code == 200
    assert User.query.filter_by(email="ok@t.local").one().tenant_id == ctx["t2"]


def test_platform_admin_unknown_tenant_rejected(client, app, ctx):
    _login(client, ctx["admin"])
    rv = _post(client, ctx, "ghost@t.local", 999999, ctx["std"])
    assert rv.status_code == 400
    assert User.query.filter_by(email="ghost@t.local").first() is None


def test_unknown_role_id_rejected(client, app, ctx):
    _login(client, ctx["ta"])
    rv = _post(client, ctx, "norole@t.local", ctx["t1"], 999999)
    assert rv.status_code == 400
    assert User.query.filter_by(email="norole@t.local").first() is None
