
from __init__ import create_app
from models import User
app = create_app()
with app.app_context():
    u = User.query.filter_by(username='1salih').first()
    if u:
        print(f"User: {u.username}, Role: {u.sistem_rol}")
    else:
        print("User not found")
