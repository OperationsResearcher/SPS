# -*- coding: utf-8 -*-
"""
SQL Server'a doğrudan bağlanıp SQL script'ini çalıştırır
"""
import pyodbc
import os

# SQL Server bağlantı bilgileri (LocalDB için)
SERVER = os.environ.get('SQL_SERVER', '(localdb)\\MSSQLLocalDB')
DATABASE = os.environ.get('SQL_DATABASE', 'stratejik_planlama')
USERNAME = os.environ.get('SQL_USERNAME', '')
PASSWORD = os.environ.get('SQL_PASSWORD', '')
DRIVER = os.environ.get('SQL_DRIVER', 'ODBC Driver 17 for SQL Server')

print("=" * 60)
print("SQL Server'a bağlanılıyor...")
print(f"Server: {SERVER}")
print(f"Database: {DATABASE}")
print(f"Username: {USERNAME}")
print("=" * 60)

try:
    # Bağlantı string'i oluştur (LocalDB için Windows Authentication)
    # LocalDB her zaman Windows Authentication kullanır
    conn_str = (
        f"DRIVER={{{DRIVER}}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        f"Trusted_Connection=yes;"
        f"TrustServerCertificate=yes;"
    )
    
    # Bağlan
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    print("\n✓ SQL Server'a bağlanıldı!")
    
    # SQL script'ini oku
    with open('create_activity_tables_sqlserver.sql', 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    # GO komutlarına göre böl
    batches = [batch.strip() for batch in sql_script.split('GO') if batch.strip()]
    
    print(f"\n{len(batches)} batch çalıştırılıyor...\n")
    
    for i, batch in enumerate(batches, 1):
        # USE komutunu atla (zaten bağlıyız)
        if batch.strip().upper().startswith('USE'):
            print(f"Batch {i}: USE komutu atlandı")
            continue
        
        try:
            cursor.execute(batch)
            conn.commit()
            print(f"✓ Batch {i} tamamlandı")
        except Exception as e:
            # Bazı hatalar normal olabilir (zaten var gibi)
            error_msg = str(e).lower()
            if 'already exists' in error_msg or 'duplicate' in error_msg or 'already an object' in error_msg:
                print(f"  ⚠ Batch {i}: Zaten mevcut (normal)")
            else:
                print(f"  ❌ Batch {i} hatası: {e}")
                # Kritik olmayan hatalarda devam et
                if 'foreign key' not in error_msg.lower():
                    conn.rollback()
    
    print("\n" + "=" * 60)
    print("✅ Tüm işlemler tamamlandı!")
    print("=" * 60)
    
    cursor.close()
    conn.close()
    
except pyodbc.Error as e:
    print(f"\n❌ SQL Server bağlantı hatası: {e}")
    print("\nLütfen environment variable'ları kontrol edin:")
    print("  - SQL_SERVER")
    print("  - SQL_DATABASE")
    print("  - SQL_USERNAME")
    print("  - SQL_PASSWORD")
    print("\nVeya SQL script'ini SQL Server Management Studio'da manuel çalıştırın:")
    print("  create_activity_tables_sqlserver.sql")
except FileNotFoundError:
    print("\n❌ create_activity_tables_sqlserver.sql dosyası bulunamadı!")
except Exception as e:
    print(f"\n❌ Beklenmeyen hata: {e}")
    import traceback
    traceback.print_exc()

