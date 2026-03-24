# -*- coding: utf-8 -*-
"""Admin sifresini sifirla. Kullanim: python scripts/reset_admin_password.py [yeni_sifre]"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    from app import create_app
    from app.models.core import User
    from werkzeug.security import generate_password_hash

    app = create_app()
    password = (sys.argv[1] if len(sys.argv) > 1 else "admin123").strip()

    with app.app_context():
        u = User.query.filter_by(email="admin@kokpitim.com").first()
        if not u:
            print("admin@kokpitim.com bulunamadi!")
            sys.exit(1)
        u.password_hash = generate_password_hash(password)
        from app.models import db
        db.session.commit()
        print(f"Sifre guncellendi. admin@kokpitim.com / {password}")

if __name__ == "__main__":
    main()
