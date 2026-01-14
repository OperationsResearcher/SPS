
import pandas as pd
import os

base_path = r"c:\SPY_Cursor\SP_Code\belge"
files = [
    "PERSONEL LİSTESİ.xlsx", 
    "SP VE SÜREÇ YAPISI.xlsx",
    "SR4 Pazarlama Stratejileri Yönetimi Süreç Karnesi.xlsx"
]

print("=== EXCEL SÜTUN ANALİZİ ===\n")

for f in files:
    full_path = os.path.join(base_path, f)
    if os.path.exists(full_path):
        print(f"--- DOSYA: {f} ---")
        try:
            # Sadece başlıkları okumaya çalışalım
            # Sheet isimlerini de görmek iyi olur
            xls = pd.ExcelFile(full_path)
            print(f"Sayfalar (Sheets): {xls.sheet_names}")
            
            for sheet in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet, nrows=2)
                print(f"  [Sheet: {sheet}] Kolonlar: {list(df.columns)}")
                # İlk satırı örnek veri olarak göster
                if not df.empty:
                    print(f"  [Sheet: {sheet}] Örnek Veri: {df.iloc[0].values.tolist()}")
            
        except Exception as e:
            print(f"  HATA: {e}")
    else:
        print(f"--- DOSYA BULUNAMADI: {f} ---")
    print("\n")
