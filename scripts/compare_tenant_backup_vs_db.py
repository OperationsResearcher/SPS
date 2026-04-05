# -*- coding: utf-8 -*-
"""
Kurum yedeği (.json.gz) ile yerel DB ve isteğe bağlı VM (canlı) DB satır sayılarını karşılaştırır.

VM bağlantısı (gizli tutun, repoya yazmayın):
  set KOKPITIM_VM_DATABASE_URI=postgresql://...
  py scripts/compare_tenant_backup_vs_db.py backups/kurum_16_....json.gz

veya:
  py scripts/compare_tenant_backup_vs_db.py backups/kurum_16_....json.gz --vm-database-uri "postgresql://..."
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import sys
from pathlib import Path

from sqlalchemy import create_engine, inspect, text

# Proje kökü
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _audit_count_sql():
    """Şemada process_kpi_id yok; kpi_data üzerinden tenant filtrelenir."""
    return text(
        "SELECT COUNT(*) FROM kpi_data_audits a "
        "JOIN kpi_data kd ON kd.id = a.kpi_data_id "
        "JOIN process_kpis pk ON pk.id = kd.process_kpi_id "
        "JOIN processes p ON p.id = pk.process_id "
        "WHERE p.tenant_id = :tid"
    )


def fetch_tenant_table_counts(database_uri: str, tenant_id: int, table_plan: list) -> dict[str, int | str]:
    """TABLE_PLAN ile tablo başına COUNT; kpi_data_audits için düzeltilmiş sorgu."""
    engine = create_engine(database_uri, pool_pre_ping=True)
    try:
        insp = inspect(engine)
        existing = set(insp.get_table_names())
        out: dict[str, int | str] = {}
        with engine.connect() as conn:
            for table_name, where_clause in table_plan:
                if table_name not in existing:
                    continue
                try:
                    if table_name == "kpi_data_audits":
                        n = conn.execute(_audit_count_sql(), {"tid": tenant_id}).scalar()
                    else:
                        sql = text(f"SELECT COUNT(*) FROM {table_name} WHERE {where_clause}")  # noqa: S608
                        n = conn.execute(sql, {"tid": tenant_id}).scalar()
                    out[table_name] = int(n)
                except Exception as exc:
                    out[table_name] = f"ERR: {exc!s}"[:180]
        return out
    finally:
        engine.dispose()


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Tenant yedek (.json.gz) vs yerel DB vs VM DB satir sayisi",
    )
    ap.add_argument("backup_gz", type=Path, help=".json.gz yol")
    ap.add_argument("--tenant-id", type=int, default=None, help="DB sorgusu icin tenant id (yoksa yedek meta)")
    ap.add_argument(
        "--vm-database-uri",
        default=None,
        help="VM / canli PostgreSQL URI (alternatif: KOKPITIM_VM_DATABASE_URI)",
    )
    args = ap.parse_args()

    from app import create_app
    from services.tenant_backup_service import TABLE_PLAN

    vm_uri = (args.vm_database_uri or os.environ.get("KOKPITIM_VM_DATABASE_URI") or "").strip()
    if not vm_uri:
        vm_uri = None

    with gzip.open(args.backup_gz, "rt", encoding="utf-8") as f:
        payload = json.load(f)
    meta = payload.get("meta") or {}
    tid = args.tenant_id or int(meta.get("tenant_id") or 0)
    if not tid:
        print("tenant_id bulunamadi; --tenant-id verin.", file=sys.stderr)
        return 1

    backup_counts: dict[str, int] = dict(meta.get("table_counts") or {})
    tables_blob = payload.get("tables") or {}
    for t, rows in tables_blob.items():
        if t not in backup_counts:
            backup_counts[t] = len(rows)
    for t, _ in TABLE_PLAN:
        backup_counts.setdefault(t, len(tables_blob.get(t, [])))

    app = create_app()
    with app.app_context():
        local_uri = app.config.get("SQLALCHEMY_DATABASE_URI") or ""

    if not local_uri:
        print("Yerel SQLALCHEMY_DATABASE_URI bulunamadi.", file=sys.stderr)
        return 1

    local_counts = fetch_tenant_table_counts(local_uri, tid, TABLE_PLAN)
    vm_counts: dict[str, int | str] | None = None
    if vm_uri:
        try:
            vm_counts = fetch_tenant_table_counts(vm_uri, tid, TABLE_PLAN)
        except Exception as exc:
            vm_counts = {"_connection": f"ERR: {exc!s}"[:200]}

    order = [t for t, _ in TABLE_PLAN]
    seen: set[str] = set()
    all_tables: list[str] = []
    for t in order:
        if t in backup_counts or t in local_counts or (vm_counts and t in vm_counts):
            all_tables.append(t)
            seen.add(t)
    for t in sorted(backup_counts.keys()):
        if t not in seen:
            all_tables.append(t)

    print("## Yedek meta (backup file)")
    print(f"- tenant_id: {meta.get('tenant_id')}")
    print(f"- tenant_name: {meta.get('tenant_name')}")
    print(f"- exported_at: {meta.get('exported_at')}")
    print(f"- yedek total_records (meta): {meta.get('total_records')}")
    print()
    print("- yerel DB: uygulama SQLALCHEMY_DATABASE_URI")
    if vm_uri:
        print("- VM DB: KOKPITIM_VM_DATABASE_URI veya --vm-database-uri (parola ciktida gosterilmez)")
    else:
        print("- VM DB: **bagli degil** — VM sutunu icin `KOKPITIM_VM_DATABASE_URI` veya `--vm-database-uri` verin")
    print()
    print("## Karsilastirma tablosu")
    print()
    if vm_counts and "_connection" in vm_counts:
        print(f"| **VM baglanti** | | | **{vm_counts['_connection']}** |")
        print()
        vm_counts = None

    print(
        f"| Tablo | Yedek | Yerel (tenant {tid}) | VM canli | "
        f"Fark VM-Yedek | Fark VM-Yerel |"
    )
    print("| --- | ---: | ---: | ---: | ---: | ---: |")

    sum_b = sum(x for x in backup_counts.values() if isinstance(x, int))
    sum_l = sum(x for x in local_counts.values() if isinstance(x, int))
    sum_v: int | None = None
    if vm_counts:
        sum_v = sum(x for x in vm_counts.values() if isinstance(x, int))

    for t in all_tables:
        b = backup_counts.get(t, "—")
        loc = local_counts.get(t, "—")
        vm = "—"
        if vm_counts is not None:
            vm = vm_counts.get(t, "—")
        f_v_b = "—"
        f_v_l = "—"
        if isinstance(b, int) and isinstance(vm, int):
            f_v_b = vm - b
        if isinstance(loc, int) and isinstance(vm, int):
            f_v_l = vm - loc
        print(f"| `{t}` | {b} | {loc} | {vm} | {f_v_b} | {f_v_l} |")

    print()
    tail_vm = f"**{sum_v}**" if sum_v is not None else "—"
    print(
        f"| **TOPLAM (sayilan tablolar)** | **{sum_b}** | **{sum_l}** | {tail_vm} | "
        f"{(sum_v - sum_b) if sum_v is not None else '—'} | "
        f"{(sum_v - sum_l) if sum_v is not None else '—'} |"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
