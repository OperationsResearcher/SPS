
from app import create_app
from extensions import db
from models import User, Kurum, Surec, SurecPerformansGostergesi, BireyselPerformansGostergesi, PerformansGostergeVeri, Activity
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random
import sys

# Encoding fix
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

app = create_app()

def safe_commit():
    try:
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Commit hatası: {e}")
        return False

def create_data():
    with app.app_context():
        print("Veri onarımı ve tamamlama başlıyor...")
        
        # Admin User (Garanti olsun)
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("Admin kullanıcısı bulunamadı! Lütfen önce admin oluşturun.")
            return

        # 1. KURUMLAR & USERLAR (Basit kontrol)
        kurum_data = [
             {"kisa_ad": "TechNova", "ticari_unvan": "TechNova Bilişim A.Ş."},
             {"kisa_ad": "MegaYapi", "ticari_unvan": "Mega Yapı İnşaat Ltd."},
        ]
        
        for k_info in kurum_data:
            k = Kurum.query.filter_by(kisa_ad=k_info['kisa_ad']).first()
            if not k:
                k = Kurum(kisa_ad=k_info['kisa_ad'], ticari_unvan=k_info['ticari_unvan'])
                db.session.add(k)
                safe_commit()
                print(f"+ Kurum: {k.kisa_ad}")

        # Users
        user_roles = [
            {"u": "tech_ceo", "k": "TechNova", "r": "ust_yonetim"},
            {"u": "yapi_mudur", "k": "MegaYapi", "r": "kurum_yoneticisi"},
        ]
        
        pw_hash = generate_password_hash('123456')
        
        for u_info in user_roles:
            kurum = Kurum.query.filter_by(kisa_ad=u_info['k']).first()
            if not kurum: continue
            
            u = User.query.filter_by(username=u_info['u']).first()
            if not u:
                u = User(
                    username=u_info['u'],
                    email=f"{u_info['u']}@example.com",
                    first_name=u_info['u'],
                    password_hash=pw_hash,
                    kurum_id=kurum.id,
                    sistem_rol=u_info['r']
                )
                db.session.add(u)
                safe_commit()
                print(f"+ User: {u.username}")

        # 2. SÜREÇLER & KPI (Daha detaylı)
        surec_defs = [
            {
                "ad": "Yazılım Geliştirme", "kurum": "TechNova",
                "kpi": [
                    {"ad": "Sprint Başarısı", "hedef": "90", "unit": "%"},
                    {"ad": "Hata Sayısı", "hedef": "5", "unit": "Adet"},
                ]
            },
            {
                "ad": "Satış Süreci", "kurum": "TechNova",
                "kpi": [
                    {"ad": "Aylık Ciro", "hedef": "100000", "unit": "TL"},
                ]
            }
        ]
        
        for s in surec_defs:
            kurum = Kurum.query.filter_by(kisa_ad=s['kurum']).first()
            if not kurum: continue
            
            surec = Surec.query.filter_by(ad=s['ad'], kurum_id=kurum.id).first()
            if not surec:
                surec = Surec(ad=s['ad'], aciklama="Otomatik", kurum_id=kurum.id)
                db.session.add(surec)
                if not safe_commit(): continue
                print(f"+ Süreç: {surec.ad}")
            
            # KPI
            for k_def in s['kpi']:
                # SurecPG
                pg = SurecPerformansGostergesi.query.filter_by(ad=k_def['ad'], surec_id=surec.id).first()
                if not pg:
                    pg = SurecPerformansGostergesi(
                        surec_id=surec.id,
                        ad=k_def['ad'],
                        hedef_deger=k_def['hedef'],
                        olcum_birimi=k_def['unit'],
                        baslangic_tarihi=datetime(2025, 1, 1),
                        bitis_tarihi=datetime(2025, 12, 31)
                    )
                    db.session.add(pg)
                    if not safe_commit(): continue
                    print(f"  + KPI: {pg.ad}")

                # Bireysel Atama (Admin'e veya ilgili kurum userına)
                target_user = User.query.filter_by(kurum_id=kurum.id).first()
                if not target_user: target_user = admin

                # BireyselPG Kontrol - Unique index (user_id, kaynak_surec_pg_id) YOK ama mantıken olmalı.
                # Modelde: idx_bireysel_pg_user (user_id, kaynak) var. O da yetmez.
                # Manuel kontrol:
                bpg = BireyselPerformansGostergesi.query.filter_by(
                    kaynak_surec_pg_id=pg.id,
                    user_id=target_user.id
                ).first()
                
                if not bpg:
                    bpg = BireyselPerformansGostergesi(
                        kaynak_surec_pg_id=pg.id,
                        user_id=target_user.id,
                        hedef_deger=k_def['hedef'],
                        olcum_birimi=k_def['unit'],
                        baslangic_tarihi=datetime(2025, 1, 1),
                        bitis_tarihi=datetime(2025, 12, 31),
                        ad=pg.ad,  # Ad alanı zorunlu! (Bu eksikti galiba)
                        kaynak='Süreç'
                    )
                    db.session.add(bpg)
                    if not safe_commit(): continue
                    print(f"    -> Atandı: {target_user.username}")
                
                # VERİ Ekleme
                # Mevcut veri sayısını kontrol et
                veri_count = PerformansGostergeVeri.query.filter_by(bireysel_pg_id=bpg.id).count()
                if veri_count < 3:
                    # Eksik verileri tamamla
                    base_date = datetime.now()
                    for i in range(3):
                         # Ayın 1'ine sabitle
                         d = base_date - timedelta(days=30*i)
                         d = d.replace(day=1)
                         
                         existing_data = PerformansGostergeVeri.query.filter_by(
                             bireysel_pg_id=bpg.id,
                             veri_tarihi=d
                         ).first()
                         
                         if not existing_data:
                             val = float(k_def['hedef']) * (0.8 + 0.4*random.random()) # %80-%120
                             data = PerformansGostergeVeri(
                                 bireysel_pg_id=bpg.id,
                                 yil=d.year,
                                 giris_periyot_tipi='aylik',
                                 giris_periyot_no=d.month,
                                 giris_periyot_ay=d.month,
                                 gerceklesen_deger=f"{val:.2f}",
                                 veri_tarihi=d,
                                 user_id=target_user.id
                             )
                             db.session.add(data)
                    safe_commit()
                    print(f"      + Veriler eklendi ({bpg.ad})")

        print("İşlem tamamlandı.")

if __name__ == "__main__":
    create_data()
