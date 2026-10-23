# -*- coding: utf-8 -*-
"""Masaüstüm: "veri girişi bekleyen PG'lerim" (UX-PLANI B / Faz 2.3).

Tanım (öneriyle onaylanan varsayılanlar):
  - Kullanıcı = PG'nin süreci üzerinde **lider veya üye**.
  - "Bekleyen" = bu yıl için **tamamlanmış** (dönemi bitmiş) ama verisi olmayan dönem.
      aylık: bugünkü aydan önceki aylar · çeyreklik: bitmiş çeyrekler · yarıyıllık: bitmişse 1. yarı.
    Yıllık, haftalık, günlük PG'ler kapsam dışı. Cari (bitmemiş) dönem "bekleyen" sayılmaz.
  - Yalnız bugünün takvim yılına ait plan yılındaki PG'ler.
  - Holding oturumunda (veri girişi yok) boş döner.
"""
from __future__ import annotations

from datetime import date

from app.constants.periods import normalize_period_type
from app.models import db
from app.models.plan_year import PlanYear
from app.models.process import KpiData, Process, ProcessKpi, process_leaders, process_members
from app.utils.process_utils import data_date_to_period_keys

_AY = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]


def tamamlanmis_donemler(period_type: str | None, bugun: date) -> list[tuple[str, str]]:
    """[(hücre_anahtarı, etiket), ...] — bu yıl bitmiş dönemler. Desteklenmeyen tür → []."""
    pt = normalize_period_type(period_type)
    if pt == "aylik":
        return [(f"aylik_{m}", _AY[m - 1]) for m in range(1, bugun.month)]
    if pt == "ceyrek":
        return [(f"ceyrek_{q}", f"{q}. Çeyrek") for q in range(1, (bugun.month - 1) // 3 + 1)]
    if pt == "halfyear":
        return [("halfyear_1", "Ocak–Haziran")] if bugun.month > 6 else []
    return []


def bekleyen_pg_listesi(user, bugun: date | None = None, limit: int = 8) -> dict:
    """{"items": [...], "toplam": n}. items: kpi_id, code, name, process_id, process_name, eksik[], eksik_sayi."""
    bos = {"items": [], "toplam": 0}
    if not getattr(user, "tenant_id", None):
        return bos
    bugun = bugun or date.today()
    yil = bugun.year

    uye = db.session.query(process_members.c.process_id).filter(process_members.c.user_id == user.id)
    lider = db.session.query(process_leaders.c.process_id).filter(process_leaders.c.user_id == user.id)
    kpis = (
        ProcessKpi.query.join(Process, ProcessKpi.process_id == Process.id)
        .join(PlanYear, ProcessKpi.plan_year_id == PlanYear.id)
        .filter(
            ProcessKpi.is_active.is_(True),
            Process.is_active.is_(True),
            Process.tenant_id == user.tenant_id,
            PlanYear.tenant_id == user.tenant_id,
            PlanYear.year == yil,
            db.or_(Process.id.in_(uye.scalar_subquery()), Process.id.in_(lider.scalar_subquery())),
        )
        .all()
    )
    adaylar = [(k, tamamlanmis_donemler(k.period, bugun)) for k in kpis]
    adaylar = [(k, d) for k, d in adaylar if d]
    if not adaylar:
        return bos

    girilen: dict[int, set[str]] = {}
    for kpi_id, veri_tarihi in (
        db.session.query(KpiData.process_kpi_id, KpiData.data_date)
        .filter(KpiData.process_kpi_id.in_([k.id for k, _ in adaylar]), KpiData.year == yil, KpiData.is_active.is_(True))
        .all()
    ):
        girilen.setdefault(kpi_id, set()).update(data_date_to_period_keys(veri_tarihi, yil))

    sonuc = []
    for k, donemler in adaylar:
        eksik = [etiket for anahtar, etiket in donemler if anahtar not in girilen.get(k.id, set())]
        if eksik:
            sonuc.append({
                "kpi_id": k.id, "code": k.code or "", "name": k.name,
                "process_id": k.process_id, "process_name": k.process.name if k.process else "",
                "eksik": eksik, "eksik_sayi": len(eksik),
            })
    sonuc.sort(key=lambda r: (-r["eksik_sayi"], r["name"]))
    return {"items": sonuc[:limit], "toplam": len(sonuc)}
