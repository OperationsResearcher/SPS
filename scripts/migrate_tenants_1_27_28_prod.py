"""
Yerel PostgreSQL'deki tenant_id 1/27/28 (Default Corp, Tomofil Otomotiv,
Eskisehir Makine) verisini Yayin (production, www.kokpitim.com, PG14)
veritabanina tasir.

ONEMLI — CALISTIRMADAN ONCE:
  1. Bu script SSH tunelini KENDISI ACMAZ. Ayri bir terminalde:
       ssh -i C:\\crt\\ssh-key-2026-04-18_v4.key -L 15432:localhost:5432 ubuntu@129.159.30.175 -N
     tuneli acik tutulmali (script calisirken pencere kapatilmamali).
  2. Ortam degiskenleri (PowerShell):
       $env:PROD_DB_PASSWORD = "<kokpitim_user sifresi>"
       $env:DRY_RUN = "True"   # varsayilan True; gercek yazim icin "False" yap
  3. Yayin'da onceden TAM DB yedegi alinmis olmali (bu is oncesi zaten alindi:
     /opt/kokpitim/backups/pre_tenant_migration_pg_20260706_200122.dump).

KAPSAM:
  - Yerel tenant_id IN (1, 27, 28) -> Yayin ayni tenant_id'lerin YERINE.
  - Yayin'daki tenant_id IN (16, 29, 30, 31) HIC DOKUNULMAZ (yalniz salt-okunur sayim).
  - tenant_id SABIT kalir (1->1, 27->27, 28->28). Icindeki BAGIMLI kayitlarin (users,
    processes, strategies, kpi_data, ...) id'leri Yayin'da YENIDEN uretilir (id-remap),
    cunku 'users' tablosunda id araligi ciddi cakisiyor (bkz. plan dosyasi).

CALISTIRMA:
  cd C:\\kokpitim
  .venv\\Scripts\\python.exe scripts\\migrate_tenants_1_27_28_prod.py

Her adim oncesi kullanicidan 'EVET' onayi ister. DRY_RUN=True iken hicbir INSERT/DELETE
YAYIN'a yazilmaz, sadece rapor uretilir (yerel DB'ye yazma zaten hic yapilmaz).
"""

import os
import re
import sys
from collections import OrderedDict
from datetime import datetime
from pathlib import Path

import psycopg2
import psycopg2.extras

# ── Genel ayarlar ────────────────────────────────────────────────────────────

ROOT = Path(__file__).parent.parent
TARGET_TENANT_IDS = (1, 27, 28)
UNTOUCHED_TENANT_IDS = (16, 29, 30, 31)  # Kayseri MF, Kara Brothers, VolTure Tech x2

DRY_RUN = os.environ.get("DRY_RUN", "True").strip().lower() not in ("false", "0", "no")

PROD_DB_HOST = "localhost"
PROD_DB_PORT = int(os.environ.get("PROD_DB_PORT", "15432"))  # SSH tunel hedef portu
PROD_DB_NAME = "kokpitim_db"
PROD_DB_USER = "kokpitim_user"
# PROD_DB_PASSWORD_FILE: sifreyi shell/process ortamina degil, salt-okunur bir
# dosyadan okumak icin (VM uzerinde calistirirken SSH komut gecmisinde/process
# listesinde sifrenin gorunmesini onlemek amaciyla eklendi).
if os.environ.get("PROD_DB_PASSWORD_FILE"):
    PROD_DB_PASSWORD = Path(os.environ["PROD_DB_PASSWORD_FILE"]).read_text(encoding="utf-8").strip()
else:
    PROD_DB_PASSWORD = os.environ.get("PROD_DB_PASSWORD")

# KAYIT_DOSYA_DIR override: script /tmp gibi proje disi bir yerden calistirilirsa
# (ornek: VM host'unda dogrudan calistirma, bkz. ust bilgideki performans notu)
# ROOT/docs/kontrol yazma izni olmayabilir — bu durumda KAYIT_DOSYA_DIR ile
# alternatif bir dizin (orn. /tmp) belirtilebilir.
_kayit_dir = Path(os.environ["KAYIT_DOSYA_DIR"]) if os.environ.get("KAYIT_DOSYA_DIR") else (ROOT / "docs" / "kontrol")
KAYIT_DOSYASI = _kayit_dir / f"yayinverileri_{datetime.now().strftime('%Y-%m-%d_%H%M')}.md"

REFERANS_KMF = {
    # docs/kontrol/yayinverileri_2026-07-06_2200.md — Kayseri MF (16) referans sayimlari
    "users": 8,
    "processes": 11,
    "process_kpis": 146,
    "kpi_data": 497,
    "strategies": 6,
}


AUTO_YES = os.environ.get("AUTO_YES", "").strip().lower() in ("1", "true", "yes")


def onay_al(mesaj: str) -> None:
    """Kullaniciya 'EVET' yazdirmadan bir sonraki adima gecirmez.

    AUTO_YES=1 ortam degiskeni ile onaylar otomatik gecilir — SADECE DRY_RUN=True
    ile birlikte kontrollu test/provalarda kullanilmali (stdin pipe'in Windows'ta
    uzun suren DB islemlerinden sonraki input() cagrisini bloke ettigi bu oturumda
    kesfedildi). Gercek migration (DRY_RUN=False) icin AUTO_YES KULLANILMAMALI —
    her adim elle onaylanmali.
    """
    print(f"\n{'=' * 70}")
    print(mesaj)
    print("=" * 70)
    if AUTO_YES:
        print("AUTO_YES=1: onay otomatik gecildi (SADECE DRY_RUN test modu icin).")
        return
    cevap = input("Devam etmek icin 'EVET' yazin (baska her sey durdurur): ").strip()
    if cevap != "EVET":
        print("Onay alinamadi. Script durduruluyor.")
        sys.exit(1)


# ── Baglanti yardimcilari ────────────────────────────────────────────────────

def yerel_baglanti_bilgisi():
    """Yerel DB baglanti bilgisini dondurur.

    Oncelik: LOCAL_DB_* ortam degiskenleri (script'i Yayin VM'inde calistirirken
    kullanilir — VM'de .env yok, yerele ters SSH tuneli uzerinden erisilir, bkz.
    'ssh -R 15433:localhost:5432' notu ust bilgide). Bunlar yoksa .env'den
    SQLALCHEMY_DATABASE_URI parse edilir (yerel makineden calisirken).
    """
    if os.environ.get("LOCAL_DB_HOST"):
        return dict(
            dbname=os.environ.get("LOCAL_DB_NAME", "kokpitim_db"),
            user=os.environ.get("LOCAL_DB_USER", "kokpitim_user"),
            password=os.environ.get("LOCAL_DB_PASSWORD", ""),
            host=os.environ["LOCAL_DB_HOST"],
            port=os.environ.get("LOCAL_DB_PORT", "5432"),
        )

    # NOT: kmf_import_local.py'deki regex yalnizca 'postgresql://' onekini
    # yakaliyordu; bu projede URI 'postgresql+psycopg2://' seklinde, bu yuzden
    # regex genisletildi (+psycopg2 opsiyonel).
    env_path = ROOT / ".env"
    env = {}
    for line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        m = re.match(r'^([A-Z_]+)=(.+)$', line.strip())
        if m:
            env[m.group(1)] = m.group(2)

    db_url = env.get("SQLALCHEMY_DATABASE_URI", "")
    m = re.match(r'postgresql(?:\+psycopg2)?://([^:]+):([^@]+)@([^/]+)/(.+)', db_url)
    if not m:
        raise SystemExit(f"Yerel DB URL okunamadi: {db_url}")
    user, pwd, host, dbname = m.groups()
    # host icinde port olabilir (host:port)
    if ":" in host:
        host, port = host.split(":", 1)
    else:
        port = "5432"
    return dict(dbname=dbname, user=user, password=pwd, host=host, port=port)


def baglan_yerel():
    info = yerel_baglanti_bilgisi()
    conn = psycopg2.connect(client_encoding="UTF8", **info)
    conn.autocommit = False
    print(f"Yerel DB'ye baglanildi: {info['dbname']}@{info['host']}:{info['port']}")
    return conn


def baglan_prod():
    if not PROD_DB_PASSWORD:
        raise SystemExit(
            "PROD_DB_PASSWORD ortam degiskeni tanimli degil. "
            "PowerShell: $env:PROD_DB_PASSWORD = '...' seklinde ayarlayip tekrar calistirin."
        )
    conn = psycopg2.connect(
        dbname=PROD_DB_NAME, user=PROD_DB_USER, password=PROD_DB_PASSWORD,
        host=PROD_DB_HOST, port=PROD_DB_PORT, client_encoding="UTF8",
    )
    conn.autocommit = False
    print(f"Yayin DB'ye SSH tuneli uzerinden baglanildi: {PROD_DB_NAME}@localhost:{PROD_DB_PORT}")
    print("  (Tunel acik degilse burada baglanti hatasi alinir — once SSH tunelini acin.)")
    return conn


# ── Tablo plani ──────────────────────────────────────────────────────────────
# Her giris: (tablo_adi, tenant_filtre_tipi, filtre_detaylari, fk_kolonlari)
#   tenant_filtre_tipi:
#     "direct"      -> tabloda dogrudan tenant_id kolonu var, WHERE tenant_id IN (...)
#     "via_users"   -> tabloda tenant_id yok, users tablosu uzerinden erisilir (user_id FK)
#     "via_parent"  -> tabloda tenant_id yok, ust tablo(lar) uzerinden erisilir (parent id remap ile)
#     "special"     -> ozel SELECT (users/tenants)
#   fk_kolonlari: {kolon_adi: remap_edilecek_tablo} - remap_edilecek_tablo None ise
#     (orn. tenant_id) deger degistirilmeden kopyalanir.
#
# SIRA ONEMLI: parent tablolar child'lardan ONCE gelir (INSERT sirasi).
# DELETE SIRASI bunun TERSIDIR (kmf_import_local.py mantigi ile ayni).

