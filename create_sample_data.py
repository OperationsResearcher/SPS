
from app import create_app
from extensions import db
from models import User, Kurum, Surec, SurecPerformansGostergesi, BireyselPerformansGostergesi, PerformansGostergeVeri, Activity
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random
import sys
import traceback

# Encoding fix
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

app = create_app()

def create_data():
    try:
        with app.app_context():
            print("Örnek veri girişi başlıyor...")
            
            # 1. KURUMLAR
            kurum_data = [
                {"kisa_ad": "TechNova", "ticari_unvan": "TechNova Bilişim Çözümleri A.Ş."},
                {"kisa_ad": "MegaYapi", "ticari_unvan": "Mega Yapı ve İnşaat Sanayi Tic. Ltd."},
                {"kisa_ad": "EcoDoga", "ticari_unvan": "EcoDoğa Geri Dönüşüm ve Enerji A.Ş."}
            ]
            
            db_kurumlar = []
            for k_info in kurum_data:
                k = Kurum.query.filter_by(kisa_ad=k_info['kisa_ad']).first()
                if not k:
                    k = Kurum(kisa_ad=k_info['kisa_ad'], ticari_unvan=k_info['ticari_unvan'])
                    db.session.add(k)
                    db.session.commit()
                    print(f"Kurum eklendi: {k.kisa_ad}")
                db_kurumlar.append(k)

            test_kurum = Kurum.query.first()
            if test_kurum and test_kurum not in db_kurumlar:
                db_kurumlar.insert(0, test_kurum)
                
            print(f"Toplam {len(db_kurumlar)} kurum.")

            # 2. KULLANICILAR
            pw_hash = generate_password_hash('123456')
            
            user_roles = [
                {"u": "tech_ceo", "f": "Ahmet", "l": "Yılmaz", "role": "ust_yonetim", "kurum_idx": 1},
                {"u": "tech_cto", "f": "Zeynep", "l": "Kaya", "role": "kurum_yoneticisi", "kurum_idx": 1},
                {"u": "dev_lead", "f": "Can", "l": "Demir", "role": "surec_lideri", "kurum_idx": 1},
                {"u": "dev_user", "f": "Elif", "l": "Çelik", "role": "kurum_kullanici", "kurum_idx": 1},
                {"u": "yapi_mudur", "f": "Murat", "l": "Şahin", "role": "kurum_yoneticisi", "kurum_idx": 2},
                {"u": "saha_sef", "f": "Veli", "l": "Öztürk", "role": "surec_lideri", "kurum_idx": 2},
                {"u": "eco_uzman", "f": "Ayşe", "l": "Yıldız", "role": "kurum_kullanici", "kurum_idx": 3}
            ]
            
            db_users = []
            for u_info in user_roles:
                if u_info['kurum_idx'] < len(db_kurumlar):
                    kurum = db_kurumlar[u_info['kurum_idx']]
                else:
                    kurum = db_kurumlar[0]
                    
                u = User.query.filter_by(username=u_info['u']).first()
                if not u:
                    u = User(
                        username=u_info['u'],
                        email=f"{u_info['u']}@example.com",
                        first_name=u_info['f'],
                        last_name=u_info['l'],
                        password_hash=pw_hash,
                        kurum_id=kurum.id,
                        sistem_rol=u_info['role']
                    )
                    db.session.add(u)
                    db.session.commit()
                    print(f"Kullanıcı eklendi: {u.username}")
                db_users.append(u)
            
            admin = User.query.filter_by(username='admin').first()
            if admin:
                db_users.insert(0, admin)

            # 3. SÜREÇLER VE KPI
            surec_defs = [
                {
                    "ad": "Yazılım Geliştirme", 
                    "hedef": "Sıfır hata ile zamanında teslimat", 
                    "kurum": "TechNova",
                    "kpi": [
                        {"ad": "Sprint Tamamlama Oranı", "hedef": "90", "unit": "%", "dir": "Increasing"},
                        {"ad": "Canlıya Geçiş Sayısı", "hedef": "4", "unit": "Adet", "dir": "Increasing"},
                    ]
                },
                {
                    "ad": "Müşteri Destek", 
                    "hedef": "Maksimum müşteri memnuniyeti", 
                    "kurum": "TechNova",
                    "kpi": [
                        {"ad": "Ortalama Yanıt Süresi", "hedef": "30", "unit": "Dakika", "dir": "Decreasing"},
                    ]
                }
            ]
            
            for s_def in surec_defs:
                try:
                    kurum = next((k for k in db_kurumlar if k.kisa_ad == s_def['kurum']), db_kurumlar[0])
                    surec = Surec.query.filter_by(ad=s_def['ad'], kurum_id=kurum.id).first()
                    
                    if not surec:
                        surec = Surec(
                            ad=s_def['ad'],
                            aciklama=f"{s_def['ad']} süreci. Hedef: {s_def['hedef']}",
                            kurum_id=kurum.id
                        )
                        db.session.add(surec)
                        db.session.commit()
                        print(f"Süreç eklendi: {surec.ad}")
                
                    for kpi_def in s_def['kpi']:
                        pg = SurecPerformansGostergesi.query.filter_by(ad=kpi_def['ad'], surec_id=surec.id).first()
                        if not pg:
                            pg = SurecPerformansGostergesi(
                                surec_id=surec.id,
                                ad=kpi_def['ad'],
                                aciklama=f"{kpi_def['ad']}",
                                hedef_deger=kpi_def['hedef'],
                                olcum_birimi=kpi_def['unit'],
                                direction=kpi_def['dir'],
                                periyot="Aylık",
                                kodu=f"K-{random.randint(1000,9999)}",
                                baslangic_tarihi=datetime(2025, 1, 1),
                                bitis_tarihi=datetime(2025, 12, 31)
                            )
                            db.session.add(pg)
                            db.session.commit()
                            
                            sorumlu = next((u for u in db_users if u.kurum_id == kurum.id), admin)
                            if not sorumlu: sorumlu = admin
                            
                            bpg = BireyselPerformansGostergesi.query.filter_by(kaynak_surec_pg_id=pg.id, user_id=sorumlu.id).first()
                            if not bpg:
                                bpg = BireyselPerformansGostergesi(
                                    kaynak_surec_pg_id=pg.id,
                                    user_id=sorumlu.id,
                                    hedef_deger=kpi_def['hedef'],
                                    olcum_birimi=kpi_def['unit'],
                                    baslangic_tarihi=datetime(2025, 1, 1),
                                    bitis_tarihi=datetime(2025, 12, 31),
                                    kaynak='Süreç'
                                )
                                db.session.add(bpg)
                                db.session.commit()
                                print(f"KPI atandı: {pg.ad} -> {sorumlu.username}")
                                
                                # VERİ GİRİŞİ
                                base_date = datetime.now()
                                hedef_val = float(kpi_def['hedef'])
                                for i in range(6):
                                    date = base_date - timedelta(days=30 * i)
                                    variance = random.uniform(-10, 10)
                                    gerceklesen = hedef_val * (1 + (variance/100))
                                    data_entry = PerformansGostergeVeri(
                                        bireysel_pg_id=bpg.id,
                                        yil=date.year,
                                        giris_periyot_tipi='aylik',
                                        giris_periyot_no=date.month,
                                        giris_periyot_ay=date.month,
                                        gerceklesen_deger=f"{gerceklesen:.2f}",
                                        aciklama="Otomatik",
                                        veri_tarihi=date,
                                        user_id=sorumlu.id
                                    )
                                    db.session.add(data_entry)
                                db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    print(f"Hata (Süreç döngüsü): {e}")

            # 4. AKTİVİTELER
            task_subjects = ["Toplantı", "Rapor", "Analiz", "Bakım"]
            statuses = ["Açık", "Devam Ediyor", "Tamamlandı"]
            
            all_users = User.query.all()
            for u in all_users:
                try:
                    for _ in range(5):
                        act = Activity(
                            source="System",
                            subject=f"{random.choice(task_subjects)} - {random.randint(1,100)}",
                            description="Otomatik",
                            status=random.choice(statuses),
                            priority="Normal",
                            assigned_to_id=u.id,
                            project_name="Genel",
                            date=datetime.now() - timedelta(days=random.randint(0, 30))
                        )
                        db.session.add(act)
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    print(f"Hata (Aktivite): {e}")
                    
            print("Veri oluşturma tamamlandı.")
            
    except Exception as e:
        traceback.print_exc()

if __name__ == "__main__":
    create_data()
