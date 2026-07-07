# -*- coding: utf-8 -*-
"""
Kurum (Tenant) bazlı JSON yedekleme ve geri yükleme servisi.

Export: tenant_id'ye bağlı ~55 tablodan tüm veri → .json.gz
Restore: .json.gz → mevcut veriyi temizle + yeniden yükle (aynı ID'ler)
"""
import gzip
import json
import logging
from datetime import datetime, date
from decimal import Decimal

from sqlalchemy import text, inspect as sa_inspect

from extensions import db

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tablo planı — (tablo_adı, WHERE koşulu)
# :tid = tenant_id parametresi
# Sıra önemli: parent tablolar önce (export/insert), ters sıra delete için
# ---------------------------------------------------------------------------
TABLE_PLAN = [
    # ── Kurum & Kullanıcı ──────────────────────────────────────────────────
    ("tenants",                    "id = :tid"),
    ("users",                      "tenant_id = :tid"),

    # ── Strateji ──────────────────────────────────────────────────────────
    ("strategies",                 "tenant_id = :tid"),
    ("sub_strategies",
     "strategy_id IN (SELECT id FROM strategies WHERE tenant_id = :tid)"),

    # ── Süreç ─────────────────────────────────────────────────────────────
    ("processes",                  "tenant_id = :tid"),
    ("process_leaders",
     "process_id IN (SELECT id FROM processes WHERE tenant_id = :tid)"),
    ("process_members",
     "process_id IN (SELECT id FROM processes WHERE tenant_id = :tid)"),
    ("process_owners_table",
     "process_id IN (SELECT id FROM processes WHERE tenant_id = :tid)"),
    ("process_sub_strategy_links",
     "process_id IN (SELECT id FROM processes WHERE tenant_id = :tid)"),
    ("process_maturity",           "tenant_id = :tid"),

    # ── PG (Performans Göstergesi) ─────────────────────────────────────────
    ("process_kpis",
     "process_id IN (SELECT id FROM processes WHERE tenant_id = :tid)"),
    ("kpi_data",
     "process_kpi_id IN (SELECT id FROM process_kpis"
     " WHERE process_id IN (SELECT id FROM processes WHERE tenant_id = :tid))"),
    ("kpi_data_audits",
     "kpi_data_id IN (SELECT id FROM kpi_data WHERE process_kpi_id IN"
     " (SELECT id FROM process_kpis"
     " WHERE process_id IN (SELECT id FROM processes WHERE tenant_id = :tid)))"),
    ("favorite_kpis",
     "process_kpi_id IN (SELECT id FROM process_kpis"
     " WHERE process_id IN (SELECT id FROM processes WHERE tenant_id = :tid))"),
    ("bottleneck_log",             "tenant_id = :tid"),

    # ── Süreç Faaliyetleri ─────────────────────────────────────────────────
    ("process_activities",
     "process_id IN (SELECT id FROM processes WHERE tenant_id = :tid)"),
    ("process_activity_assignees",
     "activity_id IN (SELECT id FROM process_activities"
     " WHERE process_id IN (SELECT id FROM processes WHERE tenant_id = :tid))"),
    ("process_activity_reminders",
     "activity_id IN (SELECT id FROM process_activities"
     " WHERE process_id IN (SELECT id FROM processes WHERE tenant_id = :tid))"),
    ("activity_tracks",
     "user_id IN (SELECT id FROM users WHERE tenant_id = :tid)"),

    # ── Yıllık Plan ────────────────────────────────────────────────────────
    ("plan_years",                 "tenant_id = :tid"),
    ("kpi_year_configs",
     "process_kpi_id IN (SELECT id FROM process_kpis"
     " WHERE process_id IN (SELECT id FROM processes WHERE tenant_id = :tid))"),
    ("process_year_configs",
     "process_id IN (SELECT id FROM processes WHERE tenant_id = :tid)"),
    ("strategy_year_configs",
     "strategy_id IN (SELECT id FROM strategies WHERE tenant_id = :tid)"),
    ("sub_strategy_year_configs",
     "sub_strategy_id IN (SELECT id FROM sub_strategies"
     " WHERE strategy_id IN (SELECT id FROM strategies WHERE tenant_id = :tid))"),
    ("individual_kpi_year_configs",
     "plan_year_id IN (SELECT id FROM plan_years WHERE tenant_id = :tid)"),

    # ── Bireysel Performans ────────────────────────────────────────────────
    ("individual_performance_indicators",
     "user_id IN (SELECT id FROM users WHERE tenant_id = :tid)"),
    ("individual_activities",
     "user_id IN (SELECT id FROM users WHERE tenant_id = :tid)"),
    ("individual_kpi_data",
     "user_id IN (SELECT id FROM users WHERE tenant_id = :tid)"),
    ("individual_kpi_data_audits",
     "user_id IN (SELECT id FROM users WHERE tenant_id = :tid)"),
    ("individual_activity_tracks",
     "user_id IN (SELECT id FROM users WHERE tenant_id = :tid)"),

    # ── Projeler ──────────────────────────────────────────────────────────
    ("project",                    "tenant_id = :tid"),
    ("sprint",
     "project_id IN (SELECT id FROM project WHERE tenant_id = :tid)"),
    ("task",
     "project_id IN (SELECT id FROM project WHERE tenant_id = :tid)"),
    ("task_activity",
     "task_id IN (SELECT id FROM task"
     " WHERE project_id IN (SELECT id FROM project WHERE tenant_id = :tid))"),
    ("task_comment",
     "task_id IN (SELECT id FROM task"
     " WHERE project_id IN (SELECT id FROM project WHERE tenant_id = :tid))"),
    ("task_mention",
     "task_id IN (SELECT id FROM task"
     " WHERE project_id IN (SELECT id FROM project WHERE tenant_id = :tid))"),
    ("task_subtask",
     "task_id IN (SELECT id FROM task"
     " WHERE project_id IN (SELECT id FROM project WHERE tenant_id = :tid))"),
    ("task_dependency",
     "project_id IN (SELECT id FROM project WHERE tenant_id = :tid)"),
    ("time_entry",
     "task_id IN (SELECT id FROM task"
     " WHERE project_id IN (SELECT id FROM project WHERE tenant_id = :tid))"),
    ("project_file",
     "project_id IN (SELECT id FROM project WHERE tenant_id = :tid)"),
    ("project_risk",
     "project_id IN (SELECT id FROM project WHERE tenant_id = :tid)"),
    ("raid_item",
     "project_id IN (SELECT id FROM project WHERE tenant_id = :tid)"),
    ("sla",
     "project_id IN (SELECT id FROM project WHERE tenant_id = :tid)"),
    ("working_day",
     "project_id IN (SELECT id FROM project WHERE tenant_id = :tid)"),
    ("recurring_task",
     "project_id IN (SELECT id FROM project WHERE tenant_id = :tid)"),
    ("capacity_plan",
     "project_id IN (SELECT id FROM project WHERE tenant_id = :tid)"),
    ("evm_snapshots",              "tenant_id = :tid"),
    ("project_leaders",
     "project_id IN (SELECT id FROM project WHERE tenant_id = :tid)"),
    ("project_members",
     "project_id IN (SELECT id FROM project WHERE tenant_id = :tid)"),
    ("project_observers",
     "project_id IN (SELECT id FROM project WHERE tenant_id = :tid)"),
    ("project_related_processes",
     "project_id IN (SELECT id FROM project WHERE tenant_id = :tid)"),
    ("integration_hook",
     "project_id IN (SELECT id FROM project WHERE tenant_id = :tid)"),
    ("rule_definition",
     "project_id IN (SELECT id FROM project WHERE tenant_id = :tid)"),
    ("activity",
     "project_id IN (SELECT id FROM project WHERE tenant_id = :tid)"),

    # ── Analiz Araçları ───────────────────────────────────────────────────
    ("a3_reports",                 "tenant_id = :tid"),
    ("competitor_analyses",        "tenant_id = :tid"),
    ("risk_heatmap_items",         "tenant_id = :tid"),
    ("stakeholder_maps",           "tenant_id = :tid"),
    ("stakeholder_surveys",        "tenant_id = :tid"),
    ("value_chain_items",          "tenant_id = :tid"),

    # ── K-Vektör / K-Radar ────────────────────────────────────────────────
    ("k_vektor_strategy_weights",      "tenant_id = :tid"),
    ("k_vektor_sub_strategy_weights",  "tenant_id = :tid"),
    ("k_vektor_config_snapshots",      "tenant_id = :tid"),
    ("k_radar_recommendation_actions", "tenant_id = :tid"),

    # ── Ayarlar & Bildirimler ─────────────────────────────────────────────
    ("tenant_email_configs",       "tenant_id = :tid"),
    ("notifications",              "tenant_id = :tid"),
    ("tickets",                    "tenant_id = :tid"),
    ("push_subscriptions",
     "user_id IN (SELECT id FROM users WHERE tenant_id = :tid)"),

    # ── Legacy Tablolar ───────────────────────────────────────────────────
    ("kurum",                      "tenant_id = :tid"),
    ("user",                       "tenant_id = :tid"),
    ("ana_strateji",               "tenant_id = :tid"),
    ("corporate_identity",         "tenant_id = :tid"),
    ("deger",                      "tenant_id = :tid"),
    ("etik_kural",                 "tenant_id = :tid"),
    ("kalite_politikasi",          "tenant_id = :tid"),

    # ── Audit (son — büyük olabilir) ──────────────────────────────────────
    ("audit_logs",                 "tenant_id = :tid"),
]