# 1. seviye: tenant_id'ye DOGRUDAN bagli (plandaki liste)
TABLES_LEVEL1 = [
    # (tablo, fk_kolonlari)
    ("plan_years",              {"tenant_id": None, "template_source_id": "plan_years", "scenario_of_id": "plan_years"}),
    ("strategies",               {"tenant_id": None, "plan_year_id": "plan_years", "source_strategy_id": "strategies"}),
    ("sub_strategies",           {"strategy_id": "strategies", "plan_year_id": "plan_years", "source_sub_strategy_id": "sub_strategies"}),
    ("processes",                {"tenant_id": None, "parent_id": "processes", "plan_year_id": "plan_years",
                                   "source_process_id": "processes", "deleted_by": "users"}),
    ("process_kpis",             {"process_id": "processes", "sub_strategy_id": "sub_strategies",
                                   "plan_year_id": "plan_years", "source_kpi_id": "process_kpis"}),
    # plan_year_id eksikti — DRY_RUN'da kesfedildi: "bsc_kpi_perspectives_plan_year_id_fkey"
    # ihlaliyle TUM 420 satir atlaniyordu (tenant_id de var ama sabit kalir, remap gerekmez).
    ("bsc_kpi_perspectives",     {"process_kpi_id": "process_kpis", "plan_year_id": "plan_years", "tenant_id": None}),
    ("blue_ocean_canvases",      {"tenant_id": None}),
    ("esg_metrics",              {"tenant_id": None}),
    ("initiatives",              {"tenant_id": None, "strategy_id": "strategies", "sub_strategy_id": "sub_strategies",
                                   "owner_user_id": "users"}),
    ("k_vektor_strategy_weights", {"tenant_id": None, "strategy_id": "strategies"}),
    ("llm_usage_logs",           {"tenant_id": None, "user_id": "users"}),
    ("notifications",            {"user_id": "users", "tenant_id": None, "related_user_id": "users"}),
    ("okr_objectives",           {"tenant_id": None, "plan_year_id": "plan_years",
                                   "linked_strategy_id": "strategies", "linked_sub_strategy_id": "sub_strategies"}),
    ("pestel_analyses",          {"tenant_id": None, "plan_year_id": "plan_years", "source_pestel_id": "pestel_analyses"}),
    ("plan_projects",            {"plan_year_id": "plan_years", "tenant_id": None, "source_project_id": "plan_projects"}),
    ("porter_analyses",          {"tenant_id": None, "plan_year_id": "plan_years", "source_porter_id": "porter_analyses"}),
    ("process_maturity",         {"tenant_id": None, "process_id": "processes", "assessed_by": "users"}),
    # manager_id/deleted_by/initiative_id eksikti — DRY_RUN'da kesfedildi:
    # "project_manager_id_fkey" ihlaliyle satirlar atlaniyordu (manager_id NOT NULL).
    ("project",                  {"tenant_id": None, "manager_id": "users", "deleted_by": "users",
                                   "initiative_id": "initiatives"}),
    ("risk_heatmap_items",       {"tenant_id": None, "plan_year_id": "plan_years", "owner_id": "users"}),
    ("swot_analyses",            {"tenant_id": None, "plan_year_id": "plan_years", "source_swot_id": "swot_analyses"}),
    ("tenant_email_configs",     {"tenant_id": None, "updated_by": "users"}),
    ("tenant_ethics_codes",      {"tenant_id": None}),
    ("tenant_quality_policies",  {"tenant_id": None}),
    ("tenant_values",            {"tenant_id": None}),
    ("tenant_year_identities",   {"plan_year_id": "plan_years", "tenant_id": None}),
    ("value_chain_items",        {"tenant_id": None, "linked_process_id": "processes"}),
]

# Sifir satirli ama script'e dahil edilecek 1. seviye tablolar (tenant_id direkt kolon)
TABLES_LEVEL1_EMPTY = [
    # audit_logs: DRY_RUN provasi sirasinda kesfedildi — users.id'ye FK'li, tenant_id
    # VE user_id kolonu var, 1/27/28'de 149 satir. Silme sirasi users'tan ONCE olmali
    # (aksi halde "audit_logs_user_id_fkey" ihlali — bu turda tam olarak yasandi).
    ("audit_logs",              {"tenant_id": None, "user_id": "users"}),
    ("a3_reports",              {"tenant_id": None}),
    ("ana_strateji",            {"tenant_id": None}),   # legacy tablo — kolon adi netlesmemis, bos ise atlanir
    ("bottleneck_log",          {"tenant_id": None, "process_id": "processes", "kpi_id": "process_kpis"}),
    ("competitor_analyses",     {"tenant_id": None, "plan_year_id": "plan_years"}),
    ("corporate_identity",      {"tenant_id": None}),
    ("deger",                   {"tenant_id": None}),    # legacy
    ("etik_kural",              {"tenant_id": None}),    # legacy
    ("evm_snapshots",           {"tenant_id": None, "project_id": "project"}),
    ("k_radar_recommendation_actions", {"tenant_id": None, "user_id": "users"}),
    ("k_vektor_config_snapshots", {"tenant_id": None, "user_id": "users"}),
    ("k_vektor_sub_strategy_weights", {"tenant_id": None, "sub_strategy_id": "sub_strategies"}),
    ("kalite_politikasi",       {"tenant_id": None}),    # legacy
    ("kurum",                   {}),                      # legacy, id=tenant_id ile birebir esler varsayimi belirsiz -> bos, atla
    ("llm_quota_overrides",     {"tenant_id": None}),
    ("replan_triggers",         {"tenant_id": None, "target_kpi_id": "process_kpis"}),
    ("stakeholder_maps",        {"tenant_id": None, "plan_year_id": "plan_years"}),
    ("stakeholder_surveys",     {"tenant_id": None}),
    ("tenant_llm_configs",      {"tenant_id": None}),
    ("tickets",                 {"user_id": "users", "tenant_id": None}),
    ("tows_analyses",           {"tenant_id": None, "plan_year_id": "plan_years", "source_tows_id": "tows_analyses"}),
    ("user_year_assignments",   {"user_id": "users", "plan_year_id": "plan_years", "tenant_id": None}),
    ("vrio_resources",          {"tenant_id": None}),
]

# 2. seviye: tenant_id YOK, process_id/strategy_id/user_id vb. uzerinden 1/27/28'e bagli.
# INSERT SIRASI: process_kpis/processes/sub_strategies/users/individual_performance_indicators
# vb. YUKARIDA (Level 1) zaten yuklendikten SONRA calisir.
TABLES_LEVEL2 = [
    ("process_sub_strategy_links", {"process_id": "processes", "sub_strategy_id": "sub_strategies"}),  # composite PK, id yok
    ("process_members",          {"process_id": "processes", "user_id": "users"}),   # composite PK, id yok
    ("process_leaders",          {"process_id": "processes", "user_id": "users"}),   # composite PK, id yok
    ("process_owners_table",     {"process_id": "processes", "user_id": "users"}),   # composite PK, id yok
    ("process_activities",       {"process_id": "processes", "process_kpi_id": "process_kpis",
                                   "plan_year_id": "plan_years", "source_activity_id": "process_activities",
                                   "auto_pgv_kpi_data_id": "kpi_data"}),
    ("process_activity_assignees", {"activity_id": "process_activities", "user_id": "users", "assigned_by": "users"}),  # composite PK
    ("kpi_data",                  {"process_kpi_id": "process_kpis"}),
    ("kpi_data_audits",           {"kpi_data_id": "kpi_data", "user_id": "users"}),
    ("individual_performance_indicators", {"user_id": "users", "source_process_id": "processes",
                                            "source_process_kpi_id": "process_kpis", "strategy_id": "strategies",
                                            "plan_year_id": "plan_years",
                                            "source_individual_kpi_id": "individual_performance_indicators"}),
    ("individual_kpi_data",        {"individual_pg_id": "individual_performance_indicators", "user_id": "users"}),
    ("individual_kpi_data_audits", {"individual_kpi_data_id": "individual_kpi_data", "user_id": "users"}),
    ("favorite_kpis",              {"user_id": "users", "process_kpi_id": "process_kpis"}),
    ("okr_key_results",            {"objective_id": "okr_objectives", "linked_process_kpi_id": "process_kpis"}),
    ("initiative_milestones",      {"initiative_id": "initiatives"}),
    ("esg_metric_values",          {"metric_id": "esg_metrics", "user_id": "users"}),
    ("blue_ocean_factors",         {"canvas_id": "blue_ocean_canvases"}),
    ("blue_ocean_errc_items",      {"canvas_id": "blue_ocean_canvases"}),
    ("strategy_year_configs",      {"plan_year_id": "plan_years", "strategy_id": "strategies"}),
    ("sub_strategy_year_configs",  {"plan_year_id": "plan_years", "sub_strategy_id": "sub_strategies"}),
    ("process_year_configs",       {"plan_year_id": "plan_years", "process_id": "processes"}),
    ("kpi_year_configs",           {"plan_year_id": "plan_years", "process_kpi_id": "process_kpis"}),
    ("individual_kpi_year_configs", {"plan_year_id": "plan_years", "individual_performance_id": "individual_performance_indicators"}),
    ("plan_project_activities",    {"project_id": "plan_projects", "plan_year_id": "plan_years"}),
    ("plan_project_tasks",         {"project_id": "plan_projects", "plan_year_id": "plan_years",
                                     "assignee_id": "users", "depends_on_task_id": "plan_project_tasks"}),
    # Task / proje portfoyu (legacy 'project' tablosu tenant_id'li; 'task' project_id uzerinden bagli)
    ("task",                       {"project_id": "project", "assignee_id": "users", "reporter_id": "users",
                                     "parent_id": "task", "process_kpi_id": "process_kpis"}),
    ("task_baseline",              {"task_id": "task"}),
    ("recurring_task",             {"project_id": "project", "template_task_id": "task"}),
    ("raid_item",                  {"project_id": "project", "owner_id": "users"}),
    ("project_risk",               {"project_id": "project"}),
    ("working_day",                {"project_id": "project"}),
    ("capacity_plan",              {"project_id": "project", "user_id": "users"}),
    ("integration_hook",           {"project_id": "project"}),
    ("rule_definition",            {"project_id": "project"}),
    ("sla",                        {"project_id": "project"}),
    ("replan_trigger_events",      {"trigger_id": "replan_triggers", "acknowledged_by_user_id": "users"}),
]

