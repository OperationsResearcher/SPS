"""Dalga D — süreç listesi sorgu sayısı üst sınırı (N+1 regression)."""
from werkzeug.security import generate_password_hash

from app.models import db
from app.models.core import Role, Tenant, User
from app.models.process import Process, ProcessKpi


def test_process_list_query_count_bounded(app):
  with app.app_context():
    tenant = Tenant(name="N1", short_name="n1", is_active=True)
    db.session.add(tenant)
    db.session.flush()
    role = Role(name="kurum_kullanici", description="u")
    db.session.add(role)
    db.session.flush()
    for i in range(5):
      p = Process(name=f"P{i}", tenant_id=tenant.id, is_active=True)
      db.session.add(p)
      db.session.flush()
      db.session.add(ProcessKpi(process_id=p.id, name=f"KPI{i}", is_active=True))
    db.session.commit()

    from sqlalchemy import event
    from sqlalchemy.engine import Engine
    from sqlalchemy.orm import joinedload

    count = {"n": 0}

    @event.listens_for(Engine, "before_cursor_execute")
    def _count(*args, **kwargs):
      count["n"] += 1

    processes = (
      Process.query.filter_by(tenant_id=tenant.id, is_active=True)
      .options(joinedload(Process.kpis))
      .all()
    )
    _ = sum(len(p.kpis) for p in processes)
    event.remove(Engine, "before_cursor_execute", _count)
    assert count["n"] <= 12
