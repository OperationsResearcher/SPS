
import os
import pandas as pd
from docx import Document
from pypdf import PdfReader
import sys

# Encoding fix
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

DOCS_DIR = r"c:\SPY_Cursor\SP_Code\belge"

def analyze_docx(filename):
    path = os.path.join(DOCS_DIR, filename)
    print(f"\n{'='*20} ANALIZ: {filename} {'='*20}")
    try:
        doc = Document(path)
        print("--- BAŞLIKLAR VE ÖNEMLİ METİNLER ---")
        for para in doc.paragraphs:
            if para.style.name.startswith('Heading') or (para.runs and para.runs[0].bold):
                text = para.text.strip()
                if text:
                    print(f"[{para.style.name}] {text}")
            # Ayrıca normal paragrafların da ilk cümlesini alalım ki bağlamı anlayalım
            elif para.text.strip():
                 print(f"[Text] {para.text.strip()[:100]}...")
    except Exception as e:
        print(f"HATA: {e}")

def analyze_excel(filename):
    path = os.path.join(DOCS_DIR, filename)
    print(f"\n{'='*20} ANALIZ: {filename} {'='*20}")
    try:
        xl = pd.ExcelFile(path)
        print(f"Sayfalar: {xl.sheet_names}")
        
        for sheet in xl.sheet_names:
            print(f"\n--- SHEET: {sheet} ---")
            df = pd.read_excel(path, sheet_name=sheet, nrows=5)
            print("Kolonlar:", list(df.columns))
            print("Örnek Veri (İlk Satır):")
            if not df.empty:
                print(df.iloc[0].to_dict())
    except Exception as e:
        print(f"HATA: {e}")

def analyze_pdf(filename):
    path = os.path.join(DOCS_DIR, filename)
    print(f"\n{'='*20} ANALIZ: {filename} {'='*20}")
    try:
        reader = PdfReader(path)
        print(f"Sayfa Sayısı: {len(reader.pages)}")
        print("--- İÇERİK ÖZETİ (İlk Sayfa) ---")
        text = reader.pages[0].extract_text()
        print(text[:1000])
    except Exception as e:
        print(f"HATA: {e}")


        
if __name__ == "__main__":
    files = os.listdir(DOCS_DIR)
    
    with open("analysis_report.md", "w", encoding="utf-8") as f:
        # Print fonksiyonunu override et veya f.write kullan
        original_print = print
        def print(*args, **kwargs):
            f.write(" ".join(map(str, args)) + "\n")
            
        try:
            for file in files:
                if file.endswith(".docx"):
                    analyze_docx(file)
                elif file.endswith(".xlsx"):
                    analyze_excel(file)
                elif file.endswith(".pdf"):
                    analyze_pdf(file)
        finally:
            # Geri yükle (gerekirse)
            pass

