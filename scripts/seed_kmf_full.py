
import sys
import os
import pandas as pd
from datetime import datetime

# Proje kök dizinini path'e ekle
sys.path.append(os.getcwd())

# from app import create_app, db  <-- Bu hata verebilir çünkü app.py da init import ediyor
try:
    from __init__ import create_app, db
except ImportError:
    # Alternatif: Eğer script kök dizinden çalıştırılıyorsa
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from __init__ import create_app, db
from models.user import User, Role, Kurum
from models.process import Surec, SurecPerformansGostergesi, Faaliyet
from models.strategy import AnaStrateji, AltStrateji
from werkzeug.security import generate_password_hash

app = create_app()

def seed_database():
    with app.app_context():
        print("!!! VERİTABANI SIFIRLANIYOR !!!")
        db.drop_all()
        db.create_all()
        print("✓ Tablolar yeniden oluşturuldu.")

        # 1. KURUMLAR
        kurum_sistem = Kurum(ad="Sistem Yönetimi")
        kurum_kmf = Kurum(ad="KMF Yönetim Danışmanlığı")
        db.session.add_all([kurum_sistem, kurum_kmf])
        db.session.commit()
        print(f"✓ Kurumlar oluşturuldu: {kurum_sistem.ad}, {kurum_kmf.ad}")

        # 2. ROLLER
        roles = {}
        for r_name in ['Admin', 'Süreç Lideri', 'Personel']:
            role = Role(ad=r_name)
            db.session.add(role)
            roles[r_name] = role
        db.session.commit()
        
        # 3. SİSTEM ADMİNİ
        admin_user = User(
            username="admin", 
            email="admin@sistem.com", 
            first_name="Sistem", 
            last_name="Yöneticisi",
            is_active=True,
            kurum_id=kurum_sistem.id
        )
        admin_user.set_password("123456")
        admin_user.roles.append(roles['Admin'])
        db.session.add(admin_user)
        print("✓ Admin kullanıcısı oluşturuldu (admin / 123456)")

        # 4. PERSONEL LİSTESİNDEN KULLANICILARI YÜKLE
        excel_path = r"c:\SPY_Cursor\SP_Code\belge\PERSONEL LİSTESİ.xlsx"
        created_users = []
        
        try:
            # Sheet ismine dikkat: 'Personel ' olabilir
            xls = pd.ExcelFile(excel_path)
            sheet_name = 'Personel'
            if 'Personel ' in xls.sheet_names:
                sheet_name = 'Personel '
            elif 'Personel' in xls.sheet_names:
                sheet_name = 'Personel'
            else:
                sheet_name = xls.sheet_names[0] # İlk sayfayı al
            
            print(f"Not: Excel'den '{sheet_name}' sayfası okunuyor...")
            
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
            
            for index, row in df.iterrows():
                # AD SOYAD kolonu
                ad_soyad = None
                if 'AD SOYAD' in df.columns: ad_soyad = row['AD SOYAD']
                elif 'Ad Soyad' in df.columns: ad_soyad = row['Ad Soyad']
                
                # GÖREV kolonu
                gorev = None
                if 'GÖREV' in df.columns: gorev = row['GÖREV']
                elif 'Görev' in df.columns: gorev = row['Görev']
                
                ad_soyad = str(ad_soyad).strip()
                if pd.isna(ad_soyad) or ad_soyad == 'nan' or not ad_soyad or ad_soyad == 'None':
                    continue
                    
                # İsim ayrıştırma
                parts = ad_soyad.split()
                if len(parts) >= 2:
                    first_name = " ".join(parts[:-1])
                    last_name = parts[-1]
                else:
                    first_name = ad_soyad
                    last_name = ""
                    
                # Username ve Email oluşturma
                tr_map = str.maketrans("ığüşöçİĞÜŞÖÇ ", "igusocIGUSOC.")
                username = ad_soyad.lower().translate(tr_map)
                email = f"{username}@kmf.com.tr"
                
                # Mükerrer kontrolü
                if User.query.filter_by(username=username).first():
                    username = f"{username}{index}"
                
                user = User(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    unvan=str(gorev) if gorev else "Personel",
                    is_active=True,
                    kurum_id=kurum_kmf.id
                )
                user.set_password("123456")
                user.roles.append(roles['Personel'])
                
                db.session.add(user)
                created_users.append(user)
                
            db.session.commit()
            print(f"✓ {len(created_users)} personel Excel'den yüklendi.")
            
        except Exception as e:
            print(f"!!! Excel Okuma Hatası: {e}")
            # Devam et, en azından manuel kullanıcı ekle

        # 5. STRATEJİ VE SÜREÇLER (SR4 ve SR6)
        
        # Ana Strateji
        ana_strat = AnaStrateji(
            ad="S1. Kurumsal Gelişimi Sağlamak",
            kod="S1",
            kurum_id=kurum_kmf.id,
            yil=2025
        )
        db.session.add(ana_strat)
        db.session.commit()
        
        # Alt Strateji
        alt_strat = AltStrateji(
            ad="S1.1 Pazarlama ve Satış Etkinliğini Artırmak",
            kod="S1.1",
            ana_strateji_id=ana_strat.id
        )
        db.session.add(alt_strat)
        db.session.commit()

        # Süreç Lideri Atamaları
        # Excel'den okunanlar varsa onları kullan, yoksa admin'i kullan
        lider1 = created_users[0] if len(created_users) > 0 else admin_user
        lider2 = created_users[1] if len(created_users) > 1 else admin_user
        
        # Lider rolü ver
        if roles['Süreç Lideri'] not in lider1.roles: lider1.roles.append(roles['Süreç Lideri'])
        if roles['Süreç Lideri'] not in lider2.roles: lider2.roles.append(roles['Süreç Lideri'])

        # SR4 Pazarlama Süreci
        sr4 = Surec(
            ad="Pazarlama Stratejileri Yönetimi",
            kod="SR4",
            aciklama="Pazarlama faaliyetlerinin planlanması ve yönetimi.",
            kurum_id=kurum_kmf.id,
            alt_strateji_id=alt_strat.id
        )
        sr4.liderler.append(lider1)
        sr4.uyeler.append(lider1)
        # 3 tane üye ekle
        for u in created_users[2:5]: 
            sr4.uyeler.append(u)
            
        db.session.add(sr4)
        
        # SR6 Danışmanlık Süreci
        sr6 = Surec(
            ad="Danışmanlık Hizmetleri Yönetimi",
            kod="SR6",
            aciklama="Müşteri danışmanlık projelerinin yönetimi.",
            kurum_id=kurum_kmf.id,
            alt_strateji_id=alt_strat.id
        )
        sr6.liderler.append(lider2)
        sr6.uyeler.append(lider2)
        # 3 tane üye ekle
        for u in created_users[5:8]: 
            sr6.uyeler.append(u)
            
        db.session.add(sr6)
        db.session.commit()
        
        print(f"✓ Süreçler oluşturuldu:\n  - SR4 (Lider: {lider1.first_name})\n  - SR6 (Lider: {lider2.first_name})")

        # 6. KPI'lar
        
        # SR4 KPI'ları
        pg1 = SurecPerformansGostergesi(
            surec_id=sr4.id,
            ad="Teklif Geri Dönüş Oranı",
            kodu="PG-4.1",
            hedef_deger="25",
            olcum_birimi="Yüzde",
            periyot="Aylık",
            gosterge_turu="İyileştirme",
            target_method="HK"
        )
        
        pg2 = SurecPerformansGostergesi(
            surec_id=sr4.id,
            ad="Yeni Kazanılan Müşteri Sayısı",
            kodu="PG-4.2",
            hedef_deger="50",
            olcum_birimi="Adet",
            periyot="Çeyreklik",
            gosterge_turu="İyileştirme",
            target_method="ÖHK"
        )

        # SR6 KPI'ları
        pg3 = SurecPerformansGostergesi(
            surec_id=sr6.id,
            ad="Müşteri Memnuniyet Skoru",
            kodu="PG-6.1",
            hedef_deger="4.5",
            olcum_birimi="Puan (5 Üzerinden)",
            periyot="Yıllık",
            gosterge_turu="Koruma",
            target_method="RG"
        )
        
        db.session.add_all([pg1, pg2, pg3])
        db.session.commit()
        
        print("✓ KPI'lar oluşturuldu.")
        
        # Kullanıcı bilgilerini bir dosyaya yaz (kolaylık olsun diye)
        with open("yenilenen_kullanicilar.txt", "w", encoding="utf-8") as f:
            f.write("=== YENİLENEN SİSTEM KULLANICILARI ===\n")
            f.write(f"Admin: admin / 123456\n")
            f.write(f"SR4 Lideri: {lider1.username} / 123456\n")
            f.write(f"SR6 Lideri: {lider2.username} / 123456\n\n")
            f.write("--- Personel Listesi ---\n")
            for u in created_users:
                f.write(f"{u.first_name} {u.last_name} ({u.username}) - {u.unvan}\n")
        
        print(f"✓ Kullanıcı listesi 'yenilenen_kullanicilar.txt' dosyasına kaydedildi.")

if __name__ == "__main__":
    seed_database()
