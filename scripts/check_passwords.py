# -*- coding: utf-8 -*-
"""
Kullanıcı şifrelerini kontrol et (hash'leri göster)
"""
from dotenv import load_dotenv
load_dotenv()

from __init__ import create_app
from models import User
from werkzeug.security import check_password_hash

app = create_app()

with app.app_context():
    users = User.query.filter(User.sistem_rol.in_(['admin', 'kurum_yoneticisi', 'kurum_kullanici'])).limit(5).all()
    print("=" * 60)
    print("Kullanıcı Şifre Kontrolü")
    print("=" * 60)
    test_passwords = ['admin', 'burak', 'Ali', '123456', 'password']
    
    for user in users:
        print(f"\nUsername: {user.username}, Rol: {user.sistem_rol}")
        for test_pwd in test_passwords:
            if check_password_hash(user.password_hash, test_pwd):
                print(f"  ✅ Şifre: {test_pwd}")
                break
        else:
            print(f"  ❌ Test şifreleri eşleşmedi")