# Sifir satirli 2. seviye tablolar (bulgular: yerelde 0 satir olabilir, ama sema/kod destegi kalsin)
TABLES_LEVEL2_EMPTY = [
    # (yukaridaki listede zaten yer alanlar tekrar edilmiyor; bu bolum "gorev
    # listesinde 0 satir dendigi icin ayrica belirtilenler" icin placeholder.
    # Fiili calisma zamaninda satir sayisi 0 ise otomatik olarak "atlaniyor" loglanir,
    # bu yuzden TABLES_LEVEL1_EMPTY/TABLES_LEVEL2 ayrimi sadece dokumantasyon amaclidir.)
]

# Tum tablolarin (silme + trigger disable + kopyalama) TEK birlesik sirali listesi.
# INSERT sirasi (parent -> child):
ALL_TABLES_INSERT_ORDER = (
    [("tenants", {})]  # ozel: sadece guncelleme, id sabit — asagida ayri ele alinir
    + [t for t in TABLES_LEVEL1 if t[0] not in ("tenants",)]
    + TABLES_LEVEL1_EMPTY
    + TABLES_LEVEL2
    + TABLES_LEVEL2_EMPTY
)

# DELETE sirasi tam TERSI (child -> parent), + users + tenants en sonda silinir.
ALL_TABLES_DELETE_ORDER = list(reversed([t[0] for t in ALL_TABLES_INSERT_ORDER if t[0] != "tenants"])) + ["users"]

# users tablosu: tenant_id direkt kolon, TABLES_LEVEL1'in mantigen basinda olmali
# (processes/strategies vb. deleted_by/owner_id gibi FK'leri users'a verdigi icin
# users'in prod'da ONCE var olmasi lazim). users, INSERT_ORDER'da en basa eklenir:
TABLES_LEVEL1.insert(0, ("users", {"tenant_id": None, "role_id": None}))  # role_id: PAYLASILAN tablo, remap EDILMEZ


def sirali_tablo_listesi():
    """(tablo, fk_map) ciftlerini INSERT sirasiyla dondurur (users basta)."""
    seen = set()
    out = []
    for tbl, fk in TABLES_LEVEL1 + TABLES_LEVEL1_EMPTY + TABLES_LEVEL2 + TABLES_LEVEL2_EMPTY:
        if tbl in seen:
            continue
        seen.add(tbl)
        out.append((tbl, fk))
    return out


# Trigger disable icin TUM tablolar (FK'li her tablo + guvenlik icin ekstra bilinen tablolar)
TABLES_WITH_FK = [t for t, _ in sirali_tablo_listesi()] + ["tenants"]


# ── ADIM 1: snapshot_and_verify ──────────────────────────────────────────────

def satir_sayisi(cur, tablo, where_sql, params, conn=None):
    """Satir sayar. Tablo/kolon yoksa (Yayin semasi yerelden geri kalmis olabilir —
    ornek: tenant_ethics_codes/tenant_quality_policies/tenant_values yerelde var,
    Yayin'da henuz yok) 0 doner.

    KRITIK (tek-transaction mimarisi ile kesfedilen ciddi hata): 'conn.rollback()'
    ile hata izolasyonu, snapshot_and_verify() (ADIM 1, henuz hicbir DELETE/INSERT
    yokken) icin GUVENLIYDI, ama verify() (ADIM 5, DELETE+INSERT'ten SONRA) icin
    AYNI cagri TUM migration'i SESSIZCE geri aliyordu — ADIM 5'te tenant_ethics_codes
    gibi eksik bir tablo sorgulanip conn.rollback() tetiklendiginde, o ana kadar
    yapilan TUM silme+kopyalama islemleri kayboluyordu (esg_metrics/okr_objectives
    gibi basariyla kopyalanmis tablolarin verify'da 0 cikmasi bu turda boyle
    kesfedildi). Bu yuzden artik conn.rollback() KULLANILMIYOR — SAVEPOINT ile
    yalniz bu sorgu izole edilir, ana transaction'daki onceki degisiklikler korunur.
    """
    if conn is not None:
        cur.execute("SAVEPOINT sp_sayim")
    try:
        cur.execute(f"SELECT count(*) FROM {tablo} WHERE {where_sql}", params)
        sonuc = cur.fetchone()[0]
        if conn is not None:
            cur.execute("RELEASE SAVEPOINT sp_sayim")
        return sonuc
    except Exception as e:
        print(f"    UYARI: {tablo} sayilamadi ({e}) -> 0 varsayildi")
        if conn is not None:
            cur.execute("ROLLBACK TO SAVEPOINT sp_sayim")
            cur.execute("RELEASE SAVEPOINT sp_sayim")
        return 0


def tenant_id_filtreli_sayim(cur, tenant_ids, conn=None):
    """Her tablo icin (dogrudan tenant_id kolonu varsa) satir sayisini dondurur."""
    sonuc = OrderedDict()
    ids_tuple = tuple(tenant_ids)
    for tbl, fk in sirali_tablo_listesi():
        if tbl == "users":
            n = satir_sayisi(cur, "users", "tenant_id IN %s", (ids_tuple,), conn=conn)
        elif "tenant_id" in fk:
            n = satir_sayisi(cur, tbl, "tenant_id IN %s", (ids_tuple,), conn=conn)
        else:
            n = None  # dogrudan tenant_id yok, transitif — ayri hesaplanmali
        sonuc[tbl] = n
    return sonuc


def _joinli_sayim(cur, conn, sql):
    """JOIN'li COUNT sorgusu — tablo/kolon yoksa (Yayin semasi geri kalmis olabilir)
    0 doner. SAVEPOINT ile izole edilir (bkz. satir_sayisi() docstring — conn.rollback()
    tek-transaction mimarisinde ADIM 5'te tum migration'i sessizce geri aliyordu)."""
    cur.execute("SAVEPOINT sp_join_sayim")
    try:
        cur.execute(sql)
        sonuc = cur.fetchone()[0]
        cur.execute("RELEASE SAVEPOINT sp_join_sayim")
        return sonuc
    except Exception as e:
        print(f"    UYARI: sayilamadi ({e}) -> 0 varsayildi")
        cur.execute("ROLLBACK TO SAVEPOINT sp_join_sayim")
        cur.execute("RELEASE SAVEPOINT sp_join_sayim")
        return 0


