# -*- coding: utf-8 -*-
"""
Veritabanı Bakım ve Senkronizasyon Scripti
------------------------------------------
Mevcut tabloları kontrol eder ve eksik olanları oluşturur.
"""
import os
import sys

# Proje kök dizinini Python path'ine ekle
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# Flask uygulamasını import et
from dotenv import load_dotenv
load_dotenv()  # .env dosyasını yükle

from __init__ import create_app
from extensions import db
from sqlalchemy import inspect

def check_database_sync():
    """
    Veritabanı senkronizasyonunu kontrol eder ve eksik tabloları oluşturur.
    """
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("🔍 VERİTABANI SENKRONİZASYON KONTROLÜ")
        print("=" * 60)
        print()
        
        try:
            # SQLAlchemy Inspector ile mevcut tabloları kontrol et
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            print(f"📊 Mevcut Tablolar ({len(existing_tables)} adet):")
            print("-" * 60)
            
            # Tabloları alfabetik sırala ve listele
            sorted_tables = sorted(existing_tables)
            for i, table_name in enumerate(sorted_tables, 1):
                # Tablo sütun sayısını al
                columns = inspector.get_columns(table_name)
                column_count = len(columns)
                print(f"  {i:2d}. {table_name:<30} ({column_count} sütun)")
            
            print("-" * 60)
            print()
            
            # Feedback tablosu kontrolü
            if 'feedback' in existing_tables:
                print("✅ Sistem güncel. Feedback tablosu zaten mevcut.")
                print()
                
                # Feedback tablosunun sütunlarını göster
                feedback_columns = inspector.get_columns('feedback')
                print("📋 Feedback Tablosu Sütunları:")
                for col in feedback_columns:
                    nullable = "NULL" if col['nullable'] else "NOT NULL"
                    default = f" DEFAULT {col['default']}" if col.get('default') is not None else ""
                    print(f"   - {col['name']:<20} {str(col['type']):<30} {nullable}{default}")
                print()
            else:
                print("⚠️  Feedback tablosu eksik, oluşturuluyor...")
                print()
                
                # Eksik tabloları oluştur (sadece eksikler, mevcutlara dokunmaz)
                db.create_all()
                
                # Tekrar kontrol et
                inspector = inspect(db.engine)
                updated_tables = inspector.get_table_names()
                
                if 'feedback' in updated_tables:
                    print("✅ Feedback tablosu başarıyla eklendi.")
                    print()
                    
                    # Yeni oluşturulan tablonun sütunlarını göster
                    feedback_columns = inspector.get_columns('feedback')
                    print("📋 Oluşturulan Feedback Tablosu Sütunları:")
                    for col in feedback_columns:
                        nullable = "NULL" if col['nullable'] else "NOT NULL"
                        default = f" DEFAULT {col['default']}" if col.get('default') is not None else ""
                        print(f"   - {col['name']:<20} {str(col['type']):<30} {nullable}{default}")
                    print()
                else:
                    print("❌ HATA: Feedback tablosu oluşturulamadı!")
                    print("   Lütfen logları kontrol edin ve manuel müdahale yapın.")
                    sys.exit(1)
            
            print("=" * 60)
            print("✅ Veritabanı senkronizasyon kontrolü tamamlandı!")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ Hata oluştu: {e}")
            print("-" * 60)
            print("⚠️  Lütfen hata mesajını kontrol edin ve gerekirse manuel müdahale yapın.")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    check_database_sync()
