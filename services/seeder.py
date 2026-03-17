# -*- coding: utf-8 -*-
"""
Veri Simülasyonu (Seeder) Servisi
---------------------------------
Faker ile demo veri üretimi için
"""
from faker import Faker
from faker.providers import company, lorem, date_time, internet, person
from datetime import datetime, timedelta
import random
from sqlalchemy.exc import IntegrityError

fake = Faker('tr_TR')
fake.add_provider(company)
fake.add_provider(lorem)
fake.add_provider(date_time)
fake.add_provider(internet)
fake.add_provider(person)


def seed_kurum(db):
    """Kurum verileri oluştur"""
    from models import Kurum
    
    kurumlar = []
    for _ in range(5):
        kurum = Kurum(
            kisa_ad=fake.company(),
            ticari_unvan=fake.company() + ' A.S.',
            sektor=random.choice(['Teknoloji', 'Finans', 'Saglik', 'Egitim', 'Uretim', 'Hizmet']),
            faaliyet_alani=fake.sentence(nb_words=5),
            calisan_sayisi=random.randint(10, 500),
            email=fake.company_email(),
            telefon=fake.phone_number(),
            web_adresi=fake.url()
        )
        kurumlar.append(kurum)
        db.session.add(kurum)
    
    try:
        db.session.commit()
        return kurumlar
    except IntegrityError:
        db.session.rollback()
        return []


