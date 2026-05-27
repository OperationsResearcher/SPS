# -*- coding: utf-8 -*-
"""Plan Year Diff — iki yılı karşılaştırıp neyin değiştiğini üretir.

Çıktı: kategori bazlı değişim listesi (yeni, silinen, yeniden adlandırılan,
ağırlığı değişen, taşınan). Tomofil meta'sındaki `override_ozet` formatının
canlı versiyonu.

Tasarım: clone birincil (`entity.plan_year_id`). İki yılın kaydını
`source_*_id` zinciriyle veya kod eşleşmesiyle bağdaştırır.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import or_

from app.models import db
from app.models.plan_year import PlanYear
from app.models.core import Strategy, SubStrategy
from app.models.process import Process, ProcessKpi, ProcessSubStrategyLink
from app.models.swot import SwotAnalysis, PestelAnalysis, PorterFiveForcesAnalysis
from app.models.initiative import Initiative
from app.models.okr import OkrObjective
from app.models.tenant_year import TenantYearIdentity


# ── Eşleştirme yardımcısı ───────────────────────────────────────────────────

def _index_by(rows, key_attr: str) -> Dict[Any, Any]:
    """Liste → dict: rows[i].<key_attr> → row. None/boş atlanır."""
    out = {}
    for r in rows:
        k = getattr(r, key_attr, None)
        if k:
            out[k] = r
    return out


def _match_by_lineage_or_code(rows_a, rows_b) -> List[Tuple[Optional[Any], Optional[Any]]]:
    """A ve B yılındaki kayıtları eşleştir.

    Strateji A: `source_*_id` chain (B → ata A varsa).
    Strateji B: kod eşleşmesi (her ikisinde aynı kod).
    Geriye `(a_row, b_row)` listesi — biri None olabilir (yeni/silinen).
    """
    a_by_id = {r.id: r for r in rows_a}
    a_by_code = _index_by(rows_a, "code")
    b_by_code = _index_by(rows_b, "code")

    pairs: List[Tuple[Optional[Any], Optional[Any]]] = []
    matched_a_ids: set = set()

    for b in rows_b:
        # 1) source chain
        src_id = getattr(b, "source_strategy_id", None) \
              or getattr(b, "source_sub_strategy_id", None) \
              or getattr(b, "source_process_id", None) \
              or getattr(b, "source_kpi_id", None)
        a = a_by_id.get(src_id) if src_id else None
        # 2) kod eşleşmesi (fallback)
        if a is None and getattr(b, "code", None):
            a = a_by_code.get(b.code)
        if a is not None:
            pairs.append((a, b))
            matched_a_ids.add(a.id)
        else:
            pairs.append((None, b))  # yeni eklenen

    # A'da var ama B'de yok → silinen
    for a in rows_a:
        if a.id not in matched_a_ids:
            pairs.append((a, None))

    return pairs


# ── Tek kategori diff ───────────────────────────────────────────────────────

def _diff_entities(
    rows_a, rows_b,
    label_fn,
    fields: List[str],
) -> Dict[str, List[Dict[str, Any]]]:
    """Genel diff hesaplayıcı.

    Args:
        rows_a, rows_b: A ve B yılının kayıtları
        label_fn: row → kullanıcı-okur etiket (ör. 'ST3 - Üretim Dönüşümü')
        fields: değişim takip edilecek alan adları
    Returns:
        {"added": [...], "removed": [...], "changed": [...]}
    """
    pairs = _match_by_lineage_or_code(rows_a, rows_b)
    added, removed, changed = [], [], []

    for a, b in pairs:
        if a is None and b is not None:
            added.append({"label": label_fn(b), "id": b.id})
        elif b is None and a is not None:
            removed.append({"label": label_fn(a), "id": a.id})
        elif a is not None and b is not None:
            diffs = {}
            for f in fields:
                va = getattr(a, f, None)
                vb = getattr(b, f, None)
                if va != vb:
                    diffs[f] = {"from": va, "to": vb}
            if diffs:
                changed.append({
                    "label_from": label_fn(a),
                    "label_to": label_fn(b),
                    "changes": diffs,
                    "a_id": a.id, "b_id": b.id,
                })

    return {"added": added, "removed": removed, "changed": changed}


# ── Üst-seviye diff: iki yıl arası tüm değişimler ────────────────────────────

def diff_plan_years(tenant_id: int, year_a: int, year_b: int) -> Dict[str, Any]:
    """`year_a` → `year_b` arasındaki değişiklikleri kategori bazlı döner."""
    py_a = PlanYear.query.filter_by(tenant_id=tenant_id, year=year_a).first()
    py_b = PlanYear.query.filter_by(tenant_id=tenant_id, year=year_b).first()
    if not py_a or not py_b:
        return {"error": "Karşılaştırılacak plan yıllarından biri bulunamadı.",
                "year_a": year_a, "year_b": year_b}

    out: Dict[str, Any] = {
        "tenant_id": tenant_id,
        "year_a": year_a, "year_b": year_b,
        "plan_year_a_id": py_a.id, "plan_year_b_id": py_b.id,
    }

    # ── Vizyon / kimlik ─────────────────────────────────────────────────
    id_a = TenantYearIdentity.query.filter_by(plan_year_id=py_a.id).first()
    id_b = TenantYearIdentity.query.filter_by(plan_year_id=py_b.id).first()
    identity_diffs = {}
    if id_a or id_b:
        for f in ("purpose", "vision", "core_values", "code_of_ethics", "quality_policy"):
            va = getattr(id_a, f, None) if id_a else None
            vb = getattr(id_b, f, None) if id_b else None
            if (va or "") != (vb or ""):
                identity_diffs[f] = {"from": va, "to": vb}
    out["identity"] = identity_diffs

    # ── Ana stratejiler ─────────────────────────────────────────────────
    strat_a = Strategy.query.filter_by(tenant_id=tenant_id, plan_year_id=py_a.id, is_active=True).all()
    strat_b = Strategy.query.filter_by(tenant_id=tenant_id, plan_year_id=py_b.id, is_active=True).all()
    out["strategies"] = _diff_entities(
        strat_a, strat_b,
        label_fn=lambda r: f"{r.code or '?'} - {r.title or ''}".strip(' -'),
        fields=["code", "title", "description"],
    )

    # ── Alt stratejiler ─────────────────────────────────────────────────
    strat_a_ids = [s.id for s in strat_a] or [0]
    strat_b_ids = [s.id for s in strat_b] or [0]
    sub_a = SubStrategy.query.filter(SubStrategy.strategy_id.in_(strat_a_ids), SubStrategy.is_active.is_(True)).all()
    sub_b = SubStrategy.query.filter(SubStrategy.strategy_id.in_(strat_b_ids), SubStrategy.is_active.is_(True)).all()
    out["sub_strategies"] = _diff_entities(
        sub_a, sub_b,
        label_fn=lambda r: f"{r.code or '?'} - {r.title or ''}".strip(' -'),
        fields=["code", "title", "description"],
    )

    # ── Süreçler ────────────────────────────────────────────────────────
    proc_a = Process.query.filter_by(tenant_id=tenant_id, plan_year_id=py_a.id, is_active=True).all()
    proc_b = Process.query.filter_by(tenant_id=tenant_id, plan_year_id=py_b.id, is_active=True).all()
    out["processes"] = _diff_entities(
        proc_a, proc_b,
        label_fn=lambda r: f"{r.code or '?'} - {r.name or ''}".strip(' -'),
        fields=["code", "name", "weight", "status"],
    )

    # ── PG (process_kpis) ───────────────────────────────────────────────
    proc_a_ids = [p.id for p in proc_a] or [0]
    proc_b_ids = [p.id for p in proc_b] or [0]
    kpi_a = ProcessKpi.query.filter(ProcessKpi.process_id.in_(proc_a_ids), ProcessKpi.is_active.is_(True)).all()
    kpi_b = ProcessKpi.query.filter(ProcessKpi.process_id.in_(proc_b_ids), ProcessKpi.is_active.is_(True)).all()
    out["kpis"] = _diff_entities(
        kpi_a, kpi_b,
        label_fn=lambda r: f"{r.code or '?'} - {r.name or ''}".strip(' -'),
        fields=["code", "name", "target_value", "unit", "weight", "direction"],
    )

    # ── SWOT/PESTEL/Porter (içerik diff yapmıyor, sadece var/yok + plan_year) ─
    def _has(model, py_id):
        return model.query.filter_by(tenant_id=tenant_id, plan_year_id=py_id).first() is not None
    out["analyses"] = {
        "swot": {"a": _has(SwotAnalysis, py_a.id), "b": _has(SwotAnalysis, py_b.id)},
        "pestel": {"a": _has(PestelAnalysis, py_a.id), "b": _has(PestelAnalysis, py_b.id)},
        "porter": {"a": _has(PorterFiveForcesAnalysis, py_a.id), "b": _has(PorterFiveForcesAnalysis, py_b.id)},
    }

    # ── Initiatives ─────────────────────────────────────────────────────
    # Initiative yıllı değil, span. A yılını span'e dahil eden initiatives vs B yılı.
    inits_a = Initiative.query.filter(
        Initiative.tenant_id == tenant_id,
        Initiative.is_active.is_(True),
        Initiative.start_year <= year_a,
        Initiative.end_year >= year_a,
    ).all()
    inits_b = Initiative.query.filter(
        Initiative.tenant_id == tenant_id,
        Initiative.is_active.is_(True),
        Initiative.start_year <= year_b,
        Initiative.end_year >= year_b,
    ).all()
    a_ids = {i.id for i in inits_a}
    b_ids = {i.id for i in inits_b}
    out["initiatives"] = {
        "started_in_b": [{"id": i.id, "label": f"{i.code or ''} {i.name}".strip()}
                         for i in inits_b if i.id not in a_ids],
        "ended_after_a": [{"id": i.id, "label": f"{i.code or ''} {i.name}".strip()}
                          for i in inits_a if i.id not in b_ids],
        "continuing": len(a_ids & b_ids),
    }

    # ── OKR (içerik diff'i değil sayım) ─────────────────────────────────
    okr_a_count = OkrObjective.query.filter_by(tenant_id=tenant_id, plan_year_id=py_a.id, is_active=True).count()
    okr_b_count = OkrObjective.query.filter_by(tenant_id=tenant_id, plan_year_id=py_b.id, is_active=True).count()
    out["okr"] = {"count_a": okr_a_count, "count_b": okr_b_count}

    # ── Süreç ↔ Alt-strateji bağ haritası diff ──────────────────────────
    link_a = ProcessSubStrategyLink.query.filter(
        ProcessSubStrategyLink.process_id.in_(proc_a_ids)
    ).all()
    link_b = ProcessSubStrategyLink.query.filter(
        ProcessSubStrategyLink.process_id.in_(proc_b_ids)
    ).all()
    out["links"] = {"a_count": len(link_a), "b_count": len(link_b)}

    # ── Özet sayılar ────────────────────────────────────────────────────
    out["summary"] = {
        "identity_changed_fields": len(identity_diffs),
        "strategies": {k: len(v) for k, v in out["strategies"].items()},
        "sub_strategies": {k: len(v) for k, v in out["sub_strategies"].items()},
        "processes": {k: len(v) for k, v in out["processes"].items()},
        "kpis": {k: len(v) for k, v in out["kpis"].items()},
    }
    return out
