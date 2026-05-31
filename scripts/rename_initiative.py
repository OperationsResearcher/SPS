"""UI'da yalın 'Initiative' kelimesini 'Stratejik Girişim' yapar.
URL pathları (initiative-bubble), route adları (raporlar_initiative_*), data attributes ('initiative_id') KORUNUR.

Sadece tek başına geçen 'Initiative' / 'initiative' kelimesini değiştirir.
"""
import re
from pathlib import Path

ROOTS = [
    Path(r"c:\kokpitim\ui\templates\platform"),
    Path(r"c:\kokpitim\ui\static\platform\js"),
]

# Kelime sınırlı ama önünde/arkasında . - _ / olan teknik kullanımlardan kaçınılır
TEXT_PATTERNS = [
    # "Initiative" başlı (büyük harf) — display string
    (re.compile(r"(?<![\w.\-_/])Initiative(?![\w.\-_/])"), "Stratejik Girişim"),
    # "Initiative'ler" gibi takılı haller
    (re.compile(r"(?<![\w.\-_/])Initiative'(ler|in|i|ye|den|nin)"), r"Stratejik Girişim'\1"),
]

# Belirli string'ler için özel düzeltmeler (compound)
COMPOUND = [
    ("Initiative Portföy Bubble",   "Stratejik Girişim Portföyü Balon Grafiği"),
    ("Initiative Roadmap",          "Stratejik Girişim Yol Haritası"),
    ("Initiative Onay Zinciri",     "Stratejik Girişim Onay Zinciri"),
    ("Toplam Initiative",           "Toplam Stratejik Girişim"),
    ("Yeni Initiative",             "Yeni Stratejik Girişim"),
    ("Tamamlanan Initiative",       "Tamamlanan Stratejik Girişim"),
    ("En Büyük 5 Initiative",       "En Büyük 5 Stratejik Girişim"),
    ("Çok Yıllık Initiative",       "Çok Yıllık Stratejik Girişim"),
    ("Çok yıllık Initiative",       "Çok yıllık stratejik girişim"),
    ("Initiative bütçeleri",        "Stratejik girişim bütçeleri"),
    ("Initiative listesi",          "Stratejik girişim listesi"),
    ("Initiative yok",              "Stratejik girişim yok"),
    ("Initiative satırları",        "Stratejik girişim satırları"),
    ("Initiative satırı",           "Stratejik girişim satırı"),
    ("Girişim (Initiative)",        "Stratejik Girişim"),
]

changed = 0
for root in ROOTS:
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in (".html", ".js", ".css"):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        orig = text
        for needle, repl in COMPOUND:
            text = text.replace(needle, repl)
        # Sonra kelime sınırlı
        for pat, repl in TEXT_PATTERNS:
            text = pat.sub(repl, text)
        if text != orig:
            path.write_text(text, encoding="utf-8")
            changed += 1
            print(f"  {path.relative_to(Path('c:/kokpitim'))}")

print(f"\nToplam {changed} dosya değiştirildi.")
