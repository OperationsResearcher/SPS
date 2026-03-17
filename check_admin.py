import sys
sys.path.insert(0, 'c:/kokpitim')
from app import create_app
from app.models import User

app = create_app()
with app.app_context():
    users = User.query.all()
    for u in users:
        print("Email:", u.email, "| Admin:", u.is_admin, "| Active:", u.is_active)
