# -*- coding: utf-8 -*-
"""Demo: Tomofil tenant'ını yeni bir tenant_id'ye klonlar (Tom1/Tom2/Tom3 için).

`services.tenant_backup_service.restore_tenant_data` yalnızca AYNI tenant_id'ye
geri yükleme yapar (id remap yok). Bu script farklı bir hedef tenant_id'ye
klonlamak için TABLE_PLAN'daki her tabloyu okuyup PK'leri ve FK referanslarını
yeni bir id-map ile yeniden yazar.

YALNIZCA KOKPITIM_DEMO_MODE=1 ortamında çalışır.

Kullanım (demo container içinde):
    python -m scripts.demo_clone_tenant --source 27 --target 28 --name Tom1 --package baslangic
    python -m scripts.demo_clone_tenant --source 27 --target 29 --name Tom2 --package yonetim
    python -m scripts.demo_clone_tenant --source 27 --target 30 --name Tom3 --package strateji
"""
from __future__ import annotations

import argparse
import sys

from sqlalchemy import text, inspect as sa_inspect

from services.tenant_backup_service import TABLE_PLAN

# Kaynak tenant'a FK ile bağlı olup id-remap gerektirmeyen (tenant scope dışı,
# global) tablolar TABLE_PLAN'da zaten yok — bu yüzden TABLE_PLAN'ın tamamı
# "tenant'a ait" kabul edilir ve her satırın id'si yeniden numaralandırılır.

# Klonlanan her tabloda, o tablonun başka bir klonlanan tabloya işaret eden
# FK kolonları (id-remap uygulanacak kolonlar). "tenant_id" ayrıca ele alınır.
_FK_COLUMNS = {
    "users": ["tenant_id"],
    "strategies": ["tenant_id"],
    "sub_strategies": ["strategy_id"],
    "processes": ["tenant_id"],
    "process_leaders": ["process_id", "user_id"],
    "process_members": ["process_id", "user_id"],
    "process_owners_table": ["process_id", "user_id"],
    "process_sub_strategy_links": ["process_id", "sub_strategy_id"],
    "process_maturity": ["tenant_id", "process_id"],
    "process_kpis": ["process_id"],
    "kpi_data": ["process_kpi_id"],
    "kpi_data_audits": ["process_kpi_id"],
    "favorite_kpis": ["process_kpi_id", "user_id"],
    "bottleneck_log": ["tenant_id", "process_id"],
    "process_activities": ["process_id"],
    "process_activity_assignees": ["activity_id", "user_id"],
    "process_activity_reminders": ["activity_id", "user_id"],
    "activity_tracks": ["user_id"],
    "plan_years": ["tenant_id"],
    "kpi_year_configs": ["process_kpi_id", "plan_year_id"],
    "process_year_configs": ["process_id", "plan_year_id"],
    "strategy_year_configs": ["strategy_id", "plan_year_id"],
    "sub_strategy_year_configs": ["sub_strategy_id", "plan_year_id"],
    "individual_kpi_year_configs": ["plan_year_id", "user_id"],
    "individual_performance_indicators": ["user_id"],
    "individual_activities": ["user_id"],
    "individual_kpi_data": ["user_id"],
    "individual_kpi_data_audits": ["user_id"],
    "individual_activity_tracks": ["user_id"],
    "project": ["tenant_id"],
    "sprint": ["project_id"],
    "task": ["project_id"],
    "task_activity": ["task_id", "user_id"],
    "task_comment": ["task_id", "user_id"],
    "task_mention": ["task_id", "user_id"],
    "task_subtask": ["task_id"],
    "task_dependency": ["project_id"],
    "time_entry": ["task_id", "user_id"],
    "project_file": ["project_id", "user_id"],
    "project_risk": ["project_id"],
    "raid_item": ["project_id"],
    "sla": ["project_id"],
    "working_day": ["project_id"],
    "recurring_task": ["project_id"],
    "capacity_plan": ["project_id"],
    "evm_snapshots": ["tenant_id", "project_id"],
    "project_leaders": ["project_id", "user_id"],
    "project_members": ["project_id", "user_id"],
    "project_observers": ["project_id", "user_id"],
    "project_related_processes": ["project_id", "process_id"],
    "integration_hook": ["project_id"],
    "rule_definition": ["project_id"],
    "activity": ["project_id", "user_id"],
    "a3_reports": ["tenant_id"],
    "competitor_analyses": ["tenant_id"],
    "risk_heatmap_items": ["tenant_id"],
    "stakeholder_maps": ["tenant_id"],
    "stakeholder_surveys": ["tenant_id"],
    "value_chain_items": ["tenant_id"],
    "k_vektor_strategy_weights": ["tenant_id", "strategy_id"],
    "k_vektor_sub_strategy_weights": ["tenant_id", "sub_strategy_id"],
    "k_vektor_config_snapshots": ["tenant_id"],
    "k_radar_recommendation_actions": ["tenant_id"],
    "tenant_email_configs": ["tenant_id"],
    "notifications": ["tenant_id", "user_id"],
    "tickets": ["tenant_id", "user_id"],
    "push_subscriptions": ["user_id"],
    "audit_logs": ["tenant_id", "user_id"],
}