def snapshot_and_verify(conn_prod, conn_local):
    """On kontroller: satir sayimi + Kayseri MF referans karsilastirma + email cakisma."""
    cur_prod = conn_prod.cursor()

    print("\n--- ADIM 1: Yayin'da mevcut durumun kaydi ve dogrulama ---")

    # (a) Yayin'da 1/27/28 mevcut satir sayilari (rollback referansi)
    print("Yayin'da 1/27/28 mevcut sayimlar aliniyor...")
    mevcut_1_27_28 = tenant_id_filtreli_sayim(cur_prod, TARGET_TENANT_IDS, conn=conn_prod)

    # (b) Yayin'da 16/29/30/31 referans sayim + Kayseri MF karsilastirma
    print("Yayin'da 16/29/30/31 sayimlari aliniyor (dokunulmayacaklarin dogrulamasi)...")
    mevcut_16_29_30_31 = tenant_id_filtreli_sayim(cur_prod, UNTOUCHED_TENANT_IDS, conn=conn_prod)

    sapma_var = False
    for kolon, beklenen in REFERANS_KMF.items():
        if kolon == "users":
            gercek = satir_sayisi(cur_prod, "users", "tenant_id = 16", (), conn=conn_prod)
        elif kolon in ("processes", "process_kpis", "kpi_data", "strategies"):
            if kolon == "processes":
                gercek = satir_sayisi(cur_prod, "processes", "tenant_id = 16", (), conn=conn_prod)
            elif kolon == "strategies":
                gercek = satir_sayisi(cur_prod, "strategies", "tenant_id = 16", (), conn=conn_prod)
            elif kolon == "process_kpis":
                gercek = _joinli_sayim(
                    cur_prod, conn_prod,
                    "SELECT count(*) FROM process_kpis pk JOIN processes p ON p.id=pk.process_id WHERE p.tenant_id=16",
                )
            else:  # kpi_data
                gercek = _joinli_sayim(
                    cur_prod, conn_prod,
                    "SELECT count(*) FROM kpi_data kd JOIN process_kpis pk ON pk.id=kd.process_kpi_id "
                    "JOIN processes p ON p.id=pk.process_id WHERE p.tenant_id=16",
                )
        else:
            continue
        durum = "OK" if gercek == beklenen else "SAPMA"
        if durum == "SAPMA":
            sapma_var = True
        print(f"  Kayseri MF (16) {kolon}: beklenen={beklenen} gercek={gercek} -> {durum}")

    if sapma_var:
        print("\nHATA: Kayseri MF (16) referans sayimlarinda sapma var. "
              "Bu, Yayin'da bu turdan beri veri degistigini gosterir. Script DURUYOR.")
        sys.exit(1)

    # (c) Email cakisma kontrolu
    print("\nEmail cakisma kontrolu (yerel 1/27/28 vs Yayin 16/29/30/31)...")
    cur_local = conn_local.cursor()
    cur_local.execute("SELECT lower(email) FROM users WHERE tenant_id IN %s", (TARGET_TENANT_IDS,))
    yerel_emailler = {r[0] for r in cur_local.fetchall()}

    cur_prod.execute("SELECT lower(email) FROM users WHERE tenant_id IN %s", (UNTOUCHED_TENANT_IDS,))
    prod_emailler = {r[0] for r in cur_prod.fetchall()}

    cakisan = sorted(yerel_emailler & prod_emailler)
    if cakisan:
        print(f"\nHATA: {len(cakisan)} email cakismasi bulundu:")
        for e in cakisan:
            print(f"  - {e}")
        print("Script DURUYOR — karar kullaniciya birakildi (otomatik cozulmez).")
        sys.exit(1)
    else:
        print("  Email cakismasi YOK.")

    # (d) Yerelden 1/27/28 sayimlari (karsilastirma icin)
    print("\nYerelden 1/27/28 sayimlari aliniyor...")
    yerel_1_27_28 = tenant_id_filtreli_sayim(cur_local, TARGET_TENANT_IDS, conn=conn_local)

    # Kayit dosyasi yaz
    KAYIT_DOSYASI.parent.mkdir(parents=True, exist_ok=True)
    with open(KAYIT_DOSYASI, "w", encoding="utf-8") as f:
        f.write(f"# Yayin verileri kaydi — {datetime.now().isoformat()}\n\n")
        f.write("## Migration ONCESI — Yayin'da 1/27/28 mevcut satir sayimlari (silinecek)\n\n")
        f.write("| Tablo | Satir |\n|---|---|\n")
        for tbl, n in mevcut_1_27_28.items():
            f.write(f"| {tbl} | {n if n is not None else 'transitif (asagida)'} |\n")
        f.write("\n## Yayin'da 16/29/30/31 mevcut sayimlar (DEGISMEMELI)\n\n")
        f.write("| Tablo | Satir |\n|---|---|\n")
        for tbl, n in mevcut_16_29_30_31.items():
            f.write(f"| {tbl} | {n if n is not None else 'transitif (asagida)'} |\n")
        f.write("\n## Yerelden gelecek 1/27/28 sayimlari (Yayin sonrasi bunlarla eslesecek)\n\n")
        f.write("| Tablo | Satir |\n|---|---|\n")
        for tbl, n in yerel_1_27_28.items():
            f.write(f"| {tbl} | {n if n is not None else 'transitif (asagida)'} |\n")

    print(f"\nKayit dosyasi yazildi: {KAYIT_DOSYASI}")
    return mevcut_16_29_30_31, yerel_1_27_28


# ── ADIM 2: delete_target_tenants ────────────────────────────────────────────

