"""
Yerelde olup Yayin'da (production, www.kokpitim.com) HIC bulunmayan 6 kurumu
(tenant_id 58 tomofiltest, 76 YeniTomofil, 77 Yenicag Yazilim, 83 tom1, 84 tom2,
85 tom3) tum bagimli verisiyle birlikte Yayin'a EKLER.

Bu, migrate_tenants_1_27_28_prod.py'nin (2026-07-07, 1. asama) id-remap altyapisini
temel alir ama TEMEL FARK: burada DELETE YOK — sadece INSERT. Mevcut Yayin
verisine (1/16/27/28/29/30/31, hicbirine) dokunulmaz.

ONEMLI — CALISTIRMADAN ONCE:
  1. SSH tunelini KENDISI ACMAZ. Yerelden calistirirken:
       ssh -i C:\\crt\\ssh-key-2026-04-18_v4.key -L 15432:localhost:5432 ubuntu@129.159.30.175 -N
     VM uzerinde dogrudan calistirirken (performans icin onerilir — bkz. 1. asama
     deneyimi, SSH tuneli uzerinden buyuk tablolar cok yavasti):
       ssh -i C:\\crt\\ssh-key-2026-04-18_v4.key -R 15433:localhost:5432 ubuntu@129.159.30.175 -N
     ve LOCAL_DB_HOST=localhost, LOCAL_DB_PORT=15433 ortam degiskenleriyle.
  2. Ortam degiskenleri:
       PROD_DB_PASSWORD (veya PROD_DB_PASSWORD_FILE) — Yayin DB sifresi
       DRY_RUN=True   (varsayilan; gercek yazim icin DRY_RUN=False)
       AUTO_YES=1     (SADECE DRY_RUN=True ile, otomatik onay icin)
  3. Yayin'da onceden TAM DB yedegi alinmis olmali (1. asamada zaten alindi;
     bu asama SADECE INSERT yaptigi icin ek risk dusuk ama yine de kontrol edilmeli).

ON KONTROLLER (bu script yazilmadan once salt-okunur dogrulandi):
  - Email cakismasi: 6 kurumun 306 kullanicisi ile Yayin'daki mevcut 145
    kullanicinin email'leri arasinda kesisim YOK.
  - Tenant id cakismasi: Yayin tenants.max(id)=31; 58/76/77/83/84/85 Yayin'da BOS.
  - User id araligi: yerel 8320-9160, Yayin mevcut max=8294 — cakismiyor ama
    id-remap yine de kullanilir (guvenlik icin, "belki cakismaz" varsayimina
    guvenilmez — 1. asamadaki dersle tutarli).

KAPSAM:
  - Yerel tenant_id IN (58, 76, 77, 83, 84, 85) -> Yayin'a YENI kurum olarak EKLENIR.
  - Yayin'daki tenant_id IN (1, 16, 27, 28, 29, 30, 31) HIC DOKUNULMAZ (yalniz
    salt-okunur sayim, degismedigini dogrulamak icin).
  - tenant_id'ler TERCIHEN korunur (58->58 vb, Yayin'da bos oldugu icin) ama
    id-remap mekanizmasi tenants'a da uygulanir — bir celiskiyle karsilasilirsa
    (beklenmez ama garanti olsun diye) yeni id uretilir, FK'ler ona gore cozulur.

CALISTIRMA:
  cd C:\\kokpitim
  .venv\\Scripts\\python.exe scripts\\add_tenants_local_to_prod.py

Her adim oncesi kullaniciya 'EVET' onayi ister (AUTO_YES yoksa). DRY_RUN=True iken
hicbir INSERT YAYIN'a kalici yazilmaz (ADIM 6'da tek seferde commit/rollback).
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
TARGET_TENANT_IDS = (58, 76, 77, 83, 84, 85)
UNTOUCHED_TENANT_IDS = (1, 16, 27, 28, 29, 30, 31)  # 1. asamadan sonraki TUM Yayin kurumlari

DRY_RUN = os.environ.get("DRY_RUN", "True").strip().lower() not in ("false", "0", "no")

PROD_DB_HOST = "localhost"
PROD_DB_PORT = int(os.environ.get("PROD_DB_PORT", "15432"))
PROD_DB_NAME = "kokpitim_db"
PROD_DB_USER = "kokpitim_user"
if os.environ.get("PROD_DB_PASSWORD_FILE"):
    PROD_DB_PASSWORD = Path(os.environ["PROD_DB_PASSWORD_FILE"]).read_text(encoding="utf-8").strip()
else:
    PROD_DB_PASSWORD = os.environ.get("PROD_DB_PASSWORD")

_kayit_dir = Path(os.environ["KAYIT_DOSYA_DIR"]) if os.environ.get("KAYIT_DOSYA_DIR") else (ROOT / "docs" / "kontrol")
KAYIT_DOSYASI = _kayit_dir / f"yayinverileri_ekleme_{datetime.now().strftime('%Y-%m-%d_%H%M')}.md"

AUTO_YES = os.environ.get("AUTO_YES", "").strip().lower() in ("1", "true", "yes")


def onay_al(mesaj: str) -> None:
    """Kullaniciya 'EVET' yazdirmadan bir sonraki adima gecirmez.

    AUTO_YES=1 SADECE DRY_RUN=True ile kullanilmali (main() bunu ayrica kontrol eder).
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
    if os.environ.get("LOCAL_DB_HOST"):
        return dict(
            dbname=os.environ.get("LOCAL_DB_NAME", "kokpitim_db"),
            user=os.environ.get("LOCAL_DB_USER", "kokpitim_user"),
            password=os.environ.get("LOCAL_DB_PASSWORD", ""),
            host=os.environ["LOCAL_DB_HOST"],
            port=os.environ.get("LOCAL_DB_PORT", "5432"),
        )
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
    print(f"Yayin DB'ye baglanildi: {PROD_DB_NAME}@localhost:{PROD_DB_PORT}")
    return conn


