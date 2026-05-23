"""SQL query counter testleri."""
import pytest

from app.utils.query_counter import count_queries, assert_max_queries
from app.models.core import Tenant
from app.models.process import Process
from extensions import db


def test_count_simple_query(app):
    with app.app_context():
        with count_queries() as counter:
            db.session.execute(db.text("SELECT 1"))
        assert counter.count >= 1


def test_count_zero_queries(app):
    with app.app_context():
        with count_queries() as counter:
            x = 1 + 1
        assert counter.count == 0


def test_assert_max_queries_passes_when_under(app):
    with app.app_context():
        with count_queries() as counter:
            db.session.execute(db.text("SELECT 1"))
        # Test geçmeli
        assert_max_queries(5, counter)


def test_assert_max_queries_fails_when_over(app):
    with app.app_context():
        with count_queries() as counter:
            for _ in range(5):
                db.session.execute(db.text("SELECT 1"))
        with pytest.raises(AssertionError, match="N\\+1 regresyon"):
            assert_max_queries(2, counter)


def test_record_sql_captures_text(app):
    with app.app_context():
        with count_queries(record_sql=True) as counter:
            db.session.execute(db.text("SELECT 42"))
        assert any("42" in q for q in counter.queries)


def test_process_listing_no_lazy_load(app):
    """Sanity: tenant listing tek sorgu ile yapılır."""
    with app.app_context():
        with count_queries() as counter:
            list(Tenant.query.limit(5).all())
        # 1 SELECT bekleniyor (lazy relationship'ler erişilmeden)
        assert counter.count <= 2  # bazı engine'ler savepoint vs.
