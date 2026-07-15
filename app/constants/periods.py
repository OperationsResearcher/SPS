# -*- coding: utf-8 -*-
"""Dönem tipi (period_type) — kanonik küme ve normalizasyon (TASK-253).

SORUN (2026-07-15 ölçümü): `kpi_data.period_type` iki ayrı sözlük taşıyordu:
  - ASCII küçük harf : 'aylik' (365.925), 'ceyrek' (329), 'yillik' (260)
  - Türkçe büyük harf: 'Aylık' (202 — bulk_import_service default'u)
Kod bu dağınıklığa uyum sağlamıştı: `process_activity_service.py` her iki
yazımı ayrı ayrı kabul ediyor (`if period_type in ('aylik', 'aylık')`).
Sonuç: `GROUP BY period_type` aynı dönemi iki kovaya bölüyordu.

KARAR: Kanonik biçim **ASCII küçük harf** (DB'de %99,9 zaten böyle; JS de
bunu gönderiyor). Türkçe/büyük harfli girdiler yazma anında normalize edilir.

Yeni bir dönem tipi eklerken: PERIOD_TYPES'a ekle + _ESLEME'ye varyantlarını
yaz. Başka yerde literal 'aylik' yazma — buradan import et.
"""
from __future__ import annotations

# Kanonik değerler — DB'ye YALNIZ bunlar yazılır.
# Not: 'halfyear' JS'te üretiliyor (surec.js) ama DB'de henüz görülmedi;
# yine de kanonik kabul edilir, aksi halde çalışan giriş yolu kırılır.
PERIOD_TYPES: frozenset[str] = frozenset({
    "gunluk", "haftalik", "aylik", "ceyrek", "halfyear", "yillik",
})

# Varyant → kanonik. Türkçe karakterler, büyük harf ve eş anlamlılar.
_ESLEME: dict[str, str] = {
    "gunluk": "gunluk", "günlük": "gunluk",
    "haftalik": "haftalik", "haftalık": "haftalik",
    "aylik": "aylik", "aylık": "aylik",
    "ceyrek": "ceyrek", "çeyrek": "ceyrek",
    "ceyreklik": "ceyrek", "çeyreklik": "ceyrek",
    "halfyear": "halfyear", "yarim_yil": "halfyear", "yarıyıl": "halfyear",
    "yillik": "yillik", "yıllık": "yillik",
}


def normalize_period_type(value: str | None) -> str | None:
    """Serbest yazımı kanonik biçime çevirir; tanınmazsa DEĞİŞTİRMEDEN döner.

    Tanınmayanı zorla değiştirmiyoruz: sessizce yanlış kovaya atmaktansa
    ham hâliyle görünür kalsın (CHECK constraint yok — bkz. modül docstring'i).

    >>> normalize_period_type("Aylık")
    'aylik'
    >>> normalize_period_type("  ÇEYREKLİK ")
    'ceyrek'
    >>> normalize_period_type(None) is None
    True
    """
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    # Sadece lower(): Python'da 'AYLIK'.lower() → 'aylik' (ASCII i), 'Aylık'
    # → 'aylık' (Türkçe ı). İkisi FARKLI string; bu yüzden _ESLEME her iki
    # yazımı da anahtar olarak tutar. Elle 'I'→'ı' çevirmek (ilk denemede
    # yapılmıştı) 'AYLIK'ı 'aylık'a taşıyıp kuralı eşlemeye bağımlı kılıyor,
    # kazanç sağlamıyordu — kaldırıldı.
    return _ESLEME.get(s.lower(), s)
