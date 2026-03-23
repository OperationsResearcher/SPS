# -*- coding: utf-8 -*-
"""
Belirtilen tenant'ı (kurumu) SQLite veritabanından kalıcı olarak siler.

ÖNEMLİ:
  - Çalıştırmadan önce instance/kokpitim.db yedeğini alın.
  - Varsayılan güvenlik: yalnızca short_name='1KMF' silinebilir; başka kurum için --force.

Kullanım:
  python scripts/delete_tenant_permanent.py --dry-run
  python scripts/delete_tenant_permanent.py --execute --confirm KALICI-SIL --backup
"""
from __future__ import annotations

import argparse
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "instance" / "kokpitim.db"
ALLOWED_SHORT_DEFAULT = "1KMF"


def connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_tenant(conn: sqlite3.Connection, short_name: str) -> tuple[int, str] | None:
    row = conn.execute(
        "SELECT id, name FROM tenants WHERE short_name = ? COLLATE NOCASE",
        (short_name,),
    ).fetchone()
    if not row:
        return None
    return int(row[0]), str(row[1])


def user_ids(conn: sqlite3.Connection, tenant_id: int) -> list[int]:
    rows = conn.execute(
        "SELECT id FROM users WHERE tenant_id = ?", (tenant_id,)
    ).fetchall()
    return [int(r[0]) for r in rows]


def ph(n: int) -> str:
    return ",".join("?" * n) if n else ""


def count_report(
    conn: sqlite3.Connection, tenant_id: int, uids: list[int]
) -> dict[str, int]:
    """Dry-run için satır sayıları."""
    r: dict[str, int] = {}
    uid_t = tuple(uids)
    p = ph(len(uids))

    r["processes"] = conn.execute(
        "SELECT COUNT(*) FROM processes WHERE tenant_id = ?", (tenant_id,)
    ).fetchone()[0]
    r["sub_strategies"] = conn.execute(
        "SELECT COUNT(*) FROM sub_strategies WHERE strategy_id IN "
        "(SELECT id FROM strategies WHERE tenant_id = ?)",
        (tenant_id,),
    ).fetchone()[0]
    r["strategies"] = conn.execute(
        "SELECT COUNT(*) FROM strategies WHERE tenant_id = ?", (tenant_id,)
    ).fetchone()[0]
    r["swot_analyses"] = conn.execute(
        "SELECT COUNT(*) FROM swot_analyses WHERE tenant_id = ?", (tenant_id,)
    ).fetchone()[0]
    r["tenant_email_configs"] = conn.execute(
        "SELECT COUNT(*) FROM tenant_email_configs WHERE tenant_id = ?", (tenant_id,)
    ).fetchone()[0]

    if uids:
        r["tickets"] = conn.execute(
            f"SELECT COUNT(*) FROM tickets WHERE tenant_id = ? OR user_id IN ({p})",
            (tenant_id,) + uid_t,
        ).fetchone()[0]
        r["notifications"] = conn.execute(
            f"SELECT COUNT(*) FROM notifications WHERE tenant_id = ? OR user_id IN ({p}) "
            f"OR related_user_id IN ({p})",
            (tenant_id,) + uid_t + uid_t,
        ).fetchone()[0]
        r["notifications_ext"] = conn.execute(
            f"SELECT COUNT(*) FROM notifications_ext WHERE user_id IN ({p})", uid_t
        ).fetchone()[0]
        r["notification_preferences"] = conn.execute(
            f"SELECT COUNT(*) FROM notification_preferences WHERE user_id IN ({p})",
            uid_t,
        ).fetchone()[0]
        r["push_subscriptions"] = conn.execute(
            f"SELECT COUNT(*) FROM push_subscriptions WHERE user_id IN ({p})", uid_t
        ).fetchone()[0]
        r["individual_kpi_data"] = conn.execute(
            f"SELECT COUNT(*) FROM individual_kpi_data WHERE user_id IN ({p})", uid_t
        ).fetchone()[0]
        r["individual_activities"] = conn.execute(
            f"SELECT COUNT(*) FROM individual_activities WHERE user_id IN ({p})", uid_t
        ).fetchone()[0]
        r["individual_performance_indicators"] = conn.execute(
            f"SELECT COUNT(*) FROM individual_performance_indicators WHERE user_id IN ({p})",
            uid_t,
        ).fetchone()[0]
        r["activity_tracks_user"] = conn.execute(
            f"SELECT COUNT(*) FROM activity_tracks WHERE user_id IN ({p})", uid_t
        ).fetchone()[0]
        r["audit_logs"] = conn.execute(
            f"SELECT COUNT(*) FROM audit_logs WHERE tenant_id = ? OR user_id IN ({p})",
            (tenant_id,) + uid_t,
        ).fetchone()[0]
        r["kpi_data_orphan_user"] = conn.execute(
            f"SELECT COUNT(*) FROM kpi_data WHERE user_id IN ({p})", uid_t
        ).fetchone()[0]
        r["kpi_data_audits_orphan_user"] = conn.execute(
            f"SELECT COUNT(*) FROM kpi_data_audits WHERE user_id IN ({p})", uid_t
        ).fetchone()[0]
        r["favorite_kpis"] = conn.execute(
            f"SELECT COUNT(*) FROM favorite_kpis WHERE user_id IN ({p})", uid_t
        ).fetchone()[0]
        r["users"] = len(uids)
    else:
        r["tickets"] = conn.execute(
            "SELECT COUNT(*) FROM tickets WHERE tenant_id = ?", (tenant_id,)
        ).fetchone()[0]
        r["notifications"] = conn.execute(
            "SELECT COUNT(*) FROM notifications WHERE tenant_id = ?", (tenant_id,)
        ).fetchone()[0]
        r["audit_logs"] = conn.execute(
            "SELECT COUNT(*) FROM audit_logs WHERE tenant_id = ?", (tenant_id,)
        ).fetchone()[0]
        r["users"] = 0

    r["tenants_row"] = 1
    return r


