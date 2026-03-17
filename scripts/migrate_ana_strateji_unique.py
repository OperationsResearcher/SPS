# -*- coding: utf-8 -*-
"""Migrate AnaStrateji unique constraint.

Goal:
- Remove the old global unique constraint on ana_strateji.code (SQLite auto-index).
- Ensure uniqueness is (kurum_id, code) via uq_ana_strateji_kurum_code.

Why a script?
- This repo does not include an Alembic migrations folder.
- SQLite cannot DROP/ALTER constraints directly; we rebuild the table.

Safe-by-default notes:
- Designed for the current default SQLite DB (spsv2.db).
- It preserves existing data.

Run:
  C:/SPY_Cursor/SP_Code/.venv/Scripts/python.exe scripts/migrate_ana_strateji_unique.py
"""

from __future__ import annotations

import sqlite3
from pathlib import Path


def main() -> int:
    db_path = Path(__file__).resolve().parents[1] / "spsv2.db"
    if not db_path.exists():
        raise SystemExit(f"DB not found: {db_path}")

    con = sqlite3.connect(str(db_path))
    try:
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        # Check current schema
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ana_strateji'")
        if not cur.fetchone():
            print("[SKIP] Table ana_strateji does not exist.")
            return 0

        # Read existing columns
        cur.execute("PRAGMA table_info('ana_strateji')")
        cols = [r["name"] for r in cur.fetchall()]
        required = ["id", "kurum_id", "code", "ad", "name", "aciklama", "created_at", "updated_at"]
        missing = [c for c in required if c not in cols]
        if missing:
            raise SystemExit(f"Unexpected ana_strateji schema; missing columns: {missing}")

        print(f"[INFO] Using DB: {db_path}")
        print("[INFO] Rebuilding ana_strateji with composite unique (kurum_id, code)...")

        # SQLite table rebuild
        cur.execute("PRAGMA foreign_keys=OFF")
        con.execute("BEGIN")

        # Create new table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS ana_strateji_new (
                id INTEGER NOT NULL PRIMARY KEY,
                kurum_id INTEGER NOT NULL,
                code VARCHAR(20),
                ad VARCHAR(200) NOT NULL,
                name VARCHAR(200),
                aciklama TEXT,
                created_at DATETIME,
                updated_at DATETIME,
                CONSTRAINT uq_ana_strateji_kurum_code UNIQUE (kurum_id, code),
                FOREIGN KEY(kurum_id) REFERENCES kurum(id)
            )
            """
        )

        # Copy data
        cur.execute(
            """
            INSERT INTO ana_strateji_new (id, kurum_id, code, ad, name, aciklama, created_at, updated_at)
            SELECT id, kurum_id, code, ad, name, aciklama, created_at, updated_at
            FROM ana_strateji
            """
        )

        # Drop old and rename new
        cur.execute("DROP TABLE ana_strateji")
        cur.execute("ALTER TABLE ana_strateji_new RENAME TO ana_strateji")

        # Recreate indexes expected by SQLAlchemy (best-effort)
        cur.execute("CREATE INDEX IF NOT EXISTS ix_ana_strateji_kurum_id ON ana_strateji(kurum_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS ix_ana_strateji_code ON ana_strateji(code)")

        con.commit()
        print("[OK] Migration completed.")
        return 0
    except Exception:
        con.rollback()
        raise
    finally:
        try:
            con.execute("PRAGMA foreign_keys=ON")
        except Exception:
            pass
        con.close()


if __name__ == "__main__":
    raise SystemExit(main())
