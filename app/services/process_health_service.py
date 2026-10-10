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
    _kpi_effective_cfg,
    _load_cfg_map,
    _score_pgs,
    weighted_average,
)
from app.utils.tr_time import today_tr  # noqa: E402


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

    # A-008: tek hesap motoru — yıllık config, tarih kesimi, yön, yöntem motordan.
    from app.services.plan_year_service import get_plan_year
    plan_year = get_plan_year(process.tenant_id, year) if process.tenant_id else None

    kpis_q = ProcessKpi.query.filter_by(process_id=process.id, is_active=True)
    if plan_year is not None:
        kpis_q = kpis_q.filter(
            (ProcessKpi.plan_year_id == plan_year.id) | (ProcessKpi.plan_year_id.is_(None))
        )
    kpis = kpis_q.all()

    cfg_map = _load_cfg_map(kpis, plan_year)
    rows = _score_pgs(kpis, year, today_tr(), plan_year, cfg_map) if kpis else {}
    pairs = []
    pg_scores = []
    for kpi in kpis:
        c = _kpi_effective_cfg(kpi, cfg_map)
        if not c['is_included']:
            continue
        sc = rows[kpi.id]['score']
        pairs.append((sc, c['weight']))
        if sc is not None:
            pg_scores.append(sc)

    pg_hedef_ulasma = weighted_average(pairs) if pg_scores else None
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
            'pg_sayisi': len(pairs),
            'veri_girilen_pg': len(pg_scores),
        }
    }
