# -*- coding: utf-8 -*-
"""
SQLite Veritabanı Oluşturma Scripti (migration_init.py)

Bu script, `spsv2.db` adında boş bir SQLite veritabanı oluşturur ve
tüm tabloları oluşturur (schema'yı kurar).

KULLANIM:
1. Bu scripti çalıştırın: python migration_init.py
2. `spsv2.db` dosyası oluşturulacaktır (mevcut ise silinip yeniden oluşturulur).
3. Bir sonraki adım: python migration_import.py çalıştırın
"""

import sys
import os

# Flask uygulama context'i için
sys.path.insert(0, os.path.dirname(__file__))

from __init__ import create_app
from models import db
from config import Config

# SQLite veritabanı dosya yolu
basedir = os.path.abspath(os.path.dirname(__file__))
SQLITE_DB_PATH = os.path.join(basedir, 'spsv2.db')


def main():
    """SQLite veritabanını oluştur"""
    print("=" * 60)
    print("SQLite Veritabanı Oluşturma İşlemi Başlatılıyor...")
    print("=" * 60)
    
    # Mevcut SQLite DB'yi sil (varsa)
    if os.path.exists(SQLITE_DB_PATH):
        try:
            os.remove(SQLITE_DB_PATH)
            print(f"[WARNING] Mevcut {SQLITE_DB_PATH} dosyasi silindi")
        except Exception as e:
            print(f"[ERROR] Mevcut DB dosyasi silinirken hata: {str(e)}")
            sys.exit(1)
    
    # Flask uygulama oluştur
    app = create_app()
    
    # Config'i SQLite kullanacak şekilde geçici olarak değiştir
    original_uri = app.config['SQLALCHEMY_DATABASE_URI']
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{SQLITE_DB_PATH}'
    
    try:
        with app.app_context():
            # Engine'i yeniden başlat
            if hasattr(db, 'engine') and db.engine:
                db.engine.dispose()
            
            # Tüm tabloları oluştur
            print("\n[INFO] Tablolar olusturuluyor...")
            db.create_all()
            
            # Tablo sayısını kontrol et
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            table_names = inspector.get_table_names()
            
            print("\n[OK] Veritabani basariyla olusturuldu!")
            print(f"[FILE] Dosya: {SQLITE_DB_PATH}")
            print(f"[STAT] Olusturulan tablo sayisi: {len(table_names)}")
            print("\nTablolar:")
            for table in sorted(table_names):
                print(f"  - {table}")
            
            print("\n" + "=" * 60)
            print("Bir sonraki adım: python migration_import.py çalıştırın")
            print("=" * 60)
            
    except Exception as e:
        print(f"\n[ERROR] Veritabani olusturulurken hata: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Original URI'yi geri yükle
        app.config['SQLALCHEMY_DATABASE_URI'] = original_uri


if __name__ == '__main__':
    main()

