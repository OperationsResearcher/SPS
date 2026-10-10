# -*- coding: utf-8 -*-
"""Dalga 2 paket D — modelde olmayan alanlara erişen yollar (D-007, D-021, D-022, legacy PG)."""
import logging
import pytest
from datetime import date
from werkzeug.security import generate_password_hash

from app.models import db
from app.models.core import Role, Tenant, User
from app.models.process import Process, ProcessKpi
from models.strategy import AltStrateji, AnaStrateji


@pytest.fixture
def world(app):
    t1 = Tenant(name="T1", short_name="t1", is_active=True)
    r_mgr = Role(name="tenant_admin", description="yonetici")
    r_adm = Role(name="Admin", description="admin")
    db.session.add_all([t1, r_mgr, r_adm])
    db.session.flush()

    def mk(email, r):
        u = User(email=email, first_name="Ad", last_name="Soyad", tenant_id=t1.id, role_id=r.id,
                 password_hash=generate_password_hash("x"), is_active=True)
        db.session.add(u)
        db.session.flush()
        return u

    mgr = mk("mgr@t.local", r_mgr)
    adm = mk("adm@t.local", r_adm)
    p1 = Process(name="P1", tenant_id=t1.id, is_active=True)
    db.session.add(p1)
    db.session.flush()
    ana = AnaStrateji(tenant_id=t1.id, ad="Ana1")
    db.session.add(ana)
    db.session.flush()
    alt = AltStrateji(ana_strateji_id=ana.id, ad="Alt1")
    pg = ProcessKpi(process_id=p1.id, name="PG1", is_active=True)
    db.session.add_all([alt, pg])
    db.session.commit()
    return {"mgr": mgr.id, "adm": adm.id, "t1": t1.id, "p1": p1.id, "pg": pg.id, "alt": alt.id}


def _login(client, uid):
    with client.session_transaction() as s:
        s["_user_id"] = str(uid)
        s["_fresh"] = True


def test_admin_bilesen_senkronu_500_degil(app, client, world):
    from app.models.saas import RouteRegistry
    _login(client, world["adm"])
    rv = client.post("/admin/components/sync")
    if rv.status_code == 404:
        rv = client.post("/micro/admin/components/sync")
    assert rv.status_code == 200, rv.get_data(as_text=True)
    assert RouteRegistry.query.count() > 0


def test_legacy_pg_get_200(app, client, world):
    _login(client, world["mgr"])
    rv = client.get(f"/surec/{world['p1']}/performans-gostergesi/{world['pg']}")
    assert rv.status_code == 200, rv.get_data(as_text=True)
    g = rv.get_json()["gosterge"]
    assert g["alt_strateji"] is None


def test_legacy_pg_add_200(app, client, world):
    _login(client, world["mgr"])
    rv = client.post(f"/surec/{world['p1']}/performans-gostergesi/add",
                     json={"ad": "Yeni PG"})
    assert rv.status_code == 200, rv.get_data(as_text=True)
    assert rv.get_json()["pg_id"]


def test_pg_performans_servisi_alt_strateji_yuklemesi(app, world):
    from app.models.core import SubStrategy
    q = ProcessKpi.query.options(db.joinedload(ProcessKpi.sub_strategy).joinedload(SubStrategy.strategy))
    assert q.filter_by(process_id=world["p1"]).count() == 1


def test_timesheet_servisi_500_vermez(app, world, caplog):
    from services import timesheet_service as ts
    from app.models.portfolio_project import TimeEntry
    assert ts.start_time_entry(1, world["mgr"]) is None
    assert ts.stop_time_entry(user_id=world["mgr"]) is None
    assert ts.get_user_timesheet(world["mgr"], date(2020, 1, 1), date(2030, 1, 1)) == []
    assert ts.get_task_total_time(1) == 0.0
    assert hasattr(TimeEntry, "duration_minutes") and not hasattr(TimeEntry, "start_time")


def test_planyear_vizyon_sorgusu_gecerli(app, world):
    from app.models.plan_year import PlanYear
    db.session.add(PlanYear(tenant_id=world["t1"], year=2026, status="active"))
    db.session.commit()
    py = PlanYear.query.filter_by(tenant_id=world["t1"], status="active").order_by(PlanYear.id.desc()).first()
    assert py is not None
    from micro.modules.sp.helpers import build_strateji_harita_graph
    g = build_strateji_harita_graph(world["t1"], [])
    assert any(n["id"] == "vizyon" for n in g["nodes"])


def test_pg_add_sub_strategy_kalici_ve_kurum_siniri(app, client, world):
    from app.models.core import Strategy, SubStrategy
    t2 = Tenant(name="T2", short_name="t2", is_active=True)
    db.session.add(t2)
    db.session.flush()
    s1 = Strategy(tenant_id=world["t1"], title="S1")
    s2 = Strategy(tenant_id=t2.id, title="S2")
    db.session.add_all([s1, s2])
    db.session.flush()
    ss1 = SubStrategy(strategy_id=s1.id, title="SS1")
    ss2 = SubStrategy(strategy_id=s2.id, title="SS2")
    db.session.add_all([ss1, ss2])
    db.session.commit()
    _login(client, world["mgr"])
    rv = client.post(f"/surec/{world['p1']}/performans-gostergesi/add",
                     json={"ad": "PGx", "alt_strateji_id": ss1.id})
    assert rv.status_code == 200
    db.session.expire_all()
    assert db.session.get(ProcessKpi, rv.get_json()["pg_id"]).sub_strategy_id == ss1.id
    rv = client.post(f"/surec/{world['p1']}/performans-gostergesi/add",
                     json={"ad": "PGy", "alt_strateji_id": ss2.id})
    assert rv.status_code == 400
    rv = client.post(f"/surec/{world['p1']}/performans-gostergesi/{world['pg']}/update",
                     json={"alt_strateji_id": ss1.id})
    assert rv.status_code == 200
    db.session.expire_all()
    assert db.session.get(ProcessKpi, world["pg"]).sub_strategy_id == ss1.id
    rv = client.post(f"/surec/{world['p1']}/performans-gostergesi/{world['pg']}/update",
                     json={"alt_strateji_id": None})
    db.session.expire_all()
    assert db.session.get(ProcessKpi, world["pg"]).sub_strategy_id is None

