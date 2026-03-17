
from app import create_app
from models import User

app = create_app()

with app.app_context():
    users = User.query.all()
    print("Mevcut Kullanıcılar:")
    for u in users:
        print(f"Username: {u.username}, Role: {u.sistem_rol}, Kurum: {u.kurum_id}")
