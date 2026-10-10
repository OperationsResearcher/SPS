# -*- coding: utf-8 -*-
"""Dalga 2 paket B: bildirim servisi, hatirlatma zamanlayicilari, erken uyari."""
from datetime import date, timedelta

import pytest

from app.models import db
from app.models.core import Notification, Tenant, User, Role
from app.models.portfolio_project import Project, Task


def _mk(app_):
    t = Tenant(name="BildT", short_name="bt")
    db.session.add(t)
    db.session.flush()
    r = Role.query.first() or Role(name="User")
    db.session.add(r)
    db.session.flush()
    u1 = User(email="a@x.com", password_hash="x", first_name="A", last_name="B", tenant_id=t.id, role_id=r.id)
    u2 = User(email="c@x.com", password_hash="x", first_name="C", last_name="D", tenant_id=t.id, role_id=r.id)
    db.session.add_all([u1, u2])
    db.session.commit()
    return t, u1, u2


def test_notification_service_writes_modern_table(app):
    from services import notification_service as ns
    t, u1, u2 = _mk(app)
    n = ns.Notification(u1.id, "task_assigned", "Baslik", "Mesaj", "/x", ilgili_user_id=u2.id)
    assert ns._persist(n) is True
    assert ns._commit() is True
    row = Notification.query.filter_by(user_id=u1.id, notification_type="task_assigned").one()
    assert row.tenant_id == t.id and row.title == "Baslik" and row.related_user_id == u2.id


def test_notification_failure_keeps_caller_changes(app):
    from services import notification_service as ns
    t, u1, u2 = _mk(app)
    u1.first_name = "DEGISTI"          # caller'in bekleyen degisikligi
    bad = ns.Notification(999999, "t", "B", "M")   # gecersiz kullanici -> tenant None
    bad.title = None                                # NOT NULL ihlali
    assert ns._persist(bad) is False
    assert u1.first_name == "DEGISTI"
    db.session.commit()
    assert db.session.get(User, u1.id).first_name == "DEGISTI"


def _fake_start(monkeypatch):
    from apscheduler.schedulers.background import BackgroundScheduler
    monkeypatch.setattr(BackgroundScheduler, "start", lambda self, *a, **k: None)


def test_reminder_jobs_flag_off_not_registered(app, monkeypatch):
    import app as app_pkg
    from services import task_reminder_scheduler as trs, process_activity_scheduler as pas
    _fake_start(monkeypatch)
    trs.scheduler = None
    pas.scheduler = None
    app.config["REMINDER_SCHEDULERS_ENABLED"] = False
    app_pkg._init_reminder_schedulers(app)
    assert trs.scheduler is None and pas.scheduler is None


def test_reminder_jobs_flag_on_registered(app, monkeypatch):
    import app as app_pkg
    from services import task_reminder_scheduler as trs, process_activity_scheduler as pas
    _fake_start(monkeypatch)
    trs.scheduler = None
    pas.scheduler = None
    app.config["REMINDER_SCHEDULERS_ENABLED"] = True
    try:
        app_pkg._init_reminder_schedulers(app)
        assert "task_reminder_check" in [j.id for j in trs.scheduler.get_jobs()]
        ids = [j.id for j in pas.scheduler.get_jobs()]
        assert "process_activity_reminder_check" in ids
    finally:
        trs.scheduler = None
        pas.scheduler = None


def test_config_flag_default_off():
    from config import Config
    assert Config.REMINDER_SCHEDULERS_ENABLED is False


def test_early_warning_dedup_and_tenant_id(app):
    from services.early_warning_service import _send_notification
    t, u1, u2 = _mk(app)
    assert _send_notification(u1.id, "T", "M", "/l", tenant_id=t.id) is True
    db.session.commit()
    assert _send_notification(u1.id, "T", "M", "/l", tenant_id=t.id) is False
    db.session.commit()
    rows = Notification.query.filter_by(user_id=u1.id).all()
    assert len(rows) == 1 and rows[0].tenant_id == t.id
    # farkli PG (mesaj) -> ayri bildirim
    assert _send_notification(u1.id, "T", "M2", "/l", tenant_id=t.id) is True


def test_radar_apply_schedule_skips_non_leader(app, monkeypatch):
    from services import k_radar_scheduler_service as ks
    import app.utils.scheduler_leader as sl
    monkeypatch.setattr(sl, "is_leader", lambda a: False)
    monkeypatch.setattr(ks, "_scheduler", None)
    monkeypatch.setattr(ks, "load_schedule", lambda a: {"enabled": True, "time": "08:30"})
    ks.apply_schedule(app)
    assert ks._scheduler is None
