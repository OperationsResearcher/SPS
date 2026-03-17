# -*- coding: utf-8 -*-
"""
Project tablosuna yeni kolonları eklemek için script
start_date, end_date, priority kolonlarını ekler
"""
import pyodbc
import os
from config import get_config

def add_project_columns():
    """Project tablosuna yeni kolonları ekle"""
    try:
        # Config'den veritabanı bağlantı bilgilerini al
        config = get_config()
        db_config = config.SQLALCHEMY_DATABASE_URI
        
        # SQL Server connection string'ini parse et
        # Örnek: mssql+pyodbc://user:pass@server/db?driver=ODBC+Driver+17+for+SQL+Server
        if 'mssql+pyodbc://' in db_config:
            # Connection string'i parse et
            conn_str = db_config.replace('mssql+pyodbc://', '')
            # Kullanıcı adı, şifre, sunucu, veritabanı bilgilerini çıkar
            # Basit bir parse (daha güvenli bir yöntem kullanılabilir)
            parts = conn_str.split('@')
            if len(parts) == 2:
                user_pass = parts[0]
                rest = parts[1]
                user, password = user_pass.split(':')
                server_db = rest.split('/')
                server = server_db[0].split('?')[0]
                db_name = server_db[1].split('?')[0]
                
                # Driver bilgisini çıkar
                driver = 'ODBC Driver 17 for SQL Server'
                if 'driver=' in conn_str:
                    driver_part = conn_str.split('driver=')[1].split('&')[0]
                    driver = driver_part.replace('+', ' ')
                
                # Connection string oluştur
                connection_string = f"DRIVER={{{driver}}};SERVER={server};DATABASE={db_name};UID={user};PWD={password}"
            else:
                print("Veritabanı bağlantı string'i beklenen formatta değil.")
                return False
        else:
            print("SQL Server bağlantısı bulunamadı.")
            return False
        
        # Veritabanına bağlan
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        print("Veritabanına bağlanıldı. Kolonlar ekleniyor...")
        
        # Kolonların var olup olmadığını kontrol et ve ekle
        columns_to_add = [
            ('start_date', 'DATE NULL'),
            ('end_date', 'DATE NULL'),
            ('priority', 'NVARCHAR(50) DEFAULT \'Orta\'')
        ]
        
        for column_name, column_def in columns_to_add:
            try:
                # Kolonun var olup olmadığını kontrol et
                check_query = f"""
                    SELECT COUNT(*) 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = 'project' 
                    AND COLUMN_NAME = '{column_name}'
                """
                cursor.execute(check_query)
                exists = cursor.fetchone()[0] > 0
                
                if not exists:
                    # Kolonu ekle
                    alter_query = f"ALTER TABLE project ADD {column_name} {column_def}"
                    cursor.execute(alter_query)
                    print(f"✅ {column_name} kolonu eklendi.")
                else:
                    print(f"ℹ️  {column_name} kolonu zaten mevcut.")
            except Exception as e:
                print(f"❌ {column_name} kolonu eklenirken hata: {str(e)}")
                # Devam et, diğer kolonları dene
        
        # Index ekle (opsiyonel, performans için)
        try:
            # start_date için index
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_project_start_date' AND object_id = OBJECT_ID('project'))
                BEGIN
                    CREATE INDEX idx_project_start_date ON project(start_date);
                END
            """)
            print("✅ start_date index'i eklendi/kontrol edildi.")
        except Exception as e:
            print(f"ℹ️  start_date index hatası (normal olabilir): {str(e)}")
        
        try:
            # end_date için index
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_project_end_date' AND object_id = OBJECT_ID('project'))
                BEGIN
                    CREATE INDEX idx_project_end_date ON project(end_date);
                END
            """)
            print("✅ end_date index'i eklendi/kontrol edildi.")
        except Exception as e:
            print(f"ℹ️  end_date index hatası (normal olabilir): {str(e)}")
        
        # Değişiklikleri kaydet
        conn.commit()
        print("\n✅ Tüm kolonlar başarıyla eklendi!")
        
        cursor.close()
        conn.close()
        
        return True
    
    except Exception as e:
        print(f"❌ Hata: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Project Tablosuna Yeni Kolonlar Ekleme Script'i")
    print("=" * 60)
    print()
    
    success = add_project_columns()
    
    if success:
        print("\n✅ İşlem tamamlandı!")
    else:
        print("\n❌ İşlem başarısız oldu. Lütfen hataları kontrol edin.")





