# id-remap uygulanacak "kaynak tablolar" (bu tabloların kendi id'si başka
# tablolarda FK olarak referans alınabilir): tabloadı → id kolonunun PK olduğu varsayımı.
_ID_MAP_TABLES = {t for t, _ in TABLE_PLAN}


def _existing_tables(conn) -> set:
    return set(sa_inspect(conn).get_table_names())


def clone_tenant(source_id: int, target_id: int, new_name: str, package_code: str,
                  email_domain: str) -> dict:
    from extensions import db
    from app.models.saas import SubscriptionPackage

    conn = db.session.connection()
    existing = _existing_tables(conn)

    # Guard: hedef tenant_id zaten kullanımda olmamalı
    already = conn.execute(
        text("SELECT 1 FROM tenants WHERE id = :tid"), {"tid": target_id}
    ).first()
    if already:
        raise ValueError(f"Hedef tenant_id={target_id} zaten mevcut — önce temizle veya farklı id seç")

    pkg = SubscriptionPackage.query.filter_by(code=package_code).first()
    if not pkg:
        raise ValueError(f"Paket kodu bulunamadı: {package_code}")

    # id_map[table_name][old_id] = new_id  (yalnız "id" PK'si olan tablolar için)
    id_map: dict[str, dict[int, int]] = {}
    stats: dict[str, int] = {}

    for table_name, where_clause in TABLE_PLAN:
        if table_name not in existing:
            continue
        sql = f"SELECT * FROM {table_name} WHERE {where_clause}"  # noqa: S608
        rows = conn.execute(text(sql), {"tid": source_id}).mappings().all()
        if not rows:
            continue

        fk_cols = _FK_COLUMNS.get(table_name, [])
        has_pk_id = "id" in rows[0].keys()
        local_map = {}

        cols = list(rows[0].keys())
        insert_cols = [c for c in cols if c != "id"] if has_pk_id else cols
        col_str = ", ".join(f'"{c}"' for c in insert_cols)
        val_str = ", ".join(f":{c}" for c in insert_cols)
        # tenants tablosu için id hedef olarak açıkça belirlenir (rastgele PK atanmasın)
        if table_name == "tenants":
            col_str = f'"id", {col_str}'
            val_str = f':id, {val_str}'
        returning = ' RETURNING "id"' if has_pk_id else ""
        insert_sql = (
            f'INSERT INTO {table_name} ({col_str}) VALUES ({val_str}){returning}'  # noqa: S608
        )

        n = 0
        for row in rows:
            data = dict(row)
            old_id = data.pop("id", None) if has_pk_id else None

            if table_name == "tenants":
                data["id"] = target_id
                # parent_tenant_id kendine referans olabilir; klon bağımsız kurum olsun
                data["parent_tenant_id"] = None

            # tenant_id kolonu varsa doğrudan hedefe yaz
            if "tenant_id" in data:
                data["tenant_id"] = target_id

            # FK kolonlarını id_map üzerinden yeniden yaz (tenant_id hariç, yukarıda ele alındı)
            for fk in fk_cols:
                if fk == "tenant_id" or fk not in data or data[fk] is None:
                    continue
                parent_table = _guess_parent_table(fk, table_name)
                mapped = id_map.get(parent_table, {}).get(data[fk])
                if mapped is not None:
                    data[fk] = mapped
                # mapped yoksa (parent klonlanmadıysa/global tablo) değer aynen kalır

            # Kullanıcı e-postalarını çakışmasız hale getir
            if table_name == "users" and "email" in data and data["email"]:
                local, _, domain = str(data["email"]).partition("@")
                data["email"] = f"{local}+{email_domain}@{domain or 'kokpitim.demo'}"

            bind = {c: data.get(c) for c in insert_cols}
            if table_name == "tenants":
                bind["id"] = target_id
            result = conn.execute(text(insert_sql), bind)
            if has_pk_id:
                new_id = result.scalar()
                local_map[old_id] = new_id
            n += 1

        if has_pk_id:
            id_map[table_name] = local_map
        stats[table_name] = n

    # Yeni tenant satırının adı + paketini güncelle (tenants tablosu id=target_id ile zaten eklendi)
    conn.execute(
        text("UPDATE tenants SET name = :name, short_name = :name, package_id = :pkg WHERE id = :tid"),
        {"name": new_name, "pkg": pkg.id, "tid": target_id},
    )

    # Sequence'leri ileri al — sonraki klon veya normal kayıt akışı PK çakışmasın
    for table_name in stats:
        if table_name not in _ID_MAP_TABLES:
            continue
        try:
            conn.execute(text(
                f"SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), "  # noqa: S608
                f"COALESCE((SELECT MAX(id) FROM {table_name}), 1))"
            ))
        except Exception:
            pass

    db.session.commit()
    return {"target_id": target_id, "table_counts": stats}


