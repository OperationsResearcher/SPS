# -*- coding: utf-8 -*-
"""
EVM (Earned Value Management) Basit Hesaplamalar
PV: Planlanan iş (estimated_time toplamı)
EV: Gerçekleşen iş (estimated_time * progress/100 toplamı)
AC: Gerçek maliyet (actual_time toplamı)
SPI = EV / PV, CPI = EV / AC
Not: Basitleştirilmiş; gerçek dünyada değerleme ve ağırlıklar değişebilir.
"""
from models import Task

def compute_project_evm(project_id: int) -> dict:
    tasks = Task.query.filter_by(project_id=project_id).all()
    pv = 0.0
    ev = 0.0
    ac = 0.0
    for t in tasks:
        est = float(t.estimated_time or 0.0)
        act = float(t.actual_time or 0.0)
        prog = float(t.progress or 0.0)
        pv += est
        ev += est * (prog / 100.0)
        ac += act
    spi = (ev / pv) if pv > 0 else None
    cpi = (ev / ac) if ac > 0 else None
    return {
        'pv': pv,
        'ev': ev,
        'ac': ac,
        'spi': spi,
        'cpi': cpi,
    }
