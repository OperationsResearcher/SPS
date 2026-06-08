"""tomofiltest — Tomofil kurumunun izole klonu (Admin Araçları > Hata Kontrolü için).

Tasarım: docs/HATA-KONTROLU-TASARIM.md (K7 satır-satır id-remap, K8 wipe+yeniden klonla).

Yaklaşım:
  - Mantık satır-satır id-remap; yürütme küme-temelli (PostgreSQL temp eşleme tabloları
    + INSERT...SELECT JOIN). Tablo sırası ve kapsam filtreleri elle (wipe'tan doğrulanmış);
    FK-remap'ler SQLAlchemy introspection ile otomatik.
  - Kullanıcıya bağlı veriler (bireysel/bildirim/üyelik) v1'de klonlanmaz; yalnız 1 sentetik
    admin yaratılır. Yapısal/stratejik veri (strateji, süreç, PG, kpi_data, plan yılı,
    analizler, projeler) klonlanır.

GÜVENLİK: yalnız non-prod (Yayín'da çağrılmaz — çağıran katman kilitler). Hedef daima
'tomofiltest' kurumudur; kaynak asla değiştirilmez (salt-okunur SELECT).
"""
from __future__ import annotations

import os

from flask import current_app
from sqlalchemy import inspect as sa_inspect, text

from extensions import db

SOURCE_NAME_LIKE = "tomofil"      # kaynak kurum (Tomofil) — ada göre bulunur
TEST_TENANT_NAME = "tomofiltest"  # hedef izole kurum
SYNTH_ADMIN_EMAIL = "admin@tomofiltest.local"
SYNTH_ADMIN_PW = "HataKontrol!123"   # tek kaynak (executor de buradan import eder)


def _is_production() -> bool:
    """Yayın ortamı mı? (klon/wipe için savunma derinliği — route'a ek olarak)."""
    return (os.environ.get("FLASK_ENV") or "development").lower() == "production"

# Kullanıcıya bağlı / klonlanmayan tablolar (kullanıcılar kopyalanmıyor)
SKIP_TABLES = {
    "individual_performance_indicators", "individual_activities", "individual_kpi_data",
    "individual_kpi_data_audits", "individual_activity_tracks", "individual_kpi_year_configs",
    "favorite_kpis", "notifications", "notifications_ext", "push_subscriptions",
    "notification_preferences", "user_tour_progress", "user_year_assignment",
    "process_members", "process_leaders", "process_owners_table",
    "project_members", "project_leaders", "project_observers",
    "activity_tracks", "process_activity_assignees", "process_activity_reminders",
    "audit_logs", "tickets",
}