def delete_target_tenants(conn_prod):
    """Yayin'da 1/27/28'e ait TUM veriyi siler (users + tenants dahil).

    NOT: PostgreSQL'de FK constraint trigger'lari ("RI_ConstraintTrigger_*") SISTEM
    trigger'idir — normal DB kullanicisi (kokpitim_user, superuser degil) bunlari
    DISABLE edemez ("permission denied: is a system trigger"). Bu BEKLENEN bir
    durumdur ve script'in FK sirasini (child->parent DELETE_SQL sirasi) zaten dogru
    kurdugu icin sorun YARATMAZ.

    KRITIK (tum migration TEK transaction'da yurutulur — DRY_RUN'in silme ve
    kopyalama adimlarini AYRI rollback etmesi, kopyalama asamasinin hala YAYINDA
    DURAN eski veriyle (orn. users.email UNIQUE) sahte cakisma yasamasina yol
    aciyordu; bu turda kesfedildi, 132 kullanicinin TAMAMI "duplicate key" verdi).
    Bu yuzden BURADA conn.rollback()/commit() CAGRILMAZ — sadece SAVEPOINT ile
    hata izolasyonu yapilir, connection seviyesinde commit/rollback karari SADECE
    main()'in en sonunda, TUM adimlar bittikten sonra tek seferde verilir.
    """
    cur = conn_prod.cursor()
    print("\n--- ADIM 2: Yayin'da 1/27/28 verisi siliniyor ---")

    cur.execute("SAVEPOINT sp_trigdis")
    for t in TABLES_WITH_FK:
        try:
            cur.execute(f"ALTER TABLE {t} DISABLE TRIGGER ALL")
            cur.execute("RELEASE SAVEPOINT sp_trigdis")
            cur.execute("SAVEPOINT sp_trigdis")
        except Exception as e:
            print(f"  UYARI: {t} icin TRIGGER DISABLE basarisiz (atlaniyor): {e}")
            cur.execute("ROLLBACK TO SAVEPOINT sp_trigdis")
    cur.execute("RELEASE SAVEPOINT sp_trigdis")

    try:
        ids = tuple(TARGET_TENANT_IDS)

        # Child -> parent sirasi (ALL_TABLES_DELETE_ORDER), en direkt yol: tenant_id
        # kolonu olan tablolarda WHERE tenant_id IN (...), transitif olanlarda USING join.
        DELETE_SQL = OrderedDict([
            # --- 2. seviye (transitif), en derinden basliyoruz ---
            ("replan_trigger_events", "DELETE FROM replan_trigger_events rte USING replan_triggers rt WHERE rte.trigger_id=rt.id AND rt.tenant_id IN %(ids)s"),
            ("individual_kpi_data_audits", "DELETE FROM individual_kpi_data_audits ika USING individual_kpi_data ikd, individual_performance_indicators ipi, users u WHERE ika.individual_kpi_data_id=ikd.id AND ikd.individual_pg_id=ipi.id AND ipi.user_id=u.id AND u.tenant_id IN %(ids)s"),
            ("individual_kpi_data", "DELETE FROM individual_kpi_data ikd USING individual_performance_indicators ipi, users u WHERE ikd.individual_pg_id=ipi.id AND ipi.user_id=u.id AND u.tenant_id IN %(ids)s"),
            ("individual_kpi_year_configs", "DELETE FROM individual_kpi_year_configs c USING individual_performance_indicators ipi, users u WHERE c.individual_performance_id=ipi.id AND ipi.user_id=u.id AND u.tenant_id IN %(ids)s"),
            ("favorite_kpis", "DELETE FROM favorite_kpis fk USING users u WHERE fk.user_id=u.id AND u.tenant_id IN %(ids)s"),
            ("individual_performance_indicators", "DELETE FROM individual_performance_indicators ipi USING users u WHERE ipi.user_id=u.id AND u.tenant_id IN %(ids)s"),
            ("kpi_data_audits", "DELETE FROM kpi_data_audits ka USING kpi_data kd, process_kpis pk, processes p WHERE ka.kpi_data_id=kd.id AND kd.process_kpi_id=pk.id AND pk.process_id=p.id AND p.tenant_id IN %(ids)s"),
            ("kpi_year_configs", "DELETE FROM kpi_year_configs c USING process_kpis pk, processes p WHERE c.process_kpi_id=pk.id AND pk.process_id=p.id AND p.tenant_id IN %(ids)s"),
            ("kpi_data", "DELETE FROM kpi_data kd USING process_kpis pk, processes p WHERE kd.process_kpi_id=pk.id AND pk.process_id=p.id AND p.tenant_id IN %(ids)s"),
            ("okr_key_results", "DELETE FROM okr_key_results kr USING okr_objectives o WHERE kr.objective_id=o.id AND o.tenant_id IN %(ids)s"),
            ("okr_objectives", "DELETE FROM okr_objectives WHERE tenant_id IN %(ids)s"),
            ("process_activity_assignees", "DELETE FROM process_activity_assignees paa USING process_activities pa, processes p WHERE paa.activity_id=pa.id AND pa.process_id=p.id AND p.tenant_id IN %(ids)s"),
            ("process_activities", "DELETE FROM process_activities pa USING processes p WHERE pa.process_id=p.id AND p.tenant_id IN %(ids)s"),
            ("process_year_configs", "DELETE FROM process_year_configs c USING processes p WHERE c.process_id=p.id AND p.tenant_id IN %(ids)s"),
            ("bsc_kpi_perspectives", "DELETE FROM bsc_kpi_perspectives b USING process_kpis pk, processes p WHERE b.process_kpi_id=pk.id AND pk.process_id=p.id AND p.tenant_id IN %(ids)s"),
            ("process_sub_strategy_links", "DELETE FROM process_sub_strategy_links psl USING processes p WHERE psl.process_id=p.id AND p.tenant_id IN %(ids)s"),
            ("process_leaders", "DELETE FROM process_leaders pl USING processes p WHERE pl.process_id=p.id AND p.tenant_id IN %(ids)s"),
            ("process_members", "DELETE FROM process_members pm USING processes p WHERE pm.process_id=p.id AND p.tenant_id IN %(ids)s"),
            ("process_owners_table", "DELETE FROM process_owners_table po USING processes p WHERE po.process_id=p.id AND p.tenant_id IN %(ids)s"),
            ("value_chain_items", "DELETE FROM value_chain_items v USING processes p WHERE v.linked_process_id=p.id AND p.tenant_id IN %(ids)s"),
            ("value_chain_items_direct", "DELETE FROM value_chain_items WHERE tenant_id IN %(ids)s"),
            ("bottleneck_log", "DELETE FROM bottleneck_log WHERE tenant_id IN %(ids)s"),
            ("process_maturity", "DELETE FROM process_maturity WHERE tenant_id IN %(ids)s"),
            ("process_kpis", "DELETE FROM process_kpis pk USING processes p WHERE pk.process_id=p.id AND p.tenant_id IN %(ids)s"),
            ("k_vektor_sub_strategy_weights", "DELETE FROM k_vektor_sub_strategy_weights w USING sub_strategies ss, strategies s WHERE w.sub_strategy_id=ss.id AND ss.strategy_id=s.id AND s.tenant_id IN %(ids)s"),
            ("initiative_milestones", "DELETE FROM initiative_milestones m USING initiatives i WHERE m.initiative_id=i.id AND i.tenant_id IN %(ids)s"),
            ("initiatives", "DELETE FROM initiatives WHERE tenant_id IN %(ids)s"),
            ("strategy_year_configs", "DELETE FROM strategy_year_configs c USING strategies s WHERE c.strategy_id=s.id AND s.tenant_id IN %(ids)s"),
            ("sub_strategy_year_configs", "DELETE FROM sub_strategy_year_configs c USING sub_strategies ss, strategies s WHERE c.sub_strategy_id=ss.id AND ss.strategy_id=s.id AND s.tenant_id IN %(ids)s"),
            ("k_vektor_strategy_weights", "DELETE FROM k_vektor_strategy_weights WHERE tenant_id IN %(ids)s"),
            ("sub_strategies", "DELETE FROM sub_strategies ss USING strategies s WHERE ss.strategy_id=s.id AND s.tenant_id IN %(ids)s"),
            ("processes", "DELETE FROM processes WHERE tenant_id IN %(ids)s"),
            ("strategies", "DELETE FROM strategies WHERE tenant_id IN %(ids)s"),
            ("esg_metric_values", "DELETE FROM esg_metric_values v USING esg_metrics m WHERE v.metric_id=m.id AND m.tenant_id IN %(ids)s"),
            ("esg_metrics", "DELETE FROM esg_metrics WHERE tenant_id IN %(ids)s"),
            ("blue_ocean_factors", "DELETE FROM blue_ocean_factors f USING blue_ocean_canvases c WHERE f.canvas_id=c.id AND c.tenant_id IN %(ids)s"),
            ("blue_ocean_errc_items", "DELETE FROM blue_ocean_errc_items e USING blue_ocean_canvases c WHERE e.canvas_id=c.id AND c.tenant_id IN %(ids)s"),
            ("blue_ocean_canvases", "DELETE FROM blue_ocean_canvases WHERE tenant_id IN %(ids)s"),
            ("vrio_resources", "DELETE FROM vrio_resources WHERE tenant_id IN %(ids)s"),
            ("swot_analyses", "DELETE FROM swot_analyses WHERE tenant_id IN %(ids)s"),
            ("tows_analyses", "DELETE FROM tows_analyses WHERE tenant_id IN %(ids)s"),
            ("pestel_analyses", "DELETE FROM pestel_analyses WHERE tenant_id IN %(ids)s"),
            ("porter_analyses", "DELETE FROM porter_analyses WHERE tenant_id IN %(ids)s"),
            ("competitor_analyses", "DELETE FROM competitor_analyses WHERE tenant_id IN %(ids)s"),
            ("stakeholder_maps", "DELETE FROM stakeholder_maps WHERE tenant_id IN %(ids)s"),
            ("stakeholder_surveys", "DELETE FROM stakeholder_surveys WHERE tenant_id IN %(ids)s"),
            ("risk_heatmap_items", "DELETE FROM risk_heatmap_items WHERE tenant_id IN %(ids)s"),
            ("a3_reports", "DELETE FROM a3_reports WHERE tenant_id IN %(ids)s"),
            ("replan_triggers", "DELETE FROM replan_triggers WHERE tenant_id IN %(ids)s"),
            ("k_vektor_config_snapshots", "DELETE FROM k_vektor_config_snapshots WHERE tenant_id IN %(ids)s"),
            ("k_radar_recommendation_actions", "DELETE FROM k_radar_recommendation_actions WHERE tenant_id IN %(ids)s"),
            ("llm_usage_logs", "DELETE FROM llm_usage_logs WHERE tenant_id IN %(ids)s"),
            ("llm_quota_overrides", "DELETE FROM llm_quota_overrides WHERE tenant_id IN %(ids)s"),
            ("tenant_llm_configs", "DELETE FROM tenant_llm_configs WHERE tenant_id IN %(ids)s"),
            ("tenant_email_configs", "DELETE FROM tenant_email_configs WHERE tenant_id IN %(ids)s"),
            ("tenant_ethics_codes", "DELETE FROM tenant_ethics_codes WHERE tenant_id IN %(ids)s"),
            ("tenant_quality_policies", "DELETE FROM tenant_quality_policies WHERE tenant_id IN %(ids)s"),
            ("tenant_values", "DELETE FROM tenant_values WHERE tenant_id IN %(ids)s"),
            ("tenant_year_identities", "DELETE FROM tenant_year_identities ty USING plan_years py WHERE ty.plan_year_id=py.id AND py.tenant_id IN %(ids)s"),
            ("user_year_assignments", "DELETE FROM user_year_assignments WHERE tenant_id IN %(ids)s"),
            ("okr_objectives_dup_guard", "SELECT 1"),  # no-op guard (siralama kaydi icin)
            ("plan_project_tasks", "DELETE FROM plan_project_tasks t USING plan_projects pp WHERE t.project_id=pp.id AND pp.tenant_id IN %(ids)s"),
            ("plan_project_activities", "DELETE FROM plan_project_activities a USING plan_projects pp WHERE a.project_id=pp.id AND pp.tenant_id IN %(ids)s"),
            ("plan_projects", "DELETE FROM plan_projects WHERE tenant_id IN %(ids)s"),
            ("plan_years", "DELETE FROM plan_years WHERE tenant_id IN %(ids)s"),
            # --- Portfoy/Proje (legacy 'project' + 'task' aile) ---
            ("task_baseline", "DELETE FROM task_baseline tb USING task t, project pr WHERE tb.task_id=t.id AND t.project_id=pr.id AND pr.tenant_id IN %(ids)s"),
            ("recurring_task", "DELETE FROM recurring_task rt USING project pr WHERE rt.project_id=pr.id AND pr.tenant_id IN %(ids)s"),
            ("raid_item", "DELETE FROM raid_item r USING project pr WHERE r.project_id=pr.id AND pr.tenant_id IN %(ids)s"),
            ("project_risk", "DELETE FROM project_risk r USING project pr WHERE r.project_id=pr.id AND pr.tenant_id IN %(ids)s"),
            ("working_day", "DELETE FROM working_day w USING project pr WHERE w.project_id=pr.id AND pr.tenant_id IN %(ids)s"),
            ("capacity_plan", "DELETE FROM capacity_plan c USING project pr WHERE c.project_id=pr.id AND pr.tenant_id IN %(ids)s"),
            ("integration_hook", "DELETE FROM integration_hook h USING project pr WHERE h.project_id=pr.id AND pr.tenant_id IN %(ids)s"),
            ("rule_definition", "DELETE FROM rule_definition r USING project pr WHERE r.project_id=pr.id AND pr.tenant_id IN %(ids)s"),
            ("sla", "DELETE FROM sla s USING project pr WHERE s.project_id=pr.id AND pr.tenant_id IN %(ids)s"),
            ("evm_snapshots", "DELETE FROM evm_snapshots e USING project pr WHERE e.project_id=pr.id AND pr.tenant_id IN %(ids)s"),
            ("task", "DELETE FROM task t USING project pr WHERE t.project_id=pr.id AND pr.tenant_id IN %(ids)s"),
            ("project", "DELETE FROM project WHERE tenant_id IN %(ids)s"),
            # --- users + tenants EN SON ---
            ("notifications", "DELETE FROM notifications WHERE tenant_id IN %(ids)s"),
            ("tickets", "DELETE FROM tickets WHERE tenant_id IN %(ids)s"),
            # audit_logs users'a FK'li (user_id) — DRY_RUN'da kesfedildi, users'tan
            # ONCE silinmezse "audit_logs_user_id_fkey" ihlali olur.
            ("audit_logs", "DELETE FROM audit_logs WHERE tenant_id IN %(ids)s"),
            ("users", "DELETE FROM users WHERE tenant_id IN %(ids)s"),
        ])

        for label, sql in DELETE_SQL.items():
            if sql == "SELECT 1":
                continue
            # KRITIK: her DELETE'ten ONCE kendi savepoint'i alinir. Hata olursa SADECE
            # o statement'in savepoint'ine donulur — 'before_delete' gibi TEK bir
            # ortak savepoint'e donmek, o ana kadar basariyla silinmis TUM tablolari
            # da geri alirdi (orn. tenant_ethics_codes hatasi kpi_data'nin 91995
            # satirlik silinmesini de rollback ederdi — bu turda yasandi).
            safe_label = re.sub(r"[^a-z0-9_]", "_", label)
            cur.execute(f"SAVEPOINT sp_{safe_label}")
            try:
                cur.execute(sql, {"ids": ids})
                if cur.rowcount > 0:
                    print(f"  Silindi ({cur.rowcount}): {label}")
                cur.execute(f"RELEASE SAVEPOINT sp_{safe_label}")
            except Exception as e:
                print(f"  UYARI: {label} silinirken hata (tablo/kolon olmayabilir, atlaniyor): {e}")
                cur.execute(f"ROLLBACK TO SAVEPOINT sp_{safe_label}")
                cur.execute(f"RELEASE SAVEPOINT sp_{safe_label}")

        # tenants tablosunun kendisini SILMIYORUZ cunku tenant_id sabit kaliyor
        # (kararlar bolumu — tenant kimligi degismez, sadece icerigi degisir).
        print("  NOT: 'tenants' satirlari (id=1/27/28) SILINMEDI — tenant_id sabit kalma karari geregi.")
        print("\nSilme adimi tamamlandi (commit/rollback karari main()'in sonunda verilecek).")

    finally:
        # DISABLE ile ayni sekilde: system trigger'lar icin ENABLE de "permission
        # denied" verir (zaten hic disable edilmediler). SAVEPOINT ile izole edilir —
        # conn.rollback() ARTIK cagirilmaz (tek-transaction mimarisi, yukaridaki not).
        cur.execute("SAVEPOINT sp_trigen")
        for t in TABLES_WITH_FK:
            try:
                cur.execute(f"ALTER TABLE {t} ENABLE TRIGGER ALL")
                cur.execute("RELEASE SAVEPOINT sp_trigen")
                cur.execute("SAVEPOINT sp_trigen")
            except Exception:
                cur.execute("ROLLBACK TO SAVEPOINT sp_trigen")
        cur.execute("RELEASE SAVEPOINT sp_trigen")