# ── Tablo plani (migrate_tenants_1_27_28_prod.py'den AYNEN tasindi) ──────────
# NOT: 'tenants' burada TABLES_LEVEL1'in EN BASINA eklenir (1. asamada tenant
# sabitti/INSERT edilmiyordu — burada tenants da yeni kurum icin INSERT edilir).

TABLES_LEVEL1 = [
    # package_id: subscription_packages'a FK. KESFEDILDI (bu script yazilirken) —
    # Yayin'da SADECE 'master_package' (id=1) var, yerelin baslangic/yonetim/
    # strateji (id=2/3/4) paketleri Yayin'da YOK (ayri bir "Paketleme" isi henuz
    # Yayin'a deploy edilmemis). package_id remap edilmez (subscription_packages
    # tum tenant'lar icin ORTAK/PAYLASILAN bir tablo, yeni kurum icin YENIDEN
    # olusturulmaz) — referans Yayin'da yoksa satir NULL kalir (kolon nullable).
    ("tenants",                  {"parent_tenant_id": "tenants", "package_id": None}),
    ("users",                    {"tenant_id": "tenants", "role_id": None}),  # role_id PAYLASILAN, remap EDILMEZ
    ("plan_years",               {"tenant_id": "tenants", "template_source_id": "plan_years", "scenario_of_id": "plan_years"}),
    ("strategies",               {"tenant_id": "tenants", "plan_year_id": "plan_years", "source_strategy_id": "strategies"}),
    ("sub_strategies",           {"strategy_id": "strategies", "plan_year_id": "plan_years", "source_sub_strategy_id": "sub_strategies"}),
    ("processes",                {"tenant_id": "tenants", "parent_id": "processes", "plan_year_id": "plan_years",
                                   "source_process_id": "processes", "deleted_by": "users"}),
    ("process_kpis",             {"process_id": "processes", "sub_strategy_id": "sub_strategies",
                                   "plan_year_id": "plan_years", "source_kpi_id": "process_kpis"}),
    ("bsc_kpi_perspectives",     {"process_kpi_id": "process_kpis", "plan_year_id": "plan_years", "tenant_id": "tenants"}),
    ("blue_ocean_canvases",      {"tenant_id": "tenants"}),
    ("esg_metrics",              {"tenant_id": "tenants"}),
    ("initiatives",              {"tenant_id": "tenants", "strategy_id": "strategies", "sub_strategy_id": "sub_strategies",
                                   "owner_user_id": "users"}),
    ("k_vektor_strategy_weights", {"tenant_id": "tenants", "strategy_id": "strategies"}),
    ("llm_usage_logs",           {"tenant_id": "tenants", "user_id": "users"}),
    ("notifications",            {"user_id": "users", "tenant_id": "tenants", "related_user_id": "users"}),
    ("okr_objectives",           {"tenant_id": "tenants", "plan_year_id": "plan_years",
                                   "linked_strategy_id": "strategies", "linked_sub_strategy_id": "sub_strategies"}),
    ("pestel_analyses",          {"tenant_id": "tenants", "plan_year_id": "plan_years", "source_pestel_id": "pestel_analyses"}),
    ("plan_projects",            {"plan_year_id": "plan_years", "tenant_id": "tenants", "source_project_id": "plan_projects"}),
    ("porter_analyses",          {"tenant_id": "tenants", "plan_year_id": "plan_years", "source_porter_id": "porter_analyses"}),
    ("process_maturity",         {"tenant_id": "tenants", "process_id": "processes", "assessed_by": "users"}),
    ("project",                  {"tenant_id": "tenants", "manager_id": "users", "deleted_by": "users",
                                   "initiative_id": "initiatives"}),
    ("risk_heatmap_items",       {"tenant_id": "tenants", "plan_year_id": "plan_years", "owner_id": "users"}),
    ("swot_analyses",            {"tenant_id": "tenants", "plan_year_id": "plan_years", "source_swot_id": "swot_analyses"}),
    ("tenant_email_configs",     {"tenant_id": "tenants", "updated_by": "users"}),
    ("tenant_ethics_codes",      {"tenant_id": "tenants"}),
    ("tenant_quality_policies",  {"tenant_id": "tenants"}),
    ("tenant_values",            {"tenant_id": "tenants"}),
    ("tenant_year_identities",   {"plan_year_id": "plan_years", "tenant_id": "tenants"}),
    ("value_chain_items",        {"tenant_id": "tenants", "linked_process_id": "processes"}),
]