def _guess_parent_table(fk_col: str, child_table: str) -> str:
    """FK kolon adından kaynak (parent) tablo adını tahmin eder.

    Bilinen istisnalar için özel eşleme; aksi halde 'xxx_id' → 'xxxs' kuralı.
    """
    overrides = {
        "process_kpi_id": "process_kpis",
        "process_id": "processes",
        "sub_strategy_id": "sub_strategies",
        "strategy_id": "strategies",
        "plan_year_id": "plan_years",
        "activity_id": "process_activities",
        "task_id": "task",
        "project_id": "project",
        "user_id": "users",
    }
    return overrides.get(fk_col, fk_col[:-3] + "s")


def main(argv):
    parser = argparse.ArgumentParser(description="Tomofil'i yeni bir demo tenant'ına klonla")
    parser.add_argument("--source", type=int, required=True, help="Kaynak tenant_id (Tomofil)")
    parser.add_argument("--target", type=int, required=True, help="Hedef tenant_id (yeni, boş olmalı)")
    parser.add_argument("--name", type=str, required=True, help="Yeni kurum adı (örn. Tom1)")
    parser.add_argument("--package", type=str, required=True, help="Paket kodu (baslangic/yonetim/strateji/master_package)")
    args = parser.parse_args(argv[1:])

    from dotenv import load_dotenv
    load_dotenv()
    from app import create_app
    app = create_app()

    if not app.config.get("KOKPITIM_DEMO_MODE"):
        print("HATA: KOKPITIM_DEMO_MODE=1 değil. Bu script yalnızca demo ortamında çalışır.")
        return 2

    with app.app_context():
        print(f"→ Tomofil (tenant_id={args.source}) → {args.name} (tenant_id={args.target}, paket={args.package}) klonlanıyor…")
        try:
            result = clone_tenant(args.source, args.target, args.name, args.package,
                                   email_domain=args.name.lower())
        except Exception as e:
            print(f"HATA: {e}")
            return 1
        total = sum(result["table_counts"].values())
        print(f"✓ klonlandı: {total} kayıt, {len(result['table_counts'])} tablo")
        print("→ Sonraki adım: diğer tenant'lar için tekrarla, ardından `python -m scripts.demo_baseline snapshot`")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