# Klon sırası (ebeveyn→çocuk) + kapsam filtresi (alias s, :t, _map_ temp tabloları).
# FK-remap kolonları introspection ile otomatik bulunur — burada SADECE sıra + kapsam.
CLONE_ORDER: list[tuple[str, str]] = [
    ("plan_years",                 "s.tenant_id = :t"),
    ("tenant_year_identities",     "s.tenant_id = :t"),
    ("strategies",                 "s.tenant_id = :t"),
    ("sub_strategies",             "s.strategy_id IN (SELECT old_id FROM _map_strategies)"),
    ("processes",                  "s.tenant_id = :t"),
    ("process_sub_strategy_links", "s.process_id IN (SELECT old_id FROM _map_processes) AND s.sub_strategy_id IN (SELECT old_id FROM _map_sub_strategies)"),
    ("process_kpis",               "s.process_id IN (SELECT old_id FROM _map_processes)"),
    ("process_activities",         "s.process_id IN (SELECT old_id FROM _map_processes)"),
    ("kpi_data",                   "s.process_kpi_id IN (SELECT old_id FROM _map_process_kpis)"),
    ("kpi_data_audits",            "s.kpi_data_id IN (SELECT old_id FROM _map_kpi_data)"),
    ("kpi_year_configs",           "s.plan_year_id IN (SELECT old_id FROM _map_plan_years)"),
    ("strategy_year_configs",      "s.plan_year_id IN (SELECT old_id FROM _map_plan_years)"),
    ("sub_strategy_year_configs",  "s.plan_year_id IN (SELECT old_id FROM _map_plan_years)"),
    ("process_year_configs",       "s.plan_year_id IN (SELECT old_id FROM _map_plan_years)"),
    ("initiatives",                "s.tenant_id = :t"),
    ("initiative_milestones",      "s.initiative_id IN (SELECT old_id FROM _map_initiatives)"),
    ("okr_objectives",             "s.tenant_id = :t"),
    ("okr_key_results",            "s.objective_id IN (SELECT old_id FROM _map_okr_objectives)"),
    ("esg_metrics",                "s.tenant_id = :t"),
    ("esg_metric_values",          "s.metric_id IN (SELECT old_id FROM _map_esg_metrics)"),
    ("bsc_kpi_perspectives",       "s.tenant_id = :t"),
    ("swot_analyses",              "s.tenant_id = :t"),
    ("tows_analyses",              "s.tenant_id = :t"),
    ("pestel_analyses",            "s.tenant_id = :t"),
    ("porter_analyses",            "s.tenant_id = :t"),
    ("a3_reports",                 "s.tenant_id = :t"),
    ("competitor_analyses",        "s.tenant_id = :t"),
    ("stakeholder_maps",           "s.tenant_id = :t"),
    ("stakeholder_surveys",        "s.tenant_id = :t"),
    ("risk_heatmap_items",         "s.tenant_id = :t"),
    ("blue_ocean_canvases",        "s.tenant_id = :t"),
    ("blue_ocean_factors",         "s.canvas_id IN (SELECT old_id FROM _map_blue_ocean_canvases)"),
    ("blue_ocean_errc_items",      "s.canvas_id IN (SELECT old_id FROM _map_blue_ocean_canvases)"),
    ("vrio_resources",             "s.tenant_id = :t"),
    ("k_vektor_strategy_weights",     "s.tenant_id = :t"),
    ("k_vektor_sub_strategy_weights", "s.tenant_id = :t"),
    ("k_vektor_config_snapshots",     "s.tenant_id = :t"),
    ("k_radar_recommendation_actions","s.tenant_id = :t"),
    ("process_maturity",           "s.tenant_id = :t"),
    ("bottleneck_log",             "s.tenant_id = :t"),
    ("value_chain_items",          "s.tenant_id = :t"),
    ("replan_triggers",            "s.tenant_id = :t"),
    ("replan_trigger_events",      "s.trigger_id IN (SELECT old_id FROM _map_replan_triggers)"),
    ("project",                    "s.tenant_id = :t"),
    ("project_related_processes",  "s.project_id IN (SELECT old_id FROM _map_project)"),
    ("sprint",                     "s.project_id IN (SELECT old_id FROM _map_project)"),
    ("task",                       "s.project_id IN (SELECT old_id FROM _map_project)"),
    ("task_predecessors",          "s.task_id IN (SELECT old_id FROM _map_task) AND s.predecessor_id IN (SELECT old_id FROM _map_task)"),
    ("evm_snapshots",              "s.tenant_id = :t"),
]


# ─── Yardımcılar ─────────────────────────────────────────────────────────────

def _q(name: str) -> str:
    return '"' + name.replace('"', '') + '"'


def find_source_tenant_id() -> int | None:
    # tomofiltest'i ASLA kaynak seçme ('%tomofil%' onu da eşler!). Önce tam
    # short_name eşleşmesi, sonra ada göre — ama hedef adı (tomofiltest) hariç.
    row = db.session.execute(
        text("SELECT id FROM tenants "
             "WHERE (lower(coalesce(short_name,'')) = :n OR lower(name) LIKE :like) "
             "  AND lower(name) <> :test AND lower(coalesce(short_name,'')) <> :test "
             "ORDER BY (lower(coalesce(short_name,'')) = :n) DESC, id "
             "LIMIT 1"),
        {"n": SOURCE_NAME_LIKE, "like": f"%{SOURCE_NAME_LIKE}%", "test": TEST_TENANT_NAME},
    ).scalar()
    return int(row) if row else None


