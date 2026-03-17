
import sys
import os
import pandas as pd
from datetime import datetime

# Import sorunlarını aşmak için doğrudan kök dizinden çalışacak
from __init__ import create_app, db
from models.user import User, Role, Kurum
from models.process import Surec, SurecPerformansGostergesi, Faaliyet
from models.strategy import AnaStrateji, AltStrateji

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
            xls = pd.ExcelFile(excel_path)
            sheet_name = 'Personel'
            if 'Personel ' in xls.sheet_names:
                sheet_name = 'Personel '
            elif 'Personel' in xls.sheet_names:
                sheet_name = 'Personel'
            else:
                sheet_name = xls.sheet_names[0]
            
            print(f"Not: Excel'den '{sheet_name}' sayfası okunuyor...")
            
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
            
            for index, row in df.iterrows():
                # Kolon bulma
                col_ad = next((c for c in df.columns if 'ad soyad' in str(c).lower()), None)
                col_gorev = next((c for c in df.columns if 'görev' in str(c).lower()), None)
                
                if not col_ad: 
                    print("!!! 'AD SOYAD' kolonu bulunamadı.")
                    break
                    
                ad_soyad = str(row[col_ad]).strip()
                gorev = str(row[col_gorev]).strip() if col_gorev else "Personel"
                
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
                    
                # Username
                change_map = str.maketrans("ığüşöçİĞÜŞÖÇ ", "igusocIGUSOC.")
                username = ad_soyad.lower().translate(change_map)
                email = f"{username}@kmf.com.tr"
                
                # Mükerrer user
                if User.query.filter_by(username=username).first():
                    username = f"{username}{index}"
                
                user = User(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    unvan=gorev,
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
            print(f"!!! Excel Hatası: {e}")

        # 5. VERİLERİ OLUŞTUR
        # Ana Strateji
        ana_strat = AnaStrateji(
            ad="S1. Kurumsal Gelişim ve Sürdürülebilirlik",
            kod="S1",
            kurum_id=kurum_kmf.id,
            yil=2025
        )
        db.session.add(ana_strat)
        db.session.commit()
        
        # Alt Strateji
        alt_strat = AltStrateji(
            ad="S1.1 Hizmet Kalitesini Artırmak",
            kod="S1.1",
            ana_strateji_id=ana_strat.id
        )
        db.session.add(alt_strat)
        db.session.commit()

        # Liderler
        lider1 = created_users[0] if len(created_users) > 0 else admin_user
        lider2 = created_users[1] if len(created_users) > 1 else admin_user
        
        # Rolleri güncelle
        if roles['Süreç Lideri'] not in lider1.roles: lider1.roles.append(roles['Süreç Lideri'])
        if roles['Süreç Lideri'] not in lider2.roles: lider2.roles.append(roles['Süreç Lideri'])

        # SR4 Pazarlama
        sr4 = Surec(ad="Pazarlama ve İş Geliştirme", kod="SR4", kurum_id=kurum_kmf.id, alt_strateji_id=alt_strat.id)
        sr4.liderler.append(lider1)
        sr4.uyeler.append(lider1)
        db.session.add(sr4)
        
        # SR6 Danışmanlık
        sr6 = Surec(ad="Danışmanlık Hizmetleri", kod="SR6", kurum_id=kurum_kmf.id, alt_strateji_id=alt_strat.id)
        sr6.liderler.append(lider2)
        sr6.uyeler.append(lider2)
        db.session.add(sr6)
        db.session.commit()
        
        # KPIlar
        # ... (Önceki scriptteki gibi)
        pg1 = SurecPerformansGostergesi(surec_id=sr4.id, ad="Teklif Kabul Oranı", kodu="PG-4.1", hedef_deger="25", gosterge_turu="İyileştirme",target_method="HK", periyot="Aylık")
        pg2 = SurecPerformansGostergesi(surec_id=sr6.id, ad="Müşteri Memnuniyeti", kodu="PG-6.1", hedef_deger="4.5", gosterge_turu="Koruma", target_method="RG", periyot="Yıllık")
        
        db.session.add_all([pg1, pg2])
        db.session.commit()
        
        print("\n=== KURULUM BAŞARILI ===")
        print(f"SR4 Lideri: {lider1.username}")
        print(f"SR6 Lideri: {lider2.username}")

if __name__ == "__main__":
    seed_database()
