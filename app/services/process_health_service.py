# -*- coding: utf-8 -*-
"""
Process Health Service
Süreç sağlık skoru hesaplama servisi.
Proje modülü olmadan PG hedef ulaşma oranına dayalı basit skor.
Proje/Task entegrasyonu eklendiğinde genişletilebilir.
"""
from datetime import datetime
from app.services.date_sovereign import resolve_request_year
from typing import Optional, Dict, Any

from app.models import db
from app.models.process import Process, ProcessKpi, KpiData


# B6/D2 (2026-07-21): bu dosyanın kendi `_parse_float` kopyası vardı ve
# yalnız virgülü noktaya çeviriyordu — '%90', '1.234,5', '₺100.070' gibi
# gerçek girdileri çözemiyordu. Skor motorunun kopyası bunları tanıyor.
# Üçüncü bir kopya tutmak B2'deki ayrışma hatasının aynısı olurdu.
from app.services.score_engine_service import (  # noqa: E402
    _parse_float,
    _resolve_target_for_calculation,
    normalize_aggregation_method,
)


def calculate_process_health_score(
    process_id: int,
    year: Optional[int] = None
) -> Optional[Dict[str, Any]]:
    """
    Bir sürecin sağlık skorunu hesaplar.

    Mevcut versiyon: PG hedef ulaşma oranı + süreç ilerleme (progress).
    Proje modülü eklendiğinde: proje tamamlama, geciken görev, risk faktörü eklenir.

    Returns:
        dict: {
            'skor': float (0-100),
            'durum': str ('Sağlıklı', 'Orta', 'Riski', 'Veri yok'),
            'detay': {
                'pg_hedef_ulasma_orani': float,
                'surec_ilerleme': float,
                'pg_sayisi': int,
                'veri_girilen_pg': int
            }
        }
    """
    if year is None:
        year = resolve_request_year()

    process = Process.query.filter_by(
        id=process_id,
        is_active=True
    ).first()
    if not process:
        return None

    kpis = ProcessKpi.query.filter_by(
        process_id=process.id,
        is_active=True
    ).all()

    # N+1 önlemi: tüm KPI'ların verisini tek sorguda yükle (KPI başına ayrı sorgu yerine).
    kpi_ids = [k.id for k in kpis]
    entries_by_kpi: Dict[int, list] = {}
    if kpi_ids:
        for e in (KpiData.query
                  .filter(KpiData.process_kpi_id.in_(kpi_ids),
                          KpiData.year == year,
                          KpiData.is_active.is_(True))
                  .order_by(KpiData.process_kpi_id, KpiData.data_date.desc())
                  .all()):
            entries_by_kpi.setdefault(e.process_kpi_id, []).append(e)

    pg_scores = []
    for kpi in kpis:
        # B6: aralık/yüzde hedefleri de çözülsün ('90-100', '%85').
        target = _resolve_target_for_calculation(
            kpi.target_value, kpi.direction or 'Increasing'
        )
        if target is None or target <= 0:
            if kpi.calculated_score is not None:
                # B10: burada yalnız `min(100, …)` vardı, `max(0, …)` YOKTU —
                # ana dal (aşağıda) iki sınırı da uyguluyor. DB'de şu an
                # negatif calculated_score yok (0/565), yani hata tetiklenmiyor;
                # koruma eksikliği latent kalmasın diye simetrik yapıldı.
                pg_scores.append(min(100.0, max(0.0, float(kpi.calculated_score))))
            continue

        entries = entries_by_kpi.get(kpi.id, [])

        if not entries:
            continue

        actual_values = [_parse_float(e.actual_value) for e in entries]
        actual_values = [v for v in actual_values if v is not None]
        if not actual_values:
            continue

        # D1/D2/M2: iki dilli yöntem etiketleri tek noktadan çözülür.
        # Eskiden yalnız Türkçe etiketler tanınıyordu; `AVG` (35 satır)
        # tesadüfen doğru dala düşüyordu ama `SUM` sessizce ortalamaya
        # dönerdi.
        _yontem = normalize_aggregation_method(kpi.data_collection_method)
        if _yontem == 'SUM':
            actual = sum(actual_values)
        elif _yontem == 'LAST':
            actual = actual_values[0]
        else:  # AVG
            actual = sum(actual_values) / len(actual_values)

        if kpi.direction == 'Decreasing':
            ratio = target / actual if actual > 0 else 0
        else:
            ratio = actual / target if target > 0 else 0
        score = min(100.0, max(0.0, ratio * 100.0))
        pg_scores.append(score)

    pg_hedef_ulasma = sum(pg_scores) / len(pg_scores) if pg_scores else None
    surec_ilerleme = process.progress or 0

    if pg_hedef_ulasma is not None:
        skor = (pg_hedef_ulasma * 0.7) + (surec_ilerleme * 0.3)
    elif surec_ilerleme is not None:
        skor = float(surec_ilerleme)
    else:
        skor = 0.0

    skor = round(min(100.0, max(0.0, skor)), 1)

    if pg_scores:
        if skor >= 80:
            durum = 'Sağlıklı'
        elif skor >= 50:
            durum = 'Orta'
        else:
            durum = 'Riski'
    else:
        durum = 'Veri yok'

    return {
        'skor': skor,
        'durum': durum,
        'detay': {
            'pg_hedef_ulasma_orani': round(pg_hedef_ulasma, 1) if pg_hedef_ulasma is not None else None,
            'surec_ilerleme': surec_ilerleme,
            'pg_sayisi': len(kpis),
            'veri_girilen_pg': len(pg_scores),
        }
    }