def execute_delete(conn: sqlite3.Connection, tenant_id: int, uids: list[int]) -> None:
    uid_t = tuple(uids)
    p = ph(len(uids))

    conn.execute(
        "UPDATE processes SET deleted_by = NULL, parent_id = NULL WHERE tenant_id = ?",
        (tenant_id,),
    )
    conn.execute("DELETE FROM processes WHERE tenant_id = ?", (tenant_id,))

    conn.execute(
        "DELETE FROM sub_strategies WHERE strategy_id IN "
        "(SELECT id FROM strategies WHERE tenant_id = ?)",
        (tenant_id,),
    )
    conn.execute("DELETE FROM strategies WHERE tenant_id = ?", (tenant_id,))

    conn.execute("DELETE FROM swot_analyses WHERE tenant_id = ?", (tenant_id,))
    conn.execute("DELETE FROM tenant_email_configs WHERE tenant_id = ?", (tenant_id,))

    if uids:
        conn.execute(
            f"DELETE FROM tickets WHERE tenant_id = ? OR user_id IN ({p})",
            (tenant_id,) + uid_t,
        )
        conn.execute(
            f"DELETE FROM notifications WHERE tenant_id = ? OR user_id IN ({p}) "
            f"OR related_user_id IN ({p})",
            (tenant_id,) + uid_t + uid_t,
        )
        conn.execute(f"DELETE FROM notifications_ext WHERE user_id IN ({p})", uid_t)
        conn.execute(
            f"DELETE FROM notification_preferences WHERE user_id IN ({p})", uid_t
        )
        conn.execute(f"DELETE FROM push_subscriptions WHERE user_id IN ({p})", uid_t)
        conn.execute(
            f"DELETE FROM individual_kpi_data WHERE user_id IN ({p})", uid_t
        )
        conn.execute(
            f"DELETE FROM individual_activities WHERE user_id IN ({p})", uid_t
        )
        conn.execute(
            f"DELETE FROM individual_performance_indicators WHERE user_id IN ({p})",
            uid_t,
        )
        conn.execute(f"DELETE FROM activity_tracks WHERE user_id IN ({p})", uid_t)
        conn.execute(
            f"DELETE FROM audit_logs WHERE tenant_id = ? OR user_id IN ({p})",
            (tenant_id,) + uid_t,
        )
        conn.execute(f"DELETE FROM kpi_data WHERE user_id IN ({p})", uid_t)
        conn.execute(f"DELETE FROM kpi_data_audits WHERE user_id IN ({p})", uid_t)
        conn.execute(f"DELETE FROM favorite_kpis WHERE user_id IN ({p})", uid_t)
        conn.execute("DELETE FROM users WHERE tenant_id = ?", (tenant_id,))
    else:
        conn.execute("DELETE FROM tickets WHERE tenant_id = ?", (tenant_id,))
        conn.execute("DELETE FROM notifications WHERE tenant_id = ?", (tenant_id,))
        conn.execute("DELETE FROM audit_logs WHERE tenant_id = ?", (tenant_id,))

    conn.execute("DELETE FROM tenants WHERE id = ?", (tenant_id,))


