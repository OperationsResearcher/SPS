import sqlite3
import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

# --- AYARLAR ---
# 1. Eski Veritabanı (Kaynak)
OLD_DB_NAME = 'spsv2_yedek.db'

# 2. Yeni Veritabanı (Hedef - Supabase)
NEW_DB_URL = os.environ.get('DATABASE_URL')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
if not NEW_DB_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set!")

def run_migration():
    if not os.path.exists(OLD_DB_NAME):
        print(f"❌ HATA: '{OLD_DB_NAME}' dosyası bulunamadı! Dosya adını kontrol et.")
        return

    print(f"🚀 Veri transferi başlıyor...")
    print(f"📂 Kaynak: {OLD_DB_NAME}")
    print(f"☁️  Hedef: Supabase")

    src_conn = sqlite3.connect(OLD_DB_NAME)
    dest_engine = create_engine(NEW_DB_URL)
    
    # Tablo Listesi (Sıralama kritik)
    tables = [
        'kurum', 'user', 'project', 'task', 
        'main_strategy', 'sub_strategy', 'process', 
        'notification', 'project_file', 'task_comment',
        'task_impact', 'time_entry'
    ]

    # --- AŞAMA 1: VERİ AKTARIMI ---
    try:
        with dest_engine.connect() as dest_conn:
            # Transaction başlat
            trans = dest_conn.begin()
            try:
                print("🔓 Kısıtlamalar kaldırılıyor...")
                dest_conn.execute(text("SET session_replication_role = 'replica';"))
                
                # SQLite'dan tüm tablo isimlerini çek (Listede olmayanları da alalım)
                cursor = src_conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                all_tables = [row[0] for row in cursor.fetchall() if row[0] != 'sqlite_sequence']
                
                # Öncelikli tabloları başa al, kalanları ekle
                final_table_list = tables + [t for t in all_tables if t not in tables]

                for table in final_table_list:
                    try:
                        # SQLite'dan oku
                        df = pd.read_sql_query(f"SELECT * FROM {table}", src_conn)
                        if df.empty:
                            continue

                        print(f"📦 {table}: {len(df)} kayıt aktarılıyor...", end=" ")
                        
                        # Pandas ile Supabase'e bas
                        df.to_sql(table, dest_engine, if_exists='append', index=False, chunksize=100, method='multi')
                        print("✅ OK")
                    except Exception as e:
                        if "no such table" in str(e):
                            pass
                        elif "already exists" in str(e):
                             print(f"⚠️ {table} zaten dolu.")
                        else:
                            print(f"\n❌ {table} hatası: {str(e)}")

                print("🔒 Kısıtlamalar geri açılıyor...")
                dest_conn.execute(text("SET session_replication_role = 'origin';"))
                trans.commit()
                print("✅ Veri aktarımı ve Commit başarılı.")
            except Exception as e:
                trans.rollback()
                print(f"\n📛 AKTARIM HATASI (Rollback yapıldı): {str(e)}")
                return # Aktarım başarısızsa sequence işine hiç girme

    except Exception as e:
        print(f"Bağlantı Hatası: {e}")

    # --- AŞAMA 2: ID SAYAÇLARINI DÜZELTME (AYRI BAĞLANTI) ---
    print("\n🔧 ID Sayaçları (Sequences) düzeltiliyor...")
    
    # Her tablo için ayrı işlem yapacağız ki biri patlarsa diğerleri etkilenmesin
    with dest_engine.connect() as dest_conn:
        # Tabloları tekrar al
        insp = dest_engine.dialect.get_table_names(dest_conn)
        
        for table in insp:
            try:
                # Her deneme kendi transaction'ı içinde olsun
                with dest_conn.begin(): 
                    sql = f"""
                    SELECT setval(pg_get_serial_sequence('{table}', 'id'), coalesce(max(id), 1)) 
                    FROM "{table}";
                    """
                    dest_conn.execute(text(sql))
                    print(f"  🔹 {table} sayacı güncellendi.")
            except Exception as e:
                # Sequence olmayan tablolarda devam et, durumu görünür kıl.
                print(f"  🔸 {table} sequence güncellenemedi: {e}")

    src_conn.close()
    print("\n🏁 TÜM İŞLEMLER TAMAMLANDI.")

if __name__ == "__main__":
    try:
        import pandas
    except ImportError:
        os.system("pip install pandas")
        import pandas
    run_migration()