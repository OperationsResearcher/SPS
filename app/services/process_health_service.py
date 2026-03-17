# -*- coding: utf-8 -*-
"""
Process Health Service
Süreç sağlık skoru hesaplama servisi.
Proje modülü olmadan PG hedef ulaşma oranına dayalı basit skor.
Proje/Task entegrasyonu eklendiğinde genişletilebilir.
"""
from datetime import datetime
from typing import Optional, Dict, Any

from app.models import db
from app.models.process import Process, ProcessKpi, KpiData


def _parse_float(val) -> Optional[float]:
    """String veya sayıyı float'a çevirir."""
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    text = str(val).strip().replace(',', '.')
    if not text:
        return None
    try:
        return float(text)
    except (ValueError, TypeError):
        return None


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
        year = datetime.now().year

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

    pg_scores = []
    for kpi in kpis:
        target = _parse_float(kpi.target_value)
        if target is None or target <= 0:
            if kpi.calculated_score is not None:
                pg_scores.append(min(100.0, float(kpi.calculated_score)))
            continue

        entries = KpiData.query.filter_by(
            process_kpi_id=kpi.id,
            year=year,
            is_active=True
        ).order_by(KpiData.data_date.desc()).all()

        if not entries:
            continue

        actual_values = [_parse_float(e.actual_value) for e in entries]
        actual_values = [v for v in actual_values if v is not None]
        if not actual_values:
            continue

        if kpi.data_collection_method in ('Toplama', 'Toplam'):
            actual = sum(actual_values)
        elif kpi.data_collection_method == 'Son Değer':
            actual = actual_values[0]
        else:
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
