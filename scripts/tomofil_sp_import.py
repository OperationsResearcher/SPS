"""Tomofil SP veri import — TomofılSP_2020_2026_v2.json'dan PG'ye.

Kurallar:
- JSON tenant_id (her değer) → 27 (Tomofil DB)
- JSON user_id ref'leri → 8173 (admin@tomofil.com)
- Tüm JSON id ve FK'lere +1.000.000 offset (çakışmasın)
- Kullanıcı tablosu, kpi_data_audits, audit_logs, M:N user tabloları YÜKLENMEZ
- Tek transaction; DRY_RUN=1 → rollback, IMPORT_COMMIT=1 → commit

Çalıştırma: IMPORT_COMMIT=1 python scripts/tomofil_sp_import.py
"""
import os, json, sys
import psycopg2
from psycopg2.extras import execute_values

sys.stdout.reconfigure(encoding='utf-8')

JSON_PATH = r'C:\kokpitim\docs\tomofil\TomofılSP_2020_2026_v2.json'
TENANT_ID = 27
ADMIN_USER_ID = 8173
OFFSET = 1_000_000
COMMIT = os.environ.get("IMPORT_COMMIT", "0") == "1"

from datetime import datetime, timezone
NOW = datetime.now(timezone.utc).isoformat()

def off(v):
    return None if v is None else int(v) + OFFSET

def ts(v):
    return v if v else NOW

def get(row, key, default=None):
    v = row.get(key, default)
    return v if v != "" else default

print(f"Loading JSON...")
with open(JSON_PATH, 'r', encoding='utf-8') as f:
    D = json.load(f)
print(f"  meta: {D['meta']['belge']} — {D['meta']['toplam_yil']} yıl")

conn = psycopg2.connect(host='localhost', user='kokpitim_user',
                         password='kokpitim_dev_123', dbname='kokpitim_db')
conn.autocommit = False
cur = conn.cursor()

cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
EXISTING = {r[0] for r in cur.fetchall()}

def bulk(table, cols, rows, on_conflict=None):
    if table not in EXISTING:
        print(f"  [SKIP] {table} (tablo yok)")
        return
    if not rows:
        print(f"  [----] {table} (boş)")
        return
    sql = f"INSERT INTO {table} ({','.join(cols)}) VALUES %s"
    if on_conflict:
        sql += f" ON CONFLICT {on_conflict}"
    execute_values(cur, sql, rows, page_size=1000)
    print(f"  [{cur.rowcount:6d}] {table}")

# Self-ref UPDATE'leri için JSON kaynak listesi
SELF_REF_UPDATES = []  # (table, fk_col, json_key, id_key)

def update_self_refs():
    print("\n-- Self-ref FK UPDATE'leri --")
    for table, fk_col, json_key, id_key in SELF_REF_UPDATES:
        if table not in EXISTING: continue
        rows = D.get(json_key, [])
        pairs = [(off(r['id']), off(r.get(fk_col))) for r in rows if r.get(fk_col) is not None]
        if not pairs:
            print(f"  [----] {table}.{fk_col}")
            continue
        execute_values(cur,
            f"UPDATE {table} AS t SET {fk_col} = v.src "
            f"FROM (VALUES %s) AS v(id, src) "
            f"WHERE t.id = v.id AND EXISTS (SELECT 1 FROM {table} t2 WHERE t2.id = v.src)",
            pairs)
        print(f"  [{cur.rowcount:6d}] {table}.{fk_col}")

# ─── PLAN YEARS ────────────────────────────────────────────────────────
def to_plan_years():
    return [(
        off(r['id']), TENANT_ID, r['year'], r.get('name'),
        r.get('status', 'active'),
        None,  # template_source_id → 2nd pass
        r.get('created_at'), r.get('closed_at'),
        None, r.get('scenario_label'),  # scenario_of_id → 2nd pass
    ) for r in D.get('plan_years', [])]

# ─── TENANT YEAR IDENTITIES ────────────────────────────────────────────
def to_tenant_year_identities():
    return [(
        off(r['id']), off(r['plan_year_id']), TENANT_ID,
        r.get('purpose'), r.get('vision'), r.get('core_values'),
        r.get('code_of_ethics'), r.get('quality_policy'),
    ) for r in D.get('tenant_year_identities', [])]

