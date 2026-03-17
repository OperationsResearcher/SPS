# -*- coding: utf-8 -*-
"""
Project tablosuna yeni kolonları eklemek için basit script
SQLAlchemy kullanarak ALTER TABLE komutlarını çalıştırır
"""
from __init__ import create_app
from extensions import db
from sqlalchemy import text

def add_project_columns():
    """Project tablosuna yeni kolonları ekle"""
    app = create_app()
    
    with app.app_context():
        try:
            print("=" * 60)
            print("Project Tablosuna Yeni Kolonlar Ekleme")
            print("=" * 60)
            print()
            
            # start_date kolonu ekle
            try:
                db.session.execute(text("""
                    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                                    WHERE TABLE_NAME = 'project' AND COLUMN_NAME = 'start_date')
                    BEGIN
                        ALTER TABLE project ADD start_date DATE NULL;
                    END
                """))
                db.session.commit()
                print("✅ start_date kolonu eklendi/kontrol edildi.")
            except Exception as e:
                print(f"ℹ️  start_date kolonu (normal olabilir): {str(e)}")
                db.session.rollback()
            
            # end_date kolonu ekle
            try:
                db.session.execute(text("""
                    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                                    WHERE TABLE_NAME = 'project' AND COLUMN_NAME = 'end_date')
                    BEGIN
                        ALTER TABLE project ADD end_date DATE NULL;
                    END
                """))
                db.session.commit()
                print("✅ end_date kolonu eklendi/kontrol edildi.")
            except Exception as e:
                print(f"ℹ️  end_date kolonu (normal olabilir): {str(e)}")
                db.session.rollback()
            
            # priority kolonu ekle
            try:
                db.session.execute(text("""
                    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                                    WHERE TABLE_NAME = 'project' AND COLUMN_NAME = 'priority')
                    BEGIN
                        ALTER TABLE project ADD priority NVARCHAR(50) DEFAULT 'Orta';
                    END
                """))
                db.session.commit()
                print("✅ priority kolonu eklendi/kontrol edildi.")
            except Exception as e:
                print(f"ℹ️  priority kolonu (normal olabilir): {str(e)}")
                db.session.rollback()
            
            # Index'ler ekle
            try:
                db.session.execute(text("""
                    IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_project_start_date' AND object_id = OBJECT_ID('project'))
                    BEGIN
                        CREATE INDEX idx_project_start_date ON project(start_date);
                    END
                """))
                db.session.commit()
                print("✅ start_date index'i eklendi/kontrol edildi.")
            except Exception as e:
                print(f"ℹ️  start_date index (normal olabilir): {str(e)}")
                db.session.rollback()
            
            try:
                db.session.execute(text("""
                    IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_project_end_date' AND object_id = OBJECT_ID('project'))
                    BEGIN
                        CREATE INDEX idx_project_end_date ON project(end_date);
                    END
                """))
                db.session.commit()
                print("✅ end_date index'i eklendi/kontrol edildi.")
            except Exception as e:
                print(f"ℹ️  end_date index (normal olabilir): {str(e)}")
                db.session.rollback()
            
            print()
            print("✅ İşlem tamamlandı!")
            print()
            print("Not: Eğer hata alırsanız, SQL script'ini (add_project_columns_sql.sql) manuel olarak çalıştırabilirsiniz.")
            
        except Exception as e:
            print(f"❌ Hata: {str(e)}")
            import traceback
            traceback.print_exc()
            db.session.rollback()

if __name__ == '__main__':
    add_project_columns()





















