
from __init__ import create_app, db
from models.user import User, Kurum
from werkzeug.security import generate_password_hash, check_password_hash

app = create_app()

with app.app_context():
    print("--- DEBUGGING LOGIN ISSUE ---")
    
    # Check Institutions
    kurumlar = Kurum.query.all()
    print(f"\nFound {len(kurumlar)} institutions:")
    for k in kurumlar:
        print(f"ID: {k.id}, Short Name: {k.kisa_ad}, Commercial Name: {k.ticari_unvan}")

    # Check Admin User
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print(f"\nAdmin user found: {admin.username}")
        print(f"ID: {admin.id}")
        print(f"Kurum ID: {admin.kurum_id}")
        
        kurum = Kurum.query.get(admin.kurum_id)
        if kurum:
            print(f"Associated Kurum: {kurum.kisa_ad} (ID: {kurum.id})")
        else:
            print(f"WARNING: Associated Kurum ID {admin.kurum_id} NOT FOUND")
            
        # Verify Password
        is_valid = check_password_hash(admin.password_hash, '123456')
        print(f"Password '123456' is valid: {is_valid}")
        
        if not is_valid:
            print("Resetting password to '123456'...")
            admin.password_hash = generate_password_hash('123456')
            db.session.commit()
            print("Password reset complete.")
            
            # Verify again
            is_valid_new = check_password_hash(admin.password_hash, '123456')
            print(f"New Password '123456' is valid: {is_valid_new}")
    else:
        print("\nERROR: Admin user NOT found!")

    # Check other users
    print("\n--- Other Users ---")
    users = User.query.filter(User.username.in_(['salih.yalcin', 'pinar.balci'])).all()
    for u in users:
        print(f"User: {u.username}, Kurum ID: {u.kurum_id}")
        is_valid = check_password_hash(u.password_hash, '123456')
        print(f"Password '123456' is valid: {is_valid}")
        if not is_valid:
             print(f"Resetting password for {u.username}...")
             u.password_hash = generate_password_hash('123456')
             db.session.commit()
             print("Done.")
