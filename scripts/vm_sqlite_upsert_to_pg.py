# -*- coding: utf-8 -*-
"""
VM SQLite -> Yerel PostgreSQL UPSERT migrasyonu.

Strateji:
  - VM'de olan kayit → PostgreSQL'e INSERT veya UPDATE (VM kazanir)
  - Sadece lokalde olan kayit → dokunulmaz (korunur)
  - Sadece lokalde olan tablo (yeni modeller) → dokunulmaz

Kullanim:
  set SQLITE_PATH=backups/vm_pull/20260402_070416_vm_kokpitim_FRESH.db
  set SQLALCHEMY_DATABASE_URI=postgresql://kokpitim_user:kokpitim_dev_123@localhost/kokpitim_db
  python scripts/vm_sqlite_upsert_to_pg.py
"""
import os
import sys
import sqlite3
import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import psycopg2
    from urllib.parse import urlparse
except ImportError:
    print("HATA: psycopg2 yok. pip install psycopg2-binary")
    sys.exit(1)

# ---------------------------------------------------------------------------
# SQLite tablo adi → PostgreSQL tablo adi eslemesi
# ---------------------------------------------------------------------------
TABLE_MAP = {
    "process_sub_strategies": "process_sub_strategy_links",
}

# Onceden islenmesi gereken tablolar (FK sirasi: parent once)
FK_ORDER = [
    "roles", "subscription_packages", "system_modules", "system_components",
    "package_modules", "tenants", "users",
    "strategies", "sub_strategies",
    "processes", "process_leaders", "process_members",
    "process_owners_table", "process_sub_strategy_links", "process_sub_strategies",
    "process_kpis", "kpi_data", "kpi_data_audits",
    "process_activities", "process_activity_assignees", "process_activity_reminders",
    "individual_performance_indicators", "individual_activities", "individual_kpi_data",
    "project", "project_leaders", "project_members", "project_observers",
    "project_related_processes", "task",
    "audit_logs", "notifications",
]

# alembic_version tablosunu ASLA degistirme (yerel migration state korunmali)
SKIP_TABLES = {"alembic_version"}


def get_pg_pk_cols(pg_cur, table_name):
    """PostgreSQL tablosunun PK kolonlarini dondur."""
    pg_cur.execute(
        """
        SELECT kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
          AND tc.table_schema = kcu.table_schema
        WHERE tc.constraint_type = 'PRIMARY KEY'
          AND tc.table_name = %s
          AND tc.table_schema = 'public'
        ORDER BY kcu.ordinal_position
        """,
        (table_name,),
    )
    return [r[0] for r in pg_cur.fetchall()]


def get_pg_cols(pg_cur, table_name):
    pg_cur.execute(
        """SELECT column_name FROM information_schema.columns
           WHERE table_name = %s AND table_schema = 'public'
           ORDER BY ordinal_position""",
        (table_name,),
    )
    return [r[0] for r in pg_cur.fetchall()]


def get_pg_bool_cols(pg_cur, table_name):
    pg_cur.execute(
        """SELECT a.attname FROM pg_attribute a
           JOIN pg_class c ON a.attrelid = c.oid
           JOIN pg_type t ON a.atttypid = t.oid
           WHERE c.relname = %s AND a.attnum > 0 AND NOT a.attisdropped
           AND t.typname = 'bool'""",
        (table_name,),
    )
    return {r[0] for r in pg_cur.fetchall()}


def get_pg_col_types(pg_cur, table_name):
    pg_cur.execute(
        """SELECT column_name, data_type, character_maximum_length
           FROM information_schema.columns
           WHERE table_name = %s AND table_schema = 'public'""",
        (table_name,),
    )
    return {r[0]: (r[1], r[2]) for r in pg_cur.fetchall()}


