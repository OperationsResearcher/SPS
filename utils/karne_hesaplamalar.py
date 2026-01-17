# -*- coding: utf-8 -*-
"""
Süreç Karnesi Hesaplama Fonksiyonları
Excel formatına uygun başarı puanı ve ağırlıklı başarı puanı hesaplamaları
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
        
        # Eğer list ise, index+1'i key olarak kullan
        if isinstance(araliklar, list):
            return {i+1: v for i, v in enumerate(araliklar) if v}
        
        # Eğer dict ise, key'leri int'e çevir
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
    
    # Aralıkları parse et ve puan sırasına göre sırala
    aralik_puan_ciftleri = []
    for puan, aralik_str in basari_puani_araliklari.items():
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



