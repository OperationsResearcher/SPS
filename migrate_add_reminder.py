"""
Görev Hatırlatma Özelliği - Manuel Migration

Bu script, Task tablosuna reminder_date kolonunu ekler.
SQLAlchemy Migration kullanılmadığı için manuel çalıştırılmalıdır.
"""
from app import app
from extensions import db
from sqlalchemy import text

def add_reminder_date_column():
    """Task tablosuna reminder_date kolonunu ekle"""
    with app.app_context():
        try:
            # Veritabanı türünü kontrol et
            db_url = db.engine.url.drivername
            
            with db.engine.connect() as conn:
                if 'sqlite' in db_url:
                    # SQLite için
                    try:
                        conn.execute(text("ALTER TABLE task ADD COLUMN reminder_date DATETIME NULL"))
                        conn.commit()
                        print("✅ reminder_date kolonu başarıyla eklendi (SQLite).")
                    except Exception as e:
                        if 'duplicate column' in str(e).lower():
                            print("ℹ️  reminder_date kolonu zaten mevcut.")
                        else:
                            raise
                else:
                    # SQL Server için
                    conn.execute(text("""
                        IF NOT EXISTS (
                            SELECT * FROM sys.columns 
                            WHERE object_id = OBJECT_ID(N'[dbo].[task]') 
                            AND name = 'reminder_date'
                        )
                        BEGIN
                            ALTER TABLE [dbo].[task] ADD reminder_date DATETIME NULL
                        END
                    """))
                    conn.commit()
                    print("✅ reminder_date kolonu başarıyla eklendi (SQL Server).")
        except Exception as e:
            print(f"❌ Hata oluştu: {e}")
            print("\nAlternatif SQL (manuel çalıştırın):")
            print("-- SQLite için:")
            print("ALTER TABLE task ADD COLUMN reminder_date DATETIME NULL;")
            print("\n-- SQL Server için:")
            print("ALTER TABLE [dbo].[task] ADD reminder_date DATETIME NULL;")

if __name__ == '__main__':
    print("Görev Hatırlatma Özelliği - Migration")
    print("=" * 50)
    add_reminder_date_column()
