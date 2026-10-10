"""PERF-06 — verisiz klon PG'lerin atası toplu çözülür (adım başına sorgu yok)."""
from datetime import date

from sqlalchemy import event

from app.models import db
from app.models.core import Tenant
from app.models.plan_year import PlanYear
from app.models.process import KpiData, Process, ProcessKpi
from app.services.score_engine_service import _resolve_ancestor_entries


def _zincir(n):
    t = Tenant(name="T", short_name="t", is_active=True)
    db.session.add(t)
    db.session.flush()
    db.session.add(PlanYear(tenant_id=t.id, year=2026, status="active"))
    p = Process(name="P", tenant_id=t.id, is_active=True)
    db.session.add(p)
    db.session.flush()
    kpis, onceki = [], None
    for i in range(n):
        k = ProcessKpi(process_id=p.id, name=f"K{i}", code=f"K{i}", is_active=True,
                       target_value="10", source_kpi_id=onceki)
        db.session.add(k)
        db.session.flush()
        kpis.append(k)
        onceki = k.id
    db.session.commit()
    return kpis   # kpis[0] en eski ata, kpis[-1] en yeni klon


def test_ata_verisi_bulunur_ve_sorgu_sayisi_derinlikle_sinirli(app):
    kpis = _zincir(6)
    db.session.add(KpiData(process_kpi_id=kpis[1].id, year=2026, data_date=date(2026, 3, 1),
                           actual_value="7", is_active=True))
    db.session.commit()
    sorgular = []
    event.listen(db.engine, "before_cursor_execute", lambda *a: sorgular.append(a[2]))
    sonuc = _resolve_ancestor_entries([kpis[-1]], 2026, date(2026, 12, 31))
    assert [e.actual_value for e in sonuc[kpis[-1].id]] == ["7"]
    assert len(sorgular) <= 2 * 4 + 2       # 4 adım × (KpiData + kaynak haritası)


def test_veri_yoksa_bos_ve_dongu_korumasi(app):
    kpis = _zincir(3)
    kpis[0].source_kpi_id = kpis[-1].id      # döngü
    db.session.commit()
    assert _resolve_ancestor_entries([kpis[-1]], 2026, date(2026, 12, 31)) == {}
