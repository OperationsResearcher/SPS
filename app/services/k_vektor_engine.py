# -*- coding: utf-8 -*-
"""K-Vektör: vizyon 1000 ölçeği, ağırlıklı hiyerarşi (PG → süreç → alt → ana → vizyon)."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any, Dict, List, Optional, Tuple

from flask import current_app

from sqlalchemy import or_, and_
from sqlalchemy.orm import joinedload, selectinload

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
    plan_year=None,  # PlanYear instance; None → tenant bazlı fallback
) -> Dict[str, Any]:
    """
    K-Vektör vizyon skoru (0–1000) ve ara skorlar.
    `vision_score` alanı geriye dönük uyum için 0–100: min(100, vision_1000 / 10).
    plan_year verilirse hesaplama yalnızca o dönemin kayıtlarını kapsar.
    """
    process_scores, pg_scores = compute_process_scores_internal(
        tenant_id, year, as_of, persist_pg_scores, plan_year=plan_year
    )

    if plan_year is not None:
        processes = (
            Process.query.filter(
                Process.is_active == True,
                or_(
                    Process.plan_year_id == plan_year.id,
                    and_(Process.plan_year_id.is_(None), Process.tenant_id == tenant_id),
                ),
            )
            .options(joinedload(Process.process_sub_strategy_links))
            .all()
        )
    else:
        processes = (
            Process.query.filter_by(tenant_id=tenant_id, is_active=True)
            .options(joinedload(Process.process_sub_strategy_links))
            .all()
        )

    num: Dict[int, float] = defaultdict(float)
    den: Dict[int, float] = defaultdict(float)

    for proc in processes:
        # B1/M4: ölçülemeyen süreç (skor None — o dönemde veri yok veya
        # hedefi sayısal değil) alt stratejinin PAYDASINA da girmez.
        # Eskiden `or 0.0` ile sıfır sayılıyordu → veri girilmemiş süreç
        # alt strateji skorunu dibe çekiyordu. Paydaya girmeyince, alt
        # strateji "ölçtüğü süreçlerin ağırlıklı ortalaması" olur; hiçbiri
        # ölçülemiyorsa payda 0 kalır ve aşağıda None'a düşer.
        raw = process_scores.get(proc.id)
        if raw is None:
            continue
        sc = float(raw)
        for sid, frac in _link_fractions_for_process(proc):
            num[sid] += sc * frac
            den[sid] += frac

    if plan_year is not None:
        sub_strategies = (
            SubStrategy.query.join(Strategy)
            .filter(
                Strategy.is_active.is_(True),
                SubStrategy.is_active.is_(True),
                or_(
                    Strategy.plan_year_id == plan_year.id,
                    and_(Strategy.plan_year_id.is_(None), Strategy.tenant_id == tenant_id),
                ),
            )
            .all()
        )
    else:
        sub_strategies = (
            SubStrategy.query.join(Strategy)
            .filter(Strategy.tenant_id == tenant_id, Strategy.is_active.is_(True))
            .filter(SubStrategy.is_active.is_(True))
            .all()
        )

    # B1/M4 (2026-07-21): payda sıfırsa (= alt stratejiye bağlı ölçülebilir
    # süreç yok) skor 0.0 değil None'dır. Ölçüm: 754 aktif alt stratejinin
    # 230'u hiç aktif sürece bağlı değil; bunları "tamamen başarısız" saymak
    # Tomofil'de vizyonu 55.78 gösteriyordu (ölçülenlerin ortalaması 93.75),
    # KMF'de 6.48 (gerçek 27.73).
    sub_strategy_scores: Dict[int, Optional[float]] = {}
    for ss in sub_strategies:
        d = den.get(ss.id, 0.0)
        if d <= 1e-12:
            sub_strategy_scores[ss.id] = None  # ölçülmedi ≠ 0
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

    # N+1 önlemi: aşağıda st.sub_strategies iterate ediliyor
    if plan_year is not None:
        strategies = (
            Strategy.query.options(selectinload(Strategy.sub_strategies))
            .filter(
                Strategy.is_active == True,
                or_(
                    Strategy.plan_year_id == plan_year.id,
                    and_(Strategy.plan_year_id.is_(None), Strategy.tenant_id == tenant_id),
                ),
            )
            .order_by(Strategy.code)
            .all()
        )
    else:
        strategies = (
            Strategy.query.options(selectinload(Strategy.sub_strategies))
            .filter_by(tenant_id=tenant_id, is_active=True)
            .order_by(Strategy.code)
            .all()
        )
    main_ids = [s.id for s in strategies]
    quotas_main = _allocate_quotas(main_ids, raw_main, 1000.0)

    strategy_scores: Dict[int, float] = {}
    contrib_main: Dict[int, float] = {}

    vision_accum = 0.0
    kapsam_olculen_quota = 0.0   # ölçülebilen alt stratejilerin kota toplamı
    kapsam_toplam_quota = 0.0    # dağıtılan tüm kota
    for st in strategies:
        V_m = quotas_main.get(st.id, 0.0)
        kapsam_toplam_quota += V_m
        alts = [a for a in st.sub_strategies if a.is_active]
        # B1/M4: ölçülemeyen alt strateji ana strateji ortalamasını aşağı
        # çekmemeli. Kotası ÖLÇÜLENLERE YENİDEN DAĞITILIR — böylece ana
        # stratejinin skoru "ölçtüklerinin ağırlıklı ortalaması" olur.
        olculen_alts = [
            a for a in alts if sub_strategy_scores.get(a.id) is not None
        ]
        if not olculen_alts:
            strategy_scores[st.id] = None
            contrib_main[st.id] = 0.0
            continue
        sub_ids = [a.id for a in olculen_alts]
        sub_raw = {sid: raw_sub.get(sid) for sid in sub_ids}
        U = _allocate_quotas(sub_ids, sub_raw, V_m)

        s_m = 0.0
        if V_m > 1e-12:
            for a in olculen_alts:
                Uj = U.get(a.id, 0.0)
                tj = sub_strategy_scores.get(a.id) or 0.0
                s_m += Uj * tj
            s_m = s_m / V_m
        s_m = min(100.0, max(0.0, s_m))
        strategy_scores[st.id] = round(s_m, 2)
        c_m = V_m * (s_m / 100.0)
        contrib_main[st.id] = round(c_m, 6)
        vision_accum += c_m
        kapsam_olculen_quota += V_m

    # B1/M4: `vision_accum` yalnız ÖLÇÜLEBİLEN ana stratejilerin katkısını
    # taşır. 1000'lik tam kotaya bölmek, ölçülmemiş stratejinin kotasını
    # "sıfır puan" saymak demektir — düzeltmek istediğimiz hatanın ta kendisi.
    # Bu yüzden ölçülen kota tabanına göre ölçeklenir:
    #     vizyon = (ölçülen katkı / ölçülen kota) × 1000
    # Kapsam bilgisi ayrıca `kapsam` alanında döner; kullanıcı skorun ne
    # kadarlık bir tabana dayandığını görebilir.
    if kapsam_olculen_quota > 1e-12:
        vision_1000 = round(vision_accum / kapsam_olculen_quota * 1000.0, 4)
    else:
        vision_1000 = 0.0
    vision_1000 = min(1000.0, max(0.0, vision_1000))

    vision_legacy = min(100.0, vision_1000 / 10.0)

    _alt_toplam = len(sub_strategies)
    _alt_olculen = len([v for v in sub_strategy_scores.values() if v is not None])
    _ana_toplam = len(strategies)
    _ana_olculen = len([v for v in strategy_scores.values() if v is not None])
    kapsam = {
        "alt_strateji_toplam": _alt_toplam,
        "alt_strateji_olculen": _alt_olculen,
        "ana_strateji_toplam": _ana_toplam,
        "ana_strateji_olculen": _ana_olculen,
        "yuzde": round(_alt_olculen / _alt_toplam * 100, 1) if _alt_toplam else 0.0,
        # Skorun dayandığı ağırlık tabanı (1000 üzerinden).
        "olculen_kota": round(kapsam_olculen_quota, 2),
        "toplam_kota": round(kapsam_toplam_quota, 2),
    }

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
        # B1/M4: ölçülmemiş (None) girdiler dışarıya sızdırılmaz — tüketiciler
        # float bekliyor, None onların tarafında sessizce 0'a dönerdi.
        "strategy_scores": {k: v for k, v in strategy_scores.items() if v is not None},
        "sub_strategy_scores": {k: v for k, v in sub_strategy_scores.items() if v is not None},
        "process_scores": {k: v for k, v in process_scores.items() if v is not None},
        "pg_scores": {k: v for k, v in pg_scores.items() if v is not None},
        "k_vektor_quotas_main": {str(k): round(v, 4) for k, v in quotas_main.items()},
        "k_vektor_contrib_main": {str(k): v for k, v in contrib_main.items()},
        "kapsam": kapsam,
    }