def find_test_tenant_id() -> int | None:
    row = db.session.execute(
        text("SELECT id FROM tenants WHERE lower(name) = :n OR lower(coalesce(short_name,'')) = :n LIMIT 1"),
        {"n": TEST_TENANT_NAME},
    ).scalar()
    return int(row) if row else None


def _existing_tables() -> set[str]:
    insp = sa_inspect(db.engine)
    return set(insp.get_table_names())


def _fk_targets(table: str) -> dict[str, str]:
    """kolon -> hedef tablo (tek kolonlu FK'ler)."""
    insp = sa_inspect(db.engine)
    out: dict[str, str] = {}
    for fk in insp.get_foreign_keys(table):
        cc = fk.get("constrained_columns") or []
        rt = fk.get("referred_table")
        if len(cc) == 1 and rt:
            out[cc[0]] = rt
    return out


def _columns(table: str) -> list[str]:
    insp = sa_inspect(db.engine)
    return [c["name"] for c in insp.get_columns(table)]


# ─── Klon çekirdeği ──────────────────────────────────────────────────────────

def _copy_table(table: str, scope_where: str, source_tid: int, new_tid: int,
                admin_id: int, clone_set: set[str], existing: set[str],
                made_maps: set[str]) -> int:
    """Tek tabloyu kopyalar (küme-temelli id-remap). Kopyalanan satır sayısını döner.

    made_maps: bu klon koşusuna ait yerel set (thread-safe; global state yok)."""
    if table not in existing:
        return 0
    cols = _columns(table)
    has_id = "id" in cols
    fkmap = _fk_targets(table)

    # 1) id'li tablolar için eşleme tablosu (old_id -> new_id)
    if has_id:
        db.session.execute(text(f'CREATE TEMP TABLE _map_{table} (old_id bigint PRIMARY KEY, new_id bigint) ON COMMIT DROP'))
        db.session.execute(text(
            f'INSERT INTO _map_{table}(old_id, new_id) '
            f"SELECT s.id, nextval(pg_get_serial_sequence('{table}','id')) "
            f'FROM {_q(table)} s WHERE {scope_where}'
        ), {"t": source_tid})

    # 2) kolon ifadeleri + gerekli LEFT JOIN'ler
    select_exprs: list[str] = []
    insert_cols: list[str] = []
    joins: list[str] = []
    jn = 0
    for col in cols:
        insert_cols.append(_q(col))
        if has_id and col == "id":
            select_exprs.append("m.new_id")
            continue
        if col == "tenant_id":
            select_exprs.append(":newt")
            continue
        target = fkmap.get(col)
        if target == "tenants":
            select_exprs.append("NULL")            # parent_tenant_id vb. → null
            continue
        if target == "users":
            select_exprs.append(":adminid")        # tüm user FK'leri → sentetik admin
            continue
        if target and target in clone_set and target in existing and target != table and (f"_map_{target}") in made_maps:
            jn += 1
            a = f"j{jn}"
            joins.append(f'LEFT JOIN _map_{target} {a} ON {a}.old_id = s.{_q(col)}')
            select_exprs.append(f"{a}.new_id")
            continue
        if target == table and has_id:            # self-ref (processes.parent_id)
            jn += 1
            a = f"j{jn}"
            joins.append(f'LEFT JOIN _map_{table} {a} ON {a}.old_id = s.{_q(col)}')
            select_exprs.append(f"{a}.new_id")
            continue
        select_exprs.append(f"s.{_q(col)}")        # diğer her şey aynen

    base_from = f'FROM {_q(table)} s'
    if has_id:
        base_from += f' JOIN _map_{table} m ON m.old_id = s.id'
        where = ""  # kapsam zaten _map'e girerken uygulandı
    else:
        where = f" WHERE {scope_where}"
    sql = (f'INSERT INTO {_q(table)} ({", ".join(insert_cols)}) '
           f'SELECT {", ".join(select_exprs)} {base_from} {" ".join(joins)}{where}')
    res = db.session.execute(text(sql), {"t": source_tid, "newt": new_tid, "adminid": admin_id})
    if has_id:
        made_maps.add(f"_map_{table}")
    return res.rowcount or 0


