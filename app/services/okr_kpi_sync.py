"""OKR ↔ KPI senkron servisi (Sprint 33).

Bir Key Result `linked_process_kpi_id` set edilmişse:
- KR.current_value otomatik olarak son KpiData değerinden güncellenir
- Trigger: KpiData yazıldığında veya manuel sync endpoint'iyle

Kullanım:
    from app.services.okr_kpi_sync import sync_kr_from_kpi, sync_all_krs_for_tenant
    sync_kr_from_kpi(kr_id=42)
    sync_all_krs_for_tenant(tenant_id=27, plan_year_id=10)
"""
from __future__ import annotations

from typing import Optional

from extensions import db
from app.models.okr import OkrKeyResult
from app.models.process import KpiData, ProcessKpi
from flask_babel import gettext as _


def _latest_actual_value(kpi_id: int) -> Optional[float]:
    """ProcessKpi'nın son KpiData satırının actual_value'sunu sayı olarak döner."""
    row = (
        KpiData.query
        .filter_by(process_kpi_id=kpi_id, is_active=True)
        .order_by(KpiData.data_date.desc(), KpiData.id.desc())
        .first()
    )
    if not row or row.actual_value in (None, ""):
        return None
    try:
        return float(str(row.actual_value).replace(",", "."))
    except (ValueError, TypeError):
        return None


def sync_kr_from_kpi(kr_id: int) -> dict:
    """Belirli bir KR'yi bağlı KPI'sından senkronize et."""
    kr = OkrKeyResult.query.get(kr_id)
    if not kr:
        return {"success": False, "message": _("KR bulunamadı")}
    if not kr.linked_process_kpi_id:
        return {"success": False, "message": _("KR bağlı KPI yok")}

    val = _latest_actual_value(kr.linked_process_kpi_id)
    if val is None:
        return {"success": False, "message": _("KPI'da son değer yok")}

    old = kr.current_value
    kr.current_value = val
    db.session.commit()
    return {"success": True, "old": old, "new": val, "kr_id": kr_id}


def sync_all_krs_for_tenant(tenant_id: int, plan_year_id: Optional[int] = None) -> dict:
    """Tenant'taki tüm bağlı KR'leri senkronize et."""
    q = (
        db.session.query(OkrKeyResult)
        .join(OkrKeyResult.objective)
        .filter(OkrKeyResult.linked_process_kpi_id.isnot(None))
        .filter(OkrKeyResult.is_active == True)
    )
    from app.models.okr import OkrObjective
    q = q.filter(OkrObjective.tenant_id == tenant_id)
    if plan_year_id:
        q = q.filter(OkrObjective.plan_year_id == plan_year_id)

    krs = q.all()
    synced = 0
    skipped = 0
    for kr in krs:
        val = _latest_actual_value(kr.linked_process_kpi_id)
        if val is None:
            skipped += 1
            continue
        kr.current_value = val
        synced += 1
    if synced:
        db.session.commit()

    return {
        "success": True,
        "total": len(krs),
        "synced": synced,
        "skipped": skipped,
    }
