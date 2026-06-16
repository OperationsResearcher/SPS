
from __init__ import create_app
from extensions import db
from models.process import Surec, SurecPerformansGostergesi

app = create_app()
with app.app_context():
    print("Süreçler:")
    surecler = Surec.query.all()
    for s in surecler:
        print(f"ID: {s.id}, Ad: {s.ad}, Kurum: {s.kurum_id}")
        pgs = SurecPerformansGostergesi.query.filter_by(surec_id=s.id).all()
        for pg in pgs:
            print(f"  - PG ID: {pg.id}, Ad: {pg.ad}")
