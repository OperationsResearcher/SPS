"""GUV-16 — Socket.IO süreç odaları kurum sınırını aşmamalı."""
import pytest
from werkzeug.security import generate_password_hash

from app.models import db
from app.models.core import Role, Tenant, User
from app.models.notification import Notification
from app.models.process import Process


@pytest.fixture
def world(app):
    t1 = Tenant(name="T1", short_name="t1", is_active=True)
    t2 = Tenant(name="T2", short_name="t2", is_active=True)
    r = Role(name="standard_user", description="s")
    db.session.add_all([t1, t2, r])
    db.session.flush()

    def mk(email, t):
        u = User(email=email, first_name="a", last_name="b", tenant_id=t.id, role_id=r.id,
                 password_hash=generate_password_hash("x"), is_active=True)
        db.session.add(u)
        db.session.flush()
        return u

    a1, a2 = mk("a1@t.local", t1), mk("a2@t.local", t1)
    b1 = mk("b1@t.local", t2)
    p1 = Process(name="P1", tenant_id=t1.id, is_active=True)
    p2 = Process(name="P2", tenant_id=t2.id, is_active=True)
    db.session.add_all([p1, p2])
    db.session.commit()
    return {"a1": a1.id, "a2": a2.id, "b1": b1.id, "p1": p1.id, "p2": p2.id}


@pytest.fixture
def sio(monkeypatch):
    """Handler'ları doğrudan çağırırız; emit/join_room/rooms kayıt tutan sahtelerle değişir."""
    from app import socketio_events as se

    class Rec:
        emitted, joined, in_rooms = [], set(), set()

    rec = Rec()
    rec.emitted, rec.joined, rec.in_rooms = [], set(), set()
    monkeypatch.setattr(se, "emit", lambda ev, payload=None, **kw: rec.emitted.append((ev, kw.get("room"))))
    monkeypatch.setattr(se, "join_room", lambda room: (rec.joined.add(room), rec.in_rooms.add(room)))
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


def _events(rec):
    return [e for e, _ in rec.emitted]


def test_ayni_kurum_odaya_girer_ve_yayin_yapar(app, world, sio):
    ctx = _as(app, world["a1"])
    try:
        sio.se.handle_join_process({"process_id": world["p1"]})
        assert f"process_{world['p1']}" in sio.joined
        sio.se.handle_kpi_data_update({"process_id": world["p1"], "kpi_id": 1, "field": "x", "value": 5})
        assert "kpi_updated" in _events(sio)
    finally:
        ctx.pop()


def test_baska_kurumun_surec_odasina_girilemez(app, world, sio):
    ctx = _as(app, world["b1"])   # T2 kullanıcısı, T1'in sürecini hedefler
    try:
        sio.se.handle_join_process({"process_id": world["p1"]})
        assert sio.joined == set()
        assert "error" in _events(sio)
        # Odaya giremeyen yayın da enjekte edemez, oda üyelerini de göremez
        sio.emitted.clear()
        sio.se.handle_kpi_data_update({"process_id": world["p1"], "kpi_id": 1, "field": "x", "value": 9})
        sio.se.handle_typing({"process_id": world["p1"], "field": "x"})
        sio.se.handle_get_active_users({"process_id": world["p1"]})
        assert sio.emitted == []
    finally:
        ctx.pop()


def test_gecersiz_process_id_reddedilir(app, world, sio):
    ctx = _as(app, world["a1"])
    try:
        for bad in (None, "abc", 999999):
            sio.se.handle_join_process({"process_id": bad})
        assert sio.joined == set()
    finally:
        ctx.pop()


def test_kpi_data_entered_istemci_tenant_id_yok_sayilir(app, world, sio, monkeypatch):
    sent = []
    monkeypatch.setattr(sio.se.socketio, "emit", lambda ev, payload, room=None: sent.append(room), raising=False)
    ctx = _as(app, world["a1"])
    try:
        own = db.session.get(User, world["a1"]).tenant_id
        sio.se.handle_kpi_data_entered({"tenant_id": 999, "process_id": world["p1"], "kpi_id": 1})
        assert sent == [f"tenant_{own}"]
    finally:
        ctx.pop()


def test_bildirim_yalniz_sahibi_okundu_isaretler(app, world, sio):
    n = Notification(user_id=world["a1"], type="info", title="t", message="m", is_read=False)
    db.session.add(n)
    db.session.commit()
    nid = n.id

    ctx = _as(app, world["b1"])
    try:
        sio.se.handle_mark_notification_read({"notification_id": nid})
    finally:
        ctx.pop()
    db.session.expire_all()
    assert db.session.get(Notification, nid).is_read is False

    ctx = _as(app, world["a1"])
    try:
        sio.se.handle_mark_notification_read({"notification_id": nid})
    finally:
        ctx.pop()
    db.session.expire_all()
    assert db.session.get(Notification, nid).is_read is True