# ─── STRATEGIES ────────────────────────────────────────────────────────
def to_strategies():
    return [(
        off(r['id']), TENANT_ID, r.get('code'), r['title'], r.get('description'),
        r.get('is_active', True),
        ts(r.get('created_at')), ts(r.get('updated_at')),
        off(r.get('plan_year_id')), None,  # source_strategy_id → 2nd pass
    ) for r in D.get('strategies', [])]

# ─── SUB STRATEGIES ────────────────────────────────────────────────────
def to_sub_strategies():
    return [(
        off(r['id']), off(r['strategy_id']), r.get('code'), r['title'], r.get('description'),
        r.get('is_active', True),
        ts(r.get('created_at')), ts(r.get('updated_at')),
        off(r.get('plan_year_id')), None,  # source_sub_strategy_id → 2nd pass
    ) for r in D.get('sub_strategies', [])]

# ─── PROCESSES ─────────────────────────────────────────────────────────
def to_processes():
    return [(
        off(r['id']), TENANT_ID, None,  # parent_id → 2nd pass
        r.get('code'), r['name'], r.get('english_name'), r.get('weight'),
        r.get('document_no'), r.get('revision_no'), r.get('revision_date'),
        r.get('first_publish_date'), r.get('status', 'Aktif'), r.get('progress', 0),
        r.get('start_boundary'), r.get('end_boundary'),
        r.get('start_date'), r.get('end_date'), r.get('description'),
        off(r.get('plan_year_id')), None,  # source_process_id → 2nd pass
        r.get('is_active', True),
        ts(r.get('created_at')), ts(r.get('updated_at')),
    ) for r in D.get('processes', [])]

# ─── PROCESS-SUB STRATEGY LINKS ────────────────────────────────────────
def to_pssl():
    return [(
        off(r['process_id']), off(r['sub_strategy_id']), r.get('contribution_pct'),
    ) for r in D.get('process_sub_strategy_links', [])]

# ─── PROCESS KPIS ──────────────────────────────────────────────────────
def to_process_kpis():
    rows = []
    for r in D.get('process_kpis', []):
        rows.append((
            off(r['id']), off(r['process_id']), r['name'], r.get('description'),
            r.get('code'), r.get('target_value'), r.get('unit'), r.get('period'),
            r.get('data_source'), r.get('target_setting_method'),
            r.get('data_collection_method', 'Ortalama'),
            r.get('calculation_method', 'AVG'),
            r.get('gosterge_turu'), r.get('target_method'),
            r.get('basari_puani_araliklari'), r.get('onceki_yil_ortalamasi'),
            r.get('weight', 0), r.get('is_important', False),
            r.get('direction', 'Increasing'),
            r.get('calculated_score'), r.get('is_active', True),
            off(r.get('sub_strategy_id')),
            off(r.get('plan_year_id')), None,  # source_kpi_id → 2nd pass
            r.get('start_date'), r.get('end_date'),
            ts(r.get('created_at')), ts(r.get('updated_at')),
        ))
    return rows

# ─── KPI DATA ──────────────────────────────────────────────────────────
def to_kpi_data():
    rows = []
    for r in D.get('kpi_data', []):
        rows.append((
            off(r['id']), off(r['process_kpi_id']), r['year'], r['data_date'],
            r.get('period_type'), r.get('period_no'), r.get('period_month'),
            r.get('target_value'), r['actual_value'],
            r.get('status'), r.get('status_percentage'), r.get('description'),
            ADMIN_USER_ID,
            ts(r.get('created_at')), ts(r.get('updated_at')),
            r.get('is_active', True), r.get('deleted_at'), None,
        ))
    return rows

# ─── INDIVIDUAL PG + DATA ──────────────────────────────────────────────
def to_ipi():
    rows = []
    for r in D.get('individual_performance_indicators', []):
        rows.append((
            off(r['id']), ADMIN_USER_ID,
            r['name'], r.get('description'), r.get('code'),
            r.get('target_value'), r.get('actual_value'), r.get('unit'),
            r.get('period'), r.get('weight', 0), r.get('is_important', False),
            r.get('start_date'), r.get('end_date'),
            r.get('status', 'Devam Ediyor'),
            r.get('source', 'Bireysel'),
            off(r.get('source_process_id')), off(r.get('source_process_kpi_id')),
            r.get('direction', 'Increasing'),
            r.get('basari_puani_araliklari'),
            off(r.get('plan_year_id')), None,  # source_individual_kpi_id → 2nd pass
            r.get('is_active', True),
            ts(r.get('created_at')), ts(r.get('updated_at')),
        ))
    return rows