TABLES_LEVEL1_EMPTY = [
    ("audit_logs",              {"tenant_id": "tenants", "user_id": "users"}),
    ("a3_reports",              {"tenant_id": "tenants"}),
    ("ana_strateji",            {"tenant_id": "tenants"}),
    ("bottleneck_log",          {"tenant_id": "tenants", "process_id": "processes", "kpi_id": "process_kpis"}),
    ("competitor_analyses",     {"tenant_id": "tenants", "plan_year_id": "plan_years"}),
    ("corporate_identity",      {"tenant_id": "tenants"}),
    ("deger",                   {"tenant_id": "tenants"}),
    ("etik_kural",              {"tenant_id": "tenants"}),
    ("evm_snapshots",           {"tenant_id": "tenants", "project_id": "project"}),
    ("k_radar_recommendation_actions", {"tenant_id": "tenants", "user_id": "users"}),
    ("k_vektor_config_snapshots", {"tenant_id": "tenants", "user_id": "users"}),
    ("k_vektor_sub_strategy_weights", {"tenant_id": "tenants", "sub_strategy_id": "sub_strategies"}),
    ("kalite_politikasi",       {"tenant_id": "tenants"}),
    ("kurum",                   {}),
    ("llm_quota_overrides",     {"tenant_id": "tenants"}),
    ("replan_triggers",         {"tenant_id": "tenants", "target_kpi_id": "process_kpis"}),
    ("stakeholder_maps",        {"tenant_id": "tenants", "plan_year_id": "plan_years"}),
    ("stakeholder_surveys",     {"tenant_id": "tenants"}),
    ("tenant_llm_configs",      {"tenant_id": "tenants"}),
    ("tickets",                 {"user_id": "users", "tenant_id": "tenants"}),
    ("tows_analyses",           {"tenant_id": "tenants", "plan_year_id": "plan_years", "source_tows_id": "tows_analyses"}),
    ("user_year_assignments",   {"user_id": "users", "plan_year_id": "plan_years", "tenant_id": "tenants"}),
    ("vrio_resources",          {"tenant_id": "tenants"}),
]

