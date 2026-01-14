import sys
import os

# Kök dizini path'e ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db
from services.seeder import seed_all

def setup_database():
    app = create_app()
    with app.app_context():
        # 1. Mevcut tabloları sil (Temiz başlangıç için - DİKKAT: Veriler silinir)
        print("Mevcut veri tabanı temizleniyor...")
        db.drop_all()
        
        # 2. Yeni tabloları oluştur
        print("Tablolar oluşturuluyor...")
        db.create_all()
        
        # 3. Demo verileri yükle
        print("Demo veriler yükleniyor...")
        results = seed_all(db)
        
        if results.get('hata'):
            print(f"HATA: {results['hata']}")
        else:
            print("\n✅ Kurulum Başarılı!")
            print(f"Kurumlar: {results['kurumlar']}")
            print(f"Kullanıcılar: {results['users']}")
            print(f"Projeler: {results['projeler']}")

if __name__ == "__main__":
    setup_database()
