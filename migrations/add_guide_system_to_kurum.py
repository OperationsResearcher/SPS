"""
Migration: Kurum modeline show_guide_system kolonu ekle

Bu script, kurum tablosuna rehber sistemi kontrolü için
show_guide_system boolean kolonu ekler.
"""

import sys
import os

# Script'in bulunduğu dizinin üst dizinini Python path'ine ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from extensions import db
from models.user import Kurum
from sqlalchemy import text

def upgrade():
    """Kurum tablosuna show_guide_system kolonu ekle"""
    with app.app_context():
        try:
            # Kolon zaten var mı kontrol et
            result = db.session.execute(text(
                "SELECT COUNT(*) FROM pragma_table_info('kurum') WHERE name='show_guide_system'"
            ))
            count = result.scalar()
            
            if count == 0:
                print("Kurum tablosuna 'show_guide_system' kolonu ekleniyor...")
                db.session.execute(text(
                    "ALTER TABLE kurum ADD COLUMN show_guide_system BOOLEAN NOT NULL DEFAULT 1"
                ))
                db.session.commit()
                print("✓ 'show_guide_system' kolonu başarıyla eklendi (default: True)")
            else:
                print("⚠ 'show_guide_system' kolonu zaten mevcut")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration hatası: {e}")
            raise

def downgrade():
    """show_guide_system kolonunu kaldır"""
    with app.app_context():
        try:
            print("'show_guide_system' kolonu kaldırılıyor...")
            # SQLite'da kolon silme işlemi karmaşık olduğu için uyarı veriyoruz
            print("⚠ SQLite'da kolon silme desteklenmediğinden, bu işlem atlanıyor.")
            print("⚠ Gerekirse veritabanını yeniden oluşturun.")
        except Exception as e:
            print(f"❌ Downgrade hatası: {e}")
            raise

if __name__ == '__main__':
    print("=" * 60)
    print("Kurum Rehber Sistemi Migration")
    print("=" * 60)
    upgrade()
    print("=" * 60)
    print("Migration tamamlandı!")
    print("=" * 60)
