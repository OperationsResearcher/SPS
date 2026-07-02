import sys
import os

sys.path.insert(0, os.path.abspath("."))

from app import create_app
from extensions import db
from sqlalchemy import text
import app.services.tenant_clone_service as cloner
from werkzeug.security import generate_password_hash

def create_empty_yeni_tomofil():
    print("Bos YeniTomofil kurumu olusturma islemi baslatiliyor...")
    
    # Constants monkey-patching for YeniTomofil
    cloner.TEST_TENANT_NAME = "YeniTomofil"
    cloner.SYNTH_ADMIN_EMAIL = "admin@yenitomofil.local"
    cloner.SYNTH_ADMIN_PW = "YeniTomofil!123"
    
    app = create_app()
    with app.app_context():
        # Clean up existing YeniTomofil if it exists
        existing_tables = cloner._existing_tables()
        # Case-safe tenant ID lookup
        old_test = db.session.execute(
            text("SELECT id FROM tenants WHERE lower(name) = :n OR lower(coalesce(short_name,'')) = :n LIMIT 1"),
            {"n": cloner.TEST_TENANT_NAME.lower()}
        ).scalar()
        
        if old_test:
            print(f"Eski YeniTomofil kurumu (TID: {old_test}) siliniyor...")
            cloner._wipe_test_tenant(old_test, existing_tables)
            db.session.commit()
            
        print("Sifirdan bos YeniTomofil kurumu yaratiliyor...")
        # Create new tenant
        new_tid = db.session.execute(text(
            "INSERT INTO tenants (name, short_name, tenant_type, is_active) "
            "VALUES (:n, :n, 'normal', true) RETURNING id"
        ), {"n": cloner.TEST_TENANT_NAME}).scalar()

        # Create admin user
        role_id = db.session.execute(text(
            "SELECT id FROM roles WHERE name = 'tenant_admin' LIMIT 1"
        )).scalar()
        admin_id = db.session.execute(text(
            "INSERT INTO users (email, password_hash, first_name, last_name, tenant_id, role_id, is_active) "
            "VALUES (:e, :p, 'Test', 'Admin', :tid, :rid, true) RETURNING id"
        ), {"e": cloner.SYNTH_ADMIN_EMAIL, "p": generate_password_hash(cloner.SYNTH_ADMIN_PW),
            "tid": new_tid, "rid": role_id}).scalar()
            
        # Resync sequences
        cloner._resync_sequences(["tenants", "users"], existing_tables)
        
        db.session.commit()
        print("SUCCESS: Bos YeniTomofil kurumu basariyla olusturuldu!")
        print(f"Kurum ID (TID): {new_tid}")
        print(f"Admin E-posta: {cloner.SYNTH_ADMIN_EMAIL}")
        print(f"Admin Sifre: {cloner.SYNTH_ADMIN_PW}")

if __name__ == "__main__":
    create_empty_yeni_tomofil()
