# -*- coding: utf-8 -*-
"""
Guide System için User tablosuna alanlar ekleyen migration
"""
import sqlite3
import sys
from pathlib import Path

# Proje kök dizinini bul
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def migrate_add_guide_fields():
    """User tablosuna guide_character_style, show_page_guides, completed_walkthroughs ekle"""
    
    # config.py'deki veritabanı yolunu kullan
    db_path = project_root / 'spsv2.db'
    
    if not db_path.exists():
        print(f"❌ Veritabanı bulunamadı: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Mevcut sütunları kontrol et
        cursor.execute("PRAGMA table_info(user)")
        columns = {row[1] for row in cursor.fetchall()}
        
        added_columns = []
        
        # guide_character_style ekle
        if 'guide_character_style' not in columns:
            cursor.execute("""
                ALTER TABLE user 
                ADD COLUMN guide_character_style VARCHAR(50) DEFAULT 'professional'
            """)
            added_columns.append('guide_character_style')
            print("✓ guide_character_style sütunu eklendi")
        
        # show_page_guides ekle
        if 'show_page_guides' not in columns:
            cursor.execute("""
                ALTER TABLE user 
                ADD COLUMN show_page_guides BOOLEAN DEFAULT 1
            """)
            added_columns.append('show_page_guides')
            print("✓ show_page_guides sütunu eklendi")
        
        # completed_walkthroughs ekle
        if 'completed_walkthroughs' not in columns:
            cursor.execute("""
                ALTER TABLE user 
                ADD COLUMN completed_walkthroughs TEXT
            """)
            added_columns.append('completed_walkthroughs')
            print("✓ completed_walkthroughs sütunu eklendi")
        
        if added_columns:
            conn.commit()
            print(f"\n✅ Migration başarılı! {len(added_columns)} sütun eklendi.")
        else:
            print("\n⚠ Tüm sütunlar zaten mevcut, değişiklik yapılmadı.")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Migration hatası: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Guide System Migration - User Tablosu")
    print("=" * 60)
    print()
    
    success = migrate_add_guide_fields()
    
    if success:
        print("\n" + "=" * 60)
        print("Migration tamamlandı!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("Migration başarısız!")
        print("=" * 60)
        sys.exit(1)
