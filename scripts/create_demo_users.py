# -*- coding: utf-8 -*-
"""
KMF Demo Kurum için Örnek Kullanıcı Oluşturma Scripti
10 adet örnek kullanıcı oluşturur.
"""
import sys
import random
from werkzeug.security import generate_password_hash

# Uygulama ve modelleri import et
from __init__ import create_app
from models import db, User, Kurum

# Türkçe isim listeleri
FIRST_NAMES = ['Ahmet', 'Mehmet', 'Ali', 'Mustafa', 'Ayşe', 'Fatma', 'Zeynep', 'Emine', 'Hatice', 'Elif',
               'Can', 'Burak', 'Deniz', 'Ege', 'Cem', 'Kerem', 'Arda', 'Emre', 'Onur', 'Serkan',
               'Selin', 'Derya', 'Gizem', 'Burcu', 'Seda', 'Pınar', 'Özge', 'Esra', 'Merve', 'Selin']

LAST_NAMES = ['Yılmaz', 'Kaya', 'Demir', 'Şahin', 'Çelik', 'Yıldız', 'Yıldırım', 'Öztürk', 'Aydın', 'Özdemir',
              'Arslan', 'Doğan', 'Kılıç', 'Aslan', 'Çetin', 'Kara', 'Koç', 'Kurt', 'Özkan', 'Şimşek']

USERNAME_PREFIXES = ['user', 'kullanici', 'demo', 'test', 'dev', 'admin', 'manager', 'analyst', 'developer', 'tester']

def create_demo_users():
    """KMF Demo Kurum için örnek kullanıcılar oluştur"""
    app = create_app()
    
    with app.app_context():
        try:
            print("=" * 60)
            print("KMF DEMO KURUM - ORNEK KULLANICI OLUSTURMA SCRIPTI")
            print("=" * 60)
            
            # 1. KMF Demo Kurum'u bul
            print("\n1. KMF Demo Kurum kontrolu yapiliyor...")
            kurum = Kurum.query.filter_by(kisa_ad='KMF Demo Kurum').first()
            if not kurum:
                # Eğer yoksa oluştur
                kurum = Kurum(
                    kisa_ad='KMF Demo Kurum',
                    ticari_unvan='KMF Demo Kurum A.S.',
                    faaliyet_alani='Demo Faaliyet',
                    sektor='Demo Sektör',
                    calisan_sayisi=10,
                    email='demo@kmf.local',
                    telefon='+90 352 000 0000',
                    web_adresi='https://demo.kmf.local'
                )
                db.session.add(kurum)
                db.session.commit()
                print("   [OK] KMF Demo Kurum olusturuldu (ID: {})".format(kurum.id))
            else:
                print("   [OK] KMF Demo Kurum mevcut (ID: {})".format(kurum.id))
            
            # 2. Mevcut kullanıcıları kontrol et
            print("\n2. Mevcut kullanicilar kontrol ediliyor...")
            mevcut_kullanicilar = User.query.filter_by(kurum_id=kurum.id).all()
            print("   [BILGI] Mevcut kullanici sayisi: {}".format(len(mevcut_kullanicilar)))
            
            # 3. 10 adet örnek kullanıcı oluştur
            print("\n3. 10 adet ornek kullanici olusturuluyor...")
            
            olusturulan_kullanicilar = []
            kullanici_sayisi = 0
            
            while kullanici_sayisi < 10:
                # Benzersiz kullanıcı adı oluştur
                username_prefix = random.choice(USERNAME_PREFIXES)
                username = f"{username_prefix}{kullanici_sayisi + 1:02d}"
                email = f"{username}@kmfdemo.local"
                
                # Kullanıcı adı ve email'in benzersiz olup olmadığını kontrol et
                existing_user = User.query.filter(
                    (User.username == username) | (User.email == email)
                ).first()
                
                if existing_user:
                    continue  # Eğer varsa, yeni bir tane oluştur
                
                # İsim ve soyisim
                first_name = random.choice(FIRST_NAMES)
                last_name = random.choice(LAST_NAMES)
                
                # Sistem rolleri (çoğunlukla kurum_kullanici, birkaç tane kurum_yoneticisi)
                if kullanici_sayisi < 2:
                    sistem_rol = 'kurum_yoneticisi'
                elif kullanici_sayisi < 4:
                    sistem_rol = 'ust_yonetim'
                else:
                    sistem_rol = 'kurum_kullanici'
                
                # Telefon
                telefon = f"+90 5{random.randint(10, 99)} {random.randint(100, 999)} {random.randint(1000, 9999)}"
                
                # Unvan
                unvanlar = [
                    'Yazılım Geliştirici',
                    'Proje Yöneticisi',
                    'İş Analisti',
                    'Test Uzmanı',
                    'DevOps Mühendisi',
                    'UI/UX Tasarımcı',
                    'Veri Analisti',
                    'Pazarlama Uzmanı',
                    'İnsan Kaynakları Uzmanı',
                    'Muhasebeci'
                ]
                title = random.choice(unvanlar)
                
                # Departman
                departmanlar = [
                    'Yazılım Geliştirme',
                    'Proje Yönetimi',
                    'İş Analizi',
                    'Test ve Kalite',
                    'Altyapı',
                    'Tasarım',
                    'Veri Analizi',
                    'Pazarlama',
                    'İnsan Kaynakları',
                    'Muhasebe'
                ]
                department = random.choice(departmanlar)
                
                # Varsayılan şifre (123456)
                password_hash = generate_password_hash('123456')
                
                # Kullanıcı oluştur
                user = User(
                    username=username,
                    email=email,
                    password_hash=password_hash,
                    first_name=first_name,
                    last_name=last_name,
                    sistem_rol=sistem_rol,
                    kurum_id=kurum.id,
                    phone=telefon,
                    title=title,
                    department=department
                )
                
                db.session.add(user)
                olusturulan_kullanicilar.append({
                    'username': username,
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'rol': sistem_rol
                })
                
                kullanici_sayisi += 1
                print("   [{}/10] Kullanici olusturuldu: {} ({}) - {}".format(
                    kullanici_sayisi, username, first_name + ' ' + last_name, sistem_rol
                ))
            
            # 4. Değişiklikleri kaydet
            db.session.commit()
            
            # 5. Sonuç
            print("\n" + "=" * 60)
            print("BASARILI!")
            print("=" * 60)
            print("\nOlusturulan Kullanicilar:")
            print("-" * 60)
            for idx, kullanici in enumerate(olusturulan_kullanicilar, 1):
                print("{}. {} ({} {})".format(
                    idx,
                    kullanici['username'],
                    kullanici['first_name'],
                    kullanici['last_name']
                ))
                print("   Email: {}".format(kullanici['email']))
                print("   Rol: {}".format(kullanici['rol']))
                print("   Sifre: 123456")
                print()
            
            print("=" * 60)
            print("TOPLAM {} KULLANICI OLUSTURULDU".format(len(olusturulan_kullanicilar)))
            print("=" * 60)
            print("\nTum kullanicilarin varsayilan sifresi: 123456")
            print("Kurum: {}".format(kurum.kisa_ad))
            print("=" * 60 + "\n")
            
            return True
            
        except Exception as e:
            import traceback
            print("\n" + "=" * 60)
            print("HATA!")
            print("=" * 60)
            print("Hata mesaji: {}".format(str(e)))
            print("\nDetayli hata:")
            print(traceback.format_exc())
            print("=" * 60 + "\n")
            db.session.rollback()
            return False

if __name__ == '__main__':
    success = create_demo_users()
    sys.exit(0 if success else 1)