# ── ADIM 3: copy_with_remap ──────────────────────────────────────────────────

def kolonlari_al(cur, tablo):
    """Kolon adlarini dondurur. cur_local RealDictCursor (dict-benzeri satirlar),
    cur_prod normal cursor (tuple satirlar) olabilir — ikisiyle de calisir."""
    cur.execute(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name=%s ORDER BY ordinal_position", (tablo,)
    )
    rows = cur.fetchall()
    if rows and isinstance(rows[0], dict):
        return [r["column_name"] for r in rows]
    return [r[0] for r in rows]


def copy_with_remap(conn_local, conn_prod, remap):
    """Parent->child sirayla yerelden okuyup Yayin'a id-remap ile yazar.

    remap: {tablo_adi: {eski_id: yeni_id}} — fonksiyon boyunca doldurulur.
    """
    print("\n--- ADIM 3: Veri kopyalaniyor (id-remap ile) ---")
    cur_local = conn_local.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur_prod = conn_prod.cursor()

    CHUNK = 5000
    ids = tuple(TARGET_TENANT_IDS)

    tablolar = sirali_tablo_listesi()

    for tbl, fk_map in tablolar:
        # tenants tablosu ozel: id sabit, sadece UPDATE (silme yok, id remap yok)
        prod_cols = set(kolonlari_al(cur_prod, tbl))
        if not prod_cols:
            print(f"  ATLA (Yayin'da tablo yok): {tbl}")
            continue
        local_cols = set(kolonlari_al(cur_local, tbl))
        ortak_cols = [c for c in local_cols if c in prod_cols]
        if not ortak_cols:
            print(f"  ATLA (ortak kolon yok): {tbl}")
            continue

        has_id_pk = "id" in ortak_cols
        composite_pk = tbl in (
            "process_sub_strategy_links", "process_members", "process_leaders",
            "process_owners_table", "process_activity_assignees",
        )

        # WHERE filtresi: dogrudan tenant_id varsa onu kullan, yoksa uygun JOIN.
        where_sql, join_sql, params = _filtre_olustur(tbl, local_cols, ids)
        if where_sql is None:
            print(f"  ATLA ({tbl}): filtre kurulamadi (bilinmeyen bagimlilik yapisi)")
            continue

        select_cols = ", ".join(f't."{c}"' for c in ortak_cols)
        select_sql = f'SELECT {select_cols} FROM {tbl} t {join_sql} WHERE {where_sql}'

        try:
            cur_local.execute(select_sql, params)
        except Exception as e:
            print(f"  ATLA ({tbl}): SELECT hatasi -> {e}")
            conn_local.rollback()
            continue

        toplam = 0
        hatali = 0
        remap[tbl] = remap.get(tbl, {})
        insert_cols = [c for c in ortak_cols if c != "id"] if has_id_pk else ortak_cols

        while True:
            rows = cur_local.fetchmany(CHUNK)
            if not rows:
                break
            # FK kolonlarini remap et (her satir icin, INSERT'ten once)
            hazirlanan = []  # [(eski_id, values), ...]
            for row in rows:
                row = dict(row)
                eski_id = row.get("id") if has_id_pk else None
                for fk_col, ref_tbl in fk_map.items():
                    if fk_col not in row or fk_col not in insert_cols:
                        continue
                    val = row.get(fk_col)
                    if val is None or ref_tbl is None:
                        continue  # tenant_id gibi sabit kalanlar veya NULL
                    yeni_val = remap.get(ref_tbl, {}).get(val)
                    if yeni_val is None:
                        # Referans tablo bu 3 tenant disina cikiyor olabilir (orn.
                        # source_*_id eski/parent klonlarina isaret edebilir) — NULL yap.
                        row[fk_col] = None
                    else:
                        row[fk_col] = yeni_val
                # JSON/dict kolonlari (orn. audit_logs.old_values/new_values) psycopg2
                # tarafindan otomatik adapt edilemez ("can't adapt type 'dict'" —
                # DRY_RUN'da kesfedildi) — Json() wrapper'i ile sarmalanir.
                degerler = []
                for c in insert_cols:
                    v = row.get(c)
                    if isinstance(v, (dict, list)):
                        v = psycopg2.extras.Json(v)
                    degerler.append(v)
                hazirlanan.append((eski_id, degerler))

            col_sql = ", ".join(f'"{c}"' for c in insert_cols)
            placeholders = ", ".join(["%s"] * len(insert_cols))

            # HIZLI YOL: chunk'in TAMAMI tek savepoint altinda satir-satir denenir
            # (RETURNING id gerektigi icin execute_values kullanilamiyor — id-remap
            # her satirin kendi yeni id'sini gerektiriyor). Performans HALA satir
            # sayisi kadar INSERT yapar ama savepoint/round-trip YALNIZCA chunk
            # basina 1 kez (hata olmadigi surece) — 91995 satirlik kpi_data gibi
            # buyuk tablolarda satir-basi savepoint (~3 round-trip/satir, SSH tuneli
            # uzerinden) pratik olarak biten bir sure almiyordu (bu turda kesfedildi,
            # script durup chunk moduna gecirildi). Sadece GERCEK hata durumunda
            # (chunk toplu basarisiz olursa) o chunk satir-satir + savepoint ile
            # yeniden denenir — boylece "1 bozuk satir tum chunk'i dusurmesin" garantisi
            # korunur, ama normal/hatasiz calismada round-trip sayisi cok azalir.
            cur_prod.execute("SAVEPOINT sp_chunk")
            chunk_toplam = 0  # bu chunk'ta hizli yolda BASARIYLA eklenen satir sayisi
            try:
                for eski_id, values in hazirlanan:
                    if has_id_pk:
                        insert_sql = f'INSERT INTO {tbl} ({col_sql}) VALUES ({placeholders}) RETURNING id'
                        cur_prod.execute(insert_sql, values)
                        yeni_id = cur_prod.fetchone()[0]
                        if eski_id is not None:
                            remap[tbl][eski_id] = yeni_id
                    else:
                        insert_sql = f'INSERT INTO {tbl} ({col_sql}) VALUES ({placeholders})'
                        cur_prod.execute(insert_sql, values)
                    chunk_toplam += 1
                cur_prod.execute("RELEASE SAVEPOINT sp_chunk")
                toplam += chunk_toplam
            except Exception:
                # YAVAS YOL: chunk'ta en az 1 satir hata verdi — chunk'i rollback
                # edip HER satiri kendi savepoint'inde tek tek yeniden dene (sadece
                # bu durumda satir-basi overhead'e katlanilir). KRITIK: 'toplam'a
                # hicbir sey eklenmedi (chunk_toplam kullanilmadi, sadece asagida
                # tek-tek deneme sonrasi 'toplam += 1' calisir) — onceki versiyonda
                # 'toplam -= len(hazirlanan)' ile FAZLA cikarma yapilip negatif
                # sayaca yol aciyordu (bu turda kesfedildi: 'plan_years: -11 satir').
                cur_prod.execute("ROLLBACK TO SAVEPOINT sp_chunk")
                cur_prod.execute("RELEASE SAVEPOINT sp_chunk")
                for eski_id, values in hazirlanan:
                    cur_prod.execute("SAVEPOINT sp_row")
                    try:
                        if has_id_pk:
                            insert_sql = f'INSERT INTO {tbl} ({col_sql}) VALUES ({placeholders}) RETURNING id'
                            cur_prod.execute(insert_sql, values)
                            yeni_id = cur_prod.fetchone()[0]
                            if eski_id is not None:
                                remap[tbl][eski_id] = yeni_id
                        else:
                            insert_sql = f'INSERT INTO {tbl} ({col_sql}) VALUES ({placeholders})'
                            cur_prod.execute(insert_sql, values)
                        cur_prod.execute("RELEASE SAVEPOINT sp_row")
                        toplam += 1
                    except Exception as e2:
                        cur_prod.execute("ROLLBACK TO SAVEPOINT sp_row")
                        cur_prod.execute("RELEASE SAVEPOINT sp_row")
                        hatali += 1
                        if hatali <= 5:
                            print(f"    UYARI ({tbl}) satir atlandi: eski_id={eski_id} -> {e2}")

        hata_notu = f", {hatali} satir HATALI/ATLANDI" if hatali else ""
        if toplam:
            print(f"  OK {tbl}: {toplam} satir kopyalandi{hata_notu}")
        elif hatali:
            print(f"  UYARI {tbl}: 0 satir kopyalandi, {hatali} satir hatali")
        else:
            print(f"  0 satir, atlaniyor: {tbl}")

    print("\nKopyalama adimi tamamlandi (commit/rollback karari main()'in sonunda verilecek).")


