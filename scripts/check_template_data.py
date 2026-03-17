"""
Template'e ne gönderildiğini kontrol et
"""
from models import db, User, Kurum
from app import app

with app.app_context():
    kullanicilar = User.query.all()
    kurumlar = Kurum.query.all()
    
    print(f"Template'e gönderilecek veriler:")
    print(f"=" * 60)
    print(f"Toplam Kurum: {len(kurumlar)}")
    print(f"Toplam Kullanıcı: {len(kullanicilar)}")
    print(f"\nKurumlar:")
    for k in kurumlar:
        user_count = User.query.filter_by(kurum_id=k.id).count()
        print(f"  {k.id}: {k.kisa_ad} ({user_count} kullanıcı)")
    
    print(f"\nSistem rolleri dağılımı:")
    for rol in ['admin', 'kurum_yoneticisi', 'ust_yonetim', 'kurum_kullanici']:
        count = User.query.filter_by(sistem_rol=rol).count()
        print(f"  {rol}: {count}")
