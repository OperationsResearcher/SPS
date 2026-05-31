"""Tüm raporlar/*.html sayfalarındaki 'Raporlara Dön' anchor butonunu kaldırır.

İki tipik kalıp:
  A) Tek satır anchor + arkasından '</div>' kapanışı
  B) Birden fazla satıra yayılmış anchor

Regex ile <a ...> 'Raporlara Dön' </a> bloğunu (varsa fa ikonuyla birlikte) tekil olarak siler.
"""
import os
import re
from pathlib import Path

RAPORLAR_DIR = Path(r"c:\kokpitim\ui\templates\platform\raporlar")
PATTERN = re.compile(
    r'\s*<a [^>]*href=\"\{\{ url_for\(\'app_bp\.raporlar_index\'\) \}\}\"[^>]*>\s*'
    r'(?:<i[^>]*></i>\s*)?'
    r'Raporlara Dön\s*</a>\s*',
    re.IGNORECASE,
)

changed = 0
for path in sorted(RAPORLAR_DIR.glob("*.html")):
    text = path.read_text(encoding="utf-8")
    new_text, n = PATTERN.subn("\n    ", text)
    if n:
        path.write_text(new_text, encoding="utf-8")
        print(f"  {path.name}: {n} bloğu kaldırıldı")
        changed += 1

print(f"Toplam {changed} dosya değişti.")
