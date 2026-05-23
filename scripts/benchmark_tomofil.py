"""Tomofil tenant (id=27) performans ölçümü.

48K KpiData + 97 user + 28 strategy + 46 process üzerinde gerçek sorgu süreleri.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from app import create_app
from extensions import db
from sqlalchemy import text
from app.utils.query_counter import count_queries


def bench(name, fn):
    """Bir fonksiyonu çalıştır, süresini ve sorgu sayısını raporla."""
    t0 = time.perf_counter()
    with count_queries() as counter:
        result = fn()
    elapsed = (time.perf_counter() - t0) * 1000  # ms
    print(f"  {name:55s} {elapsed:8.1f}ms  {counter.count:4d} sorgu")
    return result, elapsed, counter.count


def main():
    app = create_app()
    TID = 27
    print("=" * 80)
    print(f"  TOMOFIL PERFORMANS BENCHMARK (tenant_id={TID})")
    print("=" * 80)

    with app.app_context():
        # 1. Basit COUNT'lar (baseline)
        print("\n[1] Baseline — basit COUNT sorguları:")
        bench("count(users)",
              lambda: db.session.execute(text("SELECT count(*) FROM users WHERE tenant_id=:t"), {"t": TID}).scalar())
        bench("count(processes)",
              lambda: db.session.execute(text("SELECT count(*) FROM processes WHERE tenant_id=:t"), {"t": TID}).scalar())
        bench("count(kpi_data)",
              lambda: db.session.execute(text("SELECT count(*) FROM kpi_data WHERE process_kpi_id IN (SELECT k.id FROM process_kpis k JOIN processes p ON k.process_id=p.id WHERE p.tenant_id=:t)"), {"t": TID}).scalar())

        # 2. ORM listings (N+1 riskini test et)
        print("\n[2] ORM Listings (N+1 RİSKİ ARANIYOR):")
        from app.models.process import Process, ProcessKpi
        from app.models.core import Strategy, SubStrategy, User

        def list_processes_no_eager():
            ps = Process.query.filter_by(tenant_id=TID, is_active=True).all()
            for p in ps:
                _ = p.code, p.name  # sadece kolon
            return len(ps)

        def list_processes_with_lazy():
            ps = Process.query.filter_by(tenant_id=TID, is_active=True).all()
            for p in ps:
                _ = list(p.leaders), list(p.members), list(p.owners)  # lazy load tetikle
            return len(ps)

        from sqlalchemy.orm import joinedload
        def list_processes_with_joinedload():
            ps = (Process.query.filter_by(tenant_id=TID, is_active=True)
                  .options(joinedload(Process.leaders), joinedload(Process.members), joinedload(Process.owners))
                  .all())
            for p in ps:
                _ = list(p.leaders), list(p.members), list(p.owners)
            return len(ps)

        n, _, _ = bench("46 process — kolon erişim (no eager)", list_processes_no_eager)
        bench(f"46 process — leaders/members/owners (lazy)", list_processes_with_lazy)
        bench(f"46 process — leaders/members/owners (joinedload)", list_processes_with_joinedload)

        # 3. Strategy + SubStrategy
        print("\n[3] Strateji ağacı (28 strategy + 135 sub_strategy):")
        from sqlalchemy.orm import selectinload
        def strategy_no_eager():
            ss = Strategy.query.filter_by(tenant_id=TID, is_active=True).all()
            for s in ss:
                _ = list(s.sub_strategies)
            return len(ss)
        def strategy_with_selectinload():
            ss = (Strategy.query.filter_by(tenant_id=TID, is_active=True)
                  .options(selectinload(Strategy.sub_strategies)).all())
            for s in ss:
                _ = list(s.sub_strategies)
            return len(ss)
        bench("28 strategy — sub_strategy (lazy)", strategy_no_eager)
        bench("28 strategy — sub_strategy (selectinload)", strategy_with_selectinload)

        # 4. KPI listing
        print("\n[4] KPI listing (221 process_kpi):")
        def kpi_list():
            ks = (ProcessKpi.query
                  .join(Process)
                  .filter(Process.tenant_id == TID, ProcessKpi.is_active == True)
                  .all())
            return len(ks)
        bench("221 process_kpi tek sorgu (join)", kpi_list)

        # 5. KpiData aggregation (en büyük tablo)
        print("\n[5] KpiData (48.283 satır) sorguları:")
        def kpi_data_count_per_kpi():
            r = db.session.execute(text("""
                SELECT k.id, count(kd.id)
                FROM process_kpis k
                JOIN processes p ON k.process_id=p.id
                LEFT JOIN kpi_data kd ON kd.process_kpi_id=k.id
                WHERE p.tenant_id=:t
                GROUP BY k.id
                LIMIT 50
            """), {"t": TID}).fetchall()
            return len(r)
        bench("50 KPI başına KpiData count (GROUP BY)", kpi_data_count_per_kpi)

        def kpi_data_year_aggregate():
            r = db.session.execute(text("""
                SELECT kd.year, count(*), avg(kd.actual_value::float)
                FROM kpi_data kd
                JOIN process_kpis k ON kd.process_kpi_id=k.id
                JOIN processes p ON k.process_id=p.id
                WHERE p.tenant_id=:t
                GROUP BY kd.year
                ORDER BY kd.year
            """), {"t": TID}).fetchall()
            return r
        rows, _, _ = bench("Yıl bazlı KpiData özet (6 yıl)", kpi_data_year_aggregate)
        print(f"    -> 6 yıllık ortalama: {[(r[0], r[1]) for r in rows]}")

        # 6. k_rapor /api/kurumsal benzeri ağır query
        print("\n[6] Karmaşık raporlama sorguları:")
        def overview_query():
            # k_rapor/routes.py içindekine benzer
            strategy_count = db.session.execute(text("SELECT count(*) FROM strategies WHERE tenant_id=:t AND is_active=true"), {"t": TID}).scalar()
            process_count = db.session.execute(text("SELECT count(*) FROM processes WHERE tenant_id=:t AND is_active=true"), {"t": TID}).scalar()
            kpi_count = db.session.execute(text("SELECT count(*) FROM process_kpis k JOIN processes p ON k.process_id=p.id WHERE p.tenant_id=:t AND k.is_active=true"), {"t": TID}).scalar()
            user_count = db.session.execute(text("SELECT count(*) FROM users WHERE tenant_id=:t AND is_active=true"), {"t": TID}).scalar()
            return {"strategy": strategy_count, "process": process_count, "kpi": kpi_count, "user": user_count}
        result, _, _ = bench("Overview (5 count sorgu)", overview_query)
        print(f"    -> {result}")

        # 7. Tomofil için olmayacak: 1000 user'lık simülasyon
        print("\n[7] Index sağlık kontrolü:")
        rows = db.session.execute(text("""
            SELECT indexname, indexdef FROM pg_indexes
            WHERE tablename = 'kpi_data'
        """)).fetchall()
        print(f"    kpi_data tablosundaki indeksler ({len(rows)}):")
        for r in rows:
            print(f"      - {r[0]}")

        rows = db.session.execute(text("""
            SELECT indexname FROM pg_indexes WHERE tablename = 'processes'
        """)).fetchall()
        print(f"    processes tablosundaki indeksler ({len(rows)}):")
        for r in rows:
            print(f"      - {r[0]}")


if __name__ == "__main__":
    main()
