"""PERF-12 — masaüstü favori PG'lerin son ölçümü tek sorguda gelir ve doğru satırı seçer."""
from datetime import date

import pytest
from flask import template_rendered
from werkzeug.security import generate_password_hash

from app.models import db
from app.models.core import Role, Tenant, User
from app.models.plan_year import PlanYear
from app.models.process import FavoriteKpi, KpiData, Process, ProcessKpi


@pytest.fixture
def masaustu(app, client):
    t = Tenant(name="T", short_name="t", is_active=True)
    r = Role(name="tenant_admin", description="ta")
    db.session.add_all([t, r])
    db.session.flush()
    db.session.add(PlanYear(tenant_id=t.id, year=2026, status="active"))
    u = User(email="ta@t.local", first_name="a", last_name="b", tenant_id=t.id, role_id=r.id,
             password_hash=generate_password_hash("x"), is_active=True)
    p = Process(name="P", tenant_id=t.id, is_active=True)
    db.session.add_all([u, p])
    db.session.flush()
    a = ProcessKpi(process_id=p.id, name="A", code="A", is_active=True, target_value="100", direction="Increasing")
    b = ProcessKpi(process_id=p.id, name="B", code="B", is_active=True, target_value="10", direction="Increasing")
    db.session.add_all([a, b])
    db.session.flush()
    db.session.add_all([
        FavoriteKpi(user_id=u.id, process_kpi_id=a.id, is_active=True),
        FavoriteKpi(user_id=u.id, process_kpi_id=b.id, is_active=True),
        KpiData(process_kpi_id=a.id, year=2025, data_date=date(2025, 12, 31), actual_value="1", is_active=True),
        KpiData(process_kpi_id=a.id, year=2026, data_date=date(2026, 1, 31), actual_value="20", is_active=True),
        KpiData(process_kpi_id=a.id, year=2026, data_date=date(2026, 2, 28), actual_value="50", is_active=True),
        KpiData(process_kpi_id=a.id, year=2026, data_date=date(2026, 3, 31), actual_value="99", is_active=False),
    ])
    db.session.commit()
    with client.session_transaction() as s:
        s["_user_id"] = str(u.id)
        s["_fresh"] = True
        s["sv"] = 0
    return {"a": a.id, "b": b.id}


def test_favori_son_olcum_dogru(app, client, masaustu):
    yakalanan = []

    def kaydet(sender, template, context, **kw):
        if "favori_pgs" in context:
            yakalanan.append(context["favori_pgs"])

    template_rendered.connect(kaydet, app)
    try:
        rv = client.get("/desktop")
    finally:
        template_rendered.disconnect(kaydet, app)
    assert rv.status_code == 200, rv.data[:200]
    pgs = {x["id"]: x for x in yakalanan[-1]}
    assert pgs[masaustu["a"]]["actual_value"] == "50"     # en yeni AKTİF kayıt
    assert pgs[masaustu["b"]]["actual_value"] is None     # verisiz PG
