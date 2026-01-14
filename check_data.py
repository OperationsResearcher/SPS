
from app import create_app
from extensions import db
from models import PerformansGostergeVeri, BireyselPerformansGostergesi, SurecPerformansGostergesi

app = create_app()

with app.app_context():
    pg_count = SurecPerformansGostergesi.query.count()
    bpg_count = BireyselPerformansGostergesi.query.count()
    data_count = PerformansGostergeVeri.query.count()
    
    print(f"SurecPG Sayısı: {pg_count}")
    print(f"BireyselPG Sayısı: {bpg_count}")
    print(f"PG Veri Sayısı: {data_count}")
    
    if data_count > 0:
        last_data = PerformansGostergeVeri.query.order_by(PerformansGostergeVeri.id.desc()).first()
        print(f"Son Veri: Değer={last_data.gerceklesen_deger}, Tarih={last_data.veri_tarihi}, User={last_data.user_id}")