def _filtre_olustur(tbl, local_cols, ids):
    """Tablo icin uygun WHERE + JOIN + params uretir. (tbl, local_cols, ids) -> (where, join, params)."""
    p = {"ids": ids}
    if "tenant_id" in local_cols:
        return "t.tenant_id IN %(ids)s", "", p

    # Transitif tablolar icin bilinen JOIN yollari:
    JOIN_MAP = {
        "sub_strategies": ("JOIN strategies s ON s.id=t.strategy_id", "s.tenant_id IN %(ids)s"),
        "process_kpis": ("JOIN processes p ON p.id=t.process_id", "p.tenant_id IN %(ids)s"),
        "bsc_kpi_perspectives": ("JOIN process_kpis pk ON pk.id=t.process_kpi_id JOIN processes p ON p.id=pk.process_id", "p.tenant_id IN %(ids)s"),
        "process_sub_strategy_links": ("JOIN processes p ON p.id=t.process_id", "p.tenant_id IN %(ids)s"),
        "process_members": ("JOIN processes p ON p.id=t.process_id", "p.tenant_id IN %(ids)s"),
        "process_leaders": ("JOIN processes p ON p.id=t.process_id", "p.tenant_id IN %(ids)s"),
        "process_owners_table": ("JOIN processes p ON p.id=t.process_id", "p.tenant_id IN %(ids)s"),
        "process_activities": ("JOIN processes p ON p.id=t.process_id", "p.tenant_id IN %(ids)s"),
        "process_activity_assignees": ("JOIN process_activities pa ON pa.id=t.activity_id JOIN processes p ON p.id=pa.process_id", "p.tenant_id IN %(ids)s"),
        "kpi_data": ("JOIN process_kpis pk ON pk.id=t.process_kpi_id JOIN processes p ON p.id=pk.process_id", "p.tenant_id IN %(ids)s"),
        "kpi_data_audits": ("JOIN kpi_data kd ON kd.id=t.kpi_data_id JOIN process_kpis pk ON pk.id=kd.process_kpi_id JOIN processes p ON p.id=pk.process_id", "p.tenant_id IN %(ids)s"),
        "individual_performance_indicators": ("JOIN users u ON u.id=t.user_id", "u.tenant_id IN %(ids)s"),
        "individual_kpi_data": ("JOIN individual_performance_indicators ipi ON ipi.id=t.individual_pg_id JOIN users u ON u.id=ipi.user_id", "u.tenant_id IN %(ids)s"),
        "individual_kpi_data_audits": ("JOIN individual_kpi_data ikd ON ikd.id=t.individual_kpi_data_id JOIN individual_performance_indicators ipi ON ipi.id=ikd.individual_pg_id JOIN users u ON u.id=ipi.user_id", "u.tenant_id IN %(ids)s"),
        "favorite_kpis": ("JOIN users u ON u.id=t.user_id", "u.tenant_id IN %(ids)s"),
        "okr_key_results": ("JOIN okr_objectives o ON o.id=t.objective_id", "o.tenant_id IN %(ids)s"),
        "initiative_milestones": ("JOIN initiatives i ON i.id=t.initiative_id", "i.tenant_id IN %(ids)s"),
        "esg_metric_values": ("JOIN esg_metrics m ON m.id=t.metric_id", "m.tenant_id IN %(ids)s"),
        "blue_ocean_factors": ("JOIN blue_ocean_canvases c ON c.id=t.canvas_id", "c.tenant_id IN %(ids)s"),
        "blue_ocean_errc_items": ("JOIN blue_ocean_canvases c ON c.id=t.canvas_id", "c.tenant_id IN %(ids)s"),
        "strategy_year_configs": ("JOIN strategies s ON s.id=t.strategy_id", "s.tenant_id IN %(ids)s"),
        "sub_strategy_year_configs": ("JOIN sub_strategies ss ON ss.id=t.sub_strategy_id JOIN strategies s ON s.id=ss.strategy_id", "s.tenant_id IN %(ids)s"),
        "process_year_configs": ("JOIN processes p ON p.id=t.process_id", "p.tenant_id IN %(ids)s"),
        "kpi_year_configs": ("JOIN process_kpis pk ON pk.id=t.process_kpi_id JOIN processes p ON p.id=pk.process_id", "p.tenant_id IN %(ids)s"),
        "individual_kpi_year_configs": ("JOIN individual_performance_indicators ipi ON ipi.id=t.individual_performance_id JOIN users u ON u.id=ipi.user_id", "u.tenant_id IN %(ids)s"),
        "plan_project_activities": ("JOIN plan_projects pp ON pp.id=t.project_id", "pp.tenant_id IN %(ids)s"),
        "plan_project_tasks": ("JOIN plan_projects pp ON pp.id=t.project_id", "pp.tenant_id IN %(ids)s"),
        "k_vektor_sub_strategy_weights": ("JOIN sub_strategies ss ON ss.id=t.sub_strategy_id JOIN strategies s ON s.id=ss.strategy_id", "s.tenant_id IN %(ids)s"),
        "bottleneck_log": (None, None),  # aslinda direkt tenant_id var, buraya dusmez
        "task": ("JOIN project pr ON pr.id=t.project_id", "pr.tenant_id IN %(ids)s"),
        "task_baseline": ("JOIN task tk ON tk.id=t.task_id JOIN project pr ON pr.id=tk.project_id", "pr.tenant_id IN %(ids)s"),
        "recurring_task": ("JOIN project pr ON pr.id=t.project_id", "pr.tenant_id IN %(ids)s"),
        "raid_item": ("JOIN project pr ON pr.id=t.project_id", "pr.tenant_id IN %(ids)s"),
        "project_risk": ("JOIN project pr ON pr.id=t.project_id", "pr.tenant_id IN %(ids)s"),
        "working_day": ("JOIN project pr ON pr.id=t.project_id", "pr.tenant_id IN %(ids)s"),
        "capacity_plan": ("JOIN project pr ON pr.id=t.project_id", "pr.tenant_id IN %(ids)s"),
        "integration_hook": ("JOIN project pr ON pr.id=t.project_id", "pr.tenant_id IN %(ids)s"),
        "rule_definition": ("JOIN project pr ON pr.id=t.project_id", "pr.tenant_id IN %(ids)s"),
        "sla": ("JOIN project pr ON pr.id=t.project_id", "pr.tenant_id IN %(ids)s"),
        # replan_trigger_events'te DOGRUDAN tenant_id kolonu var — bu JOIN_MAP girdisine
        # asla dusmez ('tenant_id' in local_cols kontrolu once calisir), belge amacli tutuluyor.
        "replan_trigger_events": ("JOIN replan_triggers rt ON rt.id=t.trigger_id", "rt.tenant_id IN %(ids)s"),
    }

    if tbl in JOIN_MAP:
        join_clause, cond = JOIN_MAP[tbl]
        if join_clause is None:
            return None, None, None
        return cond, join_clause, p

    return None, None, None


# ── ADIM 2.5: pre_copy_sequence_check ────────────────────────────────────────

def pre_copy_sequence_check(conn_prod):
    """INSERT'ten ONCE tum ilgili tablolarin sequence'lerini MAX(id)+1'e hizalar.

    KRITIK BULGU (DRY_RUN'da kesfedildi): Yayin'da 'processes' tablosunun sequence'i
    (last_value=85) gercek MAX(id)'den (1007013) COK geride kalmis — muhtemelen
    gecmiste elle yuksek id'lerle satir eklenmis, sequence hic senkronize edilmemis.
    Bu, script'ten BAGIMSIZ, Yayin'da onceden var olan bir sorun. Sonuc: silinen
    satirlarin bosalttigi dusuk id'ler (1, 2, ...) sequence tarafindan tekrar
    uretiliyor ve INSERT sirasinda 'duplicate key value violates unique constraint'
    hatasi veriyor — 85 process'ten 13'u, buna bagli olarak process_kpis'in 126
    satiri process_id NULL kalarak silinmis bulgusu bu kok nedene dayanir.

    Bu fonksiyon delete_target_tenants()'tan HEMEN SONRA, copy_with_remap()'ten
    ONCE cagrilmali — DELETE'lerin etkiledigi TUM tablolar icin (yalniz remap'e
    giren degil, TABLES_WITH_FK'nin tamami) sequence hizalanir.

    KRITIK (tek-transaction mimarisi ile celisme): Ana migration TEK transaction'da
    yurutuluyor (DRY_RUN'da tek seferde rollback edilebilsin diye). Ama sequence
    duzeltmesi DRY_RUN'da bile KALICI olmali (aksi halde her deneme ayni 'duplicate
    key' hatasini tekrarlar — bu turda kesfedildi). Bu ikisi conn_prod'un AYNI
    transaction'i uzerinden cozulemez (commit() cagirmak DELETE'leri de commit eder).
    COZUM: sequence duzeltmesi AYRI bir connection/transaction'da, ana migration'in
    conn_prod'undan BAGIMSIZ yapilir — bu fonksiyon kendi kisa omurlu connection'ini
    acar/kapatir, ana transaction'a hic dokunmaz.
    """
    print("\n--- ADIM 2.5: INSERT oncesi sequence saglik kontrolu (BAGIMSIZ connection) ---")
    conn_seq = psycopg2.connect(
        dbname=PROD_DB_NAME, user=PROD_DB_USER, password=PROD_DB_PASSWORD,
        host=PROD_DB_HOST, port=PROD_DB_PORT, client_encoding="UTF8",
    )
    conn_seq.autocommit = False
    cur = conn_seq.cursor()
    duzeltilen = 0
    for tbl in TABLES_WITH_FK:
        try:
            cur.execute("SELECT pg_get_serial_sequence(%s, 'id')", (tbl,))
            seq = cur.fetchone()[0]
            if not seq:
                continue
            cur.execute(f"SELECT COALESCE(MAX(id), 0) FROM {tbl}")
            max_id = cur.fetchone()[0]
            cur.execute("SELECT last_value FROM " + seq)
            eski_seq = cur.fetchone()[0]
            if eski_seq < max_id:
                cur.execute(f"SELECT setval(%s, %s)", (seq, max_id))
                print(f"  DUZELTILDI: {tbl} sequence {eski_seq} -> {max_id}")
                duzeltilen += 1
        except Exception as e:
            print(f"  UYARI: {tbl} sequence kontrol edilemedi: {e}")
            conn_seq.rollback()
    if duzeltilen == 0:
        print("  Tum sequence'ler zaten saglikli.")
    conn_seq.commit()  # KALICI — bagimsiz connection, ana migration transaction'ini etkilemez.
    conn_seq.close()
    print("  NOT: sequence duzeltmesi ayri/bagimsiz connection'da KALICI olarak "
          "commit edildi (veri degil sayac onarimi — 1/27/28 disi hicbir "
          "tabloya/satira dokunmaz).")


