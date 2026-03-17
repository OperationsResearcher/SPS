"""
Soft Delete Migration Script
User, Kurum ve Surec tablolarına soft delete kolonları ekler
"""
from app import app
from extensions import db
from sqlalchemy import text

def add_soft_delete_columns():
    """Soft delete kolonlarını ekle"""
    with app.app_context():
        try:
            # SQLite için ayrı ayrı ALTER TABLE komutları gerekiyor
            
            # User tablosuna kolonlar ekle
            print("User tablosuna soft delete kolonları ekleniyor...")
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE [user] ADD COLUMN silindi INTEGER NOT NULL DEFAULT 0"))
                conn.execute(text("ALTER TABLE [user] ADD COLUMN deleted_at DATETIME"))
                conn.execute(text("ALTER TABLE [user] ADD COLUMN deleted_by INTEGER"))
                conn.execute(text("CREATE INDEX idx_user_silindi ON [user](silindi)"))
                conn.commit()
            print("✓ User tablosu güncellendi")
            
            # Kurum tablosuna kolonlar ekle
            print("Kurum tablosuna soft delete kolonları ekleniyor...")
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE kurum ADD COLUMN silindi INTEGER NOT NULL DEFAULT 0"))
                conn.execute(text("ALTER TABLE kurum ADD COLUMN deleted_at DATETIME"))
                conn.execute(text("ALTER TABLE kurum ADD COLUMN deleted_by INTEGER"))
                conn.execute(text("CREATE INDEX idx_kurum_silindi ON kurum(silindi)"))
                conn.commit()
            print("✓ Kurum tablosu güncellendi")
            
            # Surec tablosuna kolonlar ekle
            print("Surec tablosuna soft delete kolonları ekleniyor...")
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE surec ADD COLUMN silindi INTEGER NOT NULL DEFAULT 0"))
                conn.execute(text("ALTER TABLE surec ADD COLUMN deleted_at DATETIME"))
                conn.execute(text("ALTER TABLE surec ADD COLUMN deleted_by INTEGER"))
                conn.execute(text("CREATE INDEX idx_surec_silindi ON surec(silindi)"))
                conn.commit()
            print("✓ Surec tablosu güncellendi")
            
            print("\n✅ Migration başarıyla tamamlandı!")
            
        except Exception as e:
            print(f"\n❌ Migration hatası: {e}")
            print("\nÖneri: Kolonlar zaten varsa migration atlanabilir.")
            raise

if __name__ == '__main__':
    print("=" * 60)
    print("SOFT DELETE MIGRATION")
    print("=" * 60)
    print("\nBu script aşağıdaki tablolara soft delete kolonları ekleyecek:")
    print("  - user (silindi, deleted_at, deleted_by)")
    print("  - kurum (silindi, deleted_at, deleted_by)")
    print("  - surec (silindi, deleted_at, deleted_by)")
    print("\n⚠️  UYARI: Bu işlem veritabanı şemasını değiştirecektir!")
    
    response = input("\nDevam etmek istiyor musunuz? (EVET/hayir): ")
    
    if response.upper() == 'EVET':
        add_soft_delete_columns()
    else:
        print("\nMigration iptal edildi.")