def to_ind_kpi_data():
    rows = []
    for r in D.get('individual_kpi_data', []):
        rows.append((
            off(r['id']), off(r['individual_pg_id']),
            r['year'], r['data_date'],
            r.get('period_type'), r.get('period_no'), r.get('period_month'),
            r.get('target_value'), r['actual_value'],
            r.get('status'), r.get('status_percentage'), r.get('description'),
            ADMIN_USER_ID, ts(r.get('created_at')), ts(r.get('updated_at')),
        ))
    return rows

# ─── ANALİZLER (SWOT/PESTEL/PORTER) ────────────────────────────────────
def to_swot():
    return [(
        off(r['id']), off(r['plan_year_id']), TENANT_ID,
        None,  # source_swot_id → 2nd pass
        r.get('strengths'), r.get('weaknesses'), r.get('opportunities'), r.get('threats'),
        ts(r.get('created_at')), ts(r.get('updated_at')),
    ) for r in D.get('swot_analyses', [])]

def to_pestel():
    return [(
        off(r['id']), off(r['plan_year_id']), TENANT_ID,
        None,  # source_pestel_id → 2nd pass
        r.get('political'), r.get('economic'), r.get('social'),
        r.get('technological'), r.get('environmental'), r.get('legal'),
        ts(r.get('created_at')), ts(r.get('updated_at')),
    ) for r in D.get('pestel_analyses', [])]

def to_porter():
    return [(
        off(r['id']), off(r['plan_year_id']), TENANT_ID,
        None,  # source_porter_id → 2nd pass
        r.get('rivalry_intensity'), r.get('supplier_power'),
        r.get('buyer_power'), r.get('new_entrant_threat'), r.get('substitute_threat'),
        ts(r.get('created_at')), ts(r.get('updated_at')),
    ) for r in D.get('porter_analyses', [])]

# ─── OKR ───────────────────────────────────────────────────────────────
def to_okr_obj():
    return [(
        off(r['id']), TENANT_ID, off(r['plan_year_id']),
        r['title'], r.get('description'), r.get('quarter'), r.get('owner'),
        r.get('order_no', 0),
        off(r.get('linked_strategy_id')), off(r.get('linked_sub_strategy_id')),
        r.get('is_active', True), ts(r.get('created_at')), ts(r.get('updated_at')),
    ) for r in D.get('okr_objectives', [])]

def to_okr_kr():
    return [(
        off(r['id']), off(r['objective_id']),
        r['title'], r.get('metric'),
        r.get('start_value'), r.get('target_value'), r.get('current_value'),
        r.get('order_no', 0), off(r.get('linked_process_kpi_id')),
        r.get('is_active', True), ts(r.get('created_at')), ts(r.get('updated_at')),
    ) for r in D.get('okr_key_results', [])]

# ─── ESG ───────────────────────────────────────────────────────────────
def to_esg_metrics():
    return [(
        off(r['id']), TENANT_ID, r.get('code'), r['name'], r.get('description'),
        r.get('category'), r.get('scope'), r.get('unit'), r.get('sdg_codes'),
        r.get('target_value'), r.get('baseline_year'), r.get('baseline_value'),
        r.get('is_active', True), ts(r.get('created_at')), ts(r.get('updated_at')),
    ) for r in D.get('esg_metrics', [])]

def to_esg_values():
    return [(
        off(r['id']), off(r['metric_id']),
        r['year'], r.get('period_type'), r.get('period_no'),
        r.get('value'), r.get('source'), r.get('notes'),
        ADMIN_USER_ID, r.get('created_at'),
    ) for r in D.get('esg_metric_values', [])]

# ─── PROCESS MATURITY & RISK ──────────────────────────────────────────
def to_process_maturity():
    return [(
        off(r['id']), TENANT_ID, off(r['process_id']),
        r['maturity_level'], r.get('dimension'),
        ADMIN_USER_ID, r.get('assessed_at'),
        r.get('is_active', True), ts(r.get('created_at')), ts(r.get('updated_at')),
    ) for r in D.get('process_maturity', [])]

def to_risk_heatmap():
    return [(
        off(r['id']), TENANT_ID, off(r.get('plan_year_id')),
        r['title'], r['probability'], r['impact'], r.get('rpn'),
        ADMIN_USER_ID, r.get('status'), r.get('source_type'),
        r.get('is_active', True), ts(r.get('created_at')), ts(r.get('updated_at')),
    ) for r in D.get('risk_heatmap_items', [])]

