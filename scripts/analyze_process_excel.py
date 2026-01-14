
import pandas as pd
import sys

# Çıktıyı dosyaya yönlendir (Encoding sorunlarını aşmak için)
sys.stdout = open('excel_analysis_log.txt', 'w', encoding='utf-8')

file_path = r"c:\SPY_Cursor\SP_Code\belge\SR4 Pazarlama Stratejileri Yönetimi Süreç Karnesi.xlsx"
print(f"Analiz Edilen Dosya: {file_path}\n")

try:
    xls = pd.ExcelFile(file_path)
    print(f"Sayfalar: {xls.sheet_names}\n")
    
    for sheet in xls.sheet_names:
        print(f"--- SAYFA: {sheet} ---")
        # İlk 20 satırı oku
        df = pd.read_excel(xls, sheet_name=sheet, header=None, nrows=20)
        
        # Satır satır gez ve dolu hücreleri göster
        for idx, row in df.iterrows():
            dolu_hucreler = [f"Col{i}: {val}" for i, val in enumerate(row) if pd.notna(val)]
            if dolu_hucreler:
                print(f"Satır {idx}: { ' | '.join(dolu_hucreler) }")
        print("\n")

except Exception as e:
    print(f"HATA: {e}")