def _resync_sequences(tables: list[str], existing: set[str]) -> None:
    for t in tables:
        if t not in existing:
            continue
        if "id" not in _columns(t):
            continue
        db.session.execute(text(
            f"SELECT setval(pg_get_serial_sequence('{t}','id'), "
            f'(SELECT COALESCE(MAX(id),1) FROM {_q(t)}))'
        ))


def clone_tomofiltest(dry_run: bool = True) -> dict:
    """Tomofil'den tomofiltest'i (yeniden) klonlar.

    dry_run=True: her şey yapılır ama sonunda ROLLBACK (yazma yok) — sayımları görmek için.
    dry_run=False: COMMIT.
    """
    # Savunma derinliği: Yayín'da asla (route da kilitler, burada da)
    if _is_production():
        return {"ok": False, "error": "Yayín ortamında klon/sıfırlama yapılamaz."}

    made_maps: set[str] = set()   # bu koşuya özel (thread-safe)
    existing = _existing_tables()
    clone_set = {t for t, _ in CLONE_ORDER}

    source_tid = find_source_tenant_id()
    if not source_tid:
        return {"ok": False, "error": "Kaynak Tomofil kurumu bulunamadı."}

    report: dict = {"source_tid": source_tid, "dry_run": dry_run, "tables": {}}
    try:
        # Mevcut tomofiltest'i temizle (wipe + yeniden klonla)
        old_test = find_test_tenant_id()
        if old_test and old_test == source_tid:
            return {"ok": False, "error": "Kaynak ve hedef aynı tenant — klon iptal (güvenlik)."}
        if old_test:
            _wipe_test_tenant(old_test, existing)

        # Yeni hedef kurum + sentetik admin
        new_tid = db.session.execute(text(
            "INSERT INTO tenants (name, short_name, tenant_type, is_active) "
            "VALUES (:n, :n, 'normal', true) RETURNING id"
        ), {"n": TEST_TENANT_NAME}).scalar()

        from werkzeug.security import generate_password_hash
        role_id = db.session.execute(text(
            "SELECT id FROM roles WHERE name = 'tenant_admin' LIMIT 1"
        )).scalar()
        admin_id = db.session.execute(text(
            "INSERT INTO users (email, password_hash, first_name, last_name, tenant_id, role_id, is_active) "
            "VALUES (:e, :p, 'Test', 'Admin', :tid, :rid, true) RETURNING id"
        ), {"e": SYNTH_ADMIN_EMAIL, "p": generate_password_hash(SYNTH_ADMIN_PW),
            "tid": new_tid, "rid": role_id}).scalar()
        report["new_tid"] = new_tid
        report["admin_id"] = admin_id

        # Tabloları sırayla kopyala
        for table, scope in CLONE_ORDER:
            n = _copy_table(table, scope, source_tid, new_tid, admin_id, clone_set, existing, made_maps)
            if n:
                report["tables"][table] = n

        # Sequence hizalama
        _resync_sequences(["tenants", "users"] + [t for t, _ in CLONE_ORDER], existing)

        report["ok"] = True
        report["total_rows"] = sum(report["tables"].values())

        if dry_run:
            db.session.rollback()
            report["committed"] = False
        else:
            db.session.commit()
            report["committed"] = True
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[tenant_clone] hata: {e}", exc_info=True)
        report["ok"] = False
        report["error"] = str(e)
    return report


