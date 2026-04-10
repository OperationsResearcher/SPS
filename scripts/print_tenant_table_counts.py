# -*- coding: utf-8 -*-
"""Konteyner veya yerelde: bir tenant için TABLE_PLAN satır sayılarını JSON yazdırır.

Örnek (VM):
  sudo docker exec sps-web bash -lc 'cd /app && python3 scripts/print_tenant_table_counts.py 16'
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_fp = Path(__file__).resolve()
ROOT = _fp.parents[1] if _fp.parent.name == "scripts" else Path("/app")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlalchemy import inspect, text  # noqa: E402

from app import create_app  # noqa: E402
from extensions import db  # noqa: E402
from services.tenant_backup_service import TABLE_PLAN  # noqa: E402


def _audit_count_sql():
    return text(
        "SELECT COUNT(*) FROM kpi_data_audits a "
        "JOIN kpi_data kd ON kd.id = a.kpi_data_id "
        "JOIN process_kpis pk ON pk.id = kd.process_kpi_id "
        "JOIN processes p ON p.id = pk.process_id "
        "WHERE p.tenant_id = :tid"
    )


def main() -> int:
    if len(sys.argv) < 2:
        print("Kullanim: print_tenant_table_counts.py <tenant_id>", file=sys.stderr)
        return 1
    tid = int(sys.argv[1])
    app = create_app()
    meta = {"tenant_id": tid}
    with app.app_context():
        row = db.session.execute(
            text("SELECT id, name, short_name FROM tenants WHERE id = :tid"),
            {"tid": tid},
        ).mappings().first()
        if row:
            meta["tenant_name"] = row.get("name")
            meta["short_name"] = row.get("short_name")
        conn = db.session.connection()
        insp = inspect(conn)
        existing = set(insp.get_table_names())
        counts: dict[str, int | str] = {}
        for table_name, where_clause in TABLE_PLAN:
            if table_name not in existing:
                continue
            try:
                if table_name == "kpi_data_audits":
                    n = conn.execute(_audit_count_sql(), {"tid": tid}).scalar()
                else:
                    sql = text(f"SELECT COUNT(*) FROM {table_name} WHERE {where_clause}")  # noqa: S608
                    n = conn.execute(sql, {"tid": tid}).scalar()
                counts[table_name] = int(n)
            except Exception as exc:
                db.session.rollback()
                counts[table_name] = f"ERR: {exc!s}"[:120]
        meta["table_counts"] = counts
        meta["total_records"] = sum(
            v for v in counts.values() if isinstance(v, int)
        )
    print(json.dumps(meta, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
