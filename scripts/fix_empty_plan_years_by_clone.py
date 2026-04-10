#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PlanYear var ama ana SP verisi olmayan yılları otomatik backfill eder.

Mantık:
- Hedef yıl: strategies=0 VE processes=0 olan PlanYear.
- Kaynak yıl: aynı tenant'ta hedef yıldan küçük ve strategies>0 olan en yakın yıl.
- Geçici bir yıla clone_full_plan_year() ile tam klon yapılır.
- Klondan çıkan ana tabloların plan_year_id değeri hedef PlanYear id'sine taşınır.
- Geçici PlanYear silinir.

Önce dry-run önerilir:
  py scripts/fix_empty_plan_years_by_clone.py --dry-run
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone

from sqlalchemy import inspect, text

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import create_app  # noqa: E402
from extensions import db  # noqa: E402
from app.models.core import Tenant, Strategy  # noqa: E402
from app.models.process import Process  # noqa: E402
from app.models.plan_year import PlanYear  # noqa: E402
from app.services.plan_year_service import clone_full_plan_year  # noqa: E402


MOVE_TABLES = [
    "strategies",
    "sub_strategies",
    "processes",
    "process_kpis",
    "process_activities",
    "individual_performance_indicators",
    "plan_projects",
    "plan_project_tasks",
    "plan_project_activities",
    "swot_analyses",
    "tows_analyses",
    "pestel_analyses",
    "porter_five_forces_analyses",
    "tenant_year_identities",
]

ONE_PER_YEAR_TABLES = {
    "swot_analyses",
    "tows_analyses",
    "pestel_analyses",
    "porter_five_forces_analyses",
    "tenant_year_identities",
}


def _count_for_plan_year(table: str, py_id: int) -> int:
    sql = text(f"SELECT COUNT(*) FROM {table} WHERE plan_year_id = :pid")  # noqa: S608
    return int(db.session.execute(sql, {"pid": py_id}).scalar() or 0)


def _move_rows(table: str, src_py_id: int, dst_py_id: int) -> tuple[int, str]:
    src_count = _count_for_plan_year(table, src_py_id)
    if src_count == 0:
        return 0, "skip-src-empty"

    dst_count = _count_for_plan_year(table, dst_py_id)
    if dst_count > 0 and table in ONE_PER_YEAR_TABLES:
        # Hedefte zaten tekil kayıt varsa klondan gelen tekili at.
        del_sql = text(f"DELETE FROM {table} WHERE plan_year_id = :pid")  # noqa: S608
        db.session.execute(del_sql, {"pid": src_py_id})
        return src_count, "drop-src-duplicate-singleton"

    upd_sql = text(f"UPDATE {table} SET plan_year_id = :dst WHERE plan_year_id = :src")  # noqa: S608
    db.session.execute(upd_sql, {"dst": dst_py_id, "src": src_py_id})
    return src_count, "moved"


def _pick_source_plan_year(tenant_id: int, target_year: int) -> PlanYear | None:
    candidate = (
        db.session.query(PlanYear)
        .filter(PlanYear.tenant_id == tenant_id, PlanYear.year < target_year)
        .order_by(PlanYear.year.desc())
        .all()
    )
    for py in candidate:
        s_cnt = (
            db.session.query(Strategy)
            .filter(Strategy.tenant_id == tenant_id, Strategy.plan_year_id == py.id, Strategy.is_active.is_(True))
            .count()
        )
        if s_cnt > 0:
            return py
    return None


def _is_target_empty(tenant_id: int, py_id: int) -> bool:
    s_cnt = (
        db.session.query(Strategy)
        .filter(Strategy.tenant_id == tenant_id, Strategy.plan_year_id == py_id, Strategy.is_active.is_(True))
        .count()
    )
    p_cnt = (
        db.session.query(Process)
        .filter(Process.tenant_id == tenant_id, Process.plan_year_id == py_id, Process.is_active.is_(True))
        .count()
    )
    return s_cnt == 0 and p_cnt == 0


def _tmp_year_for(tenant_id: int, target_year: int) -> int:
    # PlanYear.year için üst sınır constraint yok; tenant içinde unique olmalı.
    return 900000 + tenant_id * 100 + (target_year % 100)


def run(dry_run: bool, tenant_id: int | None) -> int:
    insp = inspect(db.session.connection())
    existing_tables = set(insp.get_table_names())
    move_tables = [t for t in MOVE_TABLES if t in existing_tables]

    q = db.session.query(Tenant).filter(Tenant.is_active.is_(True))
    if tenant_id:
        q = q.filter(Tenant.id == tenant_id)
    tenants = q.order_by(Tenant.id).all()

    print(f"{'[DRY-RUN] ' if dry_run else ''}Tenant sayısı: {len(tenants)}")
    total_fixed = 0

    for t in tenants:
        years = (
            db.session.query(PlanYear)
            .filter(PlanYear.tenant_id == t.id)
            .order_by(PlanYear.year.asc())
            .all()
        )
        for py in years:
            if not _is_target_empty(t.id, py.id):
                continue

            src = _pick_source_plan_year(t.id, py.year)
            if not src:
                print(f"- tenant={t.id} {t.name} year={py.year}: kaynak yıl yok, atlandı")
                continue

            print(f"- tenant={t.id} {t.name} year={py.year}: kaynak={src.year} (id={src.id})")
            if dry_run:
                continue

            tmp_year = _tmp_year_for(t.id, py.year)
            exists_tmp = db.session.query(PlanYear).filter_by(tenant_id=t.id, year=tmp_year).first()
            if exists_tmp:
                raise RuntimeError(f"Geçici yıl çakıştı tenant={t.id} tmp_year={tmp_year}")

            tmp_name = f"TMP backfill {py.year} {datetime.now(timezone.utc).isoformat()}"
            cloned = clone_full_plan_year(src, tmp_year, name=tmp_name)

            moved_summary = {}
            for table in move_tables:
                moved, mode = _move_rows(table, cloned.id, py.id)
                if moved:
                    moved_summary[table] = f"{moved} ({mode})"

            # Geçici plan year'i ORM ile silmek, bazı ortamlarda olmayan tablo ilişkilerine
            # takılabiliyor. Bu yüzden doğrudan SQL delete kullan.
            db.session.execute(text("DELETE FROM plan_years WHERE id = :pid"), {"pid": cloned.id})
            db.session.commit()
            total_fixed += 1
            print(f"  fixed year={py.year} moved={moved_summary}")

    print(f"Tamamlandı. Düzeltilen yıl sayısı: {total_fixed}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Empty PlanYear SP data backfill by clone")
    ap.add_argument("--dry-run", action="store_true", help="Yazma yapmadan raporla")
    ap.add_argument("--tenant-id", type=int, default=None, help="Sadece bu tenant")
    args = ap.parse_args()

    app = create_app()
    with app.app_context():
        return run(args.dry_run, args.tenant_id)


if __name__ == "__main__":
    raise SystemExit(main())

