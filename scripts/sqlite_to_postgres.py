# -*- coding: utf-8 -*-
"""
SQLite verisini PostgreSQL'e kopyalar.
Önce PostgreSQL'de boş schema oluşturulmuş olmalı (flask db upgrade).
Kullanım:
  set SQLALCHEMY_DATABASE_URI=postgresql://kokpitim_user:kokpitim_dev_123@localhost/kokpitim_db
  python scripts/sqlite_to_postgres.py
"""
import os
import sqlite3
import sys

# Proje kökünü path'e ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sqlite_path = os.path.join(base, "instance", "kokpitim.db")
    pg_uri = os.environ.get("SQLALCHEMY_DATABASE_URI", "")
    if not pg_uri.startswith("postgresql"):
        print("HATA: SQLALCHEMY_DATABASE_URI PostgreSQL URI olmali.")
        print('Ornek: set SQLALCHEMY_DATABASE_URI=postgresql://kokpitim_user:kokpitim_dev_123@localhost/kokpitim_db')
        sys.exit(1)
    if not os.path.isfile(sqlite_path):
        print(f"HATA: SQLite dosyasi bulunamadi: {sqlite_path}")
        sys.exit(1)

    truncate_first = os.environ.get("TRUNCATE_FIRST", "").lower() in ("1", "true", "yes")

    try:
        import psycopg2
        from urllib.parse import urlparse
    except ImportError:
        print("HATA: psycopg2 yok. pip install psycopg2-binary")
        sys.exit(1)

    parsed = urlparse(pg_uri)
    pg_config = {
        "host": parsed.hostname or "localhost",
        "port": parsed.port or 5432,
        "database": parsed.path.lstrip("/").split("?")[0],
        "user": parsed.username,
        "password": parsed.password,
    }

    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row
    pg_conn = psycopg2.connect(**pg_config)
    pg_conn.autocommit = False

    # Tablolari al - FK sirasina gore: once parent, sonra child
    cur = sqlite_conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    )
    all_tables = [r[0] for r in cur.fetchall()]
    fk_order = [
        "roles", "subscription_packages", "system_components", "system_modules",
        "module_components", "package_modules", "tenants", "users",
        "project", "task",  # proje modulu (kurum_id=tenant_id)
        "strategies", "sub_strategies", "processes", "process_leaders", "process_members",
        "process_owners_table", "process_sub_strategy_links", "process_sub_strategies",
        "process_kpis", "kpi_data", "process_activities",
        "individual_performance_indicators", "individual_activities", "individual_kpi_data",
    ]
    ordered = [t for t in fk_order if t in all_tables]
    rest = [t for t in all_tables if t not in ordered]
    tables = ordered + sorted(rest)
    if "alembic_version" in tables:
        tables = ["alembic_version"] + [t for t in tables if t != "alembic_version"]

    pg_cur = pg_conn.cursor()

    if truncate_first:
        pg_cur.execute(
            """SELECT tablename FROM pg_tables WHERE schemaname='public' AND tablename != 'alembic_version'"""
        )
        for (t,) in pg_cur.fetchall():
            try:
                pg_cur.execute(f'TRUNCATE TABLE "{t}" CASCADE')
                print(f"  Truncate: {t}")
            except Exception as e:
                print(f"  UYARI truncate {t}: {e}")
        pg_conn.commit()
        pg_cur = pg_conn.cursor()

    # FK/trigger gecici kapat (superuser gerektirir; yoksa insert sirasiyla devam)
    try:
        pg_cur.execute("SET session_replication_role = 'replica'")
        use_replica = True
    except Exception:
        use_replica = False
        print("UYARI: session_replication_role yetkisi yok, FK sirasiyla insert yapilacak.")

    # SQLite -> PG tablo adi eslemesi (schema farkliliklari)
    TABLE_MAP = {"process_sub_strategies": "process_sub_strategy_links"}

    def get_pg_cols(cursor, table_name):
        """PostgreSQL tablosundaki kolon isimlerini dondur."""
        cursor.execute(
            """SELECT column_name FROM information_schema.columns
               WHERE table_name = %s AND table_schema = 'public'
               ORDER BY ordinal_position""",
            (table_name,),
        )
        return [r[0] for r in cursor.fetchall()]

    def get_pg_bool_cols(cursor, table_name):
        """PostgreSQL'de boolean kolonlari dondur."""
        cursor.execute(
            """SELECT a.attname FROM pg_attribute a
               JOIN pg_class c ON a.attrelid = c.oid
               JOIN pg_type t ON a.atttypid = t.oid
               WHERE c.relname = %s AND a.attnum > 0 AND NOT a.attisdropped
               AND t.typname = 'bool'""",
            (table_name,),
        )
        return {r[0] for r in cursor.fetchall()}

    def get_pg_col_types(cursor, table_name):
        """PG kolon tipi: integer/str icin (bos string -> None, varchar uzunluk)."""
        cursor.execute(
            """SELECT column_name, data_type, character_maximum_length
               FROM information_schema.columns
               WHERE table_name = %s AND table_schema = 'public'""",
            (table_name,),
        )
        return {r[0]: (r[1], r[2]) for r in cursor.fetchall()}

    def sanitize_value(v, col_name, col_types, bool_cols):
        """Bos string->None (int icin), bool donusumu, varchar truncate."""
        if col_name in bool_cols and v is not None and isinstance(v, int):
            return bool(v)
        if v == "" or v == b"":
            if col_name in col_types:
                dt = col_types[col_name][0]
                if dt in ("integer", "bigint", "smallint", "numeric", "real", "double precision"):
                    return None
        if isinstance(v, str) and col_name in col_types:
            max_len = col_types[col_name][1]
            if max_len and len(v) > max_len:
                return v[:max_len]
        return v

    total_rows = 0
    for table in tables:
        pg_table = TABLE_MAP.get(table, table)
        try:
            pg_cur.execute(
                "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)",
                (pg_table,),
            )
            if not pg_cur.fetchone()[0]:
                continue  # Tablo PG'de yok, atla
            cur = sqlite_conn.execute(f"SELECT * FROM [{table}]")
            rows = cur.fetchall()
            if not rows:
                continue
            sqlite_cols = [d[0] for d in cur.description]
            pg_cols = get_pg_cols(pg_cur, pg_table)
            cols = [c for c in sqlite_cols if c in pg_cols]
            if not cols:
                continue
            bool_cols = get_pg_bool_cols(pg_cur, pg_table)
            col_types = get_pg_col_types(pg_cur, pg_table)
            col_indices = [sqlite_cols.index(c) for c in cols]
            cols_str = ", ".join(f'"{c}"' for c in cols)
            placeholders = ", ".join("%s" for _ in cols)
            insert_sql = f'INSERT INTO "{pg_table}" ({cols_str}) VALUES ({placeholders})'
            inserted = 0
            for row in rows:
                vals = []
                for idx, c in zip(col_indices, cols):
                    v = sanitize_value(row[idx], c, col_types, bool_cols)
                    vals.append(v)
                try:
                    pg_cur.execute(insert_sql, vals)
                    pg_conn.commit()
                    inserted += 1
                except Exception as e:
                    pg_conn.rollback()
                    print(f"  UYARI: {table} satir atlandi: {str(e)[:80]}...")
            pg_cur = pg_conn.cursor()
            total_rows += inserted
            if inserted > 0:
                print(f"  {table}: {inserted}/{len(rows)} satir")
        except Exception as e:
            print(f"  HATA {table}: {e}")
            pg_conn.rollback()
            pg_cur = pg_conn.cursor()

    if use_replica:
        try:
            pg_cur.execute("SET session_replication_role = 'DEFAULT'")
        except Exception:
            pass
    pg_conn.commit()
    sqlite_conn.close()
    pg_conn.close()
    print(f"\nToplam {total_rows} satir kopyalandi.")

if __name__ == "__main__":
    main()