# ---------------------------------------------------------------------------
# Yardımcılar
# ---------------------------------------------------------------------------

def _coerce_row_bind_params(row: dict) -> dict:
    """PostgreSQL/psycopg2 dict/list bağlayıcı uyumu (JSON/JSONB sütunlar)."""
    out = {}
    for k, v in row.items():
        if isinstance(v, (dict, list)):
            out[k] = json.dumps(v, ensure_ascii=False)
        else:
            out[k] = v
    return out


def _serialize(v):
    """Değeri JSON-serializable hale getirir."""
    if v is None:
        return None
    if isinstance(v, datetime):
        return v.isoformat()
    if isinstance(v, date):
        return v.isoformat()
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, bytes):
        import base64
        return base64.b64encode(v).decode("ascii")
    if isinstance(v, dict):
        return {k: _serialize(val) for k, val in v.items()}
    if isinstance(v, (list, tuple)):
        return [_serialize(i) for i in v]
    return v


def _existing_tables():
    conn = db.session.connection()
    return set(sa_inspect(conn).get_table_names())


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

def export_tenant_json(tenant_id: int) -> bytes:
    """
    Kuruma ait tüm veriyi JSON.GZ olarak döner.
    Dönüş: gzip sıkıştırılmış bytes
    """
    existing = _existing_tables()

    tenant_row = db.session.execute(
        text("SELECT * FROM tenants WHERE id = :tid"),
        {"tid": tenant_id}
    ).mappings().first()

    if not tenant_row:
        raise ValueError(f"Tenant {tenant_id} bulunamadı")

    tenant_name = tenant_row.get("name", str(tenant_id))
    tables_data = {}
    stats = {}

    for table_name, where_clause in TABLE_PLAN:
        if table_name not in existing:
            continue
        try:
            sql = f"SELECT * FROM {table_name} WHERE {where_clause}"  # noqa: S608
            result = db.session.execute(text(sql), {"tid": tenant_id})
            columns = list(result.keys())
            rows = [
                {col: _serialize(val) for col, val in zip(columns, row)}
                for row in result
            ]
            tables_data[table_name] = rows
            stats[table_name] = len(rows)
        except Exception as exc:
            logger.warning("[tenant_export] %s atlandı: %s", table_name, exc)
            db.session.rollback()

    payload = {
        "meta": {
            "format": "kokpitim-tenant-backup-v1",
            "tenant_id": tenant_id,
            "tenant_name": tenant_name,
            "exported_at": datetime.utcnow().isoformat() + "Z",
            "table_counts": stats,
            "total_records": sum(stats.values()),
        },
        "tables": tables_data,
    }

    json_bytes = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return gzip.compress(json_bytes, compresslevel=6)


