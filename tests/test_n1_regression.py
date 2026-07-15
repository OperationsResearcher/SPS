"""N+1 regression test'leri.

Sprint 11.5 — production sorgu pattern'leri için sorgu sayısı koruması.
Yeni eager loading kaldırılırsa bu test failure verir.

2026-07-15: Test artık seed edilmiş Tomofil tenant'ına (id=27) BAĞLI DEĞİL.
Önceki hali tenant yoksa `pytest.skip` ediyordu; CI'da veritabanı boş olduğu
için testler sessizce atlanıyor ve hiçbir regresyonu yakalamıyordu. Artık
gereken veriyi fixture kendisi üretir — her ortamda gerçekten çalışır.
"""
import pytest

from extensions import db
from app.utils.query_counter import count_queries, assert_max_queries
from app.models.process import Process
from app.models.core import Strategy, SubStrategy, Tenant, User, Role
from sqlalchemy.orm import joinedload, selectinload


PROCESS_COUNT = 6
STRATEGY_COUNT = 4


@pytest.fixture
def n1_data(app):
    """N+1 ölçümü için yeterli hacimde veri üretir (kendi kendine yeter)."""
    with app.app_context():
        tenant = Tenant(name="N1 Kurum", short_name="n1", is_active=True)
        db.session.add(tenant)
        db.session.commit()

        role = Role(name="n1_user", description="N1")
        db.session.add(role)
        db.session.commit()

        users = []
        for i in range(3):
            u = User(
                email=f"n1_{i}@example.com",
                first_name="N",
                last_name=str(i),
                tenant_id=tenant.id,
                role_id=role.id,
                password_hash="x",
                is_active=True,
            )
            db.session.add(u)
            users.append(u)
        db.session.commit()

        # Her sürece 3 ilişki bağla → eager loading olmazsa N+1 görünür
        for i in range(PROCESS_COUNT):
            p = Process(name=f"Surec {i}", tenant_id=tenant.id, is_active=True)
            p.leaders.append(users[0])
            p.members.append(users[1])
            p.owners.append(users[2])
            db.session.add(p)

        for i in range(STRATEGY_COUNT):
            s = Strategy(title=f"Strateji {i}", code=f"ST{i}", tenant_id=tenant.id, is_active=True)
            db.session.add(s)
            db.session.flush()
            for j in range(2):
                db.session.add(
                    SubStrategy(title=f"Alt {i}.{j}", code=f"ST{i}.{j}", strategy_id=s.id)
                )
        db.session.commit()

        yield tenant.id


def test_process_listing_with_joinedload(app, n1_data):
    """Process listing leaders/members/owners ile birlikte ≤5 sorguda dönmeli."""
    with app.app_context():
        with count_queries() as counter:
            ps = (
                Process.query
                .filter_by(tenant_id=n1_data, is_active=True)
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
        assert len(ps) == PROCESS_COUNT
        assert_max_queries(5, counter)


def test_process_listing_lazy_DETECTS_N_PLUS_1(app, n1_data):
    """Lazy load'la N+1 OLUŞMALI — eager loading'in gerçekten iş yaptığının kanıtı.

    Bu test 'kötü' davranışı doğrular: relationship default'u lazy kalmalı ki
    yukarıdaki joinedload testi anlamlı olsun. İkisi birlikte koruma sağlar.
    """
    with app.app_context():
        db.session.expire_all()
        with count_queries() as counter:
            ps = Process.query.filter_by(tenant_id=n1_data, is_active=True).all()
            for p in ps:
                _ = list(p.leaders), list(p.members), list(p.owners)
        # 6 süreç × 3 ilişki = 18 ek sorgu (+1 liste sorgusu)
        assert counter.count >= PROCESS_COUNT * 3, (
            f"N+1 beklenirken {counter.count} sorgu görüldü — "
            f"relationship default'u eager'a mı döndü?"
        )


def test_strategy_with_substrategy_selectinload(app, n1_data):
    """Strategy + sub_strategy selectinload ile az sorguda dönmeli."""
    with app.app_context():
        with count_queries() as counter:
            ss = (
                Strategy.query
                .filter_by(tenant_id=n1_data, is_active=True)
                .options(selectinload(Strategy.sub_strategies))
                .all()
            )
            for s in ss:
                _ = list(s.sub_strategies)
        assert len(ss) == STRATEGY_COUNT
        assert_max_queries(5, counter)


def test_kpi_data_aggregate_single_query(app, n1_data):
    """Aggregate sorguları tek SQL'de olmalı (satır sayısından bağımsız)."""
    from sqlalchemy import text
    with app.app_context():
        with count_queries() as counter:
            db.session.execute(text("""
                SELECT kd.year, count(*) FROM kpi_data kd
                JOIN process_kpis k ON kd.process_kpi_id=k.id
                JOIN processes p ON k.process_id=p.id
                WHERE p.tenant_id=:t
                GROUP BY kd.year
            """), {"t": n1_data}).fetchall()
        assert_max_queries(2, counter)
