# -*- coding: utf-8 -*-
"""
Activity ve ActivityStatus tablolarını SQL Server'da doğrudan oluşturur
Uygulama çalışırken kullandığı veritabanına bağlanır
"""
import pyodbc
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

# Uygulama config'ini kullan
from config import get_config

config = get_config()
db_uri = config.SQLALCHEMY_DATABASE_URI

print("=" * 60)
print("Activity ve ActivityStatus tabloları oluşturuluyor...")
print(f"Veritabanı URI: {db_uri[:80]}...")
print("=" * 60)

# SQL Server bağlantısı için engine oluştur
if 'mssql' in db_uri.lower() or 'sqlserver' in db_uri.lower():
    print("\nSQL Server tespit edildi!")
    
    # Engine oluştur
    engine = create_engine(db_uri, echo=True)
    
    with engine.connect() as conn:
        # ActivityStatus tablosu
        print("\n1. activity_status tablosu oluşturuluyor...")
        try:
            conn.execute(text("""
                IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[activity_status]') AND type in (N'U'))
                BEGIN
                    CREATE TABLE [dbo].[activity_status] (
                        [id] INT IDENTITY(1,1) PRIMARY KEY,
                        [ad] NVARCHAR(50) NOT NULL UNIQUE,
                        [renk] NVARCHAR(20) DEFAULT 'secondary',
                        [sira] INT DEFAULT 0,
                        [is_closed] BIT DEFAULT 0,
                        [created_at] DATETIME DEFAULT GETDATE()
                    );
                    PRINT 'activity_status tablosu oluşturuldu.';
                END
                ELSE
                BEGIN
                    PRINT 'activity_status tablosu zaten mevcut.';
                END
            """))
            conn.commit()
            print("✓ activity_status tablosu kontrol edildi/oluşturuldu")
        except Exception as e:
            conn.rollback()
            print(f"⚠ activity_status hatası: {e}")
        
        # Activity tablosu (önce tablo, sonra FK'ler)
        print("\n2. activity tablosu oluşturuluyor...")
        try:
            # Tabloyu oluştur (FK'ler olmadan)
            conn.execute(text("""
                IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[activity]') AND type in (N'U'))
                BEGIN
                    CREATE TABLE [dbo].[activity] (
                        [id] INT IDENTITY(1,1) PRIMARY KEY,
                        [title] NVARCHAR(200) NOT NULL,
                        [description] NTEXT NULL,
                        [assigned_to_id] INT NULL,
                        [surec_pg_id] INT NULL,
                        [status_id] INT NOT NULL DEFAULT 1,
                        [created_by_id] INT NOT NULL,
                        [due_date] DATE NULL,
                        [estimated_hours] FLOAT NULL,
                        [actual_hours] FLOAT NULL,
                        [priority] INT DEFAULT 3,
                        [progress] INT DEFAULT 0,
                        [is_measurable] BIT DEFAULT 0,
                        [output_value] NVARCHAR(100) NULL,
                        [created_at] DATETIME DEFAULT GETDATE(),
                        [updated_at] DATETIME DEFAULT GETDATE(),
                        [completed_at] DATETIME NULL
                    );
                    PRINT 'activity tablosu oluşturuldu.';
                END
                ELSE
                BEGIN
                    PRINT 'activity tablosu zaten mevcut.';
                END
            """))
            conn.commit()
            
            # Foreign key'leri ekle
            print("\n3. Foreign key'ler ekleniyor...")
            fk_constraints = [
                ('FK_activity_assigned_to', 'assigned_to_id', 'user', 'id'),
                ('FK_activity_created_by', 'created_by_id', 'user', 'id'),
                ('FK_activity_surec_pg', 'surec_pg_id', 'surec_performans_gostergesi', 'id'),
                ('FK_activity_status', 'status_id', 'activity_status', 'id')
            ]
            
            for fk_name, col_name, ref_table, ref_col in fk_constraints:
                try:
                    conn.execute(text(f"""
                        IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = '{fk_name}')
                        BEGIN
                            ALTER TABLE [activity] ADD CONSTRAINT [{fk_name}] 
                            FOREIGN KEY ([{col_name}]) REFERENCES [{ref_table}]([{ref_col}]);
                            PRINT '{fk_name} eklendi.';
                        END
                    """))
                    conn.commit()
                    print(f"  ✓ {fk_name} kontrol edildi/eklendi")
                except Exception as fk_e:
                    conn.rollback()
                    if 'duplicate' not in str(fk_e).lower() and 'already exists' not in str(fk_e).lower():
                        print(f"  ⚠ {fk_name} hatası: {fk_e}")
            
            # Index'leri ekle
            print("\n4. Index'ler ekleniyor...")
            indexes = [
                ('IX_activity_assigned_to_id', 'assigned_to_id'),
                ('IX_activity_surec_pg_id', 'surec_pg_id'),
                ('IX_activity_status_id', 'status_id'),
                ('IX_activity_created_by_id', 'created_by_id')
            ]
            
            for idx_name, col_name in indexes:
                try:
                    conn.execute(text(f"""
                        IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = '{idx_name}')
                        BEGIN
                            CREATE INDEX [{idx_name}] ON [activity]([{col_name}]);
                            PRINT '{idx_name} eklendi.';
                        END
                    """))
                    conn.commit()
                    print(f"  ✓ {idx_name} kontrol edildi/eklendi")
                except Exception as idx_e:
                    conn.rollback()
                    if 'duplicate' not in str(idx_e).lower():
                        print(f"  ⚠ {idx_name} hatası: {idx_e}")
            
            print("✓ activity tablosu kontrol edildi/oluşturuldu")
        except Exception as e:
            conn.rollback()
            print(f"❌ activity tablosu hatası: {e}")
            import traceback
            traceback.print_exc()
        
        # Varsayılan durumları ekle
        print("\n5. Varsayılan durumlar ekleniyor...")
        statuses = [
            ('Yeni', 'secondary', 1, 0),
            ('Devam Ediyor', 'primary', 2, 0),
            ('Beklemede', 'warning', 3, 0),
            ('Tamamlandı', 'success', 4, 1),
            ('İptal', 'danger', 5, 1),
        ]
        
        for ad, renk, sira, is_closed in statuses:
            try:
                conn.execute(text("""
                    IF NOT EXISTS (SELECT * FROM [activity_status] WHERE [ad] = :ad)
                    BEGIN
                        INSERT INTO [activity_status] ([ad], [renk], [sira], [is_closed]) 
                        VALUES (:ad, :renk, :sira, :is_closed);
                    END
                """), {'ad': ad, 'renk': renk, 'sira': sira, 'is_closed': bool(is_closed)})
                conn.commit()
                print(f"  ✓ {ad} durumu kontrol edildi/eklendi")
            except Exception as e:
                conn.rollback()
                if 'duplicate' not in str(e).lower():
                    print(f"  ⚠ {ad} durumu hatası: {e}")
        
        print("\n" + "=" * 60)
        print("✅ Tüm işlemler tamamlandı!")
        print("=" * 60)
        
else:
    print("\n⚠ SQL Server tespit edilmedi, SQLite kullanılıyor.")
    print("Uygulama SQL Server kullanıyorsa, environment variable'ları kontrol edin:")
    print("  - SQL_SERVER")
    print("  - SQL_DATABASE")
    print("  - SQL_USERNAME")
    print("  - SQL_PASSWORD")
    print("\nVeya create_activity_tables_sqlserver.sql dosyasını SQL Server Management Studio'da çalıştırın.")

