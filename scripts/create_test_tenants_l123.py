# -*- coding: utf-8 -*-
"""tom1 / tom2 / tom3 — L1/L2/L3 UX testi için kademeli Tomofil klonları.

Üç yeni tenant, Tomofil(kaynak) verisinden kademeli kopya + farklı paket:

  tom1 (Başlangıç/L1): kimlik(Değer/Etik/Kalite) + strateji + süreç(varlık) + PG tanımı
                       → KOE çalışır. PGV YOK, bireysel YOK, ileri analiz YOK.
  tom2 (Yönetim/L2)  : tom1 + kpi_data(PGV) + bireysel PG/faaliyet
  tom3 (Strateji/L3) : tom2 + ileri analiz (SWOT/TOWS/PESTEL/Porter/BSC/ESG/...)

Kullanıcılar: Tomofil'in 97 kullanıcısı her tenant'a PREFIX'li kopyalanır
  (ali@x → 1ali@x / 2ali@x / 3ali@x). Ortak şifre: TEST_SIFRE.
User-aware: bireysel veriler DOĞRU kullanıcıya bağlanır (_map_users).

mevcut tenant_clone_service motorundan saf yardımcılar yeniden kullanılır
(o dosyaya DOKUNULMAZ). Bu script user-remap ekler.

GÜVENLİK: yalnız Yerel. Kaynak Tomofil salt-okunur. Önce --dry-run.

Kullanım:
    python scripts/create_test_tenants_l123.py --dry-run   # sayım, yazma yok
    python scripts/create_test_tenants_l123.py             # uygula
    python scripts/create_test_tenants_l123.py --wipe      # mevcut tom1/2/3 sil + yeniden
"""
import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from __init__ import create_app
from extensions import db
from sqlalchemy import text
from werkzeug.security import generate_password_hash

from app.services.tenant_clone_service import (
    _columns, _fk_targets, _q, _existing_tables, find_source_tenant_id,
)

TEST_SIFRE = "Test1234!"   # tüm prefix'li kullanıcılar — sana bildirilecek

# ── Kademeli tablo setleri (FK ebeveyn→çocuk sırası korunur) ──────────────────
# Her satır: (tablo, kapsam_where). _map_* temp tabloları id-remap için.
_L1_TABLES = [
    ("tenant_values",              "s.tenant_id = :t"),
    ("tenant_ethics_codes",        "s.tenant_id = :t"),
    ("tenant_quality_policies",    "s.tenant_id = :t"),
    ("plan_years",                 "s.tenant_id = :t"),
    ("tenant_year_identities",     "s.tenant_id = :t"),
    ("strategies",                 "s.tenant_id = :t"),
    ("sub_strategies",             "s.strategy_id IN (SELECT old_id FROM _map_strategies)"),
    ("processes",                  "s.tenant_id = :t"),
    ("process_sub_strategy_links", "s.process_id IN (SELECT old_id FROM _map_processes) AND s.sub_strategy_id IN (SELECT old_id FROM _map_sub_strategies)"),
    ("process_kpis",               "s.process_id IN (SELECT old_id FROM _map_processes)"),
    ("process_activities",         "s.process_id IN (SELECT old_id FROM _map_processes)"),
    ("kpi_year_configs",           "s.plan_year_id IN (SELECT old_id FROM _map_plan_years)"),
    ("strategy_year_configs",      "s.plan_year_id IN (SELECT old_id FROM _map_plan_years)"),
    ("sub_strategy_year_configs",  "s.plan_year_id IN (SELECT old_id FROM _map_plan_years)"),
    ("process_year_configs",       "s.plan_year_id IN (SELECT old_id FROM _map_plan_years)"),
    ("process_maturity",           "s.tenant_id = :t"),
]
# L2 = L1 + PGV + bireysel (user-bağlı → user-remap gerekir)
_L2_TABLES = [
    ("kpi_data",                   "s.process_kpi_id IN (SELECT old_id FROM _map_process_kpis)"),
    ("kpi_data_audits",            "s.kpi_data_id IN (SELECT old_id FROM _map_kpi_data)"),
    ("individual_performance_indicators", "s.user_id IN (SELECT old_id FROM _map_users)"),
    ("individual_activities",      "s.user_id IN (SELECT old_id FROM _map_users)"),
    ("individual_kpi_data",        "s.individual_pg_id IN (SELECT old_id FROM _map_individual_performance_indicators)"),
]
# L3 = L2 + ileri analiz
_L3_TABLES = [
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
    ("vrio_resources",             "s.tenant_id = :t"),
    ("blue_ocean_canvases",        "s.tenant_id = :t"),
    ("blue_ocean_factors",         "s.canvas_id IN (SELECT old_id FROM _map_blue_ocean_canvases)"),
    ("blue_ocean_errc_items",      "s.canvas_id IN (SELECT old_id FROM _map_blue_ocean_canvases)"),
    ("value_chain_items",          "s.tenant_id = :t"),
    ("k_vektor_strategy_weights",     "s.tenant_id = :t"),
    ("k_vektor_sub_strategy_weights", "s.tenant_id = :t"),
]

