# -*- coding: utf-8 -*-
"""Schema unify pre/post count report.

Kullanım:
  python scripts/schema_unify_report.py --snapshot pre
  python scripts/schema_unify_report.py --snapshot post --compare "instance/schema_unify_pre.json"
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from sqlalchemy import text
from sqlalchemy import inspect
from app import create_app
from app.models import db

TABLES = [
    ("tenants", "Kurum"),
    ("users", "Kullanıcı"),
    ("roles", "Rol"),
    ("processes", "Süreç"),
    ("process_kpis", "Süreç KPI"),
    ("kpi_data", "KPI Veri"),
    ("individual_performance_indicators", "Bireysel KPI"),
    ("individual_activities", "Bireysel Faaliyet"),
    ("individual_kpi_data", "Bireysel KPI Veri"),
    ("project", "Proje"),
    ("task", "Görev"),
]


def _table_exists(name: str) -> bool:
    engine_name = db.engine.dialect.name
    if engine_name == "sqlite":
        insp = inspect(db.engine)
        return name in insp.get_table_names()
    return bool(
        db.session.execute(
            text(
                "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
                "WHERE table_schema='public' AND table_name=:t)"
            ),
            {"t": name},
        ).scalar()
    )


def _count(name: str) -> int | None:
    if not _table_exists(name):
        return None
    return int(db.session.execute(text(f'SELECT COUNT(*) FROM "{name}"')).scalar() or 0)


def collect() -> dict:
    data = {}
    for tbl, label in TABLES:
        data[tbl] = {"label": label, "count": _count(tbl)}
    return data


def print_report(title: str, data: dict) -> None:
    print(f"\n{title}")
    print("=" * 72)
    for tbl, item in data.items():
        count = item["count"]
        count_text = "-" if count is None else str(count)
        print(f"{item['label']:28} ({tbl:35}) : {count_text}")


def compare(pre: dict, post: dict) -> None:
    print("\nFARK RAPORU (post - pre)")
    print("=" * 72)
    for tbl, item in post.items():
        p = pre.get(tbl, {}).get("count")
        q = item.get("count")
        if p is None or q is None:
            delta_text = "n/a"
        else:
            delta = q - p
            delta_text = f"{delta:+d}"
        print(f"{item['label']:28} ({tbl:35}) : {delta_text}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Schema unify pre/post report")
    parser.add_argument("--snapshot", default="pre", choices=["pre", "post"], help="Snapshot adı")
    parser.add_argument("--compare", default="", help="Karşılaştırılacak eski snapshot JSON yolu")
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        print(f"DB dialect: {db.engine.dialect.name}")
        if db.engine.dialect.name == "sqlite":
            print("UYARI: SQLite bağlı görünüyor. PostgreSQL karşılaştırması için SQLALCHEMY_DATABASE_URI ayarlayın.")
        data = collect()

    out_dir = os.path.join(ROOT, "instance")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, f"schema_unify_{args.snapshot}.json")

    payload = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "snapshot": args.snapshot,
        "tables": data,
    }
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print_report(f"SNAPSHOT: {args.snapshot}", data)
    print(f"\nJSON yazıldı: {out_file}")

    if args.compare:
        with open(args.compare, "r", encoding="utf-8") as f:
            other = json.load(f)
        compare(other.get("tables", {}), data)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
