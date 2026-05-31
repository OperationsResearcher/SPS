"""Dalga D — tenant izolasyonu (süreç KPI listesi API)."""
from werkzeug.security import generate_password_hash

from app.models import db
from app.models.core import Role, Tenant, User
from app.models.process import Process, process_leaders


def _login(client, user_id: int):
  with client.session_transaction() as sess:
    sess["_user_id"] = str(user_id)
    sess["_fresh"] = True


def test_process_api_denies_other_tenant(client, app):
  with app.app_context():
    t1 = Tenant(name="T1", short_name="t1", is_active=True)
    t2 = Tenant(name="T2", short_name="t2", is_active=True)
    db.session.add_all([t1, t2])
    db.session.flush()
    role = Role(name="kurum_kullanici", description="u")
    db.session.add(role)
    db.session.flush()
    p1 = Process(name="P1", tenant_id=t1.id, is_active=True)
    p2 = Process(name="P2", tenant_id=t2.id, is_active=True)
    db.session.add_all([p1, p2])
    db.session.flush()
    u1 = User(
      email="u1@t.local",
      first_name="T",
      last_name="U",
      tenant_id=t1.id,
      role_id=role.id,
      password_hash=generate_password_hash("x"),
      is_active=True,
    )
    db.session.add(u1)
    db.session.flush()
    db.session.execute(
      process_leaders.insert().values(process_id=p1.id, user_id=u1.id)
    )
    db.session.commit()
    uid = u1.id
    pid_own = p1.id
    pid_other = p2.id

  _login(client, uid)
  headers = {"Accept": "application/json"}

  rv_own = client.get(f"/process/api/kpi/list/{pid_own}", headers=headers)
  assert rv_own.status_code == 200
  assert rv_own.get_json().get("success") is True

  rv_other = client.get(f"/process/api/kpi/list/{pid_other}", headers=headers)
  assert rv_other.status_code == 403
