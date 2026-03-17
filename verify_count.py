from sqlalchemy import create_engine, text
import os

# Veritabanı Adresi (Havuzlayıcı - Pooler adresi)
DB_URL = "postgresql://postgres.xeurenvaugtwtqandzje:UM949tMW04t08BiT@aws-1-eu-west-1.pooler.supabase.com:6543/postgres"

def report_counts():
    print("\n📊 VERİTABANI SAYIM RAPORU")
    print("=" * 40)
    print(f"{'TABLO ADI':<25} | {'KAYIT SAYISI'}")
    print("-" * 40)

    engine = create_engine(DB_URL)

    try:
        with engine.connect() as conn:
            # Sistemdeki public tabloları bul
            tables_query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
            """
            tables = conn.execute(text(tables_query)).fetchall()

            total_records = 0
            for table in tables:
                table_name = table[0]
                # Alembic (migration) tablosunu saymaya gerek yok
                if table_name == 'alembic_version':
                    continue
                
                # Her tablo için sayım yap
                try:
                    count = conn.execute(text(f'SELECT COUNT(*) FROM "{table_name}"')).scalar()
                    print(f"{table_name:<25} | {count}")
                    total_records += count
                except Exception:
                    print(f"{table_name:<25} | ⚠️ Erişim Hatası")

            print("=" * 40)
            print(f"TOPLAM İŞLENEN TABLO: {len(tables)-1}")
            print(f"GENEL TOPLAM KAYIT: {total_records}")

    except Exception as e:
        print(f"Bağlantı Hatası: {e}")

if __name__ == "__main__":
    report_counts()