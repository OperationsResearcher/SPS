"""Yayın sunucusunda çalıştırılacak KMF export scripti."""
import psycopg2, json, datetime, decimal

conn = psycopg2.connect(dbname="kokpitim_db", user="postgres")
cur = conn.cursor()
TENANT_ID = 16
data = {}

def q(sql, params=()):
    cur.execute(sql, params)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]

data["tenants"]                      = q("SELECT * FROM tenants WHERE id=%s", (TENANT_ID,))
data["users"]                        = q("SELECT * FROM users WHERE tenant_id=%s", (TENANT_ID,))
data["roles"]                        = q("SELECT DISTINCT r.* FROM roles r JOIN users u ON u.role_id=r.id WHERE u.tenant_id=%s", (TENANT_ID,))
data["plan_years"]                   = q("SELECT * FROM plan_years WHERE tenant_id=%s", (TENANT_ID,))
data["tenant_year_identities"]       = q("SELECT tyi.* FROM tenant_year_identities tyi JOIN plan_years py ON py.id=tyi.plan_year_id WHERE py.tenant_id=%s", (TENANT_ID,))
data["strategies"]                   = q("SELECT * FROM strategies WHERE tenant_id=%s", (TENANT_ID,))
data["strategy_year_configs"]        = q("SELECT syc.* FROM strategy_year_configs syc JOIN strategies s ON s.id=syc.strategy_id WHERE s.tenant_id=%s", (TENANT_ID,))
data["k_vektor_strategy_weights"]    = q("SELECT kw.* FROM k_vektor_strategy_weights kw JOIN strategies s ON s.id=kw.strategy_id WHERE s.tenant_id=%s", (TENANT_ID,))
data["sub_strategies"]               = q("SELECT ss.* FROM sub_strategies ss JOIN strategies s ON s.id=ss.strategy_id WHERE s.tenant_id=%s", (TENANT_ID,))
data["sub_strategy_year_configs"]    = q("SELECT ssyc.* FROM sub_strategy_year_configs ssyc JOIN sub_strategies ss ON ss.id=ssyc.sub_strategy_id JOIN strategies s ON s.id=ss.strategy_id WHERE s.tenant_id=%s", (TENANT_ID,))
data["k_vektor_sub_strategy_weights"]= q("SELECT kw.* FROM k_vektor_sub_strategy_weights kw JOIN sub_strategies ss ON ss.id=kw.sub_strategy_id JOIN strategies s ON s.id=ss.strategy_id WHERE s.tenant_id=%s", (TENANT_ID,))
data["processes"]                    = q("SELECT * FROM processes WHERE tenant_id=%s", (TENANT_ID,))
data["process_leaders"]              = q("SELECT pl.* FROM process_leaders pl JOIN processes p ON p.id=pl.process_id WHERE p.tenant_id=%s", (TENANT_ID,))
data["process_members"]              = q("SELECT pm.* FROM process_members pm JOIN processes p ON p.id=pm.process_id WHERE p.tenant_id=%s", (TENANT_ID,))
data["process_sub_strategy_links"]   = q("SELECT psl.* FROM process_sub_strategy_links psl JOIN processes p ON p.id=psl.process_id WHERE p.tenant_id=%s", (TENANT_ID,))
data["process_year_configs"]         = q("SELECT pyc.* FROM process_year_configs pyc JOIN processes p ON p.id=pyc.process_id WHERE p.tenant_id=%s", (TENANT_ID,))
data["process_kpis"]                 = q("SELECT pk.* FROM process_kpis pk JOIN processes p ON p.id=pk.process_id WHERE p.tenant_id=%s", (TENANT_ID,))
data["kpi_year_configs"]             = q("SELECT kyc.* FROM kpi_year_configs kyc JOIN process_kpis pk ON pk.id=kyc.kpi_id JOIN processes p ON p.id=pk.process_id WHERE p.tenant_id=%s", (TENANT_ID,))
data["kpi_data"]                     = q("SELECT kd.* FROM kpi_data kd JOIN process_kpis pk ON pk.id=kd.process_kpi_id JOIN processes p ON p.id=pk.process_id WHERE p.tenant_id=%s", (TENANT_ID,))
data["kpi_data_audits"]              = q("SELECT ka.* FROM kpi_data_audits ka JOIN kpi_data kd ON kd.id=ka.kpi_data_id JOIN process_kpis pk ON pk.id=kd.process_kpi_id JOIN processes p ON p.id=pk.process_id WHERE p.tenant_id=%s", (TENANT_ID,))
data["process_activities"]           = q("SELECT pa.* FROM process_activities pa JOIN processes p ON p.id=pa.process_id WHERE p.tenant_id=%s", (TENANT_ID,))
data["process_activity_assignees"]   = q("SELECT paa.* FROM process_activity_assignees paa JOIN process_activities pa ON pa.id=paa.activity_id JOIN processes p ON p.id=pa.process_id WHERE p.tenant_id=%s", (TENANT_ID,))
data["individual_performance_indicators"] = q("SELECT ipi.* FROM individual_performance_indicators ipi JOIN users u ON u.id=ipi.user_id WHERE u.tenant_id=%s", (TENANT_ID,))
data["individual_kpi_data"]          = q("SELECT ikd.* FROM individual_kpi_data ikd JOIN individual_performance_indicators ipi ON ipi.id=ikd.individual_pg_id JOIN users u ON u.id=ipi.user_id WHERE u.tenant_id=%s", (TENANT_ID,))
data["notifications"]                = q("SELECT * FROM notifications WHERE tenant_id=%s", (TENANT_ID,))
data["audit_logs"]                   = q("SELECT * FROM audit_logs WHERE tenant_id=%s", (TENANT_ID,))

for tbl, rows in data.items():
    if rows:
        print(f"  {tbl}: {len(rows)} satir")

def default(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()
    if isinstance(o, decimal.Decimal):
        return float(o)
    if isinstance(o, bytes):
        return o.decode("utf-8", errors="replace")
    raise TypeError(f"Tip hatasi: {type(o)}")

with open("/tmp/kmf_export.json", "w", encoding="utf-8") as f:
    json.dump(data, f, default=default, ensure_ascii=False, indent=2)

print(f"\nExport tamamlandi: /tmp/kmf_export.json")
conn.close()