_LEVEL_TABLES = {
    "tom1": _L1_TABLES,
    "tom2": _L1_TABLES + _L2_TABLES,
    "tom3": _L1_TABLES + _L2_TABLES + _L3_TABLES,
}
_LEVEL_PACKAGE = {"tom1": "baslangic", "tom2": "yonetim", "tom3": "strateji"}


def say(m):
    try:
        print(m)
    except UnicodeEncodeError:
        print(m.encode("ascii", "replace").decode("ascii"))


def _copy_users(source_tid, new_tid, prefix, dry_run):
    """Tomofil kullanıcılarını PREFIX'li email + ortak şifre ile kopyala.

    _map_users (old_id->new_id) temp tablosu kurar (bireysel veri remap için).
    Döner: kopyalanan kullanıcı sayısı.
    """
    db.session.execute(text(
        'CREATE TEMP TABLE _map_users (old_id bigint PRIMARY KEY, new_id bigint) ON COMMIT DROP'))
    db.session.execute(text(
        'INSERT INTO _map_users(old_id, new_id) '
        "SELECT id, nextval(pg_get_serial_sequence('users','id')) "
        'FROM users WHERE tenant_id = :t'), {"t": source_tid})

    cols = _columns("users")
    pwd_hash = generate_password_hash(TEST_SIFRE)
    select_exprs, insert_cols = [], []
    for col in cols:
        insert_cols.append(_q(col))
        if col == "id":
            select_exprs.append("m.new_id")
        elif col == "tenant_id":
            select_exprs.append(":newt")
        elif col == "email":
            select_exprs.append(":pfx || s.email")     # 1ali@x
        elif col == "password_hash":
            select_exprs.append(":pwd")                  # ortak şifre
        else:
            select_exprs.append(f"s.{_q(col)}")          # ad/soyad/rol_id vb. aynen
    sql = (f'INSERT INTO users ({", ".join(insert_cols)}) '
           f'SELECT {", ".join(select_exprs)} '
           f'FROM users s JOIN _map_users m ON m.old_id = s.id '
           f'WHERE s.tenant_id = :t')
    res = db.session.execute(text(sql),
        {"t": source_tid, "newt": new_tid, "pfx": prefix, "pwd": pwd_hash})
    return res.rowcount or 0


def _copy_table_useraware(table, scope_where, source_tid, new_tid, clone_set,
                          existing, made_maps):
    """tenant_clone_service._copy_table'ın user-aware türevi.

    Fark: user FK'leri tek admin'e DEĞİL, _map_users üzerinden DOĞRU kullanıcıya
    remap edilir. Diğer FK'ler _map_<hedef> ile remap (o tablo kopyalandıysa).
    """
    if table not in existing:
        return 0
    cols = _columns(table)
    has_id = "id" in cols
    fkmap = _fk_targets(table)

    if has_id:
        db.session.execute(text(
            f'CREATE TEMP TABLE _map_{table} (old_id bigint PRIMARY KEY, new_id bigint) ON COMMIT DROP'))
        db.session.execute(text(
            f'INSERT INTO _map_{table}(old_id, new_id) '
            f"SELECT s.id, nextval(pg_get_serial_sequence('{table}','id')) "
            f'FROM {_q(table)} s WHERE {scope_where}'), {"t": source_tid})

    select_exprs, insert_cols, joins = [], [], []
    jn = 0
    for col in cols:
        insert_cols.append(_q(col))
        if has_id and col == "id":
            select_exprs.append("m.new_id"); continue
        if col == "tenant_id":
            select_exprs.append(":newt"); continue
        target = fkmap.get(col)
        if target == "tenants":
            select_exprs.append("NULL"); continue
        if target == "users":
            # user FK → _map_users ile doğru kişiye (yoksa NULL)
            jn += 1; a = f"ju{jn}"
            joins.append(f'LEFT JOIN _map_users {a} ON {a}.old_id = s.{_q(col)}')
            select_exprs.append(f"{a}.new_id"); continue
        if target and target in clone_set and target in existing and target != table and (f"_map_{target}") in made_maps:
            jn += 1; a = f"j{jn}"
            joins.append(f'LEFT JOIN _map_{target} {a} ON {a}.old_id = s.{_q(col)}')
            select_exprs.append(f"{a}.new_id"); continue
        if target == table and has_id:
            jn += 1; a = f"j{jn}"
            joins.append(f'LEFT JOIN _map_{table} {a} ON {a}.old_id = s.{_q(col)}')
            select_exprs.append(f"{a}.new_id"); continue
        select_exprs.append(f"s.{_q(col)}")

    base_from = f'FROM {_q(table)} s'
    if has_id:
        base_from += f' JOIN _map_{table} m ON m.old_id = s.id'
        where = ""
    else:
        where = f" WHERE {scope_where}"
    sql = (f'INSERT INTO {_q(table)} ({", ".join(insert_cols)}) '
           f'SELECT {", ".join(select_exprs)} {base_from} {" ".join(joins)}{where}')
    res = db.session.execute(text(sql), {"t": source_tid, "newt": new_tid})
    if has_id:
        made_maps.add(f"_map_{table}")
    return res.rowcount or 0