TABLES_LEVEL2 = [
    ("process_sub_strategy_links", {"process_id": "processes", "sub_strategy_id": "sub_strategies"}),
    ("process_members",          {"process_id": "processes", "user_id": "users"}),
    ("process_leaders",          {"process_id": "processes", "user_id": "users"}),
    ("process_owners_table",     {"process_id": "processes", "user_id": "users"}),
    ("process_activities",       {"process_id": "processes", "process_kpi_id": "process_kpis",
                                   "plan_year_id": "plan_years", "source_activity_id": "process_activities",
                                   "auto_pgv_kpi_data_id": "kpi_data"}),
    ("process_activity_assignees", {"activity_id": "process_activities", "user_id": "users", "assigned_by": "users"}),
    # user_id + deleted_by_id eksikti — DRY_RUN'da kesfedildi (iki ayri turda):
    # ilk turda kpi_data.user_id NOT NULL + users'a FK'li oldugu icin TUM 274224
    # satir "kpi_data_user_id_fkey" ile atlaniyordu; user_id duzeltilince bu sefer
    # 91408 satir "kpi_data_deleted_by_id_fkey" ile atlandi (nullable ama FK'li).
    ("kpi_data",                  {"process_kpi_id": "process_kpis", "user_id": "users",
                                   "deleted_by_id": "users"}),
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

TABLES_LEVEL2_EMPTY = []


def sirali_tablo_listesi():
    """(tablo, fk_map) ciftlerini INSERT sirasiyla dondurur (tenants+users basta)."""
    seen = set()
    out = []
    for tbl, fk in TABLES_LEVEL1 + TABLES_LEVEL1_EMPTY + TABLES_LEVEL2 + TABLES_LEVEL2_EMPTY:
        if tbl in seen:
            continue
        seen.add(tbl)
        out.append((tbl, fk))
    return out


# ── ADIM 1: snapshot_and_verify ──────────────────────────────────────────────

def satir_sayisi(cur, tablo, where_sql, params, conn=None):
    """Satir sayar. Tablo/kolon yoksa 0 doner. SAVEPOINT ile izole edilir —
    conn.rollback() KULLANILMAZ (1. asamada ADIM 5'te tum migration'i sessizce
    geri alan kritik hataya yol acmisti, bkz. migrate_tenants_1_27_28_prod.py)."""
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
    sonuc = OrderedDict()
    ids_tuple = tuple(tenant_ids)
    for tbl, fk in sirali_tablo_listesi():
        if tbl == "tenants":
            n = satir_sayisi(cur, "tenants", "id IN %s", (ids_tuple,), conn=conn)
        elif tbl == "users":
            n = satir_sayisi(cur, "users", "tenant_id IN %s", (ids_tuple,), conn=conn)
        elif "tenant_id" in fk:
            n = satir_sayisi(cur, tbl, "tenant_id IN %s", (ids_tuple,), conn=conn)
        else:
            n = None
        sonuc[tbl] = n
    return sonuc


def snapshot_and_verify(conn_prod, conn_local):
    """On kontroller: salt-okunur sayim + email cakisma + 7 mevcut kurumun referansi."""
    cur_prod = conn_prod.cursor()

    print("\n--- ADIM 1: Yayin'da mevcut durumun kaydi ve dogrulama ---")

    print("Yayin'da 58/76/77/83/84/85 mevcut sayimlar aliniyor (BOS olmali)...")
    mevcut_hedef = tenant_id_filtreli_sayim(cur_prod, TARGET_TENANT_IDS, conn=conn_prod)
    dolu = [f"{t}={n}" for t, n in mevcut_hedef.items() if n]
    if dolu:
        print(f"\nHATA: Yayin'da hedef tenant_id'lerde ZATEN veri var: {dolu}")
        print("Bu script sadece BOS/yeni tenant icin tasarlandi. Script DURUYOR.")
        sys.exit(1)
    print("  OK — hedef tenant_id'ler Yayin'da bos.")

    # ISIM BAZLI mukerrer kayit kontrolu — id-remap yuzunden yeni tenant id
    # uretildigi icin (58 degil, sequence'ten yeni bir id), script IKINCI kez
    # calistirilirsa "tenant_id 58 bos mu" kontrolu yine gecer ve AYNI 6 kurum
    # farkli id'lerle TEKRAR eklenebilir. Bu yuzden isim bazli da kontrol edilir.
    cur_local2 = conn_local.cursor()
    cur_local2.execute("SELECT name FROM tenants WHERE id IN %s", (TARGET_TENANT_IDS,))
    yerel_isimler = [r[0] for r in cur_local2.fetchall()]
    cur_prod.execute("SELECT name FROM tenants WHERE name = ANY(%s)", (yerel_isimler,))
    cakisan_isimler = [r[0] for r in cur_prod.fetchall()]
    if cakisan_isimler:
        print(f"\nHATA: Yayin'da AYNI ISIMLE kurum(lar) zaten var: {cakisan_isimler}")
        print("Bu, script'in daha once (farkli id ile) calistirilmis olabilecegini gosterir. "
              "Mukerrer kayit riski — script DURUYOR.")
        sys.exit(1)
    print("  OK — isim bazli cakisma da yok (mukerrer kayit riski yok).")

    print("\nYayin'da 1/16/27/28/29/30/31 referans sayimlari aliniyor (DEGISMEMELI)...")
    mevcut_dokunulmayacak = tenant_id_filtreli_sayim(cur_prod, UNTOUCHED_TENANT_IDS, conn=conn_prod)

    print("\nEmail cakisma kontrolu (yerel 58/76/77/83/84/85 vs Yayin TUM kullanicilar)...")
    cur_local = conn_local.cursor()
    cur_local.execute("SELECT lower(email) FROM users WHERE tenant_id IN %s", (TARGET_TENANT_IDS,))
    yerel_emailler = {r[0] for r in cur_local.fetchall()}

    cur_prod.execute("SELECT lower(email) FROM users")
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

    print("\nYerelden 58/76/77/83/84/85 sayimlari aliniyor...")
    yerel_hedef = tenant_id_filtreli_sayim(cur_local, TARGET_TENANT_IDS, conn=conn_local)

    KAYIT_DOSYASI.parent.mkdir(parents=True, exist_ok=True)
    with open(KAYIT_DOSYASI, "w", encoding="utf-8") as f:
        f.write(f"# Yayin verileri kaydi (kurum EKLEME) — {datetime.now().isoformat()}\n\n")
        f.write("## Yayin'da 1/16/27/28/29/30/31 mevcut sayimlar (DEGISMEMELI)\n\n")
        f.write("| Tablo | Satir |\n|---|---|\n")
        for tbl, n in mevcut_dokunulmayacak.items():
            f.write(f"| {tbl} | {n if n is not None else 'transitif (asagida)'} |\n")
        f.write("\n## Yerelden gelecek 58/76/77/83/84/85 sayimlari (Yayin sonrasi bunlarla eslesecek)\n\n")
        f.write("| Tablo | Satir |\n|---|---|\n")
        for tbl, n in yerel_hedef.items():
            f.write(f"| {tbl} | {n if n is not None else 'transitif (asagida)'} |\n")

    print(f"\nKayit dosyasi yazildi: {KAYIT_DOSYASI}")
    return mevcut_dokunulmayacak, yerel_hedef


# ── ADIM 2: pre_copy_sequence_check ──────────────────────────────────────────

def pre_copy_sequence_check(conn_prod):
    """INSERT'ten ONCE tum ilgili tablolarin sequence'lerini MAX(id)+1'e hizalar.

    1. asamada Yayin'da sequence drift kesfedilmisti (bazi tablolarda sequence
    gercek MAX(id)'den geride) — bu genel bir Yayin sorunu oldugu icin bu
    script'te de INSERT oncesi ayni kontrol tekrarlanir. AYRI/bagimsiz
    connection'da calisir, ana migration transaction'ini etkilemez, DRY_RUN'da
    da KALICI commit edilir (veri degil sayac onarimi).
    """
    print("\n--- ADIM 2: INSERT oncesi sequence saglik kontrolu (BAGIMSIZ connection) ---")
    conn_seq = psycopg2.connect(
        dbname=PROD_DB_NAME, user=PROD_DB_USER, password=PROD_DB_PASSWORD,
        host=PROD_DB_HOST, port=PROD_DB_PORT, client_encoding="UTF8",
    )
    conn_seq.autocommit = False
    cur = conn_seq.cursor()
    duzeltilen = 0
    for tbl, _ in sirali_tablo_listesi():
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
                cur.execute("SELECT setval(%s, %s)", (seq, max_id))
                print(f"  DUZELTILDI: {tbl} sequence {eski_seq} -> {max_id}")
                duzeltilen += 1
        except Exception as e:
            print(f"  UYARI: {tbl} sequence kontrol edilemedi: {e}")
            conn_seq.rollback()
    if duzeltilen == 0:
        print("  Tum sequence'ler zaten saglikli.")
    conn_seq.commit()
    conn_seq.close()
    print("  NOT: sequence duzeltmesi ayri/bagimsiz connection'da KALICI olarak "
          "commit edildi (veri degil sayac onarimi).")


# ── ADIM 3: copy_with_remap ───────────────────────────────────────────────────

def kolonlari_al(cur, tablo):
    cur.execute(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name=%s ORDER BY ordinal_position", (tablo,)
    )
    rows = cur.fetchall()
    if rows and isinstance(rows[0], dict):
        return [r["column_name"] for r in rows]
    return [r[0] for r in rows]


def _filtre_olustur(tbl, local_cols, ids):
    """Tablo icin uygun WHERE + JOIN + params uretir."""
    p = {"ids": ids}
    if tbl == "tenants":
        return "t.id IN %(ids)s", "", p
    if "tenant_id" in local_cols:
        return "t.tenant_id IN %(ids)s", "", p

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
        "bottleneck_log": (None, None),
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
        "replan_trigger_events": ("JOIN replan_triggers rt ON rt.id=t.trigger_id", "rt.tenant_id IN %(ids)s"),
    }

    if tbl in JOIN_MAP:
        join_clause, cond = JOIN_MAP[tbl]
        if join_clause is None:
            return None, None, None
        return cond, join_clause, p

    return None, None, None


