# -*- coding: utf-8 -*-
"""
Activity ve ActivityStatus tablolarını veritabanında oluşturur
SQL Server ve SQLite için çalışır
"""
from __init__ import create_app
from models import db, Activity, ActivityStatus
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        print("=" * 60)
        print("Activity ve ActivityStatus tabloları oluşturuluyor...")
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        print(f"Veritabanı URI: {db_uri[:80]}...")
        print("=" * 60)
        
        # SQL Server için özel tablo oluşturma
        if 'mssql' in db_uri.lower() or 'sqlserver' in db_uri.lower():
            print("\nSQL Server tespit edildi, tablolar manuel oluşturuluyor...")
            
            # ActivityStatus tablosu
            try:
                print("activity_status tablosu oluşturuluyor...")
                db.session.execute(text("""
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
                db.session.commit()
                print("✓ activity_status tablosu kontrol edildi/oluşturuldu")
            except Exception as e:
                db.session.rollback()
                error_msg = str(e).lower()
                if 'already exists' in error_msg or 'already an object' in error_msg or 'duplicate' in error_msg:
                    print(f"  ⚠ activity_status tablosu zaten mevcut")
                else:
                    print(f"  ❌ activity_status tablosu oluşturulurken hata: {e}")
                    raise
            
            # Activity tablosu
            try:
                print("activity tablosu oluşturuluyor...")
                # Önce foreign key'leri kontrol etmeden tabloyu oluştur
                db.session.execute(text("""
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
                db.session.commit()
                
                # Foreign key'leri ayrı olarak ekle
                try:
                    db.session.execute(text("""
                        IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_activity_assigned_to')
                        BEGIN
                            ALTER TABLE [activity] ADD CONSTRAINT [FK_activity_assigned_to] 
                            FOREIGN KEY ([assigned_to_id]) REFERENCES [user]([id]);
                        END
                    """))
                    db.session.commit()
                except Exception as fk_e:
                    db.session.rollback()
                    if 'duplicate' not in str(fk_e).lower():
                        print(f"  ⚠ FK_activity_assigned_to eklenirken hata (zaten var olabilir): {fk_e}")
                
                try:
                    db.session.execute(text("""
                        IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_activity_created_by')
                        BEGIN
                            ALTER TABLE [activity] ADD CONSTRAINT [FK_activity_created_by] 
                            FOREIGN KEY ([created_by_id]) REFERENCES [user]([id]);
                        END
                    """))
                    db.session.commit()
                except Exception as fk_e:
                    db.session.rollback()
                    if 'duplicate' not in str(fk_e).lower():
                        print(f"  ⚠ FK_activity_created_by eklenirken hata (zaten var olabilir): {fk_e}")
                
                try:
                    db.session.execute(text("""
                        IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_activity_surec_pg')
                        BEGIN
                            ALTER TABLE [activity] ADD CONSTRAINT [FK_activity_surec_pg] 
                            FOREIGN KEY ([surec_pg_id]) REFERENCES [surec_performans_gostergesi]([id]);
                        END
                    """))
                    db.session.commit()
                except Exception as fk_e:
                    db.session.rollback()
                    if 'duplicate' not in str(fk_e).lower():
                        print(f"  ⚠ FK_activity_surec_pg eklenirken hata (zaten var olabilir): {fk_e}")
                
                try:
                    db.session.execute(text("""
                        IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_activity_status')
                        BEGIN
                            ALTER TABLE [activity] ADD CONSTRAINT [FK_activity_status] 
                            FOREIGN KEY ([status_id]) REFERENCES [activity_status]([id]);
                        END
                    """))
                    db.session.commit()
                except Exception as fk_e:
                    db.session.rollback()
                    if 'duplicate' not in str(fk_e).lower():
                        print(f"  ⚠ FK_activity_status eklenirken hata (zaten var olabilir): {fk_e}")
                
                # Index'leri ekle
                for idx_name, idx_col in [
                    ('IX_activity_assigned_to_id', 'assigned_to_id'),
                    ('IX_activity_surec_pg_id', 'surec_pg_id'),
                    ('IX_activity_status_id', 'status_id'),
                    ('IX_activity_created_by_id', 'created_by_id')
                ]:
                    try:
                        db.session.execute(text(f"""
                            IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = '{idx_name}')
                            BEGIN
                                CREATE INDEX [{idx_name}] ON [activity]([{idx_col}]);
                            END
                        """))
                        db.session.commit()
                    except Exception as idx_e:
                        db.session.rollback()
                        if 'duplicate' not in str(idx_e).lower():
                            print(f"  ⚠ {idx_name} index eklenirken hata: {idx_e}")
                
                print("✓ activity tablosu kontrol edildi/oluşturuldu")
            except Exception as e:
                db.session.rollback()
                error_msg = str(e).lower()
                if 'already exists' in error_msg or 'already an object' in error_msg or 'duplicate' in error_msg:
                    print(f"  ⚠ activity tablosu zaten mevcut")
                else:
                    print(f"  ❌ activity tablosu oluşturulurken hata: {e}")
                    raise
        else:
            # SQLite veya diğer veritabanları için standart yöntem
            print("\nStandart db.create_all() kullanılıyor...")
            db.create_all()
            print("✓ db.create_all() tamamlandı")
        
        # ActivityStatus için varsayılan durumları ekle
        statuses = [
            {'ad': 'Yeni', 'renk': 'secondary', 'sira': 1, 'is_closed': False},
            {'ad': 'Devam Ediyor', 'renk': 'primary', 'sira': 2, 'is_closed': False},
            {'ad': 'Beklemede', 'renk': 'warning', 'sira': 3, 'is_closed': False},
            {'ad': 'Tamamlandı', 'renk': 'success', 'sira': 4, 'is_closed': True},
            {'ad': 'İptal', 'renk': 'danger', 'sira': 5, 'is_closed': True},
        ]
        
        print("\nVarsayılan durumlar kontrol ediliyor...")
        for status_data in statuses:
            try:
                existing = ActivityStatus.query.filter_by(ad=status_data['ad']).first()
                if not existing:
                    status = ActivityStatus(**status_data)
                    db.session.add(status)
                    db.session.commit()
                    print(f"  ✓ {status_data['ad']} durumu eklendi")
                else:
                    print(f"  - {status_data['ad']} durumu zaten mevcut")
            except Exception as e:
                db.session.rollback()
                print(f"  ⚠ {status_data['ad']} durumu eklenirken hata: {e}")
        
        print("\n" + "=" * 60)
        print("✅ İşlem tamamlandı!")
        print("=" * 60)
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Hata: {str(e)}")
        import traceback
        traceback.print_exc()

