#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VM'deki orijinal pg_dump SQL'den etkilenen tabloların verilerini
UPSERT ile geri yükler.
Çalıştırma: sudo -u postgres python3 /tmp/restore_vm_original_data.py
"""
import re, sys, os

SQL_FILE = "/tmp/vm_pg_data_only.sql"
DB_URI   = os.environ.get(
    "SQLALCHEMY_DATABASE_URI",
    "postgresql+psycopg2://kokpitim_user:MfGMfG__46604660@host.docker.internal:5432/kokpitim_db"
)

try:
    import psycopg2
except ImportError:
    os.system("pip3 install psycopg2-binary -q")
    import psycopg2

from urllib.parse import urlparse
_p = urlparse(DB_URI.replace("postgresql+psycopg2://","postgresql://"))
conn = psycopg2.connect(
    host=_p.hostname, port=_p.port or 5432,
    dbname=_p.path.lstrip("/"), user=_p.username, password=_p.password
)
conn.autocommit = False
cur  = conn.cursor()

# session_replication_role denemesi
try:
    cur.execute("SET session_replication_role = 'replica'")
    conn.commit()
    print("FK geçici kapatıldı.")
except Exception:
    conn.rollback()
    cur = conn.cursor()
    print("FK devre dışı bırakılamadı, sırayla işlenecek.")

def get_pk(table):
    cur.execute("""
        SELECT kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name=kcu.constraint_name
         AND tc.table_schema=kcu.table_schema
        WHERE tc.constraint_type='PRIMARY KEY'
          AND tc.table_name=%s AND tc.table_schema='public'
        ORDER BY kcu.ordinal_position""", (table,))
    return [r[0] for r in cur.fetchall()]

def table_exists(table):
    cur.execute("SELECT EXISTS(SELECT 1 FROM information_schema.tables "
                "WHERE table_schema='public' AND table_name=%s)", (table,))
    return cur.fetchone()[0]

# SQL dosyasını oku ve multi-line INSERT'leri birleştir
with open(SQL_FILE, "r", encoding="utf-8", errors="replace") as f:
    raw = f.read()

# Her INSERT bloğunu topla (noktalı virgüle kadar)
insert_blocks = []
current = []
for line in raw.split("\n"):
    stripped = line.strip()
    if stripped.startswith("INSERT INTO public."):
        if current:
            insert_blocks.append(" ".join(current))
        current = [stripped]
    elif current:
        current.append(stripped)
        if stripped.endswith(";"):
            insert_blocks.append(" ".join(current))
            current = []
if current:
    insert_blocks.append(" ".join(current))

print(f"Toplam INSERT bloğu: {len(insert_blocks)}")

# Tablo bazlı grupla
from collections import defaultdict
by_table = defaultdict(list)
for block in insert_blocks:
    m = re.match(r"INSERT INTO public\.(\w+)\s*\(([^)]+)\)\s*VALUES\s*\((.+)\);?$", block, re.DOTALL)
    if m:
        by_table[m.group(1)].append((m.group(2), m.group(3), block))

ins_total = skip_total = 0

for table, rows in by_table.items():
    if not table_exists(table):
        print(f"  [{table}] PG'de yok, atlandı")
        continue

    pk = get_pk(table)
    ins = skip = 0

    for col_str, val_str, original_sql in rows:
        cols = [c.strip() for c in col_str.split(",")]

        if pk:
            pk_in_cols = [c for c in pk if c in cols]
            non_pk = [c for c in cols if c not in pk_in_cols]
            conf = ", ".join(f'"{c}"' for c in pk_in_cols)
            if non_pk:
                upd = ", ".join(f'"{c}" = EXCLUDED."{c}"' for c in non_pk)
                upsert_sql = (
                    f'INSERT INTO "{table}" ({col_str}) VALUES ({val_str}) '
                    f'ON CONFLICT ({conf}) DO UPDATE SET {upd}'
                )
            else:
                upsert_sql = (
                    f'INSERT INTO "{table}" ({col_str}) VALUES ({val_str}) '
                    f'ON CONFLICT ({conf}) DO NOTHING'
                )
        else:
            upsert_sql = (
                f'INSERT INTO "{table}" ({col_str}) VALUES ({val_str}) '
                f'ON CONFLICT DO NOTHING'
            )

        try:
            cur.execute(upsert_sql)
            conn.commit()
            ins += 1
        except Exception as e:
            conn.rollback()
            skip += 1
            if skip <= 2:
                print(f"    UYARI ({table}): {str(e)[:80]}")
            cur = conn.cursor()

    ins_total  += ins
    skip_total += skip
    if ins + skip > 0:
        print(f"  {table:<45} {ins+skip:>5} satır  ({ins} upsert, {skip} atlan)")

# FK geri aç
try:
    cur.execute("SET session_replication_role = 'origin'")
    conn.commit()
except Exception:
    pass

conn.close()
print(f"\nTOPLAM: {ins_total} upsert, {skip_total} atlan")
print("\nSon kontrol:")
import subprocess
result = subprocess.run(
    ["sudo", "-u", "postgres", "psql", "-d", DB_NAME, "-tAc",
     "SELECT 'kpi_data_max=' || max(created_at) FROM kpi_data; "
     "SELECT '1nis_kpi='    || count(*) FROM kpi_data WHERE created_at >= '2026-04-01'; "
     "SELECT 'process_kpis_max=' || max(updated_at) FROM process_kpis"],
    capture_output=True, text=True
)
print(result.stdout or result.stderr)