def main() -> int:
    p = argparse.ArgumentParser(description="Tenant kalıcı silme (SQLite)")
    p.add_argument("--db", type=Path, default=DEFAULT_DB, help="SQLite dosyası")
    p.add_argument(
        "--short-name",
        default=ALLOWED_SHORT_DEFAULT,
        help="tenants.short_name (varsayılan 1KMF)",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help=f"short_name '{ALLOWED_SHORT_DEFAULT}' dışındaki kurumu silmeye izin ver",
    )
    p.add_argument("--dry-run", action="store_true", help="Sadece sayımları göster")
    p.add_argument("--execute", action="store_true", help="Gerçekten sil")
    p.add_argument(
        "--confirm",
        default="",
        help="--execute ile birlikte tam olarak: KALICI-SIL",
    )
    p.add_argument(
        "--backup",
        action="store_true",
        help="--execute ile: silmeden önce DB kopyası (instance/)",
    )
    args = p.parse_args()

    if not args.short_name.strip():
        print("short_name boş olamaz.", file=sys.stderr)
        return 2

    if args.short_name.upper() != ALLOWED_SHORT_DEFAULT and not args.force:
        print(
            f"Güvenlik: Yalnızca '{ALLOWED_SHORT_DEFAULT}' silinebilir. "
            f"Başka kurum için --force ekleyin.",
            file=sys.stderr,
        )
        return 2

    if args.execute and args.confirm != "KALICI-SIL":
        print("--execute için --confirm KALICI-SIL gerekli.", file=sys.stderr)
        return 2

    if not args.dry_run and not args.execute:
        print("--dry-run veya --execute belirtin.", file=sys.stderr)
        return 2

    if args.dry_run and args.execute:
        print("Yalnızca biri: --dry-run veya --execute.", file=sys.stderr)
        return 2

    if not args.db.is_file():
        print(f"DB bulunamadı: {args.db}", file=sys.stderr)
        return 2

    if args.backup and args.execute:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        bak = args.db.parent / f"kokpitim_before_tenant_delete_{ts}.db"
        shutil.copy2(args.db, bak)
        print(f"Yedek yazıldı: {bak}")

    conn = connect(args.db)
    try:
        t = get_tenant(conn, args.short_name.strip())
        if not t:
            print(f"Tenant bulunamadı: short_name={args.short_name!r}", file=sys.stderr)
            return 1
        tid, tname = t
        uids = user_ids(conn, tid)
        print(f"Hedef tenant: id={tid} name={tname!r} short_name={args.short_name!r}")
        print(f"Kullanıcı sayısı: {len(uids)} ids={uids}")

        if args.dry_run:
            print("\n[DRY-RUN] Etkilenecek satırlar (sayım):")
            for k, v in sorted(count_report(conn, tid, uids).items()):
                print(f"  {k}: {v}")
            print("\nGerçek silme için: --execute --confirm KALICI-SIL [--backup]")
        else:
            print("\n[EXECUTE] Siliniyor...")
            conn.execute("BEGIN IMMEDIATE")
            try:
                execute_delete(conn, tid, uids)
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            print("Tamamlandı: tenant kalıcı olarak silindi.")
    finally:
        conn.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
