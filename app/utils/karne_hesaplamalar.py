# -*- coding: utf-8 -*-
"""
Süreç Karnesi Hesaplama Fonksiyonları
Excel formatına uygun başarı puanı ve ağırlıklı başarı puanı hesaplamaları.
Eski proje uyumluluğu için taşınmıştır.
"""
import json
import logging
from typing import Optional, Dict, Any, Union, Tuple, List

_log = logging.getLogger(__name__)

# JS tarafının (pg_tablo_modal.js, surec.js) ürettiği bant formatının anahtarları.
# ÖLÇÜM 2026-07-21: process_kpis'te 1920 dolu kayıt →
#   1240  [{"min":…, "max":…, "puan":…}, …]   ← bu format
#    657  {"1":"%71-80", …}                    ← eski, string
#     23  {"1":{"aralik":…,"aciklama":…}, …}   ← eski, nesne
# Yeni format kayıtların %64,6'sı; parser'da karşılığı olmadığı için hepsi
# sessizce puansız kalıyordu (M1).
_BANT_ANAHTARLARI = ("min", "max", "puan")


def _bant_listesi_mi(j: Any) -> bool:
    """JS'in ürettiği [{"min":…,"max":…,"puan":…}] biçimi mi?"""
    return (
        isinstance(j, list)
        and bool(j)
        and isinstance(j[0], dict)
        and any(k in j[0] for k in _BANT_ANAHTARLARI)
    )


def parse_bant_listesi(araliklar_str: Optional[str]) -> List[Dict[str, Any]]:
    """JS bant formatını (min/max/puan) normalize edilmiş listeye çevirir.

    Eski formattan farkı: puan bandın İÇİNDE taşınıyor (0-100 ölçeği) ve
    sınırlar zaten sayısal — string aralık ayrıştırmasına gerek yok.
    `max: null` üst sınırsız (sonsuza kadar) demektir.
    """
    if not araliklar_str:
        return []
    try:
        j = json.loads(araliklar_str)
    except (json.JSONDecodeError, ValueError, TypeError):
        return []
    if not _bant_listesi_mi(j):
        return []

    bantlar: List[Dict[str, Any]] = []
    for item in j:
        if not isinstance(item, dict):
            continue
        try:
            puan = item.get("puan")
            if puan is None:
                continue
            alt = item.get("min")
            ust = item.get("max")
            bantlar.append({
                "min": None if alt is None else float(alt),
                "max": None if ust is None else float(ust),
                "puan": float(puan),
            })
        except (ValueError, TypeError):
            continue
    return bantlar


def hesapla_bant_puani(
    gerceklesen_deger: Optional[Union[int, float]],
    bantlar: List[Dict[str, Any]],
) -> Optional[float]:
    """Bant listesine göre puan döndürür (bandın kendi ölçeğinde, tipik 0-100).

    Bantlar üst üste binerse en yüksek puanlı eşleşme kazanır — kullanıcı
    lehine yorum. Hiçbir banda düşmüyorsa None (uydurma puan üretmeyiz).
    """
    if gerceklesen_deger is None or not bantlar:
        return None
    try:
        deger = float(gerceklesen_deger)
    except (ValueError, TypeError):
        return None

    eslesen = [
        b["puan"] for b in bantlar
        if (b["min"] is None or deger >= b["min"])
        and (b["max"] is None or deger <= b["max"])
    ]
    return max(eslesen) if eslesen else None


def _normalize_basari_cell(v: Any) -> Tuple[Optional[str], Optional[str]]:
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
    JSON'dan yalnızca aralık string'lerini döndürür (hesaplama için).
    Değerler string veya {"aralik": "...", "aciklama": "..."} olabilir.
    """
    if not araliklar_str:
        return {}

    try:
        araliklar = json.loads(araliklar_str)

        # Yeni bant formatı bu fonksiyonun sözleşmesine (puan→aralık string)
        # sığmıyor: puan bandın içinde ve 0-100 ölçeğinde. Çağıran
        # hesapla_basari_puani zaten bantlı yola sapıyor; buraya düşmesi
        # çağıranın formatı kontrol etmediği anlamına gelir — sessiz kalma.
        if _bant_listesi_mi(araliklar):
            _log.warning(
                "[karne_hesaplamalar] bant formatı (min/max/puan) eski parser'a "
                "verildi; parse_bant_listesi kullanılmalı. Kayıt: %.120s",
                araliklar_str,
            )
            return {}

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
    if not aralik_str or aralik_str.strip() in ('-', ''):
        return None

    # Türkçe sayı biçimi: '.' binlik ayraç, ',' ondalık ayraç.
    # Binlik noktalarını kaldır, ondalık virgülünü standart noktaya çevir.
    # (Önceki sürüm hem ',' hem '.' siliyordu → "4,5"/"4.5" gibi ondalık aralık
    #  sınırları "45"e dönüşüp yanlış başarı puanı veriyordu.)
    temiz_str = (
        aralik_str.strip()
        .replace('%', '')
        .replace('TL', '')
        .replace('.', '')
        .replace(',', '.')
        .strip()
    )

    # İki-sayılı aralık (negatif sınırlar dahil): "-50--10", "-10-5", "4.5-9.5", "40-49".
    # Önceki split-tabanlı mantık negatif alt sınırlı aralıkları parse edemiyordu.
    import re as _re
    _m = _re.match(r'^(-?\d+\.?\d*)\s*-\s*(-?\d+\.?\d*)$', temiz_str)
    if _m:
        try:
            return (float(_m.group(1)), float(_m.group(2)))
        except ValueError:
            return None

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


def hesapla_basari_puani_ham(
    gerceklesen_deger: Optional[Union[int, float]],
    araliklar_str: Optional[str],
    direction: str = 'Increasing',
) -> Tuple[Optional[float], Optional[str]]:
    """DB'deki ham `basari_puani_araliklari` string'inden puan üretir.

    İki formatı da tanır ve hangisini kullandığını söyler — çağıranın format
    bilmesine gerek kalmaz. M1'in kök nedeni tam olarak buydu: çağıranlar
    tek formatı varsayıyordu.

    Returns:
        (puan, olcek) — olcek: '0-100' (bant formatı) | '1-5' (eski) | None
        Puan üretilemezse (None, None) ve sebebi log'a düşer.
    """
    if gerceklesen_deger is None:
        return None, None
    if not araliklar_str or not str(araliklar_str).strip():
        return None, None

    bantlar = parse_bant_listesi(araliklar_str)
    if bantlar:
        puan = hesapla_bant_puani(gerceklesen_deger, bantlar)
        if puan is None:
            _log.warning(
                "[karne_hesaplamalar] değer %s tanımlı %d bandın hiçbirine "
                "düşmedi — puan üretilemedi.", gerceklesen_deger, len(bantlar),
            )
            return None, None
        return puan, '0-100'

    araliklar = parse_basari_puani_araliklari(araliklar_str)
    if not araliklar:
        _log.warning(
            "[karne_hesaplamalar] başarı aralığı çözümlenemedi (kayıt dolu ama "
            "parse boş döndü). Kayıt: %.120s", araliklar_str,
        )
        return None, None

    puan = hesapla_basari_puani(gerceklesen_deger, araliklar, direction)
    return (float(puan) if puan is not None else None), ('1-5' if puan is not None else None)


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