# ─── INITIATIVES ───────────────────────────────────────────────────────
def to_initiatives():
    return [(
        off(r['id']), TENANT_ID, r.get('code'), r['name'], r.get('description'),
        off(r.get('strategy_id')), off(r.get('sub_strategy_id')),
        r['start_year'], r['end_year'],
        r.get('start_date'), r.get('end_date'),
        r.get('status', 'planned'), r.get('priority', 'medium'),
        r.get('budget_total'), r.get('budget_spent', 0),
        r.get('progress_pct', 0.0), ADMIN_USER_ID,
        r.get('is_active', True), ts(r.get('created_at')), ts(r.get('updated_at')),
    ) for r in D.get('initiatives', [])]

def to_init_milestones():
    return [(
        off(r['id']), off(r['initiative_id']),
        r['name'], r.get('target_date'), r.get('completed_date'),
        r.get('status', 'pending'), r.get('note'),
        r.get('order_index', 0), r.get('created_at'),
    ) for r in D.get('initiative_milestones', [])]

# ─── SP PROJECTS ──────────────────────────────────────────────────────
def to_plan_projects():
    return [(
        off(r['id']), off(r['plan_year_id']), TENANT_ID,
        None,  # source_project_id → 2nd pass
        r['name'], r.get('description'),
        r.get('status', 'Planlandı'), r.get('progress', 0),
        r.get('start_date'), r.get('end_date'),
        r.get('is_active', True),
        ts(r.get('created_at')), ts(r.get('updated_at')),
    ) for r in D.get('plan_projects', [])]

def to_plan_project_tasks():
    return [(
        off(r['id']), off(r['project_id']), off(r['plan_year_id']),
        ADMIN_USER_ID,
        r['name'], r.get('description'),
        r.get('status', 'Planlandı'),
        r.get('start_date'), r.get('end_date'),
        r.get('is_active', True),
        r.get('progress_pct', 0.0), r.get('planned_budget'), r.get('actual_cost', 0),
        None,  # depends_on_task_id → 2nd pass
        ts(r.get('created_at')), ts(r.get('updated_at')),
    ) for r in D.get('plan_project_tasks', [])]

# ─── K-VEKTÖR ──────────────────────────────────────────────────────────
def to_kv_strategy():
    return [(
        off(r['id']), TENANT_ID, off(r['strategy_id']), r.get('weight_raw'),
    ) for r in D.get('k_vektor_strategy_weights', [])]

# ─── PLAN YEAR CONFIGS ─────────────────────────────────────────────────
def to_strategy_year_configs():
    return [(
        off(r['id']), off(r['plan_year_id']), off(r['strategy_id']),
        r.get('title'), r.get('code'), r.get('description'),
        r.get('is_included', True), r.get('weight'),
        ts(r.get('created_at')), ts(r.get('updated_at')),
    ) for r in D.get('strategy_year_configs', [])]

def to_sub_strategy_year_configs():
    return [(
        off(r['id']), off(r['plan_year_id']), off(r['sub_strategy_id']),
        r.get('title'), r.get('code'), r.get('description'),
        r.get('is_included', True),
        ts(r.get('created_at')), ts(r.get('updated_at')),
    ) for r in D.get('sub_strategy_year_configs', [])]

def to_process_year_configs():
    return [(
        off(r['id']), off(r['plan_year_id']), off(r['process_id']),
        r.get('name'), r.get('weight'),
        r.get('is_included', True),
        ts(r.get('created_at')), ts(r.get('updated_at')),
    ) for r in D.get('process_year_configs', [])]

def to_kpi_year_configs():
    return [(
        off(r['id']), off(r['plan_year_id']), off(r['process_kpi_id']),
        r.get('target_value'), r.get('unit'), r.get('period'),
        r.get('direction'), r.get('target_method'), r.get('calculation_method'),
        r.get('basari_puani_araliklari'), r.get('onceki_yil_ortalamasi'),
        r.get('weight'), r.get('is_included', True),
        ts(r.get('created_at')), ts(r.get('updated_at')),
    ) for r in D.get('kpi_year_configs', [])]


print(f"\n== IMPORT — COMMIT={COMMIT} ==\n")

bulk('plan_years',
     ['id','tenant_id','year','name','status','template_source_id',
      'created_at','closed_at','scenario_of_id','scenario_label'],
     to_plan_years())

