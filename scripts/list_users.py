import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import User, Kurum

def list_users():
    app = create_app()
    with app.app_context():
        users = User.query.filter_by(sistem_rol='admin').limit(5).all()
        for u in users:
            print(f"User: {u.username} | Pass: 123456 | Kurum: {u.kurum_id}")

if __name__ == "__main__":
    list_users()