def copy_with_remap(conn_local, conn_prod, remap):
    """Parent->child sirayla yerelden okuyup Yayin'a id-remap ile YENI kayit ekler."""
    print("\n--- ADIM 3: Veri kopyalaniyor (id-remap ile, sadece INSERT) ---")
    cur_local = conn_local.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur_prod = conn_prod.cursor()

    CHUNK = 5000
    ids = tuple(TARGET_TENANT_IDS)

    for tbl, fk_map in sirali_tablo_listesi():
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
            hazirlanan = []
            for row in rows:
                row = dict(row)
                eski_id = row.get("id") if has_id_pk else None
                for fk_col, ref_tbl in fk_map.items():
                    if fk_col not in row or fk_col not in insert_cols:
                        continue
                    val = row.get(fk_col)
                    if val is None or ref_tbl is None:
                        continue
                    yeni_val = remap.get(ref_tbl, {}).get(val)
                    if yeni_val is None:
                        row[fk_col] = None
                    else:
                        row[fk_col] = yeni_val
                degerler = []
                for c in insert_cols:
                    v = row.get(c)
                    if isinstance(v, (dict, list)):
                        v = psycopg2.extras.Json(v)
                    degerler.append(v)
                hazirlanan.append((eski_id, degerler))

            col_sql = ", ".join(f'"{c}"' for c in insert_cols)
            placeholders = ", ".join(["%s"] * len(insert_cols))

            cur_prod.execute("SAVEPOINT sp_chunk")
            chunk_toplam = 0
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
            print(f"  OK {tbl}: {toplam} satir eklendi{hata_notu}")
        elif hatali:
            print(f"  UYARI {tbl}: 0 satir eklendi, {hatali} satir hatali")
        else:
            print(f"  0 satir, atlaniyor: {tbl}")

    print("\nKopyalama adimi tamamlandi (commit/rollback karari main()'in sonunda verilecek).")


