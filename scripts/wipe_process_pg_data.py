#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bir süreçteki aktif PG (ProcessKpi) ve bağlı KpiData kayıtlarını pasifleştirir
(kmf_s11_import --wipe-kpis ile aynı mantık: is_active=False).

Örnek (Boğaziçi s11 import süreci):
  py scripts/wipe_process_pg_data.py --process-id 18
  py scripts/wipe_process_pg_data.py --process-id 18 --dry-run

Birden fazla süreç:
  py scripts/wipe_process_pg_data.py --process-id 18 --process-id 1
"""
from __future__ import annotations

import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("FLASK_ENV", "development")
if not os.environ.get("SECRET_KEY"):
    os.environ["SECRET_KEY"] = "dev-only-script"

from app import create_app
from app.models import db
from app.models.process import Process, ProcessKpi, KpiData, FavoriteKpi


def main() -> int:
    ap = argparse.ArgumentParser(description="Süreç PG + KpiData pasifleştirme")
    ap.add_argument(
        "--process-id",
        type=int,
        action="append",
        dest="process_ids",
        required=True,
        help="Süreç id (birden fazla için tekrarlayın)",
    )
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    ids = sorted(set(args.process_ids))

    app = create_app()
    with app.app_context():
        for pid in ids:
            proc = Process.query.filter_by(id=pid, is_active=True).first()
            if not proc:
                print(f"[{pid}] Süreç yok veya pasif — atlandı.", file=sys.stderr)
                continue
            print(f"[{pid}] {proc.code!r} {proc.name!r} tenant_id={proc.tenant_id}")

            kpis = ProcessKpi.query.filter_by(process_id=pid, is_active=True).all()
            kpi_ids = [k.id for k in kpis]
            print(f"  Aktif PG: {len(kpis)}")

            kdata_q = (
                KpiData.query.join(ProcessKpi)
                .filter(ProcessKpi.process_id == pid, KpiData.is_active.is_(True))
            )
            nd = kdata_q.count()
            print(f"  Aktif KpiData: {nd}")

            fav = FavoriteKpi.query.filter(
                FavoriteKpi.process_kpi_id.in_(kpi_ids),
                FavoriteKpi.is_active.is_(True),
            ).count()
            print(f"  Aktif FavoriteKpi: {fav}")

            if args.dry_run:
                continue

            for k in kpis:
                k.is_active = False
            for kd in kdata_q.all():
                kd.is_active = False
            for f in FavoriteKpi.query.filter(
                FavoriteKpi.process_kpi_id.in_(kpi_ids),
                FavoriteKpi.is_active.is_(True),
            ).all():
                f.is_active = False

            db.session.commit()
            print(f"  → Pasifleştirildi.")

    if args.dry_run:
        print("(dry-run: commit yok)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
