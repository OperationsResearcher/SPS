
from app import create_app
from models import User
import sys

# Logları bastırmak için stdout'u yönlendir
import logging
logging.getLogger('werkzeug').setLevel(logging.ERROR)

app = create_app()

with app.app_context():
    users = User.query.all()
    with open('users_list.txt', 'w', encoding='utf-8') as f:
        f.write("KULLANICI LISTESI:\n")
        if not users:
            f.write("Hic kullanici bulunamadi.\n")
        for u in users:
            f.write(f"User: {u.username} | Role: {u.sistem_rol}\n")
    print("Liste users_list.txt dosyasina yazildi.")
