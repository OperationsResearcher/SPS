
import sys
import os
import pandas as pd
from werkzeug.security import generate_password_hash

# Importlar
try:
    from __init__ import create_app, db
    from models.user import User, Kurum
    from models.user import Role # Eger varsa
except:
    pass

app = create_app()

def import_users():
    with app.app_context():
        print("Import Baslatiliyor...")
        
        kmf = Kurum.query.filter(Kurum.kisa_ad.like('%KMF%')).first()
        if not kmf:
            print("HATA: KMF kurumu bulunamadi.")
            return
            
        print(f"Hedef Kurum: {kmf.ticari_unvan}")
        
        excel_path = r"c:\SPY_Cursor\SP_Code\belge\PERSONEL LİSTESİ.xlsx"
        try:
            xls = pd.ExcelFile(excel_path)
            sheet_name = 'Personel'
            for s in xls.sheet_names:
                if 'personel' in s.lower():
                    sheet_name = s
                    break
            
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
            
            count = 0
            
            col_ad = next((c for c in df.columns if 'ad soyad' in str(c).lower()), None)
            col_gorev = next((c for c in df.columns if 'görev' in str(c).lower()), None)
            
            if col_ad:
                for index, row in df.iterrows():
                    ad_soyad = str(row[col_ad]).strip()
                    gorev = str(row[col_gorev]).strip() if col_gorev else "Personel"
                    
                    if pd.isna(ad_soyad) or ad_soyad in ['nan', 'None', '', '0']:
                        continue
                        
                    # İsim logic
                    parts = ad_soyad.split()
                    if len(parts) >= 2:
                        first_name = " ".join(parts[:-1])
                        last_name = parts[-1]
                    else:
                        first_name = ad_soyad
                        last_name = ""
                    
                    # Tr character map
                    tr_map = str.maketrans("ığüşöçİĞÜŞÖÇ ", "igusocIGUSOC.")
                    username = ad_soyad.lower().translate(tr_map)
                    email = f"{username}@kmf.com.tr"
                    
                    # Check existing
                    if User.query.filter_by(username=username).first():
                        print(f"Atlandi (Mevcut): {username}")
                        continue
                    
                    user = User(
                        username=username,
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                        title=gorev,
                        kurum_id=kmf.id,
                        sistem_rol="kurum_kullanici",
                        password_hash=generate_password_hash("123456")
                    )
                    db.session.add(user)
                    count += 1
                
                db.session.commit()
                print(f"Toplam {count} personel eklendi.")
            else:
                print("Kolon bulunamadi.")
                
        except Exception as e:
            print(f"HATA: {e}")

if __name__ == "__main__":
    import_users()