bulk('tenant_year_identities',
     ['id','plan_year_id','tenant_id','purpose','vision','core_values',
      'code_of_ethics','quality_policy'],
     to_tenant_year_identities())

bulk('strategies',
     ['id','tenant_id','code','title','description','is_active',
      'created_at','updated_at','plan_year_id','source_strategy_id'],
     to_strategies())

bulk('sub_strategies',
     ['id','strategy_id','code','title','description','is_active',
      'created_at','updated_at','plan_year_id','source_sub_strategy_id'],
     to_sub_strategies())

bulk('processes',
     ['id','tenant_id','parent_id','code','name','english_name','weight',
      'document_no','revision_no','revision_date','first_publish_date',
      'status','progress','start_boundary','end_boundary',
      'start_date','end_date','description',
      'plan_year_id','source_process_id','is_active',
      'created_at','updated_at'],
     to_processes())

bulk('process_kpis',
     ['id','process_id','name','description','code','target_value','unit','period',
      'data_source','target_setting_method','data_collection_method','calculation_method',
      'gosterge_turu','target_method','basari_puani_araliklari','onceki_yil_ortalamasi',
      'weight','is_important','direction','calculated_score','is_active',
      'sub_strategy_id','plan_year_id','source_kpi_id',
      'start_date','end_date','created_at','updated_at'],
     to_process_kpis())

bulk('process_sub_strategy_links',
     ['process_id','sub_strategy_id','contribution_pct'],
     to_pssl())

bulk('kpi_data',
     ['id','process_kpi_id','year','data_date',
      'period_type','period_no','period_month',
      'target_value','actual_value','status','status_percentage','description',
      'user_id','created_at','updated_at',
      'is_active','deleted_at','deleted_by_id'],
     to_kpi_data())

bulk('individual_performance_indicators',
     ['id','user_id','name','description','code',
      'target_value','actual_value','unit','period','weight','is_important',
      'start_date','end_date','status','source',
      'source_process_id','source_process_kpi_id','direction',
      'basari_puani_araliklari','plan_year_id','source_individual_kpi_id',
      'is_active','created_at','updated_at'],
     to_ipi())

bulk('individual_kpi_data',
     ['id','individual_pg_id','year','data_date',
      'period_type','period_no','period_month',
      'target_value','actual_value','status','status_percentage','description',
      'user_id','created_at','updated_at'],
     to_ind_kpi_data())

bulk('swot_analyses',
     ['id','plan_year_id','tenant_id','source_swot_id',
      'strengths','weaknesses','opportunities','threats',
      'created_at','updated_at'],
     to_swot())

bulk('pestel_analyses',
     ['id','plan_year_id','tenant_id','source_pestel_id',
      'political','economic','social','technological','environmental','legal',
      'created_at','updated_at'],
     to_pestel())

bulk('porter_analyses',
     ['id','plan_year_id','tenant_id','source_porter_id',
      'rivalry_intensity','supplier_power','buyer_power','new_entrant_threat','substitute_threat',
      'created_at','updated_at'],
     to_porter())

bulk('okr_objectives',
     ['id','tenant_id','plan_year_id','title','description','quarter','owner','order_no',
      'linked_strategy_id','linked_sub_strategy_id','is_active','created_at','updated_at'],
     to_okr_obj())

bulk('okr_key_results',
     ['id','objective_id','title','metric','start_value','target_value','current_value',
      'order_no','linked_process_kpi_id','is_active','created_at','updated_at'],
     to_okr_kr())

bulk('esg_metrics',
     ['id','tenant_id','code','name','description','category','scope','unit','sdg_codes',
      'target_value','baseline_year','baseline_value','is_active','created_at','updated_at'],
     to_esg_metrics())

bulk('esg_metric_values',
     ['id','metric_id','year','period_type','period_no','value','source','notes',
      'user_id','created_at'],
     to_esg_values())

bulk('process_maturity',
     ['id','tenant_id','process_id','maturity_level','dimension','assessed_by','assessed_at',
      'is_active','created_at','updated_at'],
     to_process_maturity())

bulk('risk_heatmap_items',
     ['id','tenant_id','plan_year_id','title','probability','impact','rpn',
      'owner_id','status','source_type','is_active','created_at','updated_at'],
     to_risk_heatmap())

