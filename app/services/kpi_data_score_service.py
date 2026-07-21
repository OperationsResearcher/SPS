# -*- coding: utf-8 -*-
"""KpiData satırının kendi skorunu (`status` + `status_percentage`) üretir.

NEDEN VAR (K1 · 2026-07-21):
    `KpiData.status_percentage` 8 yerde OKUNUYOR ama HİÇBİR YERDE yazılmıyordu.
    Ölçüm (2026-07-21, yerel DB):

        Kayseri Model Fabrika   334 / 334 satır skorsuz   (%100)
        Eskişehir Makine        289 / 289 satır skorsuz   (%100)
        Default Corp              2 /   2 satır skorsuz   (%100)
        Tomofil (seed verisi)     0 / 91.408              (%0)

    Yani ELLE VERİ GİREN HER KURUMDA sistem skorsuzdu; Tomofil'in seed'le
    dolu gelen 91k satırı hatayı maskeliyordu. Bu yüzden aylarca fark edilmedi.

    Alanı okuyan yerler (hepsi sessizce NULL alıyordu):
        micro/modules/raporlar/routes_faz5.py:127   BI dışa aktarımı
        micro/modules/raporlar/routes_faz4.py:192   en iyi/en kötü PG sıralaması
        micro/modules/raporlar/routes_faz1.py:859   trend skorları
        micro/modules/masaustu/routes.py:159        masaüstü kartı
        micro/modules/k_rapor/routes.py:660,683,1518

TASARIM KARARI — neden tek merkezî fonksiyon:
    KpiData 5 ayrı yerde yazılıyor (surec ekle/güncelle, api ekle/güncelle,
    faaliyet otomatik üretimi). Her birine ayrı hesap kopyalamak, F10/B2'de
    görülen "kopya ayrışması" hatasını yeniden üretirdi. Tek giriş noktası var.

SEMANTİK — 0 ile None ayrımı (İ4 kararıyla uyumlu):
    - Hedef ya da gerçekleşen YOKSA        → (None, None). "Ölçülmedi" demek,
      "başarısız" demek DEĞİL. Sıfır yazmak kurumu veri girmediği için cezalandırır.
    - Sayıya çevrilemiyorsa                → (None, None) + log. Sessiz kalma.
    - Hesaplanabiliyorsa                   → ("Tuttu"/"Tutmadı", 0-100 float)

    "Tuttu"/"Tutmadı" vokabüleri mevcut 365.632 satırdan geliyor; değiştirmek
    geçmiş veriyle tutarsızlık yaratırdı.
"""
from __future__ import annotations

import logging
from typing import Any, Optional, Tuple

_log = logging.getLogger(__name__)

# Hedefe ulaşmış sayılma eşiği (yüzde). compute_pg_score 100'de kırpar,
# yani "Tuttu" = hedefin tamamına ulaşıldı.
ESIK_TUTTU = 100.0

DURUM_TUTTU = "Tuttu"
DURUM_TUTMADI = "Tutmadı"

# Kullanıcının "veri yok / hedef konulmadı" demek için yazdığı işaretler.
# Bunlar veri kalitesi hatası DEĞİL, bilinçli boş bırakmadır.
_BOS_ISARETLER = frozenset({"", "-", "--", ".", ",", "yok", "n/a", "na"})


def _anlamli_dolu(v: Any) -> bool:
    """Değer gerçekten bir sayı taşıma iddiasında mı?"""
    if v is None:
        return False
    return str(v).strip().lower() not in _BOS_ISARETLER


def hesapla_kpi_data_skoru(
    kpi: Any,
    target_value: Any,
    actual_value: Any,
) -> Tuple[Optional[str], Optional[float]]:
    """Tek bir PG verisi satırının (durum, yüzde) değerini üretir.

    Args:
        kpi: ProcessKpi — `direction` ve (varsa) `target_value` için.
        target_value: Satırın kendi hedefi. Boşsa PG'nin hedefine düşülür.
        actual_value: Satırın gerçekleşen değeri.

    Returns:
        (status, status_percentage) — hesaplanamazsa (None, None).
    """
    # Geç import: score_engine_service bu modülü import etmiyor ama
    # ileride ederse döngü oluşmasın.
    from app.services.score_engine_service import (
        _parse_float,
        _resolve_target_for_calculation,
        compute_pg_score,
    )

    direction = (getattr(kpi, "direction", None) or "Increasing")

    ham_hedef = target_value
    if ham_hedef is None or str(ham_hedef).strip() == "":
        ham_hedef = getattr(kpi, "target_value", None)

    hedef = _resolve_target_for_calculation(ham_hedef, direction)
    gerceklesen = _parse_float(actual_value)

    if hedef is None or gerceklesen is None:
        # Hedef/gerçekleşen ANLAMLI DOLU ama çevrilemiyorsa bu bir veri
        # kalitesi sorunudur — sessiz geçme, çünkü K1 tam olarak bu yüzden
        # gizli kaldı. Ama '-' kullanıcının bilinçli "veri yok" işaretidir
        # (KMF'de 42 PG bunu kullanıyor); onu uyarı saymak log'u boğar ve
        # gerçek sorunları görünmez kılar.
        if (_anlamli_dolu(ham_hedef) and hedef is None) or (
            _anlamli_dolu(actual_value) and gerceklesen is None
        ):
            _log.warning(
                "[kpi_data_score] PG %s: sayıya çevrilemedi (hedef=%r → %r, "
                "gerçekleşen=%r → %r). Satır skorsuz kaldı.",
                getattr(kpi, "id", "?"), ham_hedef, hedef, actual_value, gerceklesen,
            )
        return None, None

    yuzde = compute_pg_score(hedef, gerceklesen, direction)
    if yuzde is None:
        # compute_pg_score yalnız hedef=0'da None döner (sıfıra bölme).
        _log.warning(
            "[kpi_data_score] PG %s: hedef 0 olduğu için oran hesaplanamadı.",
            getattr(kpi, "id", "?"),
        )
        return None, None

    durum = DURUM_TUTTU if yuzde >= ESIK_TUTTU else DURUM_TUTMADI
    return durum, yuzde


def uygula_kpi_data_skoru(entry: Any, kpi: Any) -> None:
    """KpiData nesnesinin skor alanlarını yerinde günceller.

    Çağıran commit'ten ÖNCE çağırmalı. Hesaplanamazsa alanlar None'a çekilir
    — eski (artık geçersiz) skorun satırda kalması yanlış olurdu.
    """
    durum, yuzde = hesapla_kpi_data_skoru(
        kpi, getattr(entry, "target_value", None), getattr(entry, "actual_value", None)
    )
    entry.status = durum
    entry.status_percentage = yuzde
