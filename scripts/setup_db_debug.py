import sys
import os
import traceback

# Kök dizini path'e ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db
from models import User, Kurum, Surec

def debug_seeder():
    app = create_app()
    with app.app_context():
        try:
            print("Tabloları temizle...")
            db.drop_all()
            print("Tabloları oluştur...")
            db.create_all()
            
            print("Kurum oluştur...")
            kurum = Kurum(kisa_ad="Test Kurum", ticari_unvan="Test A.Ş.")
            db.session.add(kurum)
            db.session.commit()
            print(f"Kurum oluşturuldu: {kurum.id}")
            
            print("Kullanıcılar oluştur...")
            user1 = User(
                username="user1", email="user1@test.com", 
                password_hash="pw", kurum_id=kurum.id, sistem_rol="admin"
            )
            user2 = User(
                username="user2", email="user2@test.com", 
                password_hash="pw", kurum_id=kurum.id, sistem_rol="kullanici"
            )
            db.session.add(user1)
            db.session.add(user2)
            db.session.commit()
            print("Kullanıcılar oluşturuldu.")
            
            print("Süreç oluştur ve üyeleri ekle...")
            surec = Surec(
                kurum_id=kurum.id, ad="Test Süreç", 
                code="SR1", durum="Aktif"
            )
            
            # Many-to-Many testi
            surec.liderler.append(user1)
            surec.uyeler.append(user2)
            
            db.session.add(surec)
            db.session.commit()
            print("Süreç başarıyla oluşturuldu!")
            
        except Exception:
            print("\n❌ HATA OLUŞTU:")
            traceback.print_exc()

if __name__ == "__main__":
    debug_seeder()
