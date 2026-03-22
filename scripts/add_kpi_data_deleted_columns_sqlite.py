#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
kpi_data tablosuna deleted_at ve deleted_by_id ekler (SQLite).

Modelde bu alanlar varken migration çalıştırılmadıysa
`no such column: kpi_data.deleted_at` → karnesi API 500 → JSON yerine HTML döner.

Kullanım (proje kökünden):
  py scripts/add_kpi_data_deleted_columns_sqlite.py

PostgreSQL kullanıyorsanız: flask db upgrade (e7a8b9c0d1e2 migration zincirinize göre).
"""

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import Config


def _sqlite_path_from_uri(uri: str) -> str:
    if not uri.startswith("sqlite:///"):
        raise ValueError(f"Bu script yalnızca sqlite:/// URI destekler: {uri!r}")
    return uri.replace("sqlite:///", "", 1)


def main() -> int:
    if len(sys.argv) > 1:
        db_path = Path(sys.argv[1]).resolve()
        if not db_path.is_file():
            print(f"Dosya bulunamadı: {db_path}")
            return 1
        db_path = str(db_path)
        print(f"Veritabanı (argüman): {db_path}")
    else:
        uri = Config.SQLALCHEMY_DATABASE_URI
        try:
            db_path = _sqlite_path_from_uri(uri)
        except ValueError as e:
            print(e)
            print("PostgreSQL vb. için: flask db upgrade ile migration uygulayın.")
            return 1
        print(f"Veritabanı (config): {db_path}")

    conn = sqlite3.connect(db_path, timeout=30)
    try:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='kpi_data'")
        if not cur.fetchone():
            print("kpi_data tablosu bu dosyada yok.")
            print("İpucu: .env içindeki SQLALCHEMY_DATABASE_URI hangi .db ise:")
            print('  py scripts/add_kpi_data_deleted_columns_sqlite.py "instance\\kokpitim.db"')
            return 1
        cur.execute("PRAGMA table_info(kpi_data)")
        cols = {row[1] for row in cur.fetchall()}
        if "deleted_at" not in cols:
            cur.execute("ALTER TABLE kpi_data ADD COLUMN deleted_at DATETIME")
            print("OK: deleted_at eklendi.")
        else:
            print("deleted_at zaten var.")
        if "deleted_by_id" not in cols:
            cur.execute("ALTER TABLE kpi_data ADD COLUMN deleted_by_id INTEGER")
            print("OK: deleted_by_id eklendi.")
        else:
            print("deleted_by_id zaten var.")
        conn.commit()
    finally:
        conn.close()
    print("Bitti. Sunucuyu yenileyip karnesi sayfasını tekrar deneyin.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
