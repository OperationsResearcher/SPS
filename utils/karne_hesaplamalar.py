# -*- coding: utf-8 -*-
"""
Süreç Karnesi Hesaplama Fonksiyonları
Excel formatına uygun başarı puanı ve ağırlıklı başarı puanı hesaplamaları
"""

import json
from typing import Optional, Dict, Any, Union, Tuple


def _normalize_basari_cell(v: Any) -> Tuple[Optional[str], Optional[str]]:
    """
    Tek bir puan hücresini çözümler.
    Eski: "0-40" veya 0-40
    Yeni: {"aralik": "0-40", "aciklama": "..."} (aciklama isteğe bağlı, kayıtta saklanır)
    """
    if v is None:
        return None, None
    if isinstance(v, dict):
        ar_raw = v.get("aralik")
        if ar_raw is None:
            ar_raw = v.get("range")
        ar = str(ar_raw).strip() if ar_raw is not None and str(ar_raw).strip() else None
        ac_raw = v.get("aciklama") or v.get("label") or v.get("description")
        ac = str(ac_raw).strip() if ac_raw is not None and str(ac_raw).strip() else None
        return ar, ac
    if isinstance(v, str):
        s = v.strip()
        return (s if s else None), None
    s = str(v).strip()
    return (s if s else None), None


def parse_basari_puani_araliklari(araliklar_str: Optional[str]) -> Dict[int, str]:
    """
    Başarı puanı aralıklarını JSON string'den dictionary'ye çevirir (yalnızca aralık metinleri).
    hesapla_basari_puani ile kullanım için geriye dönük uyumlu: hem eski string değerler hem
    {"aralik": "...", "aciklama": "..."} nesneleri desteklenir.

    Args:
        araliklar_str: JSON formatında string (örn: '{"1": "...", "2": "..."}')
                      veya list formatında (örn: '["...", "...", ...]')

    Returns:
        Dictionary: {1: "0-40", 2: "40-60", ...} — sadece aralık string'leri
    """
    if not araliklar_str:
        return {}

    try:
        araliklar = json.loads(araliklar_str)

        if isinstance(araliklar, list):
            out: Dict[int, str] = {}
            for i, v in enumerate(araliklar):
                ar, _ = _normalize_basari_cell(v)
                if ar:
                    out[i + 1] = ar
            return out

        if isinstance(araliklar, dict):
            out = {}
            for k, v in araliklar.items():
                try:
                    ki = int(k)
                except (ValueError, TypeError):
                    continue
                ar, _ = _normalize_basari_cell(v)
                if ar:
                    out[ki] = ar
            return out

        return {}
    except (json.JSONDecodeError, ValueError, TypeError):
        return {}


def _coerce_aralik_str_for_hesap(v: Any) -> Optional[str]:
    """hesapla_basari_puani içinde ham dict/string kabul eder."""
    ar, _ = _normalize_basari_cell(v)
    return ar


def parse_aralik_degeri(aralik_str: str) -> Optional[tuple]:
    """
    Aralık string'ini parse eder (örn: "40-49", "%80-89", "400.000-449.000")
    
    Args:
        aralik_str: Aralık string'i
    
    Returns:
        Tuple: (min_deger, max_deger) veya None
    """
    if not aralik_str or aralik_str.strip() == '-' or aralik_str.strip() == '':
        return None
    
    # String'i temizle (%, TL, vb. karakterleri kaldır)
    temiz_str = aralik_str.strip().replace('%', '').replace('TL', '').replace(',', '').replace('.', '').strip()
    
    # Negatif işareti kontrol et (örn: "-39")
    if temiz_str.startswith('-'):
        # Sadece negatif bir değer varsa
        try:
            deger = float(temiz_str)
            return (deger, None)  # Minimum değer, maksimum yok
        except ValueError:
            return None
    
    # Aralık olup olmadığını kontrol et (örn: "40-49")
    if '-' in temiz_str:
        parts = temiz_str.split('-')
        if len(parts) == 2:
            try:
                min_val = float(parts[0].strip())
                max_val_str = parts[1].strip()
                if max_val_str:
                    max_val = float(max_val_str)
                    return (min_val, max_val)
                else:
                    return (min_val, None)
            except ValueError:
                return None
    
    # Tek bir değer (örn: "50", "0.95")
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
        # Sadece minimum değer var (örn: >= 40)
        return deger >= min_val
    
    # Min ve max değer var (örn: 40 <= deger <= 49)
    return min_val <= deger <= max_val


