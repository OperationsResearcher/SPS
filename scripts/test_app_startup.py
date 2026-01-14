# -*- coding: utf-8 -*-
"""
Flask Uygulama Başlatma ve SQL Server Bağlantı Testi
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

from __init__ import create_app
from extensions import db

def test_app_startup():
    """Flask uygulamasını başlat ve veritabanı bağlantısını test et"""
    try:
        print("=" * 60)
        print("Flask Uygulama Başlatma ve SQL Server Bağlantı Testi")
        print("=" * 60)
        print()
        
        # Uygulamayı oluştur
        app = create_app()
        
        with app.app_context():
            # Veritabanı bağlantısını test et
            print("Veritabanı bağlantısı test ediliyor...")
            db.engine.connect()
            print(f"✅ Veritabanı bağlantısı başarılı!")
            print(f"   URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'N/A')[:50]}...")
            
            # Tablo sayısını kontrol et
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"✅ Tablo sayısı: {len(tables)}")
            
            # Bazı temel tabloları kontrol et
            required_tables = ['user', 'kurum', 'surec', 'bireysel_performans_gostergesi']
            missing_tables = [t for t in required_tables if t not in tables]
            if missing_tables:
                print(f"⚠️  Eksik tablolar: {missing_tables}")
            else:
                print("✅ Tüm gerekli tablolar mevcut")
            
            # Veri sayısını kontrol et
            from models import User, Kurum, Surec
            user_count = User.query.count()
            kurum_count = Kurum.query.count()
            surec_count = Surec.query.count()
            
            print(f"\n📊 Veri Durumu:")
            print(f"   - Kurum: {kurum_count}")
            print(f"   - Kullanıcı: {user_count}")
            print(f"   - Süreç: {surec_count}")
            
            print("\n" + "=" * 60)
            print("✅ Flask uygulaması başarıyla başlatıldı!")
            print("=" * 60)
            return True
            
    except Exception as e:
        print(f"\n❌ Hata: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_app_startup()
    sys.exit(0 if success else 1)