# ── ADIM 4: resync_sequences ─────────────────────────────────────────────────

def resync_sequences(conn_prod, remap):
    """Kopyalanan tablolarin sequence'lerini MAX(id)'ye hizalar.

    KRITIK: commit/rollback BURADA yapilmaz (tek-transaction mimarisi — main()'in
    sonunda tum adimlar icin TEK karar verilir). Hata izolasyonu SAVEPOINT ile.
    """
    print("\n--- ADIM 4: Sequence senkronizasyonu ---")
    cur = conn_prod.cursor()
    cur.execute("SAVEPOINT sp_resync")
    for tbl in remap:
        try:
            cur.execute(
                "SELECT pg_get_serial_sequence(%s, 'id')", (tbl,)
            )
            seq = cur.fetchone()[0]
            if not seq:
                continue
            cur.execute(f"SELECT setval(%s, (SELECT COALESCE(MAX(id), 1) FROM {tbl}))", (seq,))
            print(f"  setval: {tbl} -> {seq}")
            cur.execute("RELEASE SAVEPOINT sp_resync")
            cur.execute("SAVEPOINT sp_resync")
        except Exception as e:
            print(f"  UYARI: {tbl} sequence senkronize edilemedi: {e}")
            cur.execute("ROLLBACK TO SAVEPOINT sp_resync")
    cur.execute("RELEASE SAVEPOINT sp_resync")


# ── ADIM 5: verify ───────────────────────────────────────────────────────────

def verify(conn_prod, conn_local, mevcut_16_29_30_31, yerel_1_27_28):
    print("\n--- ADIM 5: Dogrulama ---")
    cur_prod = conn_prod.cursor()

    yeni_16_29_30_31 = tenant_id_filtreli_sayim(cur_prod, UNTOUCHED_TENANT_IDS, conn=conn_prod)
    print("16/29/30/31 degismedi mi?")
    sorun = False
    for tbl, n in mevcut_16_29_30_31.items():
        yeni_n = yeni_16_29_30_31.get(tbl)
        if n is not None and yeni_n is not None and n != yeni_n:
            print(f"  SORUN: {tbl} degisti! once={n} sonra={yeni_n}")
            sorun = True
    if not sorun:
        print("  OK — degisiklik yok.")

    print("\n1/27/28 Yayin sayilari yerel ile eslesiyor mu?")
    yeni_1_27_28 = tenant_id_filtreli_sayim(cur_prod, TARGET_TENANT_IDS, conn=conn_prod)
    for tbl, n_yerel in yerel_1_27_28.items():
        n_prod = yeni_1_27_28.get(tbl)
        if n_yerel is None:
            continue
        durum = "OK" if n_yerel == n_prod else "FARK"
        if durum == "FARK":
            print(f"  {tbl}: yerel={n_yerel} yayin={n_prod} -> {durum}")
    print("(transitif tablolar icin ayni kontrol elle SELECT ile tekrarlanmali; "
          "bu ozet yalnizca dogrudan tenant_id kolonu olanlari kapsar.)")


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    print(f"DRY_RUN = {DRY_RUN}  (gercek yazim icin: $env:DRY_RUN='False')")
    print(f"Hedef tenant_id'ler: {TARGET_TENANT_IDS}  |  Dokunulmayacaklar: {UNTOUCHED_TENANT_IDS}")

    if AUTO_YES and not DRY_RUN:
        raise SystemExit(
            "GUVENLIK: AUTO_YES=1 yalniz DRY_RUN=True ile birlikte kullanilabilir. "
            "Gercek migration'da (DRY_RUN=False) her adim ELLE onaylanmalidir."
        )

    onay_al(
        "ADIM 0: Yerel ve Yayin (SSH tuneli localhost:15432 uzerinden) DB'lere baglanilacak.\n"
        "SSH tuneli ACIK oldugundan emin olun."
    )
    conn_local = baglan_yerel()
    conn_prod = baglan_prod()

    onay_al(
        "ADIM 1: snapshot_and_verify — salt okunur sayim + Kayseri MF referans karsilastirma "
        "+ email cakisma kontrolu yapilacak. Sapma/cakisma varsa script burada DURACAK."
    )
    mevcut_16_29_30_31, yerel_1_27_28 = snapshot_and_verify(conn_prod, conn_local)

    onay_al(
        f"ADIM 2: Yayin'da tenant_id {TARGET_TENANT_IDS} icin TUM bagimli veri (users dahil, "
        f"tenants HARIC) SILINECEK (ayni transaction icinde, commit/rollback karari "
        f"ADIM 6'da tek seferde verilecek). DRY_RUN={DRY_RUN}."
    )
    delete_target_tenants(conn_prod)

    onay_al(
        "ADIM 2.5: Yayin'da onceden var olan sequence drift sorunu (DRY_RUN'da "
        "kesfedildi — processes.id sequence'i gercek MAX(id)'den ciddi geride) "
        "duzeltilecek. Bu adim sequence sayaclarini MAX(id)+1'e hizalar — hicbir "
        "satiri SILMEZ/DEGISTIRMEZ, yalniz 'sonraki otomatik id ne olacak' bilgisini "
        "onarir. DRY_RUN modunda da KALICI olarak commit edilir (veri degil sayac "
        "onarimi oldugu icin)."
    )
    pre_copy_sequence_check(conn_prod)

    onay_al(
        f"ADIM 3: Yerelden 1/27/28 verisi Yayin'a id-remap ile YAZILACAK (ayni "
        f"transaction icinde — ADIM 2'nin silmeleri henuz commit edilmemis olsa da "
        f"bu adim onlari 'gormus' gibi calisir, PostgreSQL read-your-writes). "
        f"DRY_RUN={DRY_RUN}."
    )
    remap = {}
    copy_with_remap(conn_local, conn_prod, remap)

    onay_al("ADIM 4: Yeni yuklenen tablolarin PostgreSQL sequence'leri senkronize edilecek.")
    resync_sequences(conn_prod, remap)

    onay_al(
        "ADIM 5: Son dogrulama — sayim karsilastirmasi yapilacak (PostgreSQL ayni "
        "transaction icindeki KENDI degisikliklerini gorebildigi icin, DELETE+INSERT "
        "henuz commit edilmemis olsa da bu adim dogru sonuc verir)."
    )
    verify(conn_prod, conn_local, mevcut_16_29_30_31, yerel_1_27_28)

    # KRITIK — TEK KARAR NOKTASI: butun migration (silme + kopyalama + resync)
    # BURAYA kadar TEK bir conn_prod transaction'i icinde bekletildi. DRY_RUN'da
    # tumu birden ROLLBACK edilir (hicbir kalici degisiklik olmaz); gercek modda
    # tumu birden COMMIT edilir. Ayri ayri commit/rollback (onceki tasarim) DRY_RUN
    # kopyalama asamasinin hala-Yayin'da-duran eski veriyle sahte cakismasina yol
    # aciyordu (bu turda kesfedildi — bkz. delete_target_tenants docstring).
    onay_al(
        f"ADIM 6 (SON): {'ROLLBACK — hicbir kalici degisiklik YAPILMAYACAK' if DRY_RUN else 'COMMIT — TUM degisiklikler KALICI olacak'}."
    )
    if DRY_RUN:
        conn_prod.rollback()
        print("\nDRY_RUN=True: TUM migration (silme+kopyalama+resync) ROLLBACK edildi.")
    else:
        conn_prod.commit()
        print("\nTUM migration (silme+kopyalama+resync) COMMIT edildi.")

    conn_local.close()
    conn_prod.close()
    print("\nTamamlandi.")
    if DRY_RUN:
        print("NOT: DRY_RUN=True oldugu icin Yayin'da HICBIR KALICI DEGISIKLIK YAPILMADI ")
        print("(sequence onarimi HARIC — o ayri/bagimsiz connection'da kalici commit edildi).")
        print("Gercek migration icin: $env:DRY_RUN='False' yapip tekrar calistirin.")


if __name__ == "__main__":
    main()
