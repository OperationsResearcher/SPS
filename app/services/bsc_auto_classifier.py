"""BSC perspektif otomatik sınıflandırıcı.

PG adı/kodu/açıklamasından + bağlı süreç adından yola çıkarak 4 BSC perspektifinden
birine kural-tabanlı öneri üretir. Sertifikalı bir ML modeli yok — Türkçe finans/
müşteri/iç süreç/öğrenme terminolojisi keyword'leri ile heuristik.

Sınıflandırma referansı:
- Kaplan & Norton (1992 HBR, 1996 BSC kitabı): 4 perspektif neden-sonuç piramidi
- Türkçe terminoloji sözlüğü (yerel kullanım): docs/UI-TERMINOLOJI.md
"""
from __future__ import annotations
import re
from typing import Optional


# Keyword setleri — büyük/küçük harf duyarsız, Türkçe karakterler normalize edilir
_KEYWORDS = {
    "finansal": [
        # Finansal/maliyet/gelir
        "gelir", "ciro", "satis", "satış", "karlilik", "karlılık", "kar", "kâr",
        "ebitda", "fcf", "nakit", "butçe", "bütçe", "butce",
        "maliyet", "harcama", "yatirim", "yatırım", "geri donus", "geri dönüş",
        "roi", "npv", "irr", "finansal", "mali", "muhasebe", "fatura",
        "tahsilat", "alacak", "borc", "borç", "tl", "usd", "eur", "para",
        "verimlilik orani", "fiyat", "marj", "katma deger", "katma değer",
        "tasarruf", "iskonto",
    ],
    "musteri": [
        # Müşteri/pazar/marka
        "musteri", "müşteri", "musteri memnuniyeti", "müşteri memnuniyet",
        "nps", "csat", "ces", "pazar", "market", "marka", "brand",
        "pazar payi", "pazar payı", "satis sonrasi", "satış sonrası",
        "sikayet", "şikayet", "iade", "garanti", "musteri kazanim", "müşteri kazanım",
        "musteri kayip", "müşteri kayıp", "churn", "elde tutma",
        "musteri yolculuğu", "müşteri yolculuğu", "ux", "kullanici deneyimi",
        "kullanıcı deneyimi", "musteri deneyimi", "müşteri deneyimi",
        "memnuniyet", "tavsiye orani", "tavsiye oranı",
        "musteri ziyaret", "müşteri ziyaret",
    ],
    "ic_surec": [
        # Operasyon/üretim/kalite/süreç
        "uretim", "üretim", "imalat", "tedarikçi", "tedarikçi", "tedarik",
        "satınalma", "satinalma", "lojistik", "depo", "stok", "envanter",
        "kalite", "isgu", "iş güvenliği", "isg", "is sağlığı", "iş sağlığı",
        "olcum", "ölçüm", "test", "muayene", "denetim", "audit",
        "verimlilik", "cycle time", "lead time", "teslimat suresi",
        "teslimat süresi", "uretkenlik", "üretkenlik", "kapasite",
        "hata orani", "hata oranı", "ret orani", "ret oranı", "fire orani",
        "fire oranı", "yenidenisleme", "rework", "iadeler",
        "surec", "süreç", "operasyon", "is akisi", "iş akışı",
        "spc", "sigma", "yalın", "yalin", "kaizen", "5s", "olke", "ovk",
        "uretim plani", "üretim planı", "scheduled", "planlanmış",
    ],
    "ogrenme": [
        # İnsan kaynağı/eğitim/inovasyon/teknoloji
        "egitim", "eğitim", "training", "ogrenme", "öğrenme",
        "personel", "calisan", "çalışan", "kadrlo", "kadro",
        "yetkinlik", "competency", "beceri", "skill",
        "ar-ge", "arge", "ar ge", "ar&ge", "rd", "r&d", "rgd", "argd",
        "inovasyon", "innovation", "yenilik", "patent", "fikri mulkiyet",
        "fikri mülkiyet", "telif", "lisans",
        "kultur", "kültür", "engagement", "baglılık", "bağlılık",
        "isten ayrilma", "işten ayrılma", "turnover", "devamsizlik",
        "devamsızlık", "memnuniyet anketi", "bilgi yonetim", "bilgi yönetim",
        "dijital", "teknoloji", "sistem", "altyapı", "altyapi",
        "yetistirme", "yetiştirme", "calisan gelisimi", "çalışan gelişimi",
        "is guvenligi egitim", "iş güvenliği eğitim", "oryantasyon",
        "kpi 327", "efqm", "yetkinlik matrisi",
    ],
}


