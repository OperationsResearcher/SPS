# -*- coding: utf-8 -*-
"""
Süreç (surec) tablosuna parent_id sütunu ekler.
Mevcut süreçlerin parent_id değeri NULL (bağımsız) kalır.

Kullanım: python scripts/migrate_surec_parent_id.py
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from __init__ import create_app
from extensions import db


def migrate():
    app = create_app()
    with app.app_context():
        # Sütun zaten var mı kontrol et (SQLite PRAGMA table_info)
        conn = db.engine.connect()
        try:
            result = conn.execute(db.text("PRAGMA table_info(surec)"))
            columns = [row[1] for row in result.fetchall()]
            if 'parent_id' in columns:
                print("parent_id sütunu zaten mevcut. İşlem atlandı.")
                return 0
        finally:
            conn.close()

        # SQLite: ALTER TABLE ADD COLUMN (FK eklenemez, uygulama katmanında SET NULL yapıyoruz)
        db.session.execute(db.text("ALTER TABLE surec ADD COLUMN parent_id INTEGER"))
        db.session.execute(db.text("CREATE INDEX IF NOT EXISTS ix_surec_parent_id ON surec(parent_id)"))
        db.session.commit()
        print("surec.parent_id sütunu ve indeks eklendi. Mevcut kayıtlar bağımsız (NULL) kaldı.")
    return 0


if __name__ == "__main__":
    sys.exit(migrate())
