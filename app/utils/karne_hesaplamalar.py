# -*- coding: utf-8 -*-
"""
Süreç Karnesi Hesaplama Fonksiyonları
Excel formatına uygun başarı puanı ve ağırlıklı başarı puanı hesaplamaları.
Eski proje uyumluluğu için taşınmıştır.
"""
import json
import logging
import re
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


def _sayi_tr(x: str) -> float:
    """Türkçe sayı: '.' + tam 3 hane = binlik ('400.000'), aksi halde ondalık ('4.5').

    ',' her zaman ondalık ayraçtır. Önceki sürüm TÜM noktaları siliyordu:
    "4.5-9.5" → (45, 95) (HATA-07)."""
    x = x.strip()
    if re.fullmatch(r"-?\d{1,3}(\.\d{3})+(,\d+)?", x):
        x = x.replace(".", "")
    return float(x.replace(",", "."))


_RE_TEK_SINIR_ONDE = re.compile(r"^-\s*(\d[\d.,]*)$")     # "-4"   (tek sayı, önde tire)
_RE_TEK_SINIR_SONDA = re.compile(r"^(\d[\d.,]*)\s*[-+]$")  # "20-", "20+"
_RE_IKI_SINIR = re.compile(r"^(-?\d[\d.,]*)\s*-\s*(-?\d[\d.,]*)$")


def _aralik_coz(aralik_str: str):
    """Ham çözümleme. Dönüş: None | ('acik', N, onde_tire) | ('kapali', lo, hi).

    'acik' = tek sınırlı bant ("-4", "79-", "20+"). Yönünü bandın KONUMU belirler
    (bkz. bantlari_coz); ham parse_aralik_degeri eski davranışı korur."""
    if not aralik_str or aralik_str.strip() in ("-", ""):
        return None
    t = aralik_str.strip().replace("%", "").replace("TL", "").strip()
    if not t or t == "-":
        return None
    try:
        m = _RE_TEK_SINIR_ONDE.match(t)
        if m:
            return ("acik", _sayi_tr(m.group(1)), True)
        m = _RE_TEK_SINIR_SONDA.match(t)
        if m:
            return ("acik", _sayi_tr(m.group(1)), False)
        m = _RE_IKI_SINIR.match(t)
        if m:
            return ("kapali", _sayi_tr(m.group(1)), _sayi_tr(m.group(2)))
        v = _sayi_tr(t)
        return ("kapali", v, v)
    except ValueError:
        return None


def parse_aralik_degeri(aralik_str: str) -> Optional[tuple]:
    """Aralık string'ini (min, max) olarak çözer (örn: "40-49", "%80-89", "400.000-449.000").

    Tek sınırlı bantlar bu ham fonksiyonda eski anlamını korur ("-5" → (-5, None),
    "90-" / "20+" → (90, None)). Puan hesabı bunu KULLANMAZ; bandın konumuna göre
    çözen bantlari_coz kullanılır."""
    r = _aralik_coz(aralik_str)
    if r is None:
        return None
    if r[0] == "acik":
        return (-r[1] if r[2] else r[1], None)
    return (r[1], r[2])


def bantlari_coz(basari_puani_araliklari: Optional[Dict[int, Any]], direction: str = 'Increasing') -> Dict[int, tuple]:
    """{puan: (min, max)} — None = sınırsız. Tek sınırlı bantlar KONUMA göre çözülür (Karar 1).

    Artan yönde en kötü (en düşük puanlı) bant "N ve altı", en iyi bant "N ve üstü";
    azalan yönde tersi. Örnek KMF: {"1":"-4",…,"5":"20-"} → 1: (None, 4), 5: (20, None).
    Eski davranış "-4"ü (-4, sınırsız) okuyordu; 1 puanlık bant her değeri yakalıyordu."""
    ham = {}
    for puan, raw in (basari_puani_araliklari or {}).items():
        r = _aralik_coz(_coerce_aralik_str_for_hesap(raw) or "")
        if r is not None:
            try:
                ham[int(puan)] = r
            except (TypeError, ValueError):
                continue
    if not ham:
        return {}
    en_kotu, en_iyi = min(ham), max(ham)
    artan = (direction or '').strip().lower() != 'decreasing'
    out: Dict[int, tuple] = {}
    for puan, r in ham.items():
        if r[0] == "kapali":
            out[puan] = (r[1], r[2])
            continue
        alta_dogru = (puan == en_kotu) if artan else (puan == en_iyi)
        out[puan] = (None, r[1]) if alta_dogru else (r[1], None)
    return out


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

    if min_val is not None and deger < min_val:
        return False
    return max_val is None or deger <= max_val


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

    bantlar = bantlari_coz(basari_puani_araliklari, direction)
    if not bantlar:
        return None

    azalan = (direction or '').strip().lower() == 'decreasing'
    # Artan: en düşük puan önce; azalan: en yüksek puan önce (eski sıralama korunur)
    sirali = sorted(bantlar.items(), reverse=azalan)

    for puan, aralik in sirali:
        if deger_aralikta_mi(gerceklesen, aralik):
            return puan

    # Hiçbir banda düşmedi: uç değer yedek kuralı (değişmedi)
    _, (son_min, son_max) = sirali[-1]
    _, (ilk_min, _ilk_max) = sirali[0]
    if azalan:
        if son_max is not None and gerceklesen > son_max:
            return 1
        if son_min is not None and gerceklesen < son_min:
            return 5
    else:
        if son_max is not None and gerceklesen > son_max:
            return 5
        if ilk_min is not None and gerceklesen < ilk_min:
            return 1

    # A-004: bantlar arasında kalan değer (ör. {'80-99','100-'} için 99.5):
    # uydurma 3 yerine, değerin ALTINDA kalan en yakın bandın puanı (tam sayı
    # bantlarda ondalık gerçekleşen, bir alt banda aittir). Alt bant yoksa None.
    alt = [(ar[1], puan) for puan, ar in bantlar.items()
           if ar[1] is not None and ar[1] < gerceklesen]
    if alt:
        return max(alt)[1]
    return None


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
        agirlik: Ağırlık YÜZDE olarak (0-100); her zaman /100 uygulanır

    Returns:
        float: Ağırlıklı başarı puanı veya None
    """
    if basari_puani is None or agirlik is None:
        return None

    try:
        # A-005: ağırlık birimi TEK: yüzde (0-100). Eskiden >1 ise /100,
        # <=1 ise olduğu gibi çarpılıyordu (1 -> %100, 2 -> %2).
        return float(basari_puani) * (float(agirlik) / 100.0)
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
