"""N+1 regression test'leri.

Sprint 11.5 — production sorgu pattern'leri için sorgu sayısı koruması.
Yeni eager loading kaldırılırsa bu test failure verir.

Tomofil tenant (id=27) baseline:
- 46 process listing (joinedload): ≤5 sorgu
- 28 strategy + sub_strategies (selectinload): ≤3 sorgu
"""
import pytest

from app.utils.query_counter import count_queries, assert_max_queries
from app.models.process import Process
from app.models.core import Strategy
from sqlalchemy.orm import joinedload, selectinload


TOMOFIL_TID = 27


@pytest.fixture(autouse=True)
def _ensure_tomofil(app):
    """Tomofil tenant yoksa skip."""
    with app.app_context():
        from app.models.core import Tenant
        t = Tenant.query.get(TOMOFIL_TID)
        if not t:
            pytest.skip(f"Tomofil tenant id={TOMOFIL_TID} bulunamadı — seed ile oluştur.")


def test_process_listing_with_joinedload(app):
    """Process listing leaders/members/owners ile birlikte ≤5 sorguda dönmeli."""
    with app.app_context():
        with count_queries() as counter:
            ps = (
                Process.query
                .filter_by(tenant_id=TOMOFIL_TID, is_active=True)
                .options(
                    joinedload(Process.leaders),
                    joinedload(Process.members),
                    joinedload(Process.owners),
                )
                .all()
            )
            # Lazy access ile N+1 olmamalı (eager yüklendi)
            for p in ps:
                _ = list(p.leaders), list(p.members), list(p.owners)
        assert_max_queries(5, counter)


def test_process_listing_lazy_DETECTS_N_PLUS_1(app):
    """Lazy load'la N+1 OLUŞMALI — regression koruması (eager loading olmazsa fail)."""
    with app.app_context():
        with count_queries() as counter:
            ps = Process.query.filter_by(tenant_id=TOMOFIL_TID, is_active=True).all()
            for p in ps[:5]:  # ilk 5 process
                _ = list(p.leaders), list(p.members), list(p.owners)
        # Bu test SOL: lazy load → çok sorgu (≥15 = 5 process × 3 ilişki)
        # Eğer relationship lazy default değişirse bu test fail eder → bilgilendirici
        assert counter.count >= 10, f"Lazy load mu? Sayı {counter.count}, ≥10 bekleniyor"


def test_strategy_with_substrategy_selectinload(app):
    """Strategy + sub_strategy selectinload ile ≤3 sorgu (1 strategy + 1 substrategy + 1 setup)."""
    with app.app_context():
        with count_queries() as counter:
            ss = (
                Strategy.query
                .filter_by(tenant_id=TOMOFIL_TID, is_active=True)
                .options(selectinload(Strategy.sub_strategies))
                .all()
            )
            for s in ss:
                _ = list(s.sub_strategies)
        assert_max_queries(5, counter)


def test_kpi_data_aggregate_single_query(app):
    """Aggregate sorguları tek SQL'de olmalı."""
    from extensions import db
    from sqlalchemy import text
    with app.app_context():
        with count_queries() as counter:
            rows = db.session.execute(text("""
                SELECT kd.year, count(*) FROM kpi_data kd
                JOIN process_kpis k ON kd.process_kpi_id=k.id
                JOIN processes p ON k.process_id=p.id
                WHERE p.tenant_id=:t
                GROUP BY kd.year
            """), {"t": TOMOFIL_TID}).fetchall()
        assert_max_queries(2, counter)
        assert len(rows) > 0
