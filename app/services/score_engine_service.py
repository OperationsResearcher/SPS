# -*- coding: utf-8 -*-
"""
Score Engine Service
PG verisinden Vizyon puanına hiyerarşik skorlama.
PG -> Süreç -> Alt Strateji -> Ana Strateji -> Vizyon (0-100)

Soft Delete: Sadece is_active=True olan Process, ProcessKpi, SubStrategy, Strategy ve KpiData
kayıtları hesaplamaya dahil edilir.

Cache: Vision score ve ara hesaplamalar cache'lenir.
"""
from datetime import date
from typing import Optional, Dict, Any

from flask import current_app

from app.models import db
from app.models.process import Process, ProcessKpi, KpiData
from app.models.core import SubStrategy, Strategy
from app.extensions import cache
from app.utils.cache_utils import CACHE_KEYS


def _parse_float(val) -> Optional[float]:
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    try:
        s = str(val).strip().replace(',', '.')
        return float(s) if s else None
    except (ValueError, TypeError):
        return None


def compute_pg_score(
    hedef_val: Optional[float],
    gerceklesen_val: Optional[float],
    direction: str = 'Increasing'
) -> Optional[float]:
    """PG başarı puanı (0-100). Hedef yönüne göre oran hesaplanır."""
    if hedef_val is None or gerceklesen_val is None:
        return None
    try:
        hedef_f = float(hedef_val)
        gercek_f = float(gerceklesen_val)
    except (TypeError, ValueError):
        return None
    if hedef_f == 0:
        return None
    dir_ = (direction or 'Increasing').strip()
    if dir_.lower() == 'decreasing':
        if gercek_f == 0:
            return None
        ratio = hedef_f / gercek_f
    else:
        ratio = gercek_f / hedef_f
    return round(min(100.0, max(0.0, ratio * 100.0)), 2)


def _default_weight(weight: Optional[float], sibling_count: int) -> float:
    if sibling_count <= 0:
        return 100.0
    if weight is not None and weight > 0:
        return min(100.0, max(0.0, float(weight)))
    return 100.0 / sibling_count


def get_pg_scores_from_kpi_data(
    tenant_id: int,
    year: Optional[int] = None,
    as_of_date: Optional[date] = None
) -> Dict[int, Optional[float]]:
    """Her ProcessKpi için KpiData'dan hesaplanan skoru döner."""
    if year is None:
        year = date.today().year
    as_of = as_of_date or date.today()

    pgs = (
        ProcessKpi.query
        .join(Process)
        .filter(Process.tenant_id == tenant_id, Process.is_active == True)
        .filter(ProcessKpi.is_active == True)
        .all()
    )
    out = {}
    for pg in pgs:
        entries = (
            KpiData.query.filter_by(process_kpi_id=pg.id, year=year, is_active=True)
            .filter(KpiData.data_date <= as_of)
            .order_by(KpiData.data_date.desc())
            .limit(100)
        ).all()
        if not entries:
            out[pg.id] = None
            continue
        target = _parse_float(pg.target_value)
        actual_values = [_parse_float(e.actual_value) for e in entries]
        actual_values = [v for v in actual_values if v is not None]
        if not actual_values:
            out[pg.id] = None
            continue
        if pg.data_collection_method in ('Toplama', 'Toplam'):
            actual = sum(actual_values)
        elif pg.data_collection_method == 'Son Değer':
            actual = actual_values[0]
        else:
            actual = sum(actual_values) / len(actual_values)
        score = compute_pg_score(target, actual, pg.direction or 'Increasing')
        out[pg.id] = score
    return out


