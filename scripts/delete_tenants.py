"""Tenant toplu silme — TEHLİKELİ, GERİ ALINMAZ.

Yedek: backups/pre-delete-tenants-20260525_150717.dump
Geri yükleme: pg_restore -d kokpitim_db --clean --if-exists <dump_file>

Kullanım (.venv aktif):
    python scripts/delete_tenants.py
"""
from __future__ import annotations

import sys
import os
sys.stdout.reconfigure(encoding="utf-8")

# Proje kökünü sys.path'e ekle (scripts/ alt dizininden çalıştığımız için)
_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if _root not in sys.path:
    sys.path.insert(0, _root)

from app import create_app
from extensions import db
from sqlalchemy import text


TENANT_IDS = tuple([2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 17, 18, 19])
ADMIN_USER_ID = 1  # admin@kokpitim.com (Default Corp — silinmez)

DELETES = [
    # ── 1. Direkt tenant_id NO ACTION ─────────────────────────────
    ("a3_reports", "DELETE FROM a3_reports WHERE tenant_id IN :ids"),
    ("bottleneck_log", "DELETE FROM bottleneck_log WHERE tenant_id IN :ids"),
    ("competitor_analyses", "DELETE FROM competitor_analyses WHERE tenant_id IN :ids"),
    ("evm_snapshots", "DELETE FROM evm_snapshots WHERE tenant_id IN :ids"),
    ("k_radar_recommendation_actions", "DELETE FROM k_radar_recommendation_actions WHERE tenant_id IN :ids"),
    ("notifications", "DELETE FROM notifications WHERE tenant_id IN :ids"),
    ("process_maturity", "DELETE FROM process_maturity WHERE tenant_id IN :ids"),
    ("risk_heatmap_items", "DELETE FROM risk_heatmap_items WHERE tenant_id IN :ids"),
    ("stakeholder_maps", "DELETE FROM stakeholder_maps WHERE tenant_id IN :ids"),
    ("stakeholder_surveys", "DELETE FROM stakeholder_surveys WHERE tenant_id IN :ids"),
    ("tenant_email_configs", "DELETE FROM tenant_email_configs WHERE tenant_id IN :ids"),
    ("value_chain_items", "DELETE FROM value_chain_items WHERE tenant_id IN :ids"),

    # ── 2. Process zinciri ────────────────────────────────────────
    ("kpi_data_audits (process)", "DELETE FROM kpi_data_audits WHERE kpi_data_id IN (SELECT id FROM kpi_data WHERE process_kpi_id IN (SELECT id FROM process_kpis WHERE process_id IN (SELECT id FROM processes WHERE tenant_id IN :ids)))"),
    ("kpi_data (process)", "DELETE FROM kpi_data WHERE process_kpi_id IN (SELECT id FROM process_kpis WHERE process_id IN (SELECT id FROM processes WHERE tenant_id IN :ids))"),
    ("favorite_kpis", "DELETE FROM favorite_kpis WHERE process_kpi_id IN (SELECT id FROM process_kpis WHERE process_id IN (SELECT id FROM processes WHERE tenant_id IN :ids))"),
    ("process_activity_assignees", "DELETE FROM process_activity_assignees WHERE activity_id IN (SELECT id FROM process_activities WHERE process_id IN (SELECT id FROM processes WHERE tenant_id IN :ids))"),
    ("process_activity_reminders", "DELETE FROM process_activity_reminders WHERE activity_id IN (SELECT id FROM process_activities WHERE process_id IN (SELECT id FROM processes WHERE tenant_id IN :ids))"),
    ("process_activities", "DELETE FROM process_activities WHERE process_id IN (SELECT id FROM processes WHERE tenant_id IN :ids)"),
    ("process_kpis", "DELETE FROM process_kpis WHERE process_id IN (SELECT id FROM processes WHERE tenant_id IN :ids)"),
    ("process_sub_strategy_links", "DELETE FROM process_sub_strategy_links WHERE process_id IN (SELECT id FROM processes WHERE tenant_id IN :ids)"),
    ("processes", "DELETE FROM processes WHERE tenant_id IN :ids"),

    # ── 3. strategies ─────────────────────────────────────────────
    ("sub_strategies", "DELETE FROM sub_strategies WHERE strategy_id IN (SELECT id FROM strategies WHERE tenant_id IN :ids)"),
    ("strategies", "DELETE FROM strategies WHERE tenant_id IN :ids"),

    # ── 4. Bireysel ───────────────────────────────────────────────
    ("individual_kpi_data_audits", "DELETE FROM individual_kpi_data_audits WHERE individual_kpi_data_id IN (SELECT id FROM individual_kpi_data WHERE user_id IN (SELECT id FROM users WHERE tenant_id IN :ids))"),
    ("individual_kpi_data", "DELETE FROM individual_kpi_data WHERE user_id IN (SELECT id FROM users WHERE tenant_id IN :ids)"),
    ("individual_activity_tracks", "DELETE FROM individual_activity_tracks WHERE individual_activity_id IN (SELECT id FROM individual_activities WHERE user_id IN (SELECT id FROM users WHERE tenant_id IN :ids))"),
    ("individual_activities", "DELETE FROM individual_activities WHERE user_id IN (SELECT id FROM users WHERE tenant_id IN :ids)"),
    ("individual_performance_indicators", "DELETE FROM individual_performance_indicators WHERE user_id IN (SELECT id FROM users WHERE tenant_id IN :ids)"),

    # ── 5. Cross-tenant imzaları temizle (silinecek user_id'leri devret veya sil) ─
    # NOT NULL alanlar: kpi_data.user_id → admin'e devret
    ("REASSIGN kpi_data.user_id → admin", f"UPDATE kpi_data SET user_id={ADMIN_USER_ID} WHERE user_id IN (SELECT id FROM users WHERE tenant_id IN :ids)"),
    ("REASSIGN kpi_data_audits.user → admin", f"UPDATE kpi_data_audits SET user_id={ADMIN_USER_ID} WHERE user_id IN (SELECT id FROM users WHERE tenant_id IN :ids)"),
    # Cross-tenant notifications: silinen user'a gönderilmiş bildirimler — sil
    ("notifications (cross-tenant)", "DELETE FROM notifications WHERE user_id IN (SELECT id FROM users WHERE tenant_id IN :ids)"),
    # Diğer user FK NO ACTION tabloları — kullanıcı verisi silindiği için bunlar da gider
    ("activity_tracks", "DELETE FROM activity_tracks WHERE user_id IN (SELECT id FROM users WHERE tenant_id IN :ids)"),
    ("audit_logs", "DELETE FROM audit_logs WHERE user_id IN (SELECT id FROM users WHERE tenant_id IN :ids)"),
    ("push_subscriptions", "DELETE FROM push_subscriptions WHERE user_id IN (SELECT id FROM users WHERE tenant_id IN :ids)"),
    # SET NULL alanlar otomatik — burada yine de tetiklemek için boş UPDATE'ler gereksiz
    # SET NULL kuralı zaten DELETE FROM users'da otomatik tetiklenir

    # ── 6. users ──────────────────────────────────────────────────
    ("users", "DELETE FROM users WHERE tenant_id IN :ids"),

    # ── 7. tenants (CASCADE'ler tetiklenir) ───────────────────────
    ("tenants", "DELETE FROM tenants WHERE id IN :ids"),
]


