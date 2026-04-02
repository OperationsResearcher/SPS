# -*- coding: utf-8 -*-
"""K-Vektör: vizyon 1000 ölçeği, ağırlıklı hiyerarşi (PG → süreç → alt → ana → vizyon)."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any, Dict, List, Optional, Tuple

from flask import current_app

from sqlalchemy.orm import joinedload

from app.models import db
from app.models.core import Strategy, SubStrategy
from app.models.k_vektor import KVektorStrategyWeight, KVektorSubStrategyWeight
from app.models.process import Process, ProcessSubStrategyLink
from app.services.score_engine_service import compute_process_scores_internal


def _allocate_quotas(
    ids: List[int],
    raw_by_id: Dict[int, Optional[float]],
    budget: float,
) -> Dict[int, float]:
    """Ham ağırlıklarla bütçeyi böl; boş veya sıfır toplamda eşit pay."""
    n = len(ids)
    if n == 0 or budget <= 0:
        return {}
    vals = []
    for i in ids:
        r = raw_by_id.get(i)
        v = float(r) if r is not None and float(r) > 0 else 0.0
        vals.append(v)
    s = sum(vals)
    if s <= 0:
        return {i: budget / n for i in ids}
    return {ids[j]: budget * vals[j] / s for j in range(n)}


def _link_fractions_for_process(process: Process) -> List[Tuple[int, float]]:
    """Süreç → alt strateji kesirleri (toplam 1 değil; yüzde/100)."""
    links = list(process.process_sub_strategy_links or [])
    if not links:
        return []
    n = len(links)
    pcts = [lnk.contribution_pct for lnk in links]
    if all(p is None for p in pcts):
        f = 1.0 / n
        return [(lnk.sub_strategy_id, f) for lnk in links]
    vals = [float(p) if p is not None else 0.0 for p in pcts]
    s = sum(vals)
    if s <= 0:
        f = 1.0 / n
        return [(links[i].sub_strategy_id, f) for i in range(n)]
    return [(links[i].sub_strategy_id, vals[i] / 100.0) for i in range(n)]


def compute_k_vektor_bundle(
    tenant_id: int,
    year: int,
    as_of: date,
    persist_pg_scores: bool = True,
) -> Dict[str, Any]:
    """
    K-Vektör vizyon skoru (0–1000) ve ara skorlar.
    `vision_score` alanı geriye dönük uyum için 0–100: min(100, vision_1000 / 10).
    """
    process_scores, pg_scores = compute_process_scores_internal(
        tenant_id, year, as_of, persist_pg_scores
    )

    processes = (
        Process.query.filter_by(tenant_id=tenant_id, is_active=True)
        .options(joinedload(Process.process_sub_strategy_links))
        .all()
    )

    num: Dict[int, float] = defaultdict(float)
    den: Dict[int, float] = defaultdict(float)

    for proc in processes:
        sc = float(process_scores.get(proc.id, 0.0))
        for sid, frac in _link_fractions_for_process(proc):
            num[sid] += sc * frac
            den[sid] += frac

    sub_strategies = (
        SubStrategy.query.join(Strategy)
        .filter(Strategy.tenant_id == tenant_id, Strategy.is_active.is_(True))
        .filter(SubStrategy.is_active.is_(True))
        .all()
    )

    sub_strategy_scores: Dict[int, float] = {}
    for ss in sub_strategies:
        d = den.get(ss.id, 0.0)
        if d <= 1e-12:
            sub_strategy_scores[ss.id] = 0.0
        else:
            t = min(100.0, max(0.0, num[ss.id] / d))
            sub_strategy_scores[ss.id] = round(t, 2)

    strat_rows = (
        KVektorStrategyWeight.query.filter_by(tenant_id=tenant_id).all()
    )
    raw_main: Dict[int, Optional[float]] = {r.strategy_id: r.weight_raw for r in strat_rows}

    sub_w_rows = (
        KVektorSubStrategyWeight.query.filter_by(tenant_id=tenant_id).all()
    )
    raw_sub: Dict[int, Optional[float]] = {r.sub_strategy_id: r.weight_raw for r in sub_w_rows}

    strategies = (
        Strategy.query.filter_by(tenant_id=tenant_id, is_active=True)
        .order_by(Strategy.code)
        .all()
    )
    main_ids = [s.id for s in strategies]
    quotas_main = _allocate_quotas(main_ids, raw_main, 1000.0)

    strategy_scores: Dict[int, float] = {}
    contrib_main: Dict[int, float] = {}

    vision_accum = 0.0
    for st in strategies:
        V_m = quotas_main.get(st.id, 0.0)
        alts = [a for a in st.sub_strategies if a.is_active]
        if not alts:
            strategy_scores[st.id] = 0.0
            contrib_main[st.id] = 0.0
            continue
        sub_ids = [a.id for a in alts]
        sub_raw = {sid: raw_sub.get(sid) for sid in sub_ids}
        U = _allocate_quotas(sub_ids, sub_raw, V_m)

        s_m = 0.0
        if V_m > 1e-12:
            for a in alts:
                Uj = U.get(a.id, 0.0)
                tj = sub_strategy_scores.get(a.id, 0.0)
                s_m += Uj * tj
            s_m = s_m / V_m
        s_m = min(100.0, max(0.0, s_m))
        strategy_scores[st.id] = round(s_m, 2)
        c_m = V_m * (s_m / 100.0)
        contrib_main[st.id] = round(c_m, 6)
        vision_accum += c_m

    vision_1000 = min(1000.0, max(0.0, round(vision_accum, 4)))
    # Son düzeltme: çok küçük kaydırma
    if vision_1000 > 1000.0:
        vision_1000 = 1000.0

    vision_legacy = min(100.0, vision_1000 / 10.0)

    if persist_pg_scores:
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"[k_vektor_engine] commit: {e}", exc_info=True)

    return {
        "vision_score": vision_legacy,
        "vision_score_1000": vision_1000,
        "k_vektor": True,
        "as_of_date": as_of.isoformat(),
        "tenant_id": tenant_id,
        "year": year,
        "strategy_scores": strategy_scores,
        "sub_strategy_scores": sub_strategy_scores,
        "process_scores": process_scores,
        "pg_scores": {k: v for k, v in pg_scores.items() if v is not None},
        "k_vektor_quotas_main": {str(k): round(v, 4) for k, v in quotas_main.items()},
        "k_vektor_contrib_main": {str(k): v for k, v in contrib_main.items()},
    }