def seed_user(db, kurumlar):
    """Kullanıcı verileri oluştur"""
    from models import User
    
    if not kurumlar:
        return []
    
    roller = ['admin', 'kurum_yoneticisi', 'surec_lideri', 'kurum_kullanici']
    users = []
    
    for kurum in kurumlar:
        # Her kurum için admin kullanıcı
        admin_username = fake.user_name() + str(kurum.id)
        admin_user = User(
            username=admin_username,
            email=fake.unique.email(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            kurum_id=kurum.id,
            sistem_rol='admin'
        )
        from werkzeug.security import generate_password_hash
        admin_user.password_hash = generate_password_hash('123456')
        users.append(admin_user)
        db.session.add(admin_user)
        
        # Her kurum için 3-5 normal kullanıcı
        for _ in range(random.randint(3, 5)):
            username = fake.user_name() + str(random.randint(1000, 9999))
            user = User(
                username=username,
                email=fake.unique.email(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                kurum_id=kurum.id,
                sistem_rol=random.choice(roller)
            )
            user.password_hash = generate_password_hash('123456')
            users.append(user)
            db.session.add(user)
    
    try:
        db.session.commit()
        return users
    except IntegrityError:
        db.session.rollback()
        return []


def seed_ana_strateji(db, kurumlar):
    """Ana Strateji verileri oluştur"""
    from models import AnaStrateji
    
    if not kurumlar:
        return []
    
    stratejiler = []
    # Türkçe karakter sorunu çıkarmaması için basit karakterler
    strateji_konulari = [
        'Buyume ve Genisleme',
        'Musteri Memnuniyeti',
        'Operasyonel Mukemmellik',
        'Inovasyon ve Ar-Ge',
        'Surdurulebilirlik',
        'Dijital Donusum'
    ]
    
    for kurum in kurumlar:
        # Kodun benzersiz olması için global counter veya benzeri bir yapı yerine basit bir random ekliyoruz
        used_codes = set()
        for i in range(random.randint(2, 4)):
            code = f"ST{random.randint(1000, 9999)}"
            while code in used_codes:
                code = f"ST{random.randint(1000, 9999)}"
            used_codes.add(code)
            
            strateji = AnaStrateji(
                kurum_id=kurum.id,
                code=code,
                ad=random.choice(strateji_konulari),
                aciklama="Strateji aciklamasi detay metni surada yer alir."
            )
            stratejiler.append(strateji)
            db.session.add(strateji)
    
    try:
        db.session.commit()
        return stratejiler
    except IntegrityError:
        db.session.rollback()
        return []


def seed_alt_strateji(db, ana_stratejiler):
    """Alt Strateji verileri oluştur"""
    from models import AltStrateji
    
    if not ana_stratejiler:
        return []
    
    alt_stratejiler = []
    
    for ana_strateji in ana_stratejiler:
        for i in range(random.randint(2, 4)):
            alt_strateji = AltStrateji(
                ana_strateji_id=ana_strateji.id,
                code=f"{ana_strateji.code}.{i+1}" if ana_strateji.code else None,
                ad=fake.sentence(nb_words=4),
                aciklama="Alt strateji detay aciklamasi."
            )
            alt_stratejiler.append(alt_strateji)
            db.session.add(alt_strateji)
    
    try:
        db.session.commit()
        return alt_stratejiler
    except IntegrityError:
        db.session.rollback()
        return []


def seed_surec(db, kurumlar, users):
    """Süreç verileri oluştur"""
    from models import Surec
    
    if not kurumlar or not users:
        return []
    
    surec_tipleri = ['Ana', 'Destek', 'Yonetim']
    surecler = []
    
    for kurum in kurumlar:
        kurum_users = [u for u in users if u.kurum_id == kurum.id]
        if not kurum_users:
            continue
        
        for i in range(random.randint(5, 10)):
            # Önce objeyi oluştur
            surec = Surec(
                kurum_id=kurum.id,
                ad=fake.sentence(nb_words=3),
                code=f"SR{random.randint(100, 999)}",
                aciklama="Surec detay aciklamasi.",
                durum='Aktif'
            )
            
            # İlişkileri ayarla (Users listesinden rastgele seçip)
            if kurum_users:
                # Rastgele bir lider seç ve listeye ekle
                lider = random.choice(kurum_users)
                surec.liderler.append(lider)
                
                # Rastgele üyeler seç ve listeye ekle
                uyeler = random.sample(kurum_users, min(random.randint(2, 4), len(kurum_users)))
                
                # SQLAlchemy backref append metoduyla ilişki kur
                for uye in uyeler:
                    if uye.id != lider.id:
                        surec.uyeler.append(uye)
            
            surecler.append(surec)
            db.session.add(surec)
    
    try:
        db.session.commit()
        return surecler
    except IntegrityError:
        db.session.rollback()
        return []


def seed_project(db, kurumlar, users):
    """Proje verileri oluştur"""
    from models import Project
    
    if not kurumlar or not users:
        return []
    
    
    for kurum in kurumlar:
        kurum_users = [u for u in users if u.kurum_id == kurum.id]
        if not kurum_users:
            continue
        
        for _ in range(random.randint(3, 8)):
            manager = random.choice(kurum_users)
            project = Project(
                kurum_id=kurum.id,
                name=fake.sentence(nb_words=4),
                description="Proje detay aciklamasi.",
                manager_id=manager.id,
                priority=random.choice(['Yuksek', 'Orta', 'Dusuk']),
                start_date=fake.date_between(start_date='-1y', end_date='today'),
                end_date=fake.date_between(start_date='today', end_date='+1y'),
                health_status='Iyi',
                health_score=random.randint(70, 100)
            )
            
            # Üyeleri ekle
            uyeler = random.sample(kurum_users, min(random.randint(2, 5), len(kurum_users)))
            for uye in uyeler:
                project.members.append(uye)
                
            db.session.add(project)
    
    try:
        db.session.commit()
        return [] # Proje listesi döndürmeye gerek yok şimdilik
    except IntegrityError:
        db.session.rollback()
        return []


def seed_task(db, projects, users):
    """Görev verileri oluştur"""
    # Proje nesnelerini almak için db sorgusu gerekli
    return []

def seed_all(db, kurum_sayisi=3):
    """Tüm demo verileri oluştur"""
    results = {
        'kurumlar': 0,
        'users': 0,
        'ana_stratejiler': 0,
        'alt_stratejiler': 0,
        'surecler': 0,
        'projeler': 0,
        'gorevler': 0,
        'hata': None
    }
    
    try:
        # 1. Kurumlar
        print("Kurumlar oluşturuluyor...")
        kurumlar = seed_kurum(db)
        results['kurumlar'] = len(kurumlar)
        
        # 2. Kullanıcılar
        print("Kullanıcılar oluşturuluyor...")
        users = seed_user(db, kurumlar)
        results['users'] = len(users)
        
        # 3. Ana Stratejiler
        print("Ana stratejiler oluşturuluyor...")
        ana_stratejiler = seed_ana_strateji(db, kurumlar)
        results['ana_stratejiler'] = len(ana_stratejiler)
        
        # 4. Alt Stratejiler
        print("Alt stratejiler oluşturuluyor...")
        alt_stratejiler = seed_alt_strateji(db, ana_stratejiler)
        results['alt_stratejiler'] = len(alt_stratejiler)
        
        # 5. Süreçler
        print("Süreçler oluşturuluyor...")
        surecler = seed_surec(db, kurumlar, users)
        results['surecler'] = len(surecler)
        
        # 6. Projeler
        print("Projeler oluşturuluyor...")
        # projeler = seed_project(db, kurumlar, users)
        # results['projeler'] = len(projeler)
        
        print("Demo veriler başarıyla oluşturuldu!")
        
    except Exception as e:
        db.session.rollback()
        results['hata'] = str(e)
        print(f"Hata oluştu: {e}")
        import traceback
        traceback.print_exc()
    
    return results
