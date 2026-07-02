import sys
import os

sys.path.insert(0, os.path.abspath("."))

from app import create_app
from extensions import db
from sqlalchemy import text
import app.services.tenant_clone_service as cloner

def clone_to_yeni_tomofil():
    print("YeniTomofil klonlama islemi baslatiliyor...")
    
    # Constants monkey-patching for YeniTomofil
    cloner.TEST_TENANT_NAME = "YeniTomofil"
    cloner.SYNTH_ADMIN_EMAIL = "admin@yenitomofil.local"
    cloner.SYNTH_ADMIN_PW = "YeniTomofil!123"
    
    app = create_app()
    with app.app_context():
        # Clean up existing YeniTomofil if it exists
        existing_tables = cloner._existing_tables()
        old_test = cloner.find_test_tenant_id()
        if old_test:
            print("Eski YeniTomofil kurumu siliniyor...")
            cloner._wipe_test_tenant(old_test, existing_tables)
            db.session.commit()
            
        print("Tomofil'den YeniTomofil kurumu klonlaniyor...")
        # Run the clone with dry_run=False (commit)
        res = cloner.clone_tomofiltest(dry_run=False)
        
        if res.get("ok"):
            print("SUCCESS: YeniTomofil basariyla klonlandi!")
            print(f"Yeni Kurum ID (TID): {res.get('new_tid')}")
            print(f"Sentetik Admin E-posta: admin@yenitomofil.local")
            print(f"Sentetik Admin Sifre: YeniTomofil!123")
            print(f"Kopyalanan Toplam Satir: {res.get('total_rows')}")
            print("Tablo detaylari:")
            for t, count in res.get("tables", {}).items():
                print(f"  - {t}: {count} satir")
        else:
            print(f"FAILURE: Klonlama hatasi: {res.get('error')}")

if __name__ == "__main__":
    clone_to_yeni_tomofil()
