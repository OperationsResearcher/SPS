# -*- coding: utf-8 -*-
"""
Veritabanındaki kullanıcıları listele
"""
from dotenv import load_dotenv
load_dotenv()

from __init__ import create_app
from models import User

app = create_app()

with app.app_context():
    users = User.query.all()
    print("=" * 60)
    print("Veritabanındaki Kullanıcılar")
    print("=" * 60)
    for user in users:
        print(f"ID: {user.id}, Username: {user.username}, Rol: {user.sistem_rol}, Kurum: {user.kurum.kisa_ad if user.kurum else 'N/A'}")

