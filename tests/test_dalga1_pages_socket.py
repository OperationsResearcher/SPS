# -*- coding: utf-8 -*-
"""Dalga 1 paket E — D-017 (soft delete), C-003 (PG alt_strateji IDOR), D-012 (socket odaları/PII)."""
import pytest
from werkzeug.security import generate_password_hash

from app.models import db
from app.models.core import Role, Tenant, User
from app.models.process import Process, ProcessActivity, ProcessKpi
from app.models.core import Strategy, SubStrategy


@pytest.fixture
def world(app):
    t1 = Tenant(name="T1", short_name="t1", is_active=True)
    t2 = Tenant(name="T2", short_name="t2", is_active=True)
    r_mgr = Role(name="tenant_admin", description="yonetici")
    r_std = Role(name="standard_user", description="standart")
    db.session.add_all([t1, t2, r_mgr, r_std])
    db.session.flush()

    def mk(email, t, r):
        u = User(email=email, first_name="Ad", last_name="Soyad", tenant_id=t.id, role_id=r.id,
                 password_hash=generate_password_hash("x"), is_active=True)
        db.session.add(u)
        db.session.flush()
        return u

    a_mgr = mk("a-mgr@t.local", t1, r_mgr)
    b_mgr = mk("b-mgr@t.local", t2, r_mgr)
    a_std = mk("a-std@t.local", t1, r_std)

    p1 = Process(name="P1", tenant_id=t1.id, is_active=True)
    p2 = Process(name="P2", tenant_id=t2.id, is_active=True)
    db.session.add_all([p1, p2])
    db.session.flush()

    ana1 = Strategy(tenant_id=t1.id, title="Ana1")
    ana2 = Strategy(tenant_id=t2.id, title="Ana2")
    db.session.add_all([ana1, ana2])
    db.session.flush()
    alt1 = SubStrategy(strategy_id=ana1.id, title="Alt1")
    alt2 = SubStrategy(strategy_id=ana2.id, title="Alt2-B")
    db.session.add_all([alt1, alt2])
    db.session.flush()

    pg1 = ProcessKpi(process_id=p1.id, name="PG1", is_active=True)
    fa1 = ProcessActivity(process_id=p1.id, name="F1", is_active=True)
    db.session.add_all([pg1, fa1])
    db.session.commit()
    return {
        "a_mgr": a_mgr.id, "b_mgr": b_mgr.id, "a_std": a_std.id,
        "p1": p1.id, "p2": p2.id, "pg1": pg1.id, "fa1": fa1.id,
        "alt1": alt1.id, "alt2": alt2.id,
    }


def _login(client, uid):
    with client.session_transaction() as s:
        s["_user_id"] = str(uid)
        s["_fresh"] = True


# ── D-017: soft delete ───────────────────────────────────────────────────────

def test_pg_silme_soft_delete(app, client, world):
    _login(client, world["a_mgr"])
    rv = client.delete(f"/surec/{world['p1']}/performans-gostergesi/{world['pg1']}/delete")
    assert rv.status_code == 200, rv.get_data(as_text=True)
    db.session.expire_all()
    pg = db.session.get(ProcessKpi, world["pg1"])
    assert pg is not None, "PG fiziksel olarak silinmemeli"
    assert pg.is_active is False


def test_silinen_pg_okunamaz_ve_listede_yok(app, client, world):
    _login(client, world["a_mgr"])
    client.delete(f"/surec/{world['p1']}/performans-gostergesi/{world['pg1']}/delete")
    rv = client.post(f"/surec/{world['p1']}/performans-gostergesi/{world['pg1']}/update",
                     json={"ad": "yeni"})
    assert rv.status_code == 404


def test_faaliyet_silme_soft_delete(app, client, world):
    _login(client, world["a_mgr"])
    rv = client.delete(f"/surec/{world['p1']}/faaliyet/{world['fa1']}/delete")
    assert rv.status_code == 200, rv.get_data(as_text=True)
    db.session.expire_all()
    fa = db.session.get(ProcessActivity, world["fa1"])
    assert fa is not None and fa.is_active is False