def main():
    app = create_app()
    with app.app_context():
        print(f"\nSilinecek {len(TENANT_IDS)} tenant ID: {list(TENANT_IDS)}")
        print(f"Admin user (cross-tenant imza devri): {ADMIN_USER_ID}")
        print(f"Yedek: backups/pre-delete-tenants-20260525_150717.dump (1.33 MB)")
        print()
        try:
            resp = input("Devam etmek için 'EVET SIL' yaz: ").strip()
        except EOFError:
            resp = ""
        if resp != "EVET SIL":
            print("İptal edildi.")
            return

        try:
            total = 0
            for tbl, sql in DELETES:
                try:
                    r = db.session.execute(text(sql), {"ids": TENANT_IDS})
                    if r.rowcount > 0:
                        total += r.rowcount
                        print(f"  {tbl:<50} {r.rowcount:>6}")
                except Exception as e:
                    msg = str(e)[:120]
                    if "does not exist" in msg:
                        print(f"  {tbl:<50} (tablo yok)")
                        continue
                    raise
            db.session.commit()
            print(f"\n[OK] COMMIT — {total} satir islendi.")
        except Exception as e:
            db.session.rollback()
            print(f"\n[FAIL] ROLLBACK — {str(e)[:250]}")


if __name__ == "__main__":
    main()
