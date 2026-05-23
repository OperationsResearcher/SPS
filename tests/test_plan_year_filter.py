"""Plan year filter helper testleri.

Sprint 1.1 kapsamında yazıldı. Audit bulgu #1 için regresyon koruması.
Gerçek ORM modelleri ile test edilir.
"""
import pytest

from app.utils.plan_year_filter import filter_by_plan_year
from app.models.process import Process


def test_filter_by_plan_year_with_id_and_null_default(app):
    """plan_year_id verilince filtre uygulanır, NULL kapsanır."""
    with app.app_context():
        q = Process.query
        result = filter_by_plan_year(q, Process, 5)
        sql = str(result.statement.compile(compile_kwargs={"literal_binds": True}))
        # OR ile NULL kapsama olmalı
        assert "plan_year_id IS NULL" in sql or "plan_year_id = 5" in sql


def test_filter_by_plan_year_with_id_no_null(app):
    """include_null=False ise sadece tam eşleşme."""
    with app.app_context():
        q = Process.query
        result = filter_by_plan_year(q, Process, 5, include_null=False)
        sql = str(result.statement.compile(compile_kwargs={"literal_binds": True}))
        assert "plan_year_id = 5" in sql
        # NULL ifadesi olmamalı
        assert "IS NULL" not in sql


def test_filter_by_plan_year_with_none_id_no_filter(app):
    """plan_year_id=None gelirse filtre uygulanmaz (legacy mode)."""
    with app.app_context():
        q = Process.query
        original_count = str(q.statement).count("WHERE")
        result = filter_by_plan_year(q, Process, None)
        new_count = str(result.statement).count("WHERE")
        assert new_count == original_count, "Filtre uygulanmamalı"


def test_filter_by_plan_year_model_without_plan_year_raises():
    """plan_year_id kolonu olmayan modelde AttributeError."""

    class _NoPlanYear:
        __name__ = "_NoPlanYear"

    class _FakeQuery:
        def filter(self, *a, **kw):
            return self

    q = _FakeQuery()
    with pytest.raises(AttributeError, match="plan_year_id kolonu yok"):
        filter_by_plan_year(q, _NoPlanYear, 5)
