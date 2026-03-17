
from app import create_app
from models import User, Kurum, db
from werkzeug.security import generate_password_hash
import sys

# Logları bastırmak için stdout'u yönlendir
import logging
logging.getLogger('werkzeug').setLevel(logging.ERROR)

app = create_app()

with app.app_context():
    try:
        # Kurum kontrolü
        kurum = Kurum.query.first()
        if not kurum:
            # DÜZELTME: ad -> ticari_unvan
            kurum = Kurum(ticari_unvan="Test Kurum A.Ş.", kisa_ad="TEST")
            db.session.add(kurum)
            db.session.commit()
            print(f"Kurum oluşturuldu: {kurum.ticari_unvan}")
        else:
            print(f"Mevcut Kurum: {kurum.ticari_unvan}")

        # Admin Kullanıcı
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('123456'),
                first_name='Admin',
                last_name='User',
                sistem_rol='admin',
                kurum_id=kurum.id
            )
            db.session.add(admin)
            print("Admin user created (admin / 123456)")
        else:
            # Şifresini resetle (Her ihtimale karşı)
            admin.password_hash = generate_password_hash('123456')
            print("Admin password reset to 123456")

        # Standart Kullanıcı
        user = User.query.filter_by(username='user').first()
        if not user:
            user = User(
                username='user',
                email='user@example.com',
                password_hash=generate_password_hash('123456'),
                first_name='Standart',
                last_name='User',
                sistem_rol='kurum_kullanici',
                kurum_id=kurum.id
            )
            db.session.add(user)
            print("Standard user created (user / 123456)")
        else:
            # Şifresini resetle
            user.password_hash = generate_password_hash('123456')
            print("User password reset to 123456")
        
        db.session.commit()
        print("Users committed successfully.")
    except Exception as e:
        print(f"Error creating users: {e}")
        db.session.rollback()
