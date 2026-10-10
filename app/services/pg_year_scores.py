"""PG yıllık skor özeti — rapor/SP/EFQM ekranları için motor köprüsü (Dalga 3, 2b).

Hesap kuralı `score_engine_service`'e aittir (yön, toplulaştırma, yıllık hedef, parse).
Burada hesap YAPILMAZ; yalnızca motorun `_score_pgs` çıktısı PG başına tek değer olarak
sunulur. "Hedefte" = PG başarısı >= 100. Ölçülmemiş PG (skor None) paydaya girmez."""
from __future__ import annotations

from datetime import date
from typing import Dict, Iterable, Optional

from sqlalchemy import and_, or_

from app.models.process import Process, ProcessKpi
from app.services import score_engine_service as eng
from app.utils.tr_time import today_tr


def load_pgs(tenant_id: int, plan_year=None):
    """Kurumun aktif PG'leri (motorun get_pg_scores_from_kpi_data kapsamıyla aynı)."""
    q = ProcessKpi.query.join(Process, ProcessKpi.process_id == Process.id).filter(
        ProcessKpi.is_active.is_(True), Process.is_active.is_(True))
    if plan_year is not None:
        q = q.filter(or_(
            ProcessKpi.plan_year_id == plan_year.id,
            and_(ProcessKpi.plan_year_id.is_(None), Process.tenant_id == tenant_id)))
    else:
        q = q.filter(Process.tenant_id == tenant_id)
    return q.all()


def score_rows(tenant_id: int, year: int, as_of: Optional[date] = None, pgs=None):
    """{pg_id: {score, actual, target, direction, ...}} + pgs listesi (motor çıktısı)."""
    from app.services.plan_year_service import get_plan_year
    py = get_plan_year(tenant_id, year)
    pgs = pgs if pgs is not None else load_pgs(tenant_id, py)
    cfg = eng._load_cfg_map(pgs, py)
    return eng._score_pgs(pgs, year, as_of or today_tr(), py, cfg), pgs


def on_target_stats(rows: Dict[int, dict], pg_ids: Iterable[int]):
    """PG başına TEK değer: (pg_total, on_target, comparable). Tekrarlı id tek sayılır."""
    ids = set(pg_ids)
    comp = on_t = 0
    for i in ids:
        sc = (rows.get(i) or {}).get('score')
        if sc is None:
            continue
        comp += 1
        if sc >= 100:
            on_t += 1
    return len(ids), on_t, comp


def pct(on_t: int, comp: int):
    return round(on_t / comp * 100, 1) if comp else None


def recalc_after_data_change(tenant_id: int, year: int):
    """A-016: `ProcessKpi.calculated_score` kolonu yılsızdır. Yalnız CARİ yıl (aktif plan
    yılı, yoksa takvim yılı) verisi değiştiğinde kalıcı yaz; geçmiş yıl düzeltmesi
    cari skoru ezmesin (skor yine canlı hesaplanır, yazılmaz)."""
    from app.services.plan_year_service import get_active_plan_year
    if not tenant_id:
        return eng.recalc_on_pg_data_change(tenant_id, year)
    apy = get_active_plan_year(tenant_id)
    cur = apy.year if apy else today_tr().year
    if year is None or int(year) == int(cur):
        return eng.recalc_on_pg_data_change(tenant_id, year)
    return eng.compute_vision_score(tenant_id, int(year), today_tr(), persist_pg_scores=False)
