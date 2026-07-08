# -*- coding: utf-8 -*-
"""Merkezi tenant izolasyonu (app/utils/tenant_guard.py) regresyon testleri.

Senaryolar:
- enforce modda kullanıcı başka tenant'ın verisini SELECT ile göremez
  (elle tenant filtresi UNUTULSA bile)
- kendi tenant verisi görünür
- platform admin muaf (cross-tenant görür)
- tenant_guard_bypass execution option çalışır
- off modda davranış değişmez
"""
import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.models import db
from app.models.core import User, Tenant, Role, Strategy
from config import TestingConfig


class GuardConfig(TestingConfig):
    TENANT_GUARD_MODE = "enforce"


class NoGuardConfig(TestingConfig):
    TENANT_GUARD_MODE = "off"


def _make_app(cfg):
    app = create_app(cfg)
    ctx = app.app_context()
    ctx.push()
    db.create_all()
    return app, ctx


def _teardown(ctx):
    db.session.remove()
    db.drop_all()
    ctx.pop()


def _seed():
    """İki tenant, her birinde bir kullanıcı + bir Strategy kaydı."""
    role_user = Role(name="kurum_kullanici")
    role_admin = Role(name="Admin")
    t1 = Tenant(name="Kurum A", short_name="ka", is_active=True)
    t2 = Tenant(name="Kurum B", short_name="kb", is_active=True)
    db.session.add_all([role_user, role_admin, t1, t2])
    db.session.flush()

    u1 = User(email="a@a.test", password_hash=generate_password_hash("x"),
              tenant_id=t1.id, role_id=role_user.id, is_active=True)
    admin = User(email="admin@a.test", password_hash=generate_password_hash("x"),
                 tenant_id=None, role_id=role_admin.id, is_active=True)
    s1 = Strategy(title="Strateji A", tenant_id=t1.id)
    s2 = Strategy(title="Strateji B", tenant_id=t2.id)
    db.session.add_all([u1, admin, s1, s2])
    db.session.commit()
    return t1, t2, u1, admin


def _login(app, user):
    """Request context + flask_login oturumu açar; context'i döndürür."""
    from flask_login import login_user

    rctx = app.test_request_context("/")
    rctx.push()
    login_user(user)
    return rctx


@pytest.fixture
def guard_app():
    app, ctx = _make_app(GuardConfig)
    yield app
    _teardown(ctx)


@pytest.fixture
def noguard_app():
    app, ctx = _make_app(NoGuardConfig)
    yield app
    _teardown(ctx)


def test_cross_tenant_select_blocked(guard_app):
    t1, t2, u1, _ = _seed()
    rctx = _login(guard_app, u1)
    try:
        # Elle filtre YOK — guard olmasa iki kayıt da dönerdi
        titles = {s.title for s in Strategy.query.all()}
        assert titles == {"Strateji A"}, f"Cross-tenant sızıntı: {titles}"

        # Başka tenant'ın kaydına id ile doğrudan erişim de engellenmeli
        other = db.session.get(Strategy, [s.id for s in _all_bypass() if s.tenant_id == t2.id][0])
        assert other is None or other.tenant_id == t1.id
    finally:
        rctx.pop()


def test_own_tenant_visible(guard_app):
    t1, _, u1, _ = _seed()
    rctx = _login(guard_app, u1)
    try:
        rows = Strategy.query.filter_by(tenant_id=t1.id).all()
        assert len(rows) == 1 and rows[0].title == "Strateji A"
    finally:
        rctx.pop()


def test_platform_admin_sees_all(guard_app):
    _seed()
    _, _, _, admin = _refetch()
    rctx = _login(guard_app, admin)
    try:
        assert {s.title for s in Strategy.query.all()} == {"Strateji A", "Strateji B"}
    finally:
        rctx.pop()


def test_bypass_execution_option(guard_app):
    _, _, u1, _ = _seed()
    rctx = _login(guard_app, u1)
    try:
        rows = _all_bypass()
        assert {s.title for s in rows} == {"Strateji A", "Strateji B"}
    finally:
        rctx.pop()


def test_off_mode_unfiltered(noguard_app):
    _, _, u1, _ = _seed()
    rctx = _login(noguard_app, u1)
    try:
        assert {s.title for s in Strategy.query.all()} == {"Strateji A", "Strateji B"}
    finally:
        rctx.pop()


def test_no_request_context_unfiltered(guard_app):
    """CLI/Celery/scheduler benzeri bağlam: filtre uygulanmaz."""
    _seed()
    assert {s.title for s in Strategy.query.all()} == {"Strateji A", "Strateji B"}


def _all_bypass():
    from sqlalchemy import select

    return db.session.execute(
        select(Strategy), execution_options={"tenant_guard_bypass": True}
    ).scalars().all()


def _refetch():
    t1 = Tenant.query.filter_by(short_name="ka").first()
    t2 = Tenant.query.filter_by(short_name="kb").first()
    u1 = User.query.filter_by(email="a@a.test").first()
    admin = User.query.filter_by(email="admin@a.test").first()
    return t1, t2, u1, admin
