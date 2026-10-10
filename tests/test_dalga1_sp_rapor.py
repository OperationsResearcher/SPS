# -*- coding: utf-8 -*-
"""Dalga 1 paket F — B-001, B-002/B-003, B-004, B-009 regresyon testleri."""
from datetime import date

import pytest
from werkzeug.security import generate_password_hash

from app.models import db
from app.models.core import Role, Strategy, Tenant, User
from app.models.plan_year import PlanYear
from app.models.process import Process, ProcessKpi


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
    for n in ("Admin", "tenant_admin", "ust_yonetim", "standard_user"):
        r = Role(name=n, description=n)
        db.session.add(r)
        roles[n] = r
    db.session.flush()

    def mk(email, role, tenant):
        u = User(email=email, first_name="A", last_name="B", tenant_id=tenant.id,
                 role_id=roles[role].id, password_hash=generate_password_hash("x"),
                 is_active=True)
        db.session.add(u)
        db.session.flush()
        return u

    ta = mk("ta@t.l", "tenant_admin", t1)
    std = mk("std@t.l", "standard_user", t1)
    ust = mk("ust@t.l", "ust_yonetim", t1)
    other_user = mk("o@t.l", "tenant_admin", t2)

    p1 = Process(tenant_id=t1.id, name="P1")
    p2 = Process(tenant_id=t2.id, name="P2")
    db.session.add_all([p1, p2])
    db.session.flush()
    k1 = ProcessKpi(process_id=p1.id, name="K1")
    k2 = ProcessKpi(process_id=p2.id, name="K2")
    s2 = Strategy(tenant_id=t2.id, title="S2")
    db.session.add_all([k1, k2, s2])
    db.session.commit()
    return {"ta": ta.id, "std": std.id, "ust": ust.id, "other_user": other_user.id,
            "k1": k1.id, "k2": k2.id, "s2": s2.id, "t1": t1.id}


# ── B-001 ────────────────────────────────────────────────────────────────────

def test_replan_trigger_other_tenant_kpi_400(client, ctx):
    _login(client, ctx["ta"])
    rv = client.post("/k-plan/strategy/api/replan-triggers", json={
        "name": "x", "trigger_type": "kpi_below_target", "target_kpi_id": ctx["k2"]})
    assert rv.status_code == 400


def test_replan_trigger_own_kpi_ok_and_period_range(client, ctx):
    _login(client, ctx["ta"])
    rv = client.post("/k-plan/strategy/api/replan-triggers", json={
        "name": "x", "trigger_type": "kpi_below_target", "target_kpi_id": ctx["k1"]})
    assert rv.status_code == 201
    rv = client.post("/k-plan/strategy/api/replan-triggers", json={
        "name": "x", "trigger_type": "kpi_below_target", "target_kpi_id": ctx["k1"],
        "consecutive_periods": 0})
    assert rv.status_code == 400


def test_replan_service_sql_tenant_filter():
    import inspect
    from app.services import replan_trigger_service as svc
    src = inspect.getsource(svc._eval_kpi_below_target)
    assert "p.tenant_id=:tid" in src and "JOIN processes" in src


# ── B-002 / B-003 ────────────────────────────────────────────────────────────

KISISEL = [
    "/k-report/api/individual",
    "/k-report/api/audit",
    "/k-report/api/export-excel?tab=bireysel",
    "/k-report/api/audit-package/generate",
    "/k-report/api/individual-scorecard-batch/generate",
    "/k-report/api/two-fa",
]
YONETIM = [
    "/k-report/api/cfo-dashboard",
    "/k-report/api/investor-presentation/generate",
]


@pytest.mark.parametrize("url", KISISEL + YONETIM)
def test_dusuk_rol_403_json(client, ctx, url):
    _login(client, ctx["std"])
    rv = client.get(url)
    assert rv.status_code == 403
    assert rv.get_json()["success"] is False


@pytest.mark.parametrize("url", KISISEL)
def test_kisisel_ust_yonetim_403(client, ctx, url):
    _login(client, ctx["ust"])
    assert client.get(url).status_code == 403


@pytest.mark.parametrize("url", KISISEL + YONETIM)
def test_yetkili_rol_kapidan_gecer(client, ctx, url):
    _login(client, ctx["ta"])
    rv = client.get(url)
    assert rv.status_code != 403


def test_ust_yonetim_yonetim_raporu_rol_izni(app, ctx):
    from app_platform.modules.raporlar.helpers import ROLES_KISISEL, ROLES_YONETIM
    assert "ust_yonetim" in ROLES_YONETIM and "ust_yonetim" not in ROLES_KISISEL


# ── B-009 ────────────────────────────────────────────────────────────────────

def test_initiative_create_other_tenant_ids_400(client, ctx):
    _login(client, ctx["ta"])
    base = {"name": "G", "start_year": 2026, "end_year": 2027}
    for extra in ({"strategy_id": ctx["s2"]}, {"owner_user_id": ctx["other_user"]}):
        rv = client.post("/k-plan/strategy/api/initiatives", json={**base, **extra})
        assert rv.status_code == 400, extra
    rv = client.post("/k-plan/strategy/api/initiatives", json=base)
    assert rv.status_code in (201, 409)


# ── B-004 ────────────────────────────────────────────────────────────────────

def test_muhurlu_yil_409_acik_yil_basari(client, ctx):
    _login(client, ctx["ta"])
    py = PlanYear(tenant_id=ctx["t1"], year=date.today().year, status="closed")
    db.session.add(py)
    db.session.commit()
    body = {"name": "G", "start_year": 2026, "end_year": 2027}
    rv = client.post("/k-plan/strategy/api/initiatives", json=body)
    assert rv.status_code == 409
    assert "mühürlü" in rv.get_json()["message"]
    rv = client.post("/k-plan/strategy/api/swot", json={})
    assert rv.status_code == 409
    py.status = "active"
    db.session.commit()
    rv = client.post("/k-plan/strategy/api/initiatives", json=body)
    assert rv.status_code == 201