def hesapla_basari_puani(
    gerceklesen_deger: Optional[Union[int, float]],
    basari_puani_araliklari: Optional[Dict[int, Any]],
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
    
    # Aralıkları parse et ve puan sırasına göre sırala
    aralik_puan_ciftleri = []
    for puan, raw in basari_puani_araliklari.items():
        aralik_str = _coerce_aralik_str_for_hesap(raw)
        if aralik_str is None:
            continue
        aralik = parse_aralik_degeri(aralik_str)
        if aralik is not None:
            aralik_puan_ciftleri.append((puan, aralik))
    
    if not aralik_puan_ciftleri:
        return None
    
    # Direction'a göre sırala
    # Increasing ise: 1 puan en düşük, 5 puan en yüksek
    # Decreasing ise: 1 puan en yüksek, 5 puan en düşük
    if direction == 'Decreasing':
        # Decreasing için ters sırala (5'ten 1'e)
        aralik_puan_ciftleri.sort(key=lambda x: x[0], reverse=True)
    else:
        # Increasing için normal sırala (1'den 5'e)
        aralik_puan_ciftleri.sort(key=lambda x: x[0])
    
    # Değerin hangi aralıkta olduğunu bul
    for puan, aralik in aralik_puan_ciftleri:
        if deger_aralikta_mi(gerceklesen, aralik):
            return puan
    
    # Eğer hiçbir aralığa uymuyorsa, en yakın aralığı bul
    # Direction'a göre en düşük veya en yüksek puanı ver
    if direction == 'Decreasing':
        # Değer tüm aralıkların üzerinde ise 1 puan (en kötü)
        # Değer tüm aralıkların altında ise 5 puan (en iyi)
        # Bu durumda en yüksek puanlı aralığın max'ını kontrol et
        if aralik_puan_ciftleri:
            _, (min_val, max_val) = aralik_puan_ciftleri[-1]
            if max_val is not None and gerceklesen > max_val:
                return 1  # En kötü puan
            elif gerceklesen < min_val:
                return 5  # En iyi puan
    else:  # Increasing
        # Değer tüm aralıkların üzerinde ise 5 puan (en iyi)
        # Değer tüm aralıkların altında ise 1 puan (en kötü)
        if aralik_puan_ciftleri:
            _, (min_val, _) = aralik_puan_ciftleri[0]
            _, (_, max_val) = aralik_puan_ciftleri[-1]
            if max_val is not None and gerceklesen > max_val:
                return 5  # En iyi puan
            elif gerceklesen < min_val:
                return 1  # En kötü puan
    
    # Varsayılan olarak orta puan (3)
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
        # Ağırlığı normalize et (0-100 ise 0-1'e çevir)
        if agirlik > 1:
            agirlik_normalized = agirlik / 100.0
        else:
            agirlik_normalized = float(agirlik)
        
        return float(basari_puani) * agirlik_normalized
    except (ValueError, TypeError):
        return None


def hesapla_onceki_yil_ortalamasi(
    surec_pg_id: int,
    mevcut_yil: int,
    gerceklesen_degerler: list
) -> Optional[float]:
    """
    Önceki yıl ortalamasını hesaplar veya veritabanından alır
    
    Args:
        surec_pg_id: Performans göstergesi ID
        mevcut_yil: Mevcut yıl
        gerceklesen_degerler: Önceki yılın gerçekleşen değerleri listesi
    
    Returns:
        float: Önceki yıl ortalaması veya None
    """
    if not gerceklesen_degerler:
        return None
    
    try:
        # Liste içindeki numeric değerleri filtrele
        numeric_degerler = []
        for deger in gerceklesen_degerler:
            try:
                numeric_degerler.append(float(deger))
            except (ValueError, TypeError):
                continue
        
        if not numeric_degerler:
            return None
        
        # Ortalamayı hesapla
        return sum(numeric_degerler) / len(numeric_degerler)
    except Exception:
        return None