def _find_tenant_by_name(name):
    return db.session.execute(text(
        "SELECT id FROM tenants WHERE lower(name)=lower(:n) LIMIT 1"), {"n": name}).scalar()


def _package_id(code):
    return db.session.execute(text(
        "SELECT id FROM subscription_packages WHERE code=:c LIMIT 1"), {"c": code}).scalar()


def _wipe_tenant(tid):
    """Bir test tenant'ını sil (FK CASCADE çoğunu halleder; users+tenant elle)."""
    db.session.execute(text("DELETE FROM users WHERE tenant_id=:t"), {"t": tid})
    db.session.execute(text("DELETE FROM tenants WHERE id=:t"), {"t": tid})


def build(dry_run=True, wipe=False):
    app = create_app()
    with app.app_context():
        source_tid = find_source_tenant_id()
        if not source_tid:
            say("HATA: Kaynak Tomofil bulunamadı."); return 1
        say(f"Kaynak Tomofil tenant_id: {source_tid}")
        existing = _existing_tables()

        rapor = {}
        for level in ("tom1", "tom2", "tom3"):
            tables = _LEVEL_TABLES[level]
            clone_set = {t for t, _ in tables}
            made_maps = set()
            prefix = level[-1]  # '1'/'2'/'3'

            # Önceki level'dan kalan temp eşleme tablolarını temizle
            # (dry-run'da commit yok → ON COMMIT DROP tetiklenmez).
            _drop = ["_map_users"] + [f"_map_{t}" for t, _ in tables]
            for tmp in _drop:
                db.session.execute(text(f"DROP TABLE IF EXISTS {tmp}"))

            # mevcut varsa wipe
            old = _find_tenant_by_name(level)
            if old:
                if wipe:
                    say(f"  [{level}] mevcut (id={old}) siliniyor…")
                    _wipe_tenant(old)
                else:
                    say(f"  [{level}] ZATEN VAR (id={old}) — atlanıyor (--wipe ile sil/yeniden).")
                    continue

            pkg_id = _package_id(_LEVEL_PACKAGE[level])
            new_tid = db.session.execute(text(
                "INSERT INTO tenants (name, short_name, tenant_type, is_active, package_id) "
                "VALUES (:n, :n, 'normal', true, :pkg) RETURNING id"),
                {"n": level, "pkg": pkg_id}).scalar()

            n_users = _copy_users(source_tid, new_tid, prefix, dry_run)
            counts = {"users": n_users}
            for table, scope in tables:
                n = _copy_table_useraware(table, scope, source_tid, new_tid,
                                          clone_set, existing, made_maps)
                if n:
                    counts[table] = n
            rapor[level] = {"new_tid": new_tid, "package": _LEVEL_PACKAGE[level],
                            "counts": counts, "total": sum(counts.values())}
            say(f"  [{level}] tid={new_tid} paket={_LEVEL_PACKAGE[level]} "
                f"kullanıcı={n_users} toplam_satır={sum(counts.values())}")
            for t, c in counts.items():
                if t != "users":
                    say(f"        {t}: {c}")

        if dry_run:
            db.session.rollback()
            say("\nDRY-RUN: hiçbir şey yazılmadı (rollback).")
        else:
            db.session.commit()
            say(f"\nTamamlandı. Ortak şifre: {TEST_SIFRE}")
            say("Giriş: 1<tomofil_email> (tom1), 2<...> (tom2), 3<...> (tom3)")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--wipe", action="store_true", help="mevcut tom1/2/3 sil + yeniden")
    args = ap.parse_args()
    sys.exit(build(dry_run=args.dry_run, wipe=args.wipe))
