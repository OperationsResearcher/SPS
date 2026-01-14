#!/usr/bin/env python
"""SQLite'a RAID sütunlarını ekle - Flask bağımlılığı olmadan.

Bu script, config.Config.SQLALCHEMY_DATABASE_URI içindeki sqlite dosyasını hedefler.
"""

import sqlite3

from config import Config


def _sqlite_path_from_uri(uri: str) -> str:
    if not uri.startswith('sqlite:///'):
        raise ValueError(f"Bu script sadece sqlite URI destekler: {uri!r}")
    return uri.replace('sqlite:///', '', 1)


DB_PATH = _sqlite_path_from_uri(Config.SQLALCHEMY_DATABASE_URI)


COLUMNS_TO_ADD: list[tuple[str, str]] = [
    ('probability', 'INTEGER'),
    ('impact', 'INTEGER'),
    ('mitigation_plan', 'TEXT'),
    ('assumption_validation_date', 'TEXT'),
    ('assumption_validated', 'INTEGER'),
    ('assumption_notes', 'TEXT'),
    ('issue_urgency', 'TEXT'),
    ('issue_affected_work', 'TEXT'),
    ('dependency_type', 'TEXT'),
    ('dependency_task_id', 'INTEGER'),
]


def main() -> int:
    conn = sqlite3.connect(DB_PATH, timeout=30)
    try:
        cursor = conn.cursor()
        cursor.execute('PRAGMA busy_timeout = 30000')

        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='raid_item'"
        )
        if cursor.fetchone() is None:
            print(
                "raid_item tablosu bulunamadı. Uygulama ilk kez çalıştırılıp tablolar oluşturulmalı."
            )
            return 2

        cursor.execute('PRAGMA table_info(raid_item)')
        existing_columns = {row[1] for row in cursor.fetchall()}

        changed = False
        for col_name, col_type in COLUMNS_TO_ADD:
            if col_name in existing_columns:
                continue
            cursor.execute(f"ALTER TABLE raid_item ADD COLUMN {col_name} {col_type}")
            print(f"Sütun eklendi: {col_name}")
            changed = True

        if changed:
            conn.commit()
            print('Migration tamamlandı.')
        else:
            print('Eksik sütun yok; migration gerekmiyor.')
        return 0
    finally:
        conn.close()


if __name__ == '__main__':
    raise SystemExit(main())
