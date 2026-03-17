# -*- coding: utf-8 -*-
"""
Süreç Karnesi Hesaplama Fonksiyonları
Excel formatına uygun başarı puanı ve ağırlıklı başarı puanı hesaplamaları.
Eski proje uyumluluğu için taşınmıştır.
"""
import json
from typing import Optional, Dict, Any, Union


def parse_basari_puani_araliklari(araliklar_str: Optional[str]) -> Dict[int, str]:
    """
    Başarı puanı aralıklarını JSON string'den dictionary'ye çevirir

    Args:
        araliklar_str: JSON formatında string (örn: '{"1": "...", "2": "..."}')
                      veya list formatında (örn: '["...", "...", "...", "...", "..."]')

    Returns:
        Dictionary: {1: "...", 2: "...", 3: "...", 4: "...", 5: "..."}
    """
    if not araliklar_str:
        return {}

    try:
        araliklar = json.loads(araliklar_str)

        if isinstance(araliklar, list):
            return {i + 1: v for i, v in enumerate(araliklar) if v}

        if isinstance(araliklar, dict):
            return {int(k): v for k, v in araliklar.items()}

        return {}
    except (json.JSONDecodeError, ValueError, TypeError):
        return {}


def parse_aralik_degeri(aralik_str: str) -> Optional[tuple]:
    """
    Aralık string'ini parse eder (örn: "40-49", "%80-89", "400.000-449.000")

    Args:
        aralik_str: Aralık string'i

    Returns:
        Tuple: (min_deger, max_deger) veya None
    """
    if not aralik_str or aralik_str.strip() in ('-', ''):
        return None

    temiz_str = (
        aralik_str.strip()
        .replace('%', '')
        .replace('TL', '')
        .replace(',', '')
        .replace('.', '')
        .strip()
    )

    if temiz_str.startswith('-'):
        try:
            deger = float(temiz_str)
            return (deger, None)
        except ValueError:
            return None

    if '-' in temiz_str:
        parts = temiz_str.split('-')
        if len(parts) == 2:
            try:
                min_val = float(parts[0].strip())
                max_val_str = parts[1].strip()
                if max_val_str:
                    max_val = float(max_val_str)
                    return (min_val, max_val)
                return (min_val, None)
            except ValueError:
                return None

    try:
        deger = float(temiz_str)
        return (deger, deger)
    except ValueError:
        return None


def deger_aralikta_mi(deger: Union[int, float], aralik: Optional[tuple]) -> bool:
    """
    Değerin belirtilen aralıkta olup olmadığını kontrol eder

    Args:
        deger: Kontrol edilecek değer
        aralik: (min, max) tuple veya None

    Returns:
        bool: Değer aralıkta ise True
    """
    if aralik is None:
        return False

    min_val, max_val = aralik

    if max_val is None:
        return deger >= min_val

    return min_val <= deger <= max_val


def hesapla_basari_puani(
    gerceklesen_deger: Optional[Union[int, float]],
    basari_puani_araliklari: Optional[Dict[int, str]],
    direction: str = 'Increasing'
) -> Optional[int]:
    """
    Gerçekleşen değere göre başarı puanını hesaplar (1-5 arası)

    Args:
        gerceklesen_deger: Gerçekleşen değer
        basari_puani_araliklari: Başarı puanı aralıkları dictionary'si {1: "...", 2: "...", ...}
        direction: 'Increasing' (arttırmak iyi) veya 'Decreasing' (azaltmak iyi)

    Returns:
        int: Başarı puanı (1-5) veya None
    """
    if gerceklesen_deger is None:
        return None

    if not basari_puani_araliklari or len(basari_puani_araliklari) == 0:
        return None

    try:
        gerceklesen = float(gerceklesen_deger)
    except (ValueError, TypeError):
        return None

    aralik_puan_ciftleri = []
    for puan, aralik_str in basari_puani_araliklari.items():
        aralik = parse_aralik_degeri(aralik_str)
        if aralik is not None:
            aralik_puan_ciftleri.append((puan, aralik))

    if not aralik_puan_ciftleri:
        return None

    if direction == 'Decreasing':
        aralik_puan_ciftleri.sort(key=lambda x: x[0], reverse=True)
    else:
        aralik_puan_ciftleri.sort(key=lambda x: x[0])

    for puan, aralik in aralik_puan_ciftleri:
        if deger_aralikta_mi(gerceklesen, aralik):
            return puan

    if direction == 'Decreasing':
        if aralik_puan_ciftleri:
            _, (min_val, max_val) = aralik_puan_ciftleri[-1]
            if max_val is not None and gerceklesen > max_val:
                return 1
            if gerceklesen < min_val:
                return 5
    else:
        if aralik_puan_ciftleri:
            _, (min_val, _) = aralik_puan_ciftleri[0]
            _, (_, max_val) = aralik_puan_ciftleri[-1]
            if max_val is not None and gerceklesen > max_val:
                return 5
            if gerceklesen < min_val:
                return 1

    return 3


def hesapla_agirlikli_basari_puani(
    basari_puani: Optional[int],
    agirlik: Optional[Union[int, float]]
) -> Optional[float]:
    """
    Ağırlıklı başarı puanını hesaplar (Ağırlık × Başarı Puanı)

    Args:
        basari_puani: Başarı puanı (1-5)
        agirlik: Ağırlık (0-1 arası float veya 0-100 arası integer)

    Returns:
        float: Ağırlıklı başarı puanı veya None
    """
    if basari_puani is None or agirlik is None:
        return None

    try:
        if agirlik > 1:
            agirlik_normalized = agirlik / 100.0
        else:
            agirlik_normalized = float(agirlik)

        return float(basari_puani) * agirlik_normalized
    except (ValueError, TypeError):
        return None


def hesapla_onceki_yil_ortalamasi(
    gerceklesen_degerler: list
) -> Optional[float]:
    """
    Önceki yıl ortalamasını gerçekleşen değerlerden hesaplar

    Args:
        gerceklesen_degerler: Gerçekleşen değerler listesi

    Returns:
        float: Ortalama veya None
    """
    if not gerceklesen_degerler:
        return None

    try:
        numeric_degerler = []
        for deger in gerceklesen_degerler:
            try:
                numeric_degerler.append(float(deger))
            except (ValueError, TypeError):
                continue

        if not numeric_degerler:
            return None

        return sum(numeric_degerler) / len(numeric_degerler)
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"[karne_hesaplamalar] onceki_yil_ortalamasi hatası: {e}", exc_info=True)
        return None
