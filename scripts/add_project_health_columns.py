# -*- coding: utf-8 -*-
"""
Project tablosuna health_score ve health_status kolonlarını ekleme scripti
"""

import sys
import os

# Windows konsol encoding sorununu çöz
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from __init__ import create_app
from extensions import db
from sqlalchemy import inspect, text

def add_project_health_columns():
    """Project tablosuna health_score ve health_status kolonlarını ekle"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔍 Project tablosu kontrol ediliyor...")
            
            # Veritabanı tipini kontrol et
            db_url = str(db.engine.url)
            is_sqlite = 'sqlite' in db_url.lower()
            is_sqlserver = 'mssql' in db_url.lower() or 'sqlserver' in db_url.lower()
            
            print(f"📊 Veritabanı tipi: {'SQLite' if is_sqlite else 'SQL Server' if is_sqlserver else 'Bilinmeyen'}")
            
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('project')]
            
            print(f"\n📋 Mevcut kolonlar: {', '.join(columns)}")
            
            # health_score kolonunu ekle
            if 'health_score' not in columns:
                print("\n➕ health_score kolonu ekleniyor...")
                if is_sqlite:
                    try:
                        db.session.execute(text("ALTER TABLE project ADD COLUMN health_score INTEGER DEFAULT 100"))
                        db.session.commit()
                        print("✅ health_score kolonu eklendi")
                    except Exception as e:
                        print(f"⚠️  health_score kolonu eklenirken hata: {e}")
                        db.session.rollback()
                elif is_sqlserver:
                    try:
                        db.session.execute(text("ALTER TABLE project ADD health_score INT DEFAULT 100"))
                        db.session.commit()
                        print("✅ health_score kolonu eklendi")
                    except Exception as e:
                        print(f"⚠️  health_score kolonu eklenirken hata: {e}")
                        db.session.rollback()
                else:
                    # SQLAlchemy create_all kullan
                    print("⚠️  Veritabanı tipi belirlenemedi, SQLAlchemy create_all kullanılıyor...")
                    db.create_all()
            else:
                print("✅ health_score kolonu zaten mevcut")
            
            # health_status kolonunu ekle
            if 'health_status' not in columns:
                print("\n➕ health_status kolonu ekleniyor...")
                if is_sqlite:
                    try:
                        db.session.execute(text("ALTER TABLE project ADD COLUMN health_status VARCHAR(50) DEFAULT 'İyi'"))
                        db.session.commit()
                        print("✅ health_status kolonu eklendi")
                    except Exception as e:
                        print(f"⚠️  health_status kolonu eklenirken hata: {e}")
                        db.session.rollback()
                elif is_sqlserver:
                    try:
                        db.session.execute(text("ALTER TABLE project ADD health_status NVARCHAR(50) DEFAULT 'İyi'"))
                        db.session.commit()
                        print("✅ health_status kolonu eklendi")
                    except Exception as e:
                        print(f"⚠️  health_status kolonu eklenirken hata: {e}")
                        db.session.rollback()
                else:
                    # SQLAlchemy create_all kullan
                    print("⚠️  Veritabanı tipi belirlenemedi, SQLAlchemy create_all kullanılıyor...")
                    db.create_all()
            else:
                print("✅ health_status kolonu zaten mevcut")
            
            # Son kontrol
            inspector = inspect(db.engine)
            columns_after = [col['name'] for col in inspector.get_columns('project')]
            
            print(f"\n📋 Güncel kolonlar: {', '.join(columns_after)}")
            
            if 'health_score' in columns_after and 'health_status' in columns_after:
                print("\n✅ Tüm kolonlar başarıyla eklendi!")
                return True
            else:
                print("\n⚠️  Bazı kolonlar eksik olabilir")
                return False
                
        except Exception as e:
            print(f"\n❌ Hata: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

if __name__ == '__main__':
    print("=" * 60)
    print("PROJECT TABLOSU HEALTH KOLONLARI EKLEME")
    print("=" * 60)
    
    success = add_project_health_columns()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ İŞLEM BAŞARIYLA TAMAMLANDI!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ İŞLEM BAŞARISIZ!")
        print("=" * 60)
        sys.exit(1)

