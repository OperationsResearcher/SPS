# -*- coding: utf-8 -*-
"""
Skor Motoru şeması: weight (AnaStrateji, AltStrateji, Surec, SurecPerformansGostergesi),
calculated_score (SurecPerformansGostergesi), surec_pg_id (SurecFaaliyet).
Mevcut verileri bozmaz; ağırlık atanmamış kayıtlar eşit dağılım (100/kardeş) ile hesaplanır.

Kullanım: python scripts/migrate_score_engine_schema.py
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from __init__ import create_app
from extensions import db


def _column_exists(conn, table: str, column: str) -> bool:
    try:
        r = conn.execute(db.text(f"PRAGMA table_info({table})"))
        return column in [row[1] for row in r.fetchall()]
    except Exception:
        return False


def migrate():
    app = create_app()
    with app.app_context():
        conn = db.engine.connect()
        try:
            # ana_strateji.weight
            if not _column_exists(conn, 'ana_strateji', 'weight'):
                db.session.execute(db.text("ALTER TABLE ana_strateji ADD COLUMN weight REAL"))
                print("ana_strateji.weight eklendi.")
            # alt_strateji.weight
            if not _column_exists(conn, 'alt_strateji', 'weight'):
                db.session.execute(db.text("ALTER TABLE alt_strateji ADD COLUMN weight REAL"))
                print("alt_strateji.weight eklendi.")
            # surec.weight zaten var; nullable yapmak için SQLite'ta yeniden ekleyemeyiz, sadece yoksa ekle
            if not _column_exists(conn, 'surec', 'weight'):
                db.session.execute(db.text("ALTER TABLE surec ADD COLUMN weight REAL"))
                print("surec.weight eklendi.")
            # surec_performans_gostergesi.weight, calculated_score
            if not _column_exists(conn, 'surec_performans_gostergesi', 'weight'):
                db.session.execute(db.text("ALTER TABLE surec_performans_gostergesi ADD COLUMN weight REAL"))
                print("surec_performans_gostergesi.weight eklendi.")
            if not _column_exists(conn, 'surec_performans_gostergesi', 'calculated_score'):
                db.session.execute(db.text("ALTER TABLE surec_performans_gostergesi ADD COLUMN calculated_score REAL"))
                print("surec_performans_gostergesi.calculated_score eklendi.")
            # surec_faaliyet.surec_pg_id
            if not _column_exists(conn, 'surec_faaliyet', 'surec_pg_id'):
                db.session.execute(db.text("ALTER TABLE surec_faaliyet ADD COLUMN surec_pg_id INTEGER"))
                db.session.execute(db.text(
                    "CREATE INDEX IF NOT EXISTS ix_surec_faaliyet_surec_pg_id ON surec_faaliyet(surec_pg_id)"
                ))
                print("surec_faaliyet.surec_pg_id eklendi.")
            db.session.commit()
            print("Skor Motoru şema migration tamamlandı.")
        except Exception as e:
            db.session.rollback()
            print(f"Hata: {e}")
            raise
        finally:
            conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(migrate())
