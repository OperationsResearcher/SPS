
import pandas as pd
import os

file_path = r"c:\SPY_Cursor\SP_Code\belge\SP VE SÜREÇ YAPISI.xlsx"

print("=== SP VE SÜREÇ YAPISI ANALİZİ ===\n")

try:
    xls = pd.ExcelFile(file_path)
    print(f"Sayfalar: {xls.sheet_names}")
    
    for sheet in xls.sheet_names:
        print(f"\n--- Sheet: {sheet} ---")
        # İlk 5 satırı oku, belki başlıklar ilk satırda değildir
        df = pd.read_excel(xls, sheet_name=sheet, nrows=5)
        print(df.to_string())
        
except Exception as e:
    print(f"HATA: {e}")
