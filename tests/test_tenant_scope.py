"""Tenant scope decorator testleri.

monkeypatch ile current_user'ı module-level import noktasında değiştir.
"""
from unittest.mock import MagicMock

import pytest
from flask import Flask
from werkzeug.exceptions import HTTPException

from app.utils import tenant_scope as ts_module
from app.utils.tenant_scope import verify_tenant_resource


@pytest.fixture
def app():
    return Flask(__name__)


class _Resource:
    def __init__(self, id, tenant_id):
        self.id = id
        self.tenant_id = tenant_id


def _fake_user(authenticated=True, tenant_id=1, user_id=99, role_name="User"):
    u = MagicMock()
    u.is_authenticated = authenticated
    u.tenant_id = tenant_id
    u.id = user_id
    role = MagicMock()
    role.name = role_name
    u.role = role
    return u


def test_resource_id_missing_passes_through(app):
    model = MagicMock()

    @verify_tenant_resource(model, "process_id")
    def handler():
        return "ok"

    with app.test_request_context():
        assert handler() == "ok"


def test_unauthenticated_aborts_401(app, monkeypatch):
    model = MagicMock()
    monkeypatch.setattr(ts_module, "current_user", _fake_user(authenticated=False))

    @verify_tenant_resource(model, "process_id")
    def handler(process_id):
        return "ok"

    with app.test_request_context(), pytest.raises(HTTPException) as exc:
        handler(process_id=1)
    assert exc.value.code == 401


def test_resource_not_found_aborts_404(app, monkeypatch):
    model = MagicMock()
    model.__name__ = "FakeModel"
    model.query.get = MagicMock(return_value=None)
    monkeypatch.setattr(ts_module, "current_user", _fake_user(tenant_id=1))

    @verify_tenant_resource(model, "process_id")
    def handler(process_id):
        return "ok"

    with app.test_request_context(), pytest.raises(HTTPException) as exc:
        handler(process_id=999)
    assert exc.value.code == 404


def test_cross_tenant_aborts_403(app, monkeypatch):
    model = MagicMock()
    model.__name__ = "FakeModel"
    res = _Resource(id=5, tenant_id=2)
    model.query.get = MagicMock(return_value=res)
    monkeypatch.setattr(ts_module, "current_user", _fake_user(tenant_id=1))

    @verify_tenant_resource(model, "process_id")
    def handler(process_id):
        return "ok"

    with app.test_request_context(), pytest.raises(HTTPException) as exc:
        handler(process_id=5)
    assert exc.value.code == 403


def test_same_tenant_passes(app, monkeypatch):
    model = MagicMock()
    model.__name__ = "FakeModel"
    res = _Resource(id=5, tenant_id=1)
    model.query.get = MagicMock(return_value=res)
    monkeypatch.setattr(ts_module, "current_user", _fake_user(tenant_id=1))

    @verify_tenant_resource(model, "process_id")
    def handler(process_id):
        return "ok"

    with app.test_request_context():
        assert handler(process_id=5) == "ok"


def test_admin_bypasses_check(app, monkeypatch):
    """Admin kullanıcı cross-tenant erişebilir (query.get çağrılmaz)."""
    model = MagicMock()
    model.__name__ = "FakeModel"
    model.query.get = MagicMock(side_effect=AssertionError("Admin için query.get çağrılmamalı"))
    monkeypatch.setattr(ts_module, "current_user", _fake_user(tenant_id=1, role_name="Admin"))

    @verify_tenant_resource(model, "process_id")
    def handler(process_id):
        return "ok"

    with app.test_request_context():
        assert handler(process_id=999) == "ok"


def test_resolver_for_indirect_tenant(app, monkeypatch):
    """Resource indirect tenant taşıyorsa resolver kullan."""
    model = MagicMock()
    model.__name__ = "ProcessKpi"
    process = MagicMock()
    process.tenant_id = 1
    kpi = MagicMock()
    kpi.process = process
    model.query.get = MagicMock(return_value=kpi)
    monkeypatch.setattr(ts_module, "current_user", _fake_user(tenant_id=1))

    @verify_tenant_resource(model, "kpi_id", resolver=lambda r: r.process.tenant_id)
    def handler(kpi_id):
        return "ok"

    with app.test_request_context():
        assert handler(kpi_id=42) == "ok"
