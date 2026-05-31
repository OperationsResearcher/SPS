"""
Yerel PostgreSQL'e KMF (tenant_id=16) verisini yayından alınan CSV'lerden yükler.
"""
import psycopg2, csv, re
from pathlib import Path

CSV_DIR = Path(__file__).parent.parent / "backups" / "kmf_csv_2026-06-01"
TENANT_ID = 16

# Yerel bağlantı
env = {}
for line in (Path(__file__).parent.parent / ".env").read_text(encoding="utf-8", errors="ignore").splitlines():
    m = re.match(r'^([A-Z_]+)=(.+)$', line.strip())
    if m:
        env[m.group(1)] = m.group(2)

db_url = env.get("SQLALCHEMY_DATABASE_URI", "")
m = re.match(r'postgresql://([^:]+):([^@]+)@([^/]+)/(.+)', db_url)
if not m:
    raise SystemExit(f"DB URL okunamadı: {db_url}")
user, pwd, host, dbname = m.groups()

conn = psycopg2.connect(dbname=dbname, user=user, password=pwd, host=host,
                        client_encoding="UTF8")
conn.autocommit = False
cur = conn.cursor()
print(f"Yerel DB: {dbname}@{host} — bağlandı\n")

# ── FK trigger'larını devre dışı bırak (tablo sahibi yetkisi yeterli) ────────
TABLES_WITH_FK = [
    "individual_kpi_data", "individual_performance_indicators",
    "kpi_data_audits", "kpi_data", "process_kpis",
    "process_activity_assignees", "process_activities",
    "process_sub_strategy_links", "process_leaders", "process_members",
    "processes", "sub_strategies", "strategies",
    "tenant_year_identities", "plan_years",
    "notifications", "audit_logs", "users", "tenants",
]
for t in TABLES_WITH_FK:
    try:
        cur.execute(f"ALTER TABLE {t} DISABLE TRIGGER ALL")
    except Exception:
        pass  # yetki yoksa devam et

# ── 1. KMF verilerini sil ─────────────────────────────────────────────────────
print("=== KMF verisi siliniyor (FK bypass aktif) ===")

DELETES = [
    ("individual_kpi_data",   "DELETE FROM individual_kpi_data ikd USING individual_performance_indicators ipi, users u WHERE ikd.individual_pg_id=ipi.id AND ipi.user_id=u.id AND u.tenant_id=16"),
    ("individual_kpi_data",   "DELETE FROM individual_kpi_data WHERE user_id IN (SELECT id FROM users WHERE tenant_id=16)"),
    ("individual_perf_ind",   "DELETE FROM individual_performance_indicators ipi USING users u WHERE ipi.user_id=u.id AND u.tenant_id=16"),
    ("kpi_data_audits",       "DELETE FROM kpi_data_audits ka USING kpi_data kd, process_kpis pk, processes p WHERE ka.kpi_data_id=kd.id AND kd.process_kpi_id=pk.id AND pk.process_id=p.id AND p.tenant_id=16"),
    ("kpi_data",              "DELETE FROM kpi_data kd USING process_kpis pk, processes p WHERE kd.process_kpi_id=pk.id AND pk.process_id=p.id AND p.tenant_id=16"),
    ("process_kpis",          "DELETE FROM process_kpis pk USING processes p WHERE pk.process_id=p.id AND p.tenant_id=16"),
    ("process_act_assignees", "DELETE FROM process_activity_assignees paa USING process_activities pa, processes p WHERE paa.activity_id=pa.id AND pa.process_id=p.id AND p.tenant_id=16"),
    ("process_activities",    "DELETE FROM process_activities pa USING processes p WHERE pa.process_id=p.id AND p.tenant_id=16"),
    ("process_sub_str_links", "DELETE FROM process_sub_strategy_links psl USING processes p WHERE psl.process_id=p.id AND p.tenant_id=16"),
    ("process_leaders",       "DELETE FROM process_leaders pl USING processes p WHERE pl.process_id=p.id AND p.tenant_id=16"),
    ("process_members",       "DELETE FROM process_members pm USING processes p WHERE pm.process_id=p.id AND p.tenant_id=16"),
    ("processes",             "DELETE FROM processes WHERE tenant_id=16"),
    ("sub_strategies",        "DELETE FROM sub_strategies ss USING strategies s WHERE ss.strategy_id=s.id AND s.tenant_id=16"),
    ("strategies",            "DELETE FROM strategies WHERE tenant_id=16"),
    ("tenant_year_identities","DELETE FROM tenant_year_identities tyi USING plan_years py WHERE tyi.plan_year_id=py.id AND py.tenant_id=16"),
    ("plan_years",            "DELETE FROM plan_years WHERE tenant_id=16"),
    ("notifications",         "DELETE FROM notifications WHERE tenant_id=16"),
    ("audit_logs",            "DELETE FROM audit_logs WHERE tenant_id=16"),
    ("users",                 "DELETE FROM users WHERE tenant_id=16"),
    ("tenants",               "DELETE FROM tenants WHERE id=16"),
]

for label, sql in DELETES:
    cur.execute(sql)
    if cur.rowcount > 0:
        print(f"  Silindi ({cur.rowcount}): {label}")

conn.commit()
print("Silme tamamlandı.\n")


# ── 2. CSV yükle ──────────────────────────────────────────────────────────────
print("=== CSV'ler yükleniyor ===")

