# -*- coding: utf-8 -*-
"""
SQL Server Bağlantı Test Scripti

Bu script, SQL Server bağlantısını test eder ve gerekli environment variable'ları kontrol eder.

KULLANIM:
python test_sqlserver_connection.py
"""

import sys
import os

# Flask uygulama context'i için
sys.path.insert(0, os.path.dirname(__file__))

from config import build_sqlserver_uri, Config
from __init__ import create_app
from extensions import db


def check_environment_variables():
    """Environment variable'ları kontrol et"""
    print("=" * 60)
    print("Environment Variable Kontrolü")
    print("=" * 60)
    
    required_vars = {
        'SQL_SERVER': os.environ.get('SQL_SERVER'),
        'SQL_DATABASE': os.environ.get('SQL_DATABASE'),
        'SQL_USERNAME': os.environ.get('SQL_USERNAME'),
        'SQL_PASSWORD': os.environ.get('SQL_PASSWORD'),
        'SQL_DRIVER': os.environ.get('SQL_DRIVER'),
        'DATABASE_URL': os.environ.get('DATABASE_URL'),
    }
    
    print("\nMevcut Environment Variable'lar:")
    for var_name, var_value in required_vars.items():
        if var_value:
            # Password'ü gizle
            if 'PASSWORD' in var_name:
                display_value = '*' * len(var_value) if var_value else 'YOK'
            else:
                display_value = var_value
            print(f"  [OK] {var_name}: {display_value}")
        else:
            print(f"  [X] {var_name}: YOK")
    
    # Kontrol
    has_sql_server = bool(required_vars['SQL_SERVER'])
    has_database_url = bool(required_vars['DATABASE_URL'])
    
    if not has_sql_server and not has_database_url:
        print("\n[HATA] SQL Server baglanti bilgileri bulunamadi!")
        print("\nÇözüm:")
        print("1. Environment variable'ları set edin:")
        print("   set SQL_SERVER=localhost")
        print("   set SQL_DATABASE=stratejik_planlama")
        print("   set SQL_USERNAME=sa")
        print("   set SQL_PASSWORD=your_password")
        print("   set SQL_DRIVER=ODBC Driver 17 for SQL Server")
        print("\n2. Veya DATABASE_URL kullanın:")
        print("   set DATABASE_URL=mssql+pyodbc://user:pass@server/db?driver=ODBC+Driver+17+for+SQL+Server")
        return False
    
    return True


def check_pyodbc():
    """pyodbc kütüphanesinin yüklü olup olmadığını kontrol et"""
    print("\n" + "=" * 60)
    print("PyODBC Kontrolü")
    print("=" * 60)
    
    try:
        import pyodbc
        print(f"[OK] pyodbc yuklu: {pyodbc.version}")
        
        # Mevcut ODBC driver'ları listele
        print("\nMevcut ODBC Driver'lar:")
        drivers = pyodbc.drivers()
        if drivers:
            for driver in drivers:
                print(f"  - {driver}")
        else:
            print("  (Hiç driver bulunamadı)")
        
        # SQL Server driver kontrolü
        sql_server_drivers = [d for d in drivers if 'SQL Server' in d]
        if sql_server_drivers:
            print(f"\n[OK] SQL Server driver bulundu: {', '.join(sql_server_drivers)}")
        else:
            print("\n[UYARI] SQL Server ODBC driver bulunamadi!")
            print("   ODBC Driver 17 for SQL Server yükleyin:")
            print("   https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server")
        
        return True
    except ImportError:
        print("[HATA] pyodbc yuklu degil!")
        print("\nÇözüm:")
        print("  pip install pyodbc>=5.0.0")
        return False


def test_connection():
    """SQL Server bağlantısını test et"""
    print("\n" + "=" * 60)
    print("SQL Server Bağlantı Testi")
    print("=" * 60)
    
    # Flask uygulama oluştur
    app = create_app()
    
    # SQL Server URI'yi oluştur
    if os.environ.get('DATABASE_URL'):
        db_uri = os.environ.get('DATABASE_URL')
        print(f"\n[INFO] DATABASE_URL kullanılıyor")
    elif os.environ.get('SQL_SERVER'):
        db_uri = build_sqlserver_uri()
        print(f"\n[INFO] Environment variable'lardan URI oluşturuldu")
    else:
        print("\n[HATA] SQL Server baglanti bilgileri bulunamadi!")
        return False
    
    # URI'yi göster (password'ü gizle)
    display_uri = db_uri
    if '://' in db_uri and '@' in db_uri:
        parts = db_uri.split('@')
        if len(parts) == 2:
            auth_part = parts[0]
            if ':' in auth_part:
                user_pass = auth_part.split('://')[1]
                if ':' in user_pass:
                    user = user_pass.split(':')[0]
                    display_uri = db_uri.replace(user_pass, f"{user}:***")
    
    print(f"[INFO] Connection URI: {display_uri}")
    
    # Geçici olarak SQL Server URI'yi set et
    original_uri = app.config['SQLALCHEMY_DATABASE_URI']
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    
    try:
        with app.app_context():
            print("\n[INFO] Bağlantı deneniyor...")
            
            # Basit bir sorgu çalıştır
            result = db.session.execute(db.text("SELECT @@VERSION AS version"))
            version = result.fetchone()[0]
            
            print("[OK] Baglanti basarili!")
            print(f"\nSQL Server Versiyonu:")
            print(f"  {version[:100]}...")  # İlk 100 karakter
            
            # Veritabanı adını al
            result = db.session.execute(db.text("SELECT DB_NAME() AS db_name"))
            db_name = result.fetchone()[0]
            print(f"\nBağlı Veritabanı: {db_name}")
            
            # Tablo sayısını kontrol et
            result = db.session.execute(db.text("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
            """))
            table_count = result.fetchone()[0]
            print(f"Tablo Sayısı: {table_count}")
            
            return True
            
    except Exception as e:
        print(f"\n[HATA] Baglanti hatasi: {str(e)}")
        print("\nOlası nedenler:")
        print("  1. SQL Server çalışmıyor olabilir")
        print("  2. Sunucu adı/port yanlış olabilir")
        print("  3. Kullanıcı adı/şifre yanlış olabilir")
        print("  4. Veritabanı adı yanlış olabilir")
        print("  5. Firewall bağlantıyı engelliyor olabilir")
        print("  6. ODBC driver yüklü değil veya yanlış driver adı")
        
        import traceback
        print("\nDetaylı hata:")
        traceback.print_exc()
        return False
    finally:
        # Original URI'yi geri yükle
        app.config['SQLALCHEMY_DATABASE_URI'] = original_uri


def main():
    """Ana test fonksiyonu"""
    print("\n" + "=" * 60)
    print("SQL Server Bağlantı Test Scripti")
    print("=" * 60)
    
    # 1. Environment variable kontrolü
    if not check_environment_variables():
        sys.exit(1)
    
    # 2. PyODBC kontrolü
    if not check_pyodbc():
        sys.exit(1)
    
    # 3. Bağlantı testi
    if not test_connection():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("[OK] Tum testler basarili! Migration islemine devam edebilirsiniz.")
    print("=" * 60)
    print("\nSonraki adım: python migration_export.py")


if __name__ == '__main__':
    main()