# ---------------------------------------------------------------------------
# Preview
# ---------------------------------------------------------------------------

def preview_backup(data: dict) -> dict:
    """Yüklenen yedek dosyasının özetini döner."""
    meta = data.get("meta", {})
    tables = data.get("tables", {})
    counts = {t: len(rows) for t, rows in tables.items() if rows}
    return {
        "format": meta.get("format"),
        "tenant_name": meta.get("tenant_name", "?"),
        "tenant_id": meta.get("tenant_id"),
        "exported_at": meta.get("exported_at"),
        "total_records": sum(counts.values()),
        "table_counts": counts,
    }


# ---------------------------------------------------------------------------
# Restore
# ---------------------------------------------------------------------------

def restore_tenant_data(data: dict) -> dict:
    """
    Yedekten kurumu geri yükler:
    1. Mevcut kurum verisini ters sırayla sil
    2. Yedeği doğru sırayla ekle (ON CONFLICT DO NOTHING)
    3. Sequence'ları güncelle

    Dönüş: {"restored": {tablo: satır_sayısı}, "skipped": [...], "errors": [...]}
    """
    meta = data.get("meta", {})
    tables_data = data.get("tables", {})
    tenant_id = meta.get("tenant_id")

    if not tenant_id:
        raise ValueError("Yedek dosyasında tenant_id bulunamadı")

    existing = _existing_tables()
    restored = {}
    skipped = []
    errors = []

    # Silme WHERE koşulları (TABLE_PLAN'dan)
    where_map = {t: w for t, w in TABLE_PLAN}

    with db.session.begin_nested():
        # 1 ── Silme (ters sıra: leaf önce)
        for table_name in reversed([t for t, _ in TABLE_PLAN]):
            if table_name not in existing:
                continue
            if table_name not in tables_data:
                continue
            where = where_map[table_name]
            try:
                db.session.execute(
                    text(f"DELETE FROM {table_name} WHERE {where}"),  # noqa: S608
                    {"tid": tenant_id}
                )
            except Exception as exc:
                logger.warning("[restore] %s silinemedi: %s", table_name, exc)
                errors.append(f"Silme ({table_name}): {exc}")
                db.session.rollback()

        # 2 ── Ekleme (doğru sıra: parent önce)
        for table_name, _ in TABLE_PLAN:
            if table_name not in existing:
                skipped.append(table_name)
                continue
            rows = tables_data.get(table_name)
            if not rows:
                continue

            count = 0
            for row in rows:
                cols = list(row.keys())
                if not cols:
                    continue
                col_str = ", ".join(f'"{c}"' for c in cols)
                val_str = ", ".join(f":{c}" for c in cols)
                sql = (
                    f'INSERT INTO {table_name} ({col_str}) VALUES ({val_str})'  # noqa: S608
                    f' ON CONFLICT DO NOTHING'
                )
                bind = _coerce_row_bind_params(dict(row))
                try:
                    with db.session.begin_nested():
                        db.session.execute(text(sql), bind)
                    count += 1
                except Exception as exc:
                    logger.warning("[restore] %s satır eklenemedi: %s", table_name, exc)
                    errors.append(f"Ekleme ({table_name}): {exc}")

            if count:
                restored[table_name] = count

    db.session.commit()

    # 3 ── Sequence güncelle
    _reset_sequences(existing, tables_data)

    return {
        "restored": restored,
        "skipped": skipped,
        "errors": errors[:20],  # ilk 20 hata
        "total_restored": sum(restored.values()),
    }


def _reset_sequences(existing: set, tables_data: dict):
    """
    PostgreSQL sequence'larını restore sonrası MAX(id)'ye göre günceller.
    """
    for table_name, _ in TABLE_PLAN:
        if table_name not in existing:
            continue
        if not tables_data.get(table_name):
            continue
        try:
            db.session.execute(text(
                f"SELECT setval("  # noqa: S608
                f"  pg_get_serial_sequence('{table_name}', 'id'),"
                f"  COALESCE((SELECT MAX(id) FROM {table_name}), 1)"
                f")"
            ))
            db.session.commit()
        except Exception:
            db.session.rollback()
