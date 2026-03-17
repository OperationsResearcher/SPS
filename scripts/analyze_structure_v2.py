
import pandas as pd

file_path = r"c:\SPY_Cursor\SP_Code\belge\SP VE SÜREÇ YAPISI.xlsx"

try:
    df = pd.read_excel(file_path, sheet_name='KMF Stratejiler', nrows=0)
    print(f"KMF Stratejiler Kolonlar: {list(df.columns)}")
    
    # PI VE (KPI?) sayfasına da bakalım
    xls = pd.ExcelFile(file_path)
    if 'PI VE' in xls.sheet_names: # Tam ismini bilmiyorum, startswith bakmalıydım ama yukarıda PI VE gördüm
        pass 
        
    # Sayfa isimlerini tekrar net alalım
    print(f"Sayfalar: {xls.sheet_names}")
    
    # KPI sayfası muhtemelen 'Performans Göstergeleri' veya benzeri
    for s in xls.sheet_names:
        if 'Performans' in s or 'Gösterge' in s or 'PI' in s:
            df2 = pd.read_excel(file_path, sheet_name=s, nrows=0)
            print(f"[{s}] Kolonlar: {list(df2.columns)}")

except Exception as e:
    print(e)
