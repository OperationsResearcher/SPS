import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import User

def find_admin():
    app = create_app()
    with app.app_context():
        admin = User.query.filter_by(sistem_rol='admin').first()
        if admin:
            print(f"Admin Kullanıcı: {admin.username}")
            print(f"Şifre: 123456")
            print(f"Kurum ID: {admin.kurum_id}")
        else:
            print("Admin bulunamadı.")

if __name__ == "__main__":
    find_admin()
