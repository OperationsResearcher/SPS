from app import create_app
from app.models import db
from app.models.core import User, Role
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    r = Role.query.filter_by(name='standard_user').first()
    if r:
        u = User.query.filter_by(email='user@kokpitim.com').first()
        if not u:
            u = User(email='user@kokpitim.com', password_hash=generate_password_hash('123456'), role_id=r.id, is_active=True)
            db.session.add(u)
            db.session.commit()
            print("User created")
        else:
            u.role_id = r.id
            db.session.commit()
            print("User existed")