def tomofiltest_status() -> dict:
    """tomofiltest kurumunun mevcut durumu (UI için)."""
    tid = find_test_tenant_id()
    if not tid:
        return {"exists": False}

    def c(sql: str) -> int:
        try:
            return int(db.session.execute(text(sql), {"t": tid}).scalar() or 0)
        except Exception:
            return 0

    return {
        "exists": True,
        "tid": tid,
        "admin_email": SYNTH_ADMIN_EMAIL,
        "strategies": c("SELECT count(*) FROM strategies WHERE tenant_id=:t"),
        "processes": c("SELECT count(*) FROM processes WHERE tenant_id=:t"),
        "process_kpis": c("SELECT count(*) FROM process_kpis pk JOIN processes p ON pk.process_id=p.id WHERE p.tenant_id=:t"),
        "kpi_data": c("SELECT count(*) FROM kpi_data kd JOIN process_kpis pk ON kd.process_kpi_id=pk.id JOIN processes p ON pk.process_id=p.id WHERE p.tenant_id=:t"),
    }


def _wipe_test_tenant(test_tid: int, existing: set[str]) -> None:
    """tomofiltest verisini siler (sıfırlama için). Sıra: çocuk→ebeveyn (CLONE_ORDER tersi)."""
    if _is_production():
        raise RuntimeError("Yayín ortamında wipe yapılamaz (güvenlik).")
    # En basiti: FK'leri geçici kaldırmadan, ters sırada sil. Tüm tablolarda tenant_id yok;
    # bu yüzden id-map yerine doğrudan tenant kapsamı + FK zinciriyle silmek karmaşık.
    # v1: CLONE_ORDER'ı tersine gez, tenant_id'si olanı tenant_id ile, olmayanı atlayıp
    # CASCADE'e bırak; sonra users + tenant.
    for table, _ in reversed(CLONE_ORDER):
        if table not in existing:
            continue
        if "tenant_id" in _columns(table):
            db.session.execute(text(f'DELETE FROM {_q(table)} WHERE tenant_id = :t'), {"t": test_tid})

    # Kullanıcı-bağlı runtime tabloları (login/işlem sırasında üretilir) — users'tan ÖNCE temizle.
    _usub = "(SELECT id FROM users WHERE tenant_id = :t)"
    _user_linked = [
        f"DELETE FROM audit_logs WHERE tenant_id = :t OR user_id IN {_usub}",
        "DELETE FROM llm_usage_logs WHERE tenant_id = :t",
        "DELETE FROM llm_quota_overrides WHERE tenant_id = :t",
        f"DELETE FROM notifications WHERE tenant_id = :t OR user_id IN {_usub}",
        f"DELETE FROM notifications_ext WHERE user_id IN {_usub}",
        f"DELETE FROM push_subscriptions WHERE user_id IN {_usub}",
        f"DELETE FROM notification_preferences WHERE user_id IN {_usub}",
        f"DELETE FROM user_tour_progress WHERE user_id IN {_usub}",
        f"DELETE FROM user_year_assignment WHERE user_id IN {_usub} OR tenant_id = :t",
        f"DELETE FROM favorite_kpis WHERE user_id IN {_usub}",
        # bireysel veri: user_id FK'leri CASCADE DEĞİL → users'tan önce sil (audit önce)
        f"DELETE FROM individual_kpi_data_audits WHERE user_id IN {_usub}",
        f"DELETE FROM individual_kpi_data WHERE user_id IN {_usub}",
        "DELETE FROM tickets WHERE tenant_id = :t",
    ]
    for sql in _user_linked:
        tbl = sql.split("FROM", 1)[1].split()[0]
        if tbl in existing:
            db.session.execute(text(sql), {"t": test_tid})

    db.session.execute(text("DELETE FROM users WHERE tenant_id = :t"), {"t": test_tid})
    db.session.execute(text("DELETE FROM tenants WHERE id = :t"), {"t": test_tid})