def compute_vision_score(
    tenant_id: int,
    year: Optional[int] = None,
    as_of_date: Optional[date] = None,
    persist_pg_scores: bool = True
) -> Dict[str, Any]:
    """
    Hiyerarşik vizyon puanı hesaplar.
    PG -> Süreç -> Alt Strateji -> Ana Strateji -> Vizyon (0-100)
    """
    if year is None:
        year = date.today().year
    as_of = as_of_date or date.today()

    try:
        pg_scores = get_pg_scores_from_kpi_data(tenant_id, year, as_of)

        processes = Process.query.filter_by(
            tenant_id=tenant_id,
            is_active=True
        ).all()
        children_by_parent = {}
        for p in processes:
            pid = p.parent_id
            if pid not in children_by_parent:
                children_by_parent[pid] = []
            children_by_parent[pid].append(p.id)

        process_scores = {}

        def calc_process_score(process_id: int) -> float:
            if process_id in process_scores:
                return process_scores[process_id]
            proc = next((p for p in processes if p.id == process_id), None)
            if not proc:
                return 0.0
            child_ids = children_by_parent.get(process_id, [])
            if child_ids:
                n = len(child_ids)
                total = 0.0
                w_sum = 0.0
                for cid in child_ids:
                    c = next((p for p in processes if p.id == cid), None)
                    w = _default_weight(c.weight if c else None, n)
                    total += calc_process_score(cid) * w
                    w_sum += w
                process_scores[process_id] = round(total / w_sum, 2) if (w_sum and w_sum > 0) else 0.0
                return process_scores[process_id]
            kpis = ProcessKpi.query.filter_by(process_id=process_id, is_active=True).all()
            if not kpis:
                process_scores[process_id] = 0.0
                return 0.0
            n = len(kpis)
            total = 0.0
            w_sum = 0.0
            for kpi in kpis:
                w = _default_weight(kpi.weight, n)
                sc = pg_scores.get(kpi.id)
                if sc is None:
                    sc = 0.0
                total += sc * w
                w_sum += w
                if persist_pg_scores:
                    kpi.calculated_score = sc
            process_scores[process_id] = round(total / w_sum, 2) if (w_sum and w_sum > 0) else 0.0
            return process_scores[process_id]

        for p in processes:
            if p.id not in process_scores:
                calc_process_score(p.id)

        sub_strategies = (
            SubStrategy.query
            .join(Strategy)
            .filter(Strategy.tenant_id == tenant_id, Strategy.is_active == True)
            .filter(SubStrategy.is_active == True)
            .all()
        )
        sub_strategy_scores = {}
        for ss in sub_strategies:
            linked_processes = list(ss.processes) if hasattr(ss, 'processes') else []
            linked_processes = [p for p in linked_processes if p.is_active]
            if not linked_processes:
                sub_strategy_scores[ss.id] = 0.0
                continue
            total = sum(process_scores.get(p.id, 0.0) for p in linked_processes)
            n_linked = len(linked_processes)
            sub_strategy_scores[ss.id] = round(total / n_linked, 2) if n_linked > 0 else 0.0

        strategies = Strategy.query.filter_by(
            tenant_id=tenant_id,
            is_active=True
        ).all()
        strategy_scores = {}
        for st in strategies:
            alts = [a for a in st.sub_strategies if a.is_active]
            if not alts:
                strategy_scores[st.id] = 0.0
                continue
            total = sum(sub_strategy_scores.get(a.id, 0.0) for a in alts)
            n_alts = len(alts)
            strategy_scores[st.id] = round(total / n_alts, 2) if n_alts > 0 else 0.0

        if not strategies:
            vision = 0.0
        else:
            total = sum(strategy_scores.get(s.id, 0.0) for s in strategies)
            n_strat = len(strategies)
            vision = round(total / n_strat, 2) if n_strat > 0 else 0.0

        vision = min(100.0, max(0.0, vision))

        if persist_pg_scores:
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"[score_engine_service] Veritabanı commit hatası: {e}", exc_info=True)

        return {
            'vision_score': vision,
            'as_of_date': as_of.isoformat(),
            'tenant_id': tenant_id,
            'year': year,
            'strategy_scores': strategy_scores,
            'sub_strategy_scores': sub_strategy_scores,
            'process_scores': process_scores,
            'pg_scores': {k: v for k, v in pg_scores.items() if v is not None},
        }
    except Exception as e:
        current_app.logger.error(
            f"[score_engine_service] Vizyon skoru hesaplanırken hata oluştu (tenant_id={tenant_id}, year={year}): {e}",
            exc_info=True
        )
        raise


def recalc_on_pg_data_change(
    tenant_id: Optional[int],
    year: Optional[int] = None,
    as_of_date: Optional[date] = None
) -> Dict[str, Any]:
    """PG verisi değiştiğinde skor motorunu tetikler."""
    if not tenant_id:
        return {
            'vision_score': 0.0,
            'as_of_date': (as_of_date or date.today()).isoformat(),
            'tenant_id': None
        }
    return compute_vision_score(
        tenant_id,
        year or date.today().year,
        as_of_date or date.today(),
        persist_pg_scores=True
    )
