#!/usr/bin/env python3
"""Yerel DB vs dump/VM satir sayilari karsilastirma."""
from __future__ import annotations

import os
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TABLES = ("tenants", "users", "kpi_data", "processes", "project", "task")


def counts_sqlite(path: Path) -> dict[str, int | str]:
    out: dict[str, int | str] = {}
    if not path.is_file():
        return {t: "YOK" for t in TABLES}
    con = sqlite3.connect(str(path))
    cur = con.cursor()
    for t in TABLES:
        try:
            cur.execute(f"SELECT count(*) FROM [{t}]" if t == "project" else f"SELECT count(*) FROM {t}")
            out[t] = cur.fetchone()[0]
        except sqlite3.Error as e:
            out[t] = f"hata:{e}"
    con.close()
    return out


def counts_pg(uri: str) -> dict[str, int | str]:
    try:
        from sqlalchemy import create_engine, text
    except ImportError:
        return {t: "sqlalchemy_yok" for t in TABLES}
    out: dict[str, int | str] = {}
    eng = create_engine(uri)
    with eng.connect() as conn:
        for t in TABLES:
            try:
                n = conn.execute(text(f"SELECT count(*) FROM {t}")).scalar()
                out[t] = int(n)
            except Exception as e:
                out[t] = f"hata:{e}"
    return out


def main() -> int:
    rows: list[tuple[str, dict]] = []

    dump_note = ROOT / "backups" / "oracle_migration" / "MANIFEST.txt"
    rows.append(("VM dump (manifest 19 May)", {
        "tenants": 18, "users": 78, "kpi_data": 6133,
        "processes": 63, "project": 7, "task": "?",
    }))

    ora = counts_pg(
        "postgresql+psycopg2://kokpitim_user:MfGMfG__46604660@129.159.30.175:5432/kokpitim_db"
    )
    rows.append(("Oracle canli (PG)", ora))

    for label, p in [
        ("Yerel instance/kokpitim.db", ROOT / "instance" / "kokpitim.db"),
        ("Yerel backups/oracle_migration/instance", ROOT / "backups" / "oracle_migration" / "instance" / "kokpitim.db"),
    ]:
        if p.is_file():
            rows.append((label, counts_sqlite(p)))

    local_env = ROOT / ".env"
    if local_env.is_file():
        for line in local_env.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.strip().startswith("SQLALCHEMY_DATABASE_URI="):
                uri = line.split("=", 1)[1].strip()
                if "postgresql" in uri:
                    rows.append(("Yerel .env PostgreSQL", counts_pg(uri)))
                break

    print(f"{'Kaynak':<42} " + " ".join(f"{t:>10}" for t in TABLES))
    print("-" * 110)
    for label, d in rows:
        vals = []
        for t in TABLES:
            v = d.get(t, "-")
            vals.append(f"{str(v):>10}")
        print(f"{label:<42} " + " ".join(vals))

    # Ozet
    vm = rows[0][1]
    local = next((d for l, d in rows if "instance/kokpitim" in l), None)
    ora_d = next((d for l, d in rows if "Oracle" in l), None)
    if local and ora_d:
        diff = [t for t in TABLES if isinstance(local.get(t), int) and isinstance(ora_d.get(t), int) and local[t] != ora_d[t]]
        if diff:
            print("\nYerel SQLite vs Oracle farkli tablolar:", ", ".join(diff))
        else:
            print("\nYerel SQLite ile Oracle sayilari eslesiyor (karsilastirilan tablolar).")
    print("\nNot: VM (Oracle PG) = gcp2oracle migration dump ile ayni olmali (18/78/6133).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