bulk('initiatives',
     ['id','tenant_id','code','name','description','strategy_id','sub_strategy_id',
      'start_year','end_year','start_date','end_date','status','priority',
      'budget_total','budget_spent','progress_pct','owner_user_id',
      'is_active','created_at','updated_at'],
     to_initiatives())

bulk('initiative_milestones',
     ['id','initiative_id','name','target_date','completed_date','status','note',
      'order_index','created_at'],
     to_init_milestones())

bulk('plan_projects',
     ['id','plan_year_id','tenant_id','source_project_id','name','description',
      'status','progress','start_date','end_date','is_active','created_at','updated_at'],
     to_plan_projects())

bulk('plan_project_tasks',
     ['id','project_id','plan_year_id','assignee_id','name','description',
      'status','start_date','end_date','is_active',
      'progress_pct','planned_budget','actual_cost','depends_on_task_id',
      'created_at','updated_at'],
     to_plan_project_tasks())

bulk('k_vektor_strategy_weights',
     ['id','tenant_id','strategy_id','weight_raw'],
     to_kv_strategy())

bulk('strategy_year_configs',
     ['id','plan_year_id','strategy_id','title','code','description','is_included','weight',
      'created_at','updated_at'],
     to_strategy_year_configs())

bulk('sub_strategy_year_configs',
     ['id','plan_year_id','sub_strategy_id','title','code','description','is_included',
      'created_at','updated_at'],
     to_sub_strategy_year_configs())

bulk('process_year_configs',
     ['id','plan_year_id','process_id','name','weight','is_included','created_at','updated_at'],
     to_process_year_configs())

bulk('kpi_year_configs',
     ['id','plan_year_id','process_kpi_id','target_value','unit','period',
      'direction','target_method','calculation_method','basari_puani_araliklari',
      'onceki_yil_ortalamasi','weight','is_included','created_at','updated_at'],
     to_kpi_year_configs())

# ─── SELF-REF 2nd PASS ──────────────────────────────────────────────────
SELF_REF_UPDATES = [
    ('plan_years', 'template_source_id', 'plan_years', 'id'),
    ('plan_years', 'scenario_of_id', 'plan_years', 'id'),
    ('strategies', 'source_strategy_id', 'strategies', 'id'),
    ('sub_strategies', 'source_sub_strategy_id', 'sub_strategies', 'id'),
    ('processes', 'parent_id', 'processes', 'id'),
    ('processes', 'source_process_id', 'processes', 'id'),
    ('process_kpis', 'source_kpi_id', 'process_kpis', 'id'),
    ('individual_performance_indicators', 'source_individual_kpi_id', 'individual_performance_indicators', 'id'),
    ('swot_analyses', 'source_swot_id', 'swot_analyses', 'id'),
    ('pestel_analyses', 'source_pestel_id', 'pestel_analyses', 'id'),
    ('porter_analyses', 'source_porter_id', 'porter_analyses', 'id'),
    ('plan_projects', 'source_project_id', 'plan_projects', 'id'),
    ('plan_project_tasks', 'depends_on_task_id', 'plan_project_tasks', 'id'),
]
update_self_refs()

# ─── SEQUENCE RESET ─────────────────────────────────────────────────────
print("\n-- Sequence reset --")
SEQ_TABLES = [
    'plan_years','tenant_year_identities','strategies','sub_strategies','processes',
    'process_kpis','kpi_data','individual_performance_indicators','individual_kpi_data',
    'swot_analyses','pestel_analyses','porter_analyses',
    'okr_objectives','okr_key_results','esg_metrics','esg_metric_values',
    'process_maturity','risk_heatmap_items',
    'initiatives','initiative_milestones','plan_projects','plan_project_tasks',
    'k_vektor_strategy_weights',
    'strategy_year_configs','sub_strategy_year_configs','process_year_configs','kpi_year_configs',
]
for t in SEQ_TABLES:
    if t not in EXISTING: continue
    try:
        cur.execute(f"SELECT setval(pg_get_serial_sequence('{t}','id'), COALESCE((SELECT MAX(id) FROM {t}),1))")
    except Exception as e:
        print(f"  ! {t}: {e}")
print(f"  {len(SEQ_TABLES)} sequence reset edildi")

print()
if COMMIT:
    conn.commit()
    print("COMMIT — veri yüklendi.")
else:
    conn.rollback()
    print("DRY RUN — rollback edildi. IMPORT_COMMIT=1 ile tekrar çalıştır.")
cur.close(); conn.close()
