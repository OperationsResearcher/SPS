
import sys
import os
import pandas as pd
from datetime import datetime
from werkzeug.security import generate_password_hash

# Import sorunlarını aşmak için doğrudan kök dizinden çalışacak
try:
    from __init__ import create_app, db
    from models.user import User, Kurum
    from models.process import Surec, SurecPerformansGostergesi
    from models.strategy import AnaStrateji, AltStrateji
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

app = create_app()

def seed_database():
    with app.app_context():
        print("!!! VERİTABANI SIFIRLANIYOR !!!")
        db.drop_all()
        db.create_all()
        print("✓ Tablolar yeniden oluşturuldu.")

        # 1. KURUMLAR
        kurum_sistem = Kurum(
            kisa_ad="Sistem", 
            ticari_unvan="Sistem Yönetimi",
            stratejik_durum='tamam'
        )
        kurum_kmf = Kurum(
            kisa_ad="KMF", 
            ticari_unvan="KMF Yönetim Danışmanlığı",
            stratejik_durum='tamam'
        )
        db.session.add_all([kurum_sistem, kurum_kmf])
        db.session.commit()
        print(f"✓ Kurumlar oluşturuldu.")

        # 2. SİSTEM ADMİNİ
        admin_user = User(
            username="admin", 
            email="admin@sistem.com", 
            first_name="Sistem", 
            last_name="Yöneticisi",
            is_active=True,
            kurum_id=kurum_sistem.id,
            sistem_rol="admin",
            password_hash=generate_password_hash("123456")
        )
        db.session.add(admin_user)
        db.session.commit()
        print("✓ Admin kullanıcısı oluşturuldu (admin / 123456)")

        # 4. PERSONEL LİSTESİNDEN KULLANICILARI YÜKLE
        excel_path = r"c:\SPY_Cursor\SP_Code\belge\PERSONEL LİSTESİ.xlsx"
        created_users = []
        
        try:
            xls = pd.ExcelFile(excel_path)
            # Sheet handling
            sheet_name = 'Personel'
            for s in xls.sheet_names:
                if 'personel' in s.lower():
                    sheet_name = s
                    break
            
            print(f"Not: Excel'den '{sheet_name}' sayfası okunuyor...")
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
            
            # Kolon bulma logic
            col_ad = next((c for c in df.columns if 'ad soyad' in str(c).lower()), None)
            col_gorev = next((c for c in df.columns if 'görev' in str(c).lower()), None)
            
            if col_ad:
                for index, row in df.iterrows():
                    ad_soyad = str(row[col_ad]).strip()
                    gorev = str(row[col_gorev]).strip() if col_gorev else "Personel"
                    
                    if pd.isna(ad_soyad) or ad_soyad in ['nan', 'None', '', '0']:
                        continue
                        
                    # İsim ayrıştırma
                    parts = ad_soyad.split()
                    if len(parts) >= 2:
                        first_name = " ".join(parts[:-1])
                        last_name = parts[-1]
                    else:
                        first_name = ad_soyad
                        last_name = ""
                    
                    # Username
                    tr_map = str.maketrans("ığüşöçİĞÜŞÖÇ ", "igusocIGUSOC.")
                    username = ad_soyad.lower().translate(tr_map)
                    email = f"{username}@kmf.com.tr"
                    
                    # Duplicate check
                    if User.query.filter_by(username=username).first():
                        username = f"{username}{index}"
                    
                    user = User(
                        username=username,
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                        title=gorev,  # Corrected attribute
                        is_active=True,
                        kurum_id=kurum_kmf.id,
                        sistem_rol="kurum_kullanici",
                        password_hash=generate_password_hash("123456")
                    )
                    db.session.add(user)
                    created_users.append(user)
                    
                db.session.commit()
                print(f"✓ {len(created_users)} personel Excel'den yüklendi.")
            else:
                print("!!! AD SOYAD kolonu bulunamadı.")
            
        except Exception as e:
            print(f"!!! Excel Hatası: {e}")

        # 5. VERİLERİ OLUŞTUR
        # Ana Strateji
        ana_strat = AnaStrateji(
            ad="S1. Kurumsal Gelişimi Sağlamak",
            code="S1",
            kurum_id=kurum_kmf.id
        )
        db.session.add(ana_strat)
        db.session.commit()
        
        # Alt Strateji
        alt_strat = AltStrateji(
            ad="S1.1 Pazarlama ve Satış Etkinliğini Artırmak",
            code="S1.1",
            ana_strateji_id=ana_strat.id
        )
        db.session.add(alt_strat)
        db.session.commit()

        # Liderler (İlk 2 kullanıcıyı lider yap)
        lider1 = created_users[0] if len(created_users) > 0 else admin_user
        lider2 = created_users[1] if len(created_users) > 1 else admin_user
        
        # Lider rollerini güncelle
        lider1.surec_rol = "surec_lideri"
        lider2.surec_rol = "surec_lideri"
        db.session.commit()

        # SR4 Pazarlama
        sr4 = Surec(
            ad="Pazarlama Stratejileri Yönetimi", 
            code="SR4",
            kurum_id=kurum_kmf.id 
        )
        
        # Many-To-Many ilişkiler
        sr4.liderler.append(lider1)
        sr4.uyeler.append(lider1)
        sr4.alt_stratejiler.append(alt_strat)
        
        if len(created_users) > 3:
            sr4.uyeler.extend(created_users[2:5])
            
        db.session.add(sr4)
        
        # SR6 Danışmanlık
        sr6 = Surec(
            ad="Danışmanlık Hizmetleri Yönetimi", 
            code="SR6", 
            kurum_id=kurum_kmf.id
        )
        sr6.liderler.append(lider2)
        sr6.uyeler.append(lider2)
        sr6.alt_stratejiler.append(alt_strat)
        
        if len(created_users) > 6:
            sr6.uyeler.extend(created_users[5:8])

        db.session.add(sr6)
        db.session.commit()
        
        # KPIlar
        # SR4
        pg1 = SurecPerformansGostergesi(surec_id=sr4.id, ad="Teklif Geri Dönüş Oranı", kodu="PG-4.1", hedef_deger="25", gosterge_turu="İyileştirme", target_method="HK", periyot="Aylık")
        pg2 = SurecPerformansGostergesi(surec_id=sr4.id, ad="Yeni Müşteri Sayısı", kodu="PG-4.2", hedef_deger="50", gosterge_turu="İyileştirme", target_method="ÖHK", periyot="Çeyreklik")
        
        # SR6
        pg3 = SurecPerformansGostergesi(surec_id=sr6.id, ad="Müşteri Memnuniyet Oranı", kodu="PG-6.1", hedef_deger="90", gosterge_turu="Koruma", target_method="RG", periyot="Yıllık")
        
        db.session.add_all([pg1, pg2, pg3])
        db.session.commit()
        
        print("\n=== KURULUM BAŞARILI ===")
        print(f"SR4 Lideri: {lider1.username}")
        print(f"SR6 Lideri: {lider2.username}")

        # Bilgi dosyası
        with open("yenilenen_kullanicilar.txt", "w", encoding="utf-8") as f:
            f.write("=== YENİLENEN SİSTEM KULLANICILARI ===\n")
            f.write(f"Admin: admin / 123456\n")
            f.write(f"SR4 Lideri: {lider1.username} / 123456\n")
            f.write(f"SR6 Lideri: {lider2.username} / 123456\n\n")
            f.write("--- Personel Listesi ---\n")
            for u in created_users:
                f.write(f"{u.first_name} {u.last_name} ({u.username}) - {u.title}\n")
                
if __name__ == "__main__":
    seed_database()