NOT_NULL_DEFAULTS = {
    # tablo → {kolon → varsayılan} (üretimde NULL olup yerel NOT NULL olan kolonlar)
    "kpi_data": {"actual_value": ""},
}

def read_csv(fname, table=None):
    """CSV oku, boş string → None; zorunlu NOT NULL kolonlara varsayılan ata."""
    fpath = CSV_DIR / fname
    if not fpath.exists():
        return None, None
    with open(fpath, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f)
        headers = next(reader)
        nn = NOT_NULL_DEFAULTS.get(table, {})
        rows = []
        for row in reader:
            converted = []
            for i, v in enumerate(row):
                col = headers[i] if i < len(headers) else ""
                if v == "":
                    converted.append(nn.get(col, None))
                else:
                    converted.append(v)
            rows.append(converted)
    return headers, rows


def load(fname, table):
    fpath = CSV_DIR / fname
    if not fpath.exists():
        print(f"  ATLA (yok): {fname}")
        return
    # Kolon başlıklarını oku
    with open(fpath, "r", encoding="utf-8", errors="replace") as f:
        headers = next(csv.reader(f))
    cols = ", ".join(f'"{c}"' for c in headers)
    try:
        # COPY FROM STDIN: Python string encoding sorununu bypass eder
        # NULL '' → boş alan NULL olur; actual_value için sonradan düzeltiriz
        with open(fpath, "r", encoding="utf-8", errors="replace") as f:
            cur.copy_expert(
                f"COPY {table} ({cols}) FROM STDIN WITH (FORMAT CSV, HEADER, NULL '')",
                f,
            )
        n = cur.rowcount
        conn.commit()
        print(f"  OK {table}: {n} satir")
    except Exception as e:
        conn.rollback()
        # kpi_data için actual_value NOT NULL sorunu: boşları '' yap
        if "actual_value" in str(e) and table == "kpi_data":
            try:
                import io
                rows_fixed = []
                with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                    reader = csv.reader(f)
                    hdrs = next(reader)
                    av_idx = hdrs.index("actual_value") if "actual_value" in hdrs else -1
                    for row in reader:
                        if av_idx >= 0 and (av_idx >= len(row) or row[av_idx] == ""):
                            while len(row) <= av_idx:
                                row.append("")
                            row[av_idx] = ""  # boş string (NOT NULL sağlar)
                        rows_fixed.append(row)
                placeholders = ", ".join(["%s"] * len(hdrs))
                cols2 = ", ".join(f'"{c}"' for c in hdrs)
                sql = f'INSERT INTO {table} ({cols2}) VALUES ({placeholders}) ON CONFLICT DO NOTHING'
                converted = [[None if v == "" else v for v in row] for row in rows_fixed]
                # actual_value None → '' dönüştür
                for row in converted:
                    if av_idx >= 0 and row[av_idx] is None:
                        row[av_idx] = ""
                cur.executemany(sql, converted)
                conn.commit()
                print(f"  OK {table} (fallback): {len(rows_fixed)} satir")
            except Exception as e2:
                conn.rollback()
                print(f"  HATA {table} fallback: {e2}")
        else:
            print(f"  HATA {table}: {e}")


for t in TABLES_WITH_FK:
    try:
        cur.execute(f"ALTER TABLE {t} DISABLE TRIGGER ALL")
    except Exception:
        pass

load("kmf_tenants.csv",            "tenants")
load("kmf_users.csv",              "users")
load("kmf_plan_years.csv",         "plan_years")
load("kmf_strategies.csv",         "strategies")
load("kmf_sub_strategies.csv",     "sub_strategies")
load("kmf_processes.csv",          "processes")
load("kmf_psl.csv",                "process_sub_strategy_links")
load("kmf_process_kpis.csv",       "process_kpis")
load("kmf_kpi_data.csv",           "kpi_data")
load("kmf_process_activities.csv", "process_activities")
load("kmf_ipi.csv",                "individual_performance_indicators")
load("kmf_ikd.csv",                "individual_kpi_data")

# FK trigger'ları geri aç
for t in TABLES_WITH_FK:
    try:
        cur.execute(f"ALTER TABLE {t} ENABLE TRIGGER ALL")
    except Exception:
        pass
conn.commit()

# ── 3. Doğrulama ──────────────────────────────────────────────────────────────
print("\n=== Doğrulama (yayın hedefleri) ===")
checks = [
    ("Süreç     (beklenen: 11)", "SELECT count(*) FROM processes WHERE tenant_id=16"),
    ("PG        (beklenen: 121)","SELECT count(*) FROM process_kpis pk JOIN processes p ON p.id=pk.process_id WHERE p.tenant_id=16"),
    ("PG Ölçüm  (beklenen: 497)","SELECT count(*) FROM kpi_data kd JOIN process_kpis pk ON pk.id=kd.process_kpi_id JOIN processes p ON p.id=pk.process_id WHERE p.tenant_id=16"),
    ("Kullanıcı (beklenen: 8)",  "SELECT count(*) FROM users WHERE tenant_id=16"),
    ("Strateji  (beklenen: 6)",  "SELECT count(*) FROM strategies WHERE tenant_id=16"),
    ("Alt Str.  (beklenen: 21)", "SELECT count(*) FROM sub_strategies ss JOIN strategies s ON s.id=ss.strategy_id WHERE s.tenant_id=16"),
]
for label, sql in checks:
    cur.execute(sql)
    print(f"  {label}: {cur.fetchone()[0]}")

conn.close()
print("\nTamamlandı.")