# ── C-003: alt_strateji kurum/süreç doğrulaması ─────────────────────────────

def test_pg_update_baska_kurum_alt_stratejisi_reddedilir(app, client, world):
    _login(client, world["a_mgr"])
    rv = client.post(f"/surec/{world['p1']}/performans-gostergesi/{world['pg1']}/update",
                     json={"alt_strateji_id": world["alt2"]})
    assert rv.status_code == 400
    assert rv.get_json()["success"] is False


def test_pg_update_kendi_alt_stratejisi_kabul_edilir(app, client, world):
    _login(client, world["a_mgr"])
    rv = client.post(f"/surec/{world['p1']}/performans-gostergesi/{world['pg1']}/update",
                     json={"alt_strateji_id": world["alt1"]})
    assert rv.status_code == 200, rv.get_data(as_text=True)
    db.session.expire_all()
    assert db.session.get(ProcessKpi, world["pg1"]).sub_strategy_id == world["alt1"]


# ── D-012: socket odaları ve e-posta sızıntısı ──────────────────────────────

@pytest.fixture
def sio(monkeypatch):
    from app import socketio_events as se

    class Rec:
        pass

    rec = Rec()
    rec.emitted, rec.joined, rec.in_rooms = [], set(), set()
    monkeypatch.setattr(se, "emit", lambda ev, payload=None, **kw: rec.emitted.append((ev, payload, kw.get("room"))))
    monkeypatch.setattr(se, "join_room", lambda room: (rec.joined.add(room), rec.in_rooms.add(room)))
    monkeypatch.setattr(se, "leave_room", lambda room: rec.in_rooms.discard(room))
    monkeypatch.setattr(se, "rooms", lambda sid=None: set(rec.in_rooms))
    monkeypatch.setattr(se, "request", type("R", (), {"sid": "sid-1"})())
    rec.se = se
    return rec


def _as(app, uid):
    from flask_login import login_user
    ctx = app.test_request_context()
    ctx.push()
    login_user(db.session.get(User, uid))
    return ctx


def test_baska_kurum_leave_process_olay_yayinlayamaz(app, world, sio):
    ctx = _as(app, world["b_mgr"])
    try:
        sio.se.handle_leave_process({"process_id": world["p1"]})
        assert sio.emitted == []
    finally:
        ctx.pop()


def test_leave_process_e_posta_icermez(app, world, sio):
    ctx = _as(app, world["a_mgr"])
    try:
        sio.se.handle_join_process({"process_id": world["p1"]})
        sio.emitted.clear()
        sio.se.handle_leave_process({"process_id": world["p1"]})
        left = [p for e, p, _ in sio.emitted if e == "user_left"]
        assert len(left) == 1
        assert "@" not in repr(left[0])
        assert "email" not in left[0]
    finally:
        ctx.pop()


def test_join_ve_typing_e_posta_icermez(app, world, sio):
    ctx = _as(app, world["a_mgr"])
    try:
        sio.se.handle_join_process({"process_id": world["p1"]})
        sio.se.handle_typing({"process_id": world["p1"], "field": "x"})
        sio.se.handle_kpi_data_update({"process_id": world["p1"], "kpi_id": 1, "field": "x", "value": 5})
        assert sio.emitted, "yayın beklenir"
        for _, payload, _ in sio.emitted:
            assert "@" not in repr(payload)
    finally:
        ctx.pop()


@pytest.mark.parametrize("bad", [None, [], "abc", 5])
def test_bozuk_payload_istisna_firlatmaz(app, world, sio, bad):
    ctx = _as(app, world["a_mgr"])
    try:
        for handler in ("handle_join_process", "handle_leave_process", "handle_typing",
                        "handle_kpi_data_update", "handle_get_active_users"):
            getattr(sio.se, handler)(bad)
        assert sio.joined == set()
    finally:
        ctx.pop()