# ── ADIM 4: resync_sequences ─────────────────────────────────────────────────

def resync_sequences(conn_prod, remap):
    print("\n--- ADIM 4: Sequence senkronizasyonu ---")
    cur = conn_prod.cursor()
    cur.execute("SAVEPOINT sp_resync")
    for tbl in remap:
        try:
            cur.execute("SELECT pg_get_serial_sequence(%s, 'id')", (tbl,))
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

def verify(conn_prod, conn_local, mevcut_dokunulmayacak, yerel_hedef, remap):
    """
    KRITIK BULGU (DRY_RUN'da kesfedildi): 'tenants' tablosu id-remap mekanizmasinda
    diger tablolarla AYNI mantiga tabidir — id kolonu INSERT'e dahil edilmez, yeni
    id PostgreSQL sequence'inden RETURNING ile alinir (Yayin'da 58/76/77/83/84/85
    bos oldugu icin cakisma olmasa da, sequence YINE DE yeni bir id uretir, orijinal
    id KORUNMAZ). Bu yuzden verify() ESKI TARGET_TENANT_IDS ile Yayin'da arama
    yaparsa hep 0 bulur — INSERT basarili olsa bile. Dogru kontrol: remap['tenants']
    sozlugunden YENI id'leri alip onlarla aramak.
    """
    print("\n--- ADIM 5: Dogrulama ---")
    cur_prod = conn_prod.cursor()

    yeni_dokunulmayacak = tenant_id_filtreli_sayim(cur_prod, UNTOUCHED_TENANT_IDS, conn=conn_prod)
    print("1/16/27/28/29/30/31 degismedi mi?")
    sorun = False
    for tbl, n in mevcut_dokunulmayacak.items():
        yeni_n = yeni_dokunulmayacak.get(tbl)
        if n is not None and yeni_n is not None and n != yeni_n:
            print(f"  SORUN: {tbl} degisti! once={n} sonra={yeni_n}")
            sorun = True
    if not sorun:
        print("  OK — degisiklik yok.")

    yeni_tenant_ids = tuple(remap.get("tenants", {}).values()) or TARGET_TENANT_IDS
    print(f"\n58/76/77/83/84/85 Yayin sayilari yerel ile eslesiyor mu? "
          f"(Yayin'daki YENI tenant id'leri: {yeni_tenant_ids})")
    yeni_hedef = tenant_id_filtreli_sayim(cur_prod, yeni_tenant_ids, conn=conn_prod)
    for tbl, n_yerel in yerel_hedef.items():
        n_prod = yeni_hedef.get(tbl)
        if n_yerel is None:
            continue
        durum = "OK" if n_yerel == n_prod else "FARK"
        if durum == "FARK":
            print(f"  {tbl}: yerel={n_yerel} yayin={n_prod} -> {durum}")
    print("(transitif tablolar icin ayni kontrol elle SELECT ile tekrarlanmali; "
          "bu ozet yalnizca dogrudan tenant_id/id kolonu olanlari kapsar.)")


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    print(f"DRY_RUN = {DRY_RUN}  (gercek yazim icin: $env:DRY_RUN='False')")
    print(f"Hedef (YENI eklenecek) tenant_id'ler: {TARGET_TENANT_IDS}")
    print(f"Dokunulmayacaklar: {UNTOUCHED_TENANT_IDS}")

    if AUTO_YES and not DRY_RUN:
        raise SystemExit(
            "GUVENLIK: AUTO_YES=1 yalniz DRY_RUN=True ile birlikte kullanilabilir. "
            "Gercek migration'da (DRY_RUN=False) her adim ELLE onaylanmalidir."
        )

    onay_al(
        "ADIM 0: Yerel ve Yayin DB'lere baglanilacak.\n"
        "SSH tuneli (ileri veya ters) ACIK oldugundan emin olun."
    )
    conn_local = baglan_yerel()
    conn_prod = baglan_prod()

    onay_al(
        "ADIM 1: snapshot_and_verify — salt okunur sayim + hedef tenant'larin Yayin'da "
        "BOS oldugu dogrulamasi + email cakisma kontrolu yapilacak. Sapma/cakisma "
        "varsa script burada DURACAK."
    )
    mevcut_dokunulmayacak, yerel_hedef = snapshot_and_verify(conn_prod, conn_local)

    onay_al(
        "ADIM 2: Yayin'da INSERT oncesi sequence saglik kontrolu yapilacak (bagimsiz "
        "connection, DRY_RUN'da da KALICI commit edilir — veri degil sayac onarimi)."
    )
    pre_copy_sequence_check(conn_prod)

    onay_al(
        f"ADIM 3: Yerelden 58/76/77/83/84/85 verisi Yayin'a id-remap ile YENI kayit "
        f"olarak EKLENECEK (mevcut hicbir veri silinmiyor/degistirilmiyor). "
        f"DRY_RUN={DRY_RUN}."
    )
    remap = {}
    copy_with_remap(conn_local, conn_prod, remap)

    onay_al("ADIM 4: Yeni eklenen tablolarin PostgreSQL sequence'leri senkronize edilecek.")
    resync_sequences(conn_prod, remap)

    onay_al(
        "ADIM 5: Son dogrulama — sayim karsilastirmasi yapilacak (PostgreSQL ayni "
        "transaction icindeki KENDI degisikliklerini gorebildigi icin, INSERT henuz "
        "commit edilmemis olsa da bu adim dogru sonuc verir)."
    )
    verify(conn_prod, conn_local, mevcut_dokunulmayacak, yerel_hedef, remap)

    onay_al(
        f"ADIM 6 (SON): {'ROLLBACK — hicbir kalici degisiklik YAPILMAYACAK' if DRY_RUN else 'COMMIT — TUM degisiklikler KALICI olacak'}."
    )
    if DRY_RUN:
        conn_prod.rollback()
        print("\nDRY_RUN=True: TUM ekleme (INSERT+resync) ROLLBACK edildi.")
    else:
        conn_prod.commit()
        print("\nTUM ekleme (INSERT+resync) COMMIT edildi.")

    conn_local.close()
    conn_prod.close()
    print("\nTamamlandi.")
    if DRY_RUN:
        print("NOT: DRY_RUN=True oldugu icin Yayin'da HICBIR KALICI DEGISIKLIK YAPILMADI ")
        print("(sequence onarimi HARIC — o ayri/bagimsiz connection'da kalici commit edildi).")
        print("Gercek migration icin: $env:DRY_RUN='False' yapip tekrar calistirin.")


if __name__ == "__main__":
    main()
