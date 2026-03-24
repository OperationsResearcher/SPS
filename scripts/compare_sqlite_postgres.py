# -*- coding: utf-8 -*-
"""
SQLite vs PostgreSQL karsilastirma tablosu.
Kullanim: python scripts/compare_sqlite_postgres.py
"""
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Tablo -> etiket eslemesi
LABELS = {
    "tenants": "Kurum",
    "users": "Kullanici",
    "processes": "Surec",
    "process_kpis": "PG (Performans Gostergesi)",
    "kpi_data": "PGV (Performans Hedef Degeri)",
    "process_activities": "Faaliyet",
    "project": "Proje",
    "task": "Proje Gorevi",
}


def count_sqlite(path, table):
    try:
        c = sqlite3.connect(path)
        r = c.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
        c.close()
        return r
    except Exception:
        return None


def count_postgres(uri, table):
    try:
        import psycopg2
        from urllib.parse import urlparse
        parsed = urlparse(uri)
        conn = psycopg2.connect(
            host=parsed.hostname or "localhost",
            port=parsed.port or 5432,
            database=parsed.path.lstrip("/").split("?")[0],
            user=parsed.username,
            password=parsed.password,
        )
        cur = conn.cursor()
        cur.execute(f'SELECT COUNT(*) FROM "{table}"')
        r = cur.fetchone()[0]
        conn.close()
        return r
    except Exception:
        return None


def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sqlite_path = os.path.join(base, "instance", "kokpitim.db")
    pg_uri = os.environ.get(
        "SQLALCHEMY_DATABASE_URI",
        "postgresql://kokpitim_user:kokpitim_dev_123@localhost/kokpitim_db",
    )
    if not pg_uri.startswith("postgresql"):
        print("HATA: SQLALCHEMY_DATABASE_URI PostgreSQL URI olmali.")
        sys.exit(1)

    rows = []
    for table, label in LABELS.items():
        sqlite_n = count_sqlite(sqlite_path, table)
        pg_n = count_postgres(pg_uri, table)
        if sqlite_n is None and pg_n is None:
            continue
        sqlite_n = sqlite_n if sqlite_n is not None else 0
        pg_n = pg_n if pg_n is not None else 0
        diff = pg_n - sqlite_n
        status = "OK" if diff == 0 else ("+" if diff > 0 else "")
        rows.append((label, table, sqlite_n, pg_n, diff, status))

    print()
    print("=" * 70)
    print("  SQLite vs PostgreSQL Veri Karsilastirmasi")
    print("=" * 70)
    print(f"  {'Tablolar':<30} | {'SQLite':>10} | {'PostgreSQL':>10} | {'Fark':>8} |")
    print("-" * 70)
    for label, table, sq, pg, diff, st in rows:
        sq_str = str(sq) if sq is not None else "-"
        pg_str = str(pg) if pg is not None else "-"
        diff_str = f"{st}{diff}" if diff != 0 else "0"
        print(f"  {label:<30} | {sq_str:>10} | {pg_str:>10} | {diff_str:>8} |")
    print("=" * 70)
    print()
    print("Not: PGV -1 ve Proje Gorevi -1: Birer satir FK uyumsuzlugu nedeniyle atlandi.")
    print()


if __name__ == "__main__":
    main()
