
import sys
import os
import pandas as pd
from datetime import datetime

# Çıktıyı dosyaya yönlendir (UTF-8)
sys.stdout = open('seed_debug_log.txt', 'w', encoding='utf-8')
sys.stderr = sys.stdout

print("Script Başlatılıyor...")

try:
    from __init__ import create_app, db
    from models.user import User, Kurum
    from models.process import Surec, SurecPerformansGostergesi
    from models.strategy import AnaStrateji, AltStrateji
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

app = create_app()

def seed_database():
    with app.app_context():
        print("1. Bağlam Oluşturuldu.")
        
        try:
            db.drop_all()
            db.create_all()
            print("2. DB Resetlendi.")
        except Exception as e:
            print(f"HATA DB Reset: {e}")
            return

        try:
            kurum_sistem = Kurum(kisa_ad="Sistem", ticari_unvan="Sistem Yönt.")
            db.session.add(kurum_sistem)
            db.session.commit()
            print("3. Sistem Kurumu Eklendi.")
        except Exception as e:
            print(f"HATA Sistem Kurum: {e}")
            return

        try:
            kurum_kmf = Kurum(kisa_ad="KMF", ticari_unvan="KMF Danışmanlık")
            db.session.add(kurum_kmf)
            db.session.commit()
            print("4. KMF Kurumu Eklendi.")
        except Exception as e:
            print(f"HATA KMF Kurum: {e}")
            return

        try:
            # En basit user
            admin = User(username="admin", email="admin@test.com", password_hash="hash", kurum_id=kurum_sistem.id)
            admin.first_name = "Admin" # Parametre yerine attribute atama dene
            admin.set_password("123456")
            admin.sistem_rol = "admin"
            db.session.add(admin)
            db.session.commit()
            print("5. Admin Eklendi.")
        except Exception as e:
            print(f"HATA Admin: {e}")
            # Devam etme
            import traceback
            traceback.print_exc()
            return

if __name__ == "__main__":
    seed_database()
