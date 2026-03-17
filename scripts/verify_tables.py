# -*- coding: utf-8 -*-
"""
Activity tablolarının oluşturulduğunu doğrular
"""
import pyodbc
import os

SERVER = '(localdb)\\MSSQLLocalDB'
DATABASE = 'stratejik_planlama'
DRIVER = 'ODBC Driver 17 for SQL Server'

try:
    conn_str = (
        f"DRIVER={{{DRIVER}}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        f"Trusted_Connection=yes;"
        f"TrustServerCertificate=yes;"
    )
    
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("Tablolar kontrol ediliyor...")
    print("=" * 60)
    
    # activity_status tablosu kontrolü
    cursor.execute("""
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_NAME = 'activity_status'
    """)
    if cursor.fetchone()[0] > 0:
        cursor.execute("SELECT COUNT(*) FROM activity_status")
        count = cursor.fetchone()[0]
        print(f"✓ activity_status tablosu mevcut ({count} kayıt)")
        
        # Durumları listele
        cursor.execute("SELECT id, ad, is_closed FROM activity_status ORDER BY sira")
        print("\n  Durumlar:")
        for row in cursor.fetchall():
            status = "✓ Kapalı" if row[2] else "  Açık"
            print(f"    {row[0]}. {row[1]} {status}")
    else:
        print("❌ activity_status tablosu bulunamadı!")
    
    # activity tablosu kontrolü
    cursor.execute("""
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_NAME = 'activity'
    """)
    if cursor.fetchone()[0] > 0:
        cursor.execute("SELECT COUNT(*) FROM activity")
        count = cursor.fetchone()[0]
        print(f"\n✓ activity tablosu mevcut ({count} kayıt)")
        
        # Kolonları listele
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'activity'
            ORDER BY ORDINAL_POSITION
        """)
        print("\n  Kolonlar:")
        for row in cursor.fetchall():
            nullable = "NULL" if row[2] == "YES" else "NOT NULL"
            print(f"    - {row[0]} ({row[1]}) {nullable}")
        
        # Foreign key'leri kontrol et
        cursor.execute("""
            SELECT name FROM sys.foreign_keys 
            WHERE parent_object_id = OBJECT_ID('activity')
        """)
        fks = [row[0] for row in cursor.fetchall()]
        print(f"\n  Foreign Key'ler ({len(fks)}):")
        for fk in fks:
            print(f"    - {fk}")
        
        # Index'leri kontrol et
        cursor.execute("""
            SELECT name FROM sys.indexes 
            WHERE object_id = OBJECT_ID('activity') AND name IS NOT NULL
        """)
        indexes = [row[0] for row in cursor.fetchall()]
        print(f"\n  Index'ler ({len(indexes)}):")
        for idx in indexes:
            print(f"    - {idx}")
    else:
        print("\n❌ activity tablosu bulunamadı!")
    
    print("\n" + "=" * 60)
    print("✅ Kontrol tamamlandı!")
    print("=" * 60)
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ Hata: {e}")
    import traceback
    traceback.print_exc()

