# -*- coding: utf-8 -*-
"""UX-PLANI F / Faz 2.9: etiketsiz form alanı sayısı yalnız azalır (şablonlardaki statik alanlar).

Alan etiketli sayılır: aria-label/aria-labelledby, `<label for=id>`, ya da `<label>` sarmalı içinde.
"""
import re
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent / "ui" / "templates" / "platform"
ALAN = re.compile(r"<(input|select|textarea)\b([^>]*)>", re.S)
ATLA_TIP = re.compile(r'type="(hidden|checkbox|radio|submit|button)"')

# Yalnız küçülür. Yeni etiketsiz alan eklemek bu testi kırar; düzelttikçe sayıyı düşür.
BASELINE = 1  # karne.html yorum metnindeki "<select>" (yanlış pozitif); yalnız küçülür


def _etiketsiz_say() -> int:
    toplam = 0
    for f in KOK.rglob("*.html"):
        s = f.read_text(encoding="utf-8-sig")
        etiketler = set(re.findall(r'<label[^>]*\bfor="([^"]+)"', s))
        for m in ALAN.finditer(s):
            a = m.group(2)
            if ATLA_TIP.search(a) or "aria-label" in a:
                continue
            kimlik = re.search(r'\bid="([^"]+)"', a)
            if kimlik and kimlik.group(1) in etiketler:
                continue
            onceki = s[: m.start()]
            if onceki.rfind("<label") > onceki.rfind("</label>"):
                continue
            toplam += 1
    return toplam


def test_etiketsiz_alan_sayisi_artmadi():
    n = _etiketsiz_say()
    assert n <= BASELINE, f"Etiketsiz form alanı {n} > baseline {BASELINE}: aria-label veya <label for> ekle"