def sanitize_value(v, col_name, col_types, bool_cols):
    """SQLite degerini PostgreSQL icin uygun tipe donustur."""
    if col_name in bool_cols and v is not None and isinstance(v, int):
        return bool(v)
    if v == "" or v == b"":
        if col_name in col_types:
            dt = col_types[col_name][0]
            if dt in ("integer", "bigint", "smallint", "numeric", "real",
                      "double precision", "uuid"):
                return None
    if isinstance(v, str) and col_name in col_types:
        max_len = col_types[col_name][1]
        if max_len and len(v) > max_len:
            return v[:max_len]
    return v


def pg_table_exists(pg_cur, table_name):
    pg_cur.execute(
        "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
        "WHERE table_schema='public' AND table_name=%s)",
        (table_name,),
    )
    return pg_cur.fetchone()[0]


def main():
    sqlite_path = os.environ.get(
        "SQLITE_PATH",
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "backups", "vm_pull", "20260402_070416_vm_kokpitim_FRESH.db"),
    )
    pg_uri = os.environ.get(
        "SQLALCHEMY_DATABASE_URI",
        "postgresql://kokpitim_user:kokpitim_dev_123@localhost/kokpitim_db",
    )

    if not pg_uri.startswith("postgresql"):
        print("HATA: SQLALCHEMY_DATABASE_URI PostgreSQL olmali.")
        sys.exit(1)
    if not os.path.isfile(sqlite_path):
        print(f"HATA: SQLite dosyasi bulunamadi: {sqlite_path}")
        sys.exit(1)

    print(f"SQLite kaynak : {sqlite_path}")
    print(f"PostgreSQL    : {pg_uri[:60]}...")
    print()

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

    # SQLite tabloları
    cur = sqlite_conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' "
        "AND name NOT LIKE 'sqlite_%' ORDER BY name"
    )
    all_sqlite_tables = [r[0] for r in cur.fetchall()]

    ordered = [t for t in FK_ORDER if t in all_sqlite_tables]
    rest = [t for t in all_sqlite_tables if t not in ordered]
    tables = ordered + sorted(rest)

    pg_cur = pg_conn.cursor()

    # FK kontrollerini gecici kapat
    try:
        pg_cur.execute("SET session_replication_role = 'replica'")
        pg_conn.commit()
        use_replica = True
        print("FK kontrolleri gecici kapatildi (session_replication_role=replica).")
    except Exception:
        pg_conn.rollback()
        pg_cur = pg_conn.cursor()
        use_replica = False
        print("UYARI: FK kontrolleri kapatılamadi, sira onemli.")

    stats = {"inserted": 0, "updated": 0, "skipped": 0, "tables": 0, "errors": 0}

    for table in tables:
        if table in SKIP_TABLES:
            print(f"  [{table}] ATLANDI (korunan tablo)")
            continue

        pg_table = TABLE_MAP.get(table, table)

        if not pg_table_exists(pg_cur, pg_table):
            print(f"  [{table}] PG'de yok, atlandi")
            continue

        try:
            cur = sqlite_conn.execute(f"SELECT * FROM [{table}]")
            rows = cur.fetchall()
            if not rows:
                continue

            sqlite_cols = [d[0] for d in cur.description]
            pg_cols = get_pg_cols(pg_cur, pg_table)
            pk_cols = get_pg_pk_cols(pg_cur, pg_table)
            bool_cols = get_pg_bool_cols(pg_cur, pg_table)
            col_types = get_pg_col_types(pg_cur, pg_table)

            # Sadece her iki tarafta da olan kolonlar
            cols = [c for c in sqlite_cols if c in pg_cols]
            if not cols:
                continue

            col_indices = {c: sqlite_cols.index(c) for c in cols}

            # PK kolonlari cols icinde mi?
            valid_pk = [c for c in pk_cols if c in cols]

            if valid_pk:
                # UPSERT: ON CONFLICT (pk) DO UPDATE SET non-pk cols = EXCLUDED.val
                non_pk_cols = [c for c in cols if c not in valid_pk]
                cols_str = ", ".join(f'"{c}"' for c in cols)
                placeholders = ", ".join("%s" for _ in cols)
                conflict_cols = ", ".join(f'"{c}"' for c in valid_pk)

                if non_pk_cols:
                    update_str = ", ".join(
                        f'"{c}" = EXCLUDED."{c}"' for c in non_pk_cols
                    )
                    sql = (
                        f'INSERT INTO "{pg_table}" ({cols_str}) VALUES ({placeholders}) '
                        f'ON CONFLICT ({conflict_cols}) DO UPDATE SET {update_str}'
                    )
                else:
                    # Sadece PK varsa sadece insert, conflict'te yoksay
                    sql = (
                        f'INSERT INTO "{pg_table}" ({cols_str}) VALUES ({placeholders}) '
                        f'ON CONFLICT ({conflict_cols}) DO NOTHING'
                    )
            else:
                # PK yok: basit insert, duplicate'e dikkat et
                cols_str = ", ".join(f'"{c}"' for c in cols)
                placeholders = ", ".join("%s" for _ in cols)
                sql = f'INSERT INTO "{pg_table}" ({cols_str}) VALUES ({placeholders}) ON CONFLICT DO NOTHING'

            ins = upd = skip = 0
            for row in rows:
                vals = [
                    sanitize_value(row[col_indices[c]], c, col_types, bool_cols)
                    for c in cols
                ]
                try:
                    pg_cur.execute(sql, vals)
                    if pg_cur.rowcount == 1:
                        ins += 1
                    else:
                        # ON CONFLICT DO UPDATE her zaman 1 döndürür;
                        # DO NOTHING 0 döndürür (zaten vardı)
                        skip += 1
                    pg_conn.commit()
                except Exception as e:
                    pg_conn.rollback()
                    skip += 1
                    if skip <= 3:  # ilk 3 hatayı göster
                        print(f"    UYARI satir atlandi ({table}): {str(e)[:100]}")

            pg_cur = pg_conn.cursor()
            stats["inserted"] += ins
            stats["skipped"] += skip
            stats["tables"] += 1
            total = ins + skip
            print(f"  {pg_table:<40} {total:>5} satir  ({ins} upsert, {skip} atlan)")

        except Exception as e:
            print(f"  HATA [{table}]: {e}")
            stats["errors"] += 1
            try:
                pg_conn.rollback()
            except Exception:
                pass
            pg_cur = pg_conn.cursor()

    # FK kontrollerini geri ac
    if use_replica:
        try:
            pg_cur.execute("SET session_replication_role = 'DEFAULT'")
            pg_conn.commit()
        except Exception:
            pass

    # Sequence'leri guncelle (PG'de ID'ler SQLite'tan geldi, sequence geride kalabilir)
    print("\nSequence'ler guncelleniyor...")
    pg_cur.execute(
        """
        SELECT sequence_name FROM information_schema.sequences
        WHERE sequence_schema = 'public'
        """
    )
    sequences = [r[0] for r in pg_cur.fetchall()]
    for seq in sequences:
        # sequence adından tablo/kolon bul
        # Ornek: tenants_id_seq → tenants, id
        parts = seq.rsplit("_seq", 1)[0].rsplit("_", 1)
        if len(parts) == 2:
            tbl, col = parts
            try:
                pg_cur.execute(
                    f"SELECT setval('{seq}', COALESCE(MAX(\"{col}\"), 1)) FROM \"{tbl}\""
                )
                pg_conn.commit()
            except Exception:
                pg_conn.rollback()
                pg_cur = pg_conn.cursor()

    sqlite_conn.close()
    pg_conn.close()

    print("\n" + "="*60)
    print("MIGRASYON TAMAMLANDI")
    print(f"  Islenen tablo : {stats['tables']}")
    print(f"  Upsert/insert : {stats['inserted']}")
    print(f"  Atlanan satir : {stats['skipped']}")
    print(f"  Hata (tablo)  : {stats['errors']}")
    print("="*60)


if __name__ == "__main__":
    main()
