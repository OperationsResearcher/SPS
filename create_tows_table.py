
from __init__ import create_app, db
from models.process import TowsAnalizi

app = create_app()

with app.app_context():
    db.create_all()
    print("Tables update complete.")
