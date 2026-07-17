"""Dalga D — oturum açmış kullanıcı platform akışı (login → launcher → modüller)."""
import pytest
from werkzeug.security import generate_password_hash

from app.models import db
from app.models.core import Role, Tenant, User
from app.models.process import Process


def _login(client, user_id: int):
  with client.session_transaction() as sess:
    sess["_user_id"] = str(user_id)
    sess["_fresh"] = True


def _seed_user():
  tenant = Tenant(name="Flow Tenant", short_name="ft", is_active=True)
  db.session.add(tenant)
  db.session.flush()
  role = Role(name="kurum_kullanici", description="User")
  db.session.add(role)
  db.session.flush()
  user = User(
    email="flow@local.test",
    first_name="Flow",
    last_name="User",
    tenant_id=tenant.id,
    role_id=role.id,
    password_hash=generate_password_hash("TestPassword123"),
    is_active=True,
  )
  db.session.add(user)
  db.session.flush()
  proc = Process(name="Test Process", tenant_id=tenant.id, is_active=True)
  db.session.add(proc)
  db.session.commit()
  return user


@pytest.mark.parametrize(
  "path",
  [
    "/launcher",
    "/desktop",
    "/surec",
    "/project",
    "/k-plan/strategy",
    "/k-plan/individual",
  ],
)
def test_platform_pages_authenticated(client, app, path):
  with app.app_context():
    user = _seed_user()
    uid = user.id
  _login(client, uid)
  rv = client.get(path, follow_redirects=False)
  assert rv.status_code in (200, 302, 307)
  if rv.status_code == 302:
    assert rv.location


def test_login_redirects_to_launcher_or_masaustu(client, app):
  with app.app_context():
    user = _seed_user()
    email = user.email
  rv = client.post(
    "/login",
    data={"email": email, "password": "TestPassword123"},
    follow_redirects=False,
  )
  assert rv.status_code in (302, 303)