def _normalize(text: str) -> str:
    """Türkçe karakter normalizasyonu + lowercasing."""
    if not text:
        return ""
    t = text.lower()
    # Türkçe karakterleri Latin'e çevir (eşleştirme genişliği için)
    tr_map = str.maketrans({
        "ı": "i", "ş": "s", "ğ": "g", "ü": "u", "ö": "o", "ç": "c",
        "İ": "i", "Ş": "s", "Ğ": "g", "Ü": "u", "Ö": "o", "Ç": "c",
    })
    return t.translate(tr_map)


def classify(name: str, code: str = "", description: str = "",
             process_name: str = "", process_code: str = "") -> tuple[Optional[str], int, list[str]]:
    """PG için BSC perspektif öner.

    Returns:
        (perspective_key, score, matched_keywords)
        perspective_key: 'finansal' | 'musteri' | 'ic_surec' | 'ogrenme' | None
        score: 0-100 — yüksek = daha emin
        matched_keywords: hangi kelimeler eşleşti
    """
    haystack = " ".join([
        name or "", code or "", description or "",
        process_name or "", process_code or "",
    ])
    norm = _normalize(haystack)

    scores: dict[str, int] = {}
    matched: dict[str, list[str]] = {p: [] for p in _KEYWORDS}

    for persp, kws in _KEYWORDS.items():
        s = 0
        for kw in kws:
            norm_kw = _normalize(kw)
            # Tam kelime/öbek araması (kelime sınırı ile)
            if " " in norm_kw:
                if norm_kw in norm:
                    s += 3
                    matched[persp].append(kw)
            else:
                # Kelime sınırı
                if re.search(rf"\b{re.escape(norm_kw)}\b", norm):
                    s += 2
                    matched[persp].append(kw)
                elif norm_kw in norm:
                    # Kısmi eşleşme — daha az ağırlık
                    s += 1
                    matched[persp].append(kw + "*")
        scores[persp] = s

    if not any(scores.values()):
        return None, 0, []

    best = max(scores.items(), key=lambda x: x[1])
    persp, raw_score = best
    if raw_score == 0:
        return None, 0, []

    # Skor normalize (0-100)
    max_possible = sum(scores.values()) or 1
    confidence = min(100, int(raw_score / max(max_possible, 1) * 100))
    # Tek kategori için ek prim
    if list(scores.values()).count(raw_score) == 1 and raw_score >= 3:
        confidence = min(100, confidence + 15)

    return persp, confidence, matched[persp][:5]


def balance_score(counts: dict[str, int]) -> tuple[float, dict[str, float]]:
    """4 perspektif arası denge skoru (Kaplan-Norton ideal: %25 her biri).

    Returns:
        (balance_pct, share_per_perspective)
        balance_pct: 0-100, yüksek = daha dengeli
        share_per_perspective: {persp: %share}
    """
    total = sum(counts.get(p, 0) for p in ("finansal", "musteri", "ic_surec", "ogrenme"))
    if total == 0:
        return 0.0, {p: 0.0 for p in ("finansal", "musteri", "ic_surec", "ogrenme")}

    shares = {p: round(counts.get(p, 0) / total * 100, 1) for p in
              ("finansal", "musteri", "ic_surec", "ogrenme")}

    # Gini-tarzı eşitsizlik: ideal %25'ten sapmaların ortalaması
    deviations = [abs(shares[p] - 25.0) for p in shares]
    avg_dev = sum(deviations) / 4
    # Max sapma 75 (tek perspektifte %100 olur ise)
    balance = round(max(0.0, 100.0 - (avg_dev / 75.0 * 100.0)), 1)
    return balance, shares
