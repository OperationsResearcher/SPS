# -*- coding: utf-8 -*-
"""Süreç Karnesi Hesaplama Fonksiyonları — GERİYE UYUM KABUĞU (shim).

⚠ BU DOSYADA MANTIK YOKTUR. Tek gerçek kaynak: `app/utils/karne_hesaplamalar.py`.

NEDEN BÖYLE (B2 · 2026-07-21):
    Bu dosya uzun süre bağımsız bir ikinci kopyaydı ve ondalık ayrıştırma
    hatası yalnız BURADA duruyordu:

        girdi        bu kopya (eski)   app/utils (doğru)
        "4,5-9,5"    (45.0, 95.0) ❌   (4.5, 9.5) ✅
        "3-3,99"     (3.0, 399.0) ❌   (3.0, 3.99) ✅
        "-50--10"    None         ❌   (-50.0, -10.0) ✅

    9 üretim dosyası bu kopyayı, 6 test dosyasının tamamı diğerini kullanıyordu
    → testler yeşil kalırken üretim 10-100 kat yanlış hesaplıyordu.

    İki kopyayı birleştirmek yerine import'ları tek tek değiştirmek aynı
    ayrışmayı yeniden üretirdi. Bu yüzden dosya kabuğa indirildi: eski
    `from utils.karne_hesaplamalar import ...` satırları çalışmaya devam eder
    ama artık doğru uygulamaya gider.

YENİ KOD YAZARKEN doğrudan `app.utils.karne_hesaplamalar`'ı import edin.
"""
from typing import Optional

from app.utils.karne_hesaplamalar import (  # noqa: F401
    _coerce_aralik_str_for_hesap,
    _normalize_basari_cell,
    deger_aralikta_mi,
    hesapla_agirlikli_basari_puani,
    hesapla_bant_puani,
    hesapla_basari_puani,
    hesapla_basari_puani_ham,
    parse_aralik_degeri,
    parse_bant_listesi,
    parse_basari_puani_araliklari,
)
from app.utils.karne_hesaplamalar import (
    hesapla_onceki_yil_ortalamasi as _onceki_yil_ortalamasi,
)

__all__ = [
    "parse_basari_puani_araliklari",
    "parse_aralik_degeri",
    "parse_bant_listesi",
    "deger_aralikta_mi",
    "hesapla_basari_puani",
    "hesapla_basari_puani_ham",
    "hesapla_bant_puani",
    "hesapla_agirlikli_basari_puani",
    "hesapla_onceki_yil_ortalamasi",
]


def hesapla_onceki_yil_ortalamasi(*args) -> Optional[float]:
    """Önceki yıl ortalaması — İKİ imzayı da kabul eder.

    Bu kopyanın imzası `(surec_pg_id, mevcut_yil, gerceklesen_degerler)` idi;
    doğru uygulamada ilk iki parametre hiç kullanılmadığı için kaldırılmıştı.
    Kabuk her ikisini de kabul eder, yoksa eski çağrı `TypeError` verirdi.
    """
    if len(args) == 3:
        gerceklesen_degerler = args[2]
    elif len(args) == 1:
        gerceklesen_degerler = args[0]
    else:
        raise TypeError(
            "hesapla_onceki_yil_ortalamasi() 1 veya 3 konumsal argüman alır, "
            f"{len(args)} verildi"
        )
    return _onceki_yil_ortalamasi(gerceklesen_degerler)
