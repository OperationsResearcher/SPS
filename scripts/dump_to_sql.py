"""
Yerel PostgreSQL'den schema + data'yı VM'de restore edilebilecek SQL dosyasına yazar.
Kullanım: python scripts/dump_to_sql.py
"""
import psycopg2, re, sys
from pathlib import Path

env = {}
for line in Path(".env").read_text(encoding="utf-8", errors="ignore").splitlines():
    m = re.match(r'^([A-Z_]+)=(.+)$', line.strip())
    if m: env[m.group(1)] = m.group(2)

db_url = env.get("SQLALCHEMY_DATABASE_URI","")
m = re.match(r'postgresql://([^:]+):([^@]+)@([^/]+)/(.+)', db_url)
user, pwd, host, dbname = m.groups()

conn = psycopg2.connect(dbname=dbname, user=user, password=pwd,
                        host=host, client_encoding="UTF8")
conn.autocommit = True
cur = conn.cursor()

# Bağımlılık sırasına göre sabit tablo listesi (parent önce, child sonra)
# TRUNCATE yok — DB zaten boş, sıra önemli
tables = [
    # Bağımsız / temel
    "roles", "subscription_packages", "system_modules", "system_components",
    "module_component_slugs", "package_modules", "route_registry",
    "system_settings",
    # Tenant ve kullanıcılar
    "tenants", "users", "user_tour_progress",
    # Plan yılı
    "plan_years", "tenant_year_identities",
    # Stratejik yapı
    "strategies", "strategy_year_configs",
    "k_vektor_strategy_weights", "k_vektor_config_snapshots",
    "sub_strategies", "sub_strategy_year_configs",
    "k_vektor_sub_strategy_weights",
    # Süreç
    "processes", "process_year_configs", "process_leaders", "process_members",
    "process_owners_table",
    "process_sub_strategy_links",
    "process_kpis", "kpi_year_configs",
    "kpi_data", "kpi_data_audits", "favorite_kpis",
    "process_activities", "process_activity_reminders",
    "process_activity_assignees",
    "process_maturity",
    # Girişimler / projeler
    "initiatives", "initiative_milestones",
    "plan_projects", "plan_project_tasks", "plan_project_activities",
    "project", "project_leaders", "project_members", "project_observers",
    "project_risk",
    # Bireysel performans
    "individual_performance_indicators", "individual_kpi_year_configs",
    "individual_kpi_data", "individual_kpi_data_audits",
    "individual_activities", "individual_activity_tracks",
    # Analiz araçları
    "swot_analyses", "tows_analyses", "pestel_analyses", "porter_analyses",
    "a3_reports", "competitor_analyses",
    "stakeholder_maps", "stakeholder_surveys",
    "blue_ocean_canvases", "blue_ocean_errc_items", "blue_ocean_factors",
    # OKR
    "okr_objectives", "okr_key_results",
    # BSC
    "bsc_kpi_perspectives",
    # ESG
    "esg_metrics", "esg_metric_values",
    # EVM / SLA / Kapasite
    "evm_snapshots", "sla", "capacity_plan", "value_chain_items",
    # K-Vektör / K-Radar
    "k_radar_recommendation_actions", "bottleneck_log", "process_process_links",
    "risk_heatmap_items", "raid_item", "rule_definition",
    # Diğer
    "activity_tracks", "recurring_task", "task", "task_baseline",
    "working_day", "relations",
    # Bildirim / e-posta / push
    "notifications", "tenant_email_configs", "push_subscriptions",
    "integration_hook",
    # LLM
    "llm_usage_logs", "llm_quota_overrides", "tenant_llm_configs",
    # Denetim
    "audit_logs",
    # Alembic
    "alembic_version",
]

# Veritabanında gerçekten var olan tablolara daralt
cur.execute("SELECT tablename FROM pg_tables WHERE schemaname='public'")
existing = {r[0] for r in cur.fetchall()}
tables = [t for t in tables if t in existing]

# Listede olmayan tabloları sona ekle (atlamamak için)
remaining = [t for t in existing if t not in tables]
tables.extend(sorted(remaining))

out = Path("backups/yerel_full_2026-06-01.sql")
print(f"Yazılıyor: {out}")

with open(out, "w", encoding="utf-8") as f:
    f.write("-- Kokpitim Yerel DB Dump 2026-06-01\n")
    f.write("SET client_encoding = 'UTF8';\n")
    f.write("SET standard_conforming_strings = on;\n\n")

    for tbl in tables:
        # Satır sayısı
        cur.execute(f"SELECT count(*) FROM {tbl}")
        n = cur.fetchone()[0]
        if n == 0:
            continue

        f.write(f"-- TABLE: {tbl} ({n} rows)\n")

        # Kolon adları
        cur.execute(f"""
            SELECT column_name FROM information_schema.columns
            WHERE table_name=%s AND table_schema='public'
            ORDER BY ordinal_position
        """, (tbl,))
        cols = [r[0] for r in cur.fetchall()]
        cols_sql = ", ".join(f'"{c}"' for c in cols)

        # Data
        cur.execute(f'SELECT {cols_sql} FROM "{tbl}"')
        rows = cur.fetchall()

        import json as _json, datetime, decimal
        def pg_val(v):
            if v is None: return "NULL"
            if isinstance(v, bool): return "TRUE" if v else "FALSE"
            if isinstance(v, (dict, list)):
                s = _json.dumps(v, ensure_ascii=False, default=str).replace("'","''")
                return f"'{s}'"
            if isinstance(v, (datetime.datetime, datetime.date)):
                return f"'{v.isoformat()}'"
            if isinstance(v, decimal.Decimal):
                return str(float(v))
            s = str(v).replace("'","''")
            return f"'{s}'"

        chunk = 500
        for i in range(0, len(rows), chunk):
            vals = ",\n  ".join(
                "(" + ", ".join(pg_val(c) for c in row) + ")"
                for row in rows[i:i+chunk]
            )
            f.write(f"INSERT INTO \"{tbl}\" ({cols_sql}) VALUES\n  {vals}\n  ON CONFLICT DO NOTHING;\n")
        f.write("\n")
        print(f"  {tbl}: {n} satır")

print(f"\nTamamlandı: {out} ({out.stat().st_size/1024/1024:.1f} MB)")
conn.close()
