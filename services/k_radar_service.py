"""K-Radar hesaplama servisi (Faz-1 temel sürüm)."""

from __future__ import annotations

import logging
from typing import Any
from hashlib import sha1
from datetime import date, timedelta

from sqlalchemy import func, or_
from sqlalchemy.orm import selectinload
from app.extensions import cache

from app.models import db
from app.models.core import Strategy, User
from app.models.process import (
    IndividualKpiData,
    IndividualPerformanceIndicator,
    KpiData,
    Process,
    ProcessKpi,
)
from app.models.k_radar_domain import (
    A3Report,
    BottleneckLog,
    CompetitorAnalysis,
    EvmSnapshot,
    ProcessMaturity,
    RiskHeatmapItem,
    StakeholderSurvey,
    ValueChainItem,
)
from app.models.portfolio_project import Project, Task
from app.models.k_radar import KRadarRecommendationAction

logger = logging.getLogger(__name__)


# ── Scope (belge: docs/paketler/ROL-GORUNUM-KATMANI.md §5) ──────────────────
# Privileged kullanıcı → None (filtre yok = kurum geneli).
# Ayrıcalıksız lider → yönetici/üye olduğu süreç/proje id listesi.
# Not: bölünebilir bileşenler bu id listesiyle daraltılır; kurum-tekil
# bileşenler (SWOT/PESTEL/strateji) daraltılmaz.

def scoped_process_ids(user, tenant_id: int) -> list[int] | None:
    """Kullanıcının K-Radar'da görebileceği süreç id'leri.
    Privileged → None (kurum geneli). Aksi halde üye/lider/sahip süreçleri."""
    from micro.modules.surec.permissions import is_privileged, accessible_processes_filter
    if is_privileged(user):
        return None
    q = accessible_processes_filter(db.session.query(Process.id), user, tenant_id)
    return [row[0] for row in q.all()]


def scoped_project_ids(user, tenant_id: int) -> list[int] | None:
    """Kullanıcının K-Radar'da görebileceği proje id'leri.
    Privileged → None (kurum geneli). Aksi halde yönetici/üye/gözlemci projeleri."""
    from micro.modules.proje.permissions import is_privileged, accessible_projects_query
    if is_privileged(user):
        return None
    q = accessible_projects_query(db.session.query(Project.id), user, tenant_id)
    return [row[0] for row in q.all()]


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", ".")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _score_to_band(score: float) -> str:
    if score >= 80:
        return "green"
    if score >= 60:
        return "yellow"
    return "red"


def _weighted_score(raw_values: list[tuple[float, float]]) -> float:
    total_weight = 0.0
    weighted_sum = 0.0
    for score, weight in raw_values:
        w = max(float(weight or 0.0), 0.0)
        total_weight += w
        weighted_sum += float(score) * w
    if total_weight <= 0:
        return 0.0
    return round(weighted_sum / total_weight, 2)


def _process_component(tenant_id: int, process_ids: list[int] | None = None) -> dict[str, Any]:
    q = (
        ProcessKpi.query.join(Process, Process.id == ProcessKpi.process_id)
        .filter(
            Process.tenant_id == tenant_id,
            Process.is_active.is_(True),
            ProcessKpi.is_active.is_(True),
        )
    )
    if process_ids is not None:
        q = q.filter(Process.id.in_(process_ids))
    kpis = q.all()
    # Her KPI'nın son verisini batch'le çek (N+1 önlemi)
    from collections import defaultdict as _dd
    _kpi_ids = [k.id for k in kpis]
    _latest_by_kid: dict = {}
    if _kpi_ids:
        for d in KpiData.query.filter(
            KpiData.process_kpi_id.in_(_kpi_ids),
            KpiData.is_active == True,
        ).order_by(KpiData.process_kpi_id, KpiData.data_date.desc()).all():
            if d.process_kpi_id not in _latest_by_kid:
                _latest_by_kid[d.process_kpi_id] = d

    rows: list[tuple[float, float]] = []
    critical_count = 0
    for kpi in kpis:
        latest = _latest_by_kid.get(kpi.id)
        if not latest:
            continue
        actual = _to_float(latest.actual_value)
        target = _to_float(latest.target_value)
        if actual is None or target is None or target <= 0:
            continue
        perf = max(min((actual / target) * 100.0, 150.0), 0.0)
        weight = float(kpi.weight or 1.0)
        rows.append((perf, weight))
        if perf < 70:
            critical_count += 1
    score = _weighted_score(rows)
    band = _score_to_band(score)
    if critical_count >= 3:
        band = "red"
    return {
        "score": score,
        "band": band,
        "critical_count": critical_count,
        "kpi_count": len(rows),
    }


def _project_component(tenant_id: int, project_ids: list[int] | None = None) -> dict[str, Any]:
    _pq = Project.query.filter_by(tenant_id=tenant_id, is_archived=False)
    if project_ids is not None:
        _pq = _pq.filter(Project.id.in_(project_ids))
    active_projects = _pq.all()
    if not active_projects:
        return {"score": 0.0, "band": "red", "critical_count": 0, "project_count": 0}
    # Tüm projelerin geciken görev sayısını batch'le (N+1 önlemi)
    _pids = [p.id for p in active_projects]
    _delayed_by_pid: dict = {}
    if _pids:
        _delayed_rows = db.session.query(Task.project_id, func.count(Task.id)).filter(
            Task.project_id.in_(_pids),
            Task.is_archived == False,
            Task.due_date.isnot(None),
            Task.status != "Tamamlandı",
            Task.due_date < func.current_date(),
        ).group_by(Task.project_id).all()
        _delayed_by_pid = {pid: cnt for pid, cnt in _delayed_rows}

    rows: list[tuple[float, float]] = []
    critical_count = 0
    for project in active_projects:
        health = float(project.health_score or 0.0)
        delayed_tasks = _delayed_by_pid.get(project.id, 0)
        penalty = min(delayed_tasks * 5.0, 35.0)
        proj_score = max(health - penalty, 0.0)
        rows.append((proj_score, 1.0))
        if proj_score < 60:
            critical_count += 1
    score = _weighted_score(rows)
    band = _score_to_band(score)
    if critical_count >= 2:
        band = "red"
    return {
        "score": score,
        "band": band,
        "critical_count": critical_count,
        "project_count": len(active_projects),
    }


def _individual_component(tenant_id: int) -> dict[str, Any]:
    indicators = (
        IndividualPerformanceIndicator.query.join(User, User.id == IndividualPerformanceIndicator.user_id)
        .join(
            Process,
            Process.id == IndividualPerformanceIndicator.source_process_id,
            isouter=True,
        )
        .filter(
            IndividualPerformanceIndicator.is_active.is_(True),
            User.tenant_id == tenant_id,
            or_(
                Process.tenant_id == tenant_id,
                IndividualPerformanceIndicator.source_process_id.is_(None),
            ),
        )
        .all()
    )
    # Tüm indikatörler için en son IndividualKpiData'yı batch'le (N+1 önlemi)
    _ind_ids = [i.id for i in indicators]
    _latest_by_ind: dict = {}
    if _ind_ids:
        for d in IndividualKpiData.query.filter(
            IndividualKpiData.individual_pg_id.in_(_ind_ids),
        ).order_by(IndividualKpiData.individual_pg_id, IndividualKpiData.data_date.desc()).all():
            if d.individual_pg_id not in _latest_by_ind:
                _latest_by_ind[d.individual_pg_id] = d

    rows: list[tuple[float, float]] = []
    critical_count = 0
    for indicator in indicators:
        latest = _latest_by_ind.get(indicator.id)
        if not latest:
            continue
        actual = _to_float(latest.actual_value)
        target = _to_float(latest.target_value)
        if actual is None or target is None or target <= 0:
            continue
        perf = max(min((actual / target) * 100.0, 150.0), 0.0)
        weight = float(indicator.weight or 1.0)
        rows.append((perf, weight))
        if perf < 70:
            critical_count += 1
    score = _weighted_score(rows)
    band = _score_to_band(score)
    if critical_count >= 4:
        band = "red"
    return {
        "score": score,
        "band": band,
        "critical_count": critical_count,
        "indicator_count": len(rows),
    }


def _ks_component(tenant_id: int) -> dict[str, Any]:
    strategy_count = Strategy.query.filter_by(tenant_id=tenant_id, is_active=True).count()
    process_count = Process.query.filter_by(tenant_id=tenant_id, is_active=True).count()
    if strategy_count <= 0:
        return {"score": 0.0, "band": "red", "strategy_count": 0, "process_count": process_count}
    ratio = min((process_count / strategy_count) * 100.0, 100.0)
    score = round(ratio, 2)
    return {
        "score": score,
        "band": _score_to_band(score),
        "strategy_count": strategy_count,
        "process_count": process_count,
    }


def _get_radar_weights(tenant_id: int) -> tuple[float, float, float, float]:
    """Tenant'a özgü K-Radar ağırlıklarını döner (ks, kp, kpr, bireysel)."""
    try:
        from app.models.system_setting import SystemSetting
        import json
        key = f"k_radar_weights_{tenant_id}"
        row = SystemSetting.query.filter_by(key=key).first()
        if row:
            w = json.loads(row.value)
            return (
                float(w.get("ks", 2.0)),
                float(w.get("kp", 3.0)),
                float(w.get("kpr", 3.0)),
                float(w.get("bireysel", 2.0)),
            )
    except Exception as e:
        logger.warning(f"[_get_radar_weights] suppressed: {e}")
    return 2.0, 3.0, 3.0, 2.0


@cache.memoize(timeout=300)
def get_hub_summary(
    tenant_id: int,
    scope_process_ids: tuple[int, ...] | None = None,
    scope_project_ids: tuple[int, ...] | None = None,
) -> dict[str, Any]:
    # scope_* None → kurum geneli (privileged). Tuple → lider kapsamı (belge §5).
    # ks/ind kurum-tekil kalır; yalnız kp/kpr daraltılır.
    ks = _ks_component(tenant_id)
    kp = _process_component(tenant_id, list(scope_process_ids) if scope_process_ids is not None else None)
    kpr = _project_component(tenant_id, list(scope_project_ids) if scope_project_ids is not None else None)
    ind = _individual_component(tenant_id)
    w_ks, w_kp, w_kpr, w_ind = _get_radar_weights(tenant_id)

    total = _weighted_score(
        [
            (ks["score"], w_ks),
            (kp["score"], w_kp),
            (kpr["score"], w_kpr),
            (ind["score"], w_ind),
        ]
    )
    band = _score_to_band(total)
    if kp["critical_count"] + kpr["critical_count"] + ind["critical_count"] >= 6:
        band = "red"

    return {
        "total_score": total,
        "total_band": band,
        "ks": ks,
        "kp": kp,
        "kpr": kpr,
        "individual": ind,
        "recommended_actions": get_recommendations_from_summary(
            {
                "total_score": total,
                "total_band": band,
                "ks": ks,
                "kp": kp,
                "kpr": kpr,
                "individual": ind,
            }
        ),
    }


@cache.memoize(timeout=300)
def get_ks_data(tenant_id: int) -> dict[str, Any]:
    return _ks_component(tenant_id)


@cache.memoize(timeout=300)
def get_ks_extended_data(tenant_id: int) -> dict[str, Any]:
    base = _ks_component(tenant_id)
    strategy_count = int(base.get("strategy_count") or 0)
    process_count = int(base.get("process_count") or 0)
    kpi_count = (
        ProcessKpi.query.join(Process, Process.id == ProcessKpi.process_id)
        .filter(Process.tenant_id == tenant_id, Process.is_active.is_(True), ProcessKpi.is_active.is_(True))
        .count()
    )
    kpi_rows = (
        KpiData.query.join(ProcessKpi, ProcessKpi.id == KpiData.process_kpi_id)
        .join(Process, Process.id == ProcessKpi.process_id)
        .filter(Process.tenant_id == tenant_id, Process.is_active.is_(True), KpiData.is_active.is_(True))
        .count()
    )
    return {
        "pestle": {
            "factors": 6,
            "coverage_score": min(100, strategy_count * 8 + process_count * 2),
            "strategy_count": strategy_count,
        },
        "tows": {
            "candidate_actions": max(0, strategy_count * 2),
            "linked_strategy_ratio": min(100, strategy_count * 12),
        },
        "gap": {
            "kpi_count": int(kpi_count or 0),
            "data_row_count": int(kpi_rows or 0),
            "gap_pressure": max(0, 100 - min(100, int(base.get("score") or 0))),
        },
        "okr": {
            "objective_count": strategy_count,
            "alignment_score": int(base.get("score") or 0),
        },
        "bsc": {
            "perspective_coverage": min(4, max(0, (int(kpi_count or 0) // 3) + 1 if kpi_count else 0)),
            "kpi_count": int(kpi_count or 0),
        },
        "efqm": {
            "criterion_coverage": min(7, max(0, (strategy_count // 2) + 1 if strategy_count else 0)),
            "readiness_score": min(100, int(base.get("score") or 0) + 10),
        },
        "hoshin": {
            "objective_focus": strategy_count,
            "deployment_score": min(100, strategy_count * 10 + process_count * 2),
        },
        "ansoff": {
            "growth_options": min(4, max(0, strategy_count // 2 + 1 if strategy_count else 0)),
            "risk_balance": max(0, 100 - abs(50 - min(100, strategy_count * 8))),
        },
        "bcg": {
            "portfolio_count": strategy_count,
            "balance_score": min(100, strategy_count * 7 + (process_count * 2)),
        },
    }


@cache.memoize(timeout=300)
def get_kp_data(tenant_id: int, scope_process_ids: tuple[int, ...] | None = None) -> dict[str, Any]:
    return _process_component(tenant_id, list(scope_process_ids) if scope_process_ids is not None else None)


@cache.memoize(timeout=300)
def get_kp_extended_data(tenant_id: int, scope_process_ids: tuple[int, ...] | None = None) -> dict[str, Any]:
    # scope None → kurum geneli. Tuple → yalnız o süreçlere bağlı veriler
    # (opsiyonel-bağlı tablolarda bağsız kayıtlar düşer; belge §5, TASK-244 kararı).
    _spids = list(scope_process_ids) if scope_process_ids is not None else None

    def _scope_proc(q):
        """Process.id üzerinden filtreli sorguya scope uygula."""
        return q.filter(Process.id.in_(_spids)) if _spids is not None else q

    base = _process_component(tenant_id, _spids)
    _pcq = Process.query.filter_by(tenant_id=tenant_id, is_active=True)
    if _spids is not None:
        _pcq = _pcq.filter(Process.id.in_(_spids))
    process_count = _pcq.count()
    kpi_count = _scope_proc(
        ProcessKpi.query.join(Process, Process.id == ProcessKpi.process_id)
        .filter(Process.tenant_id == tenant_id, Process.is_active.is_(True), ProcessKpi.is_active.is_(True))
    ).count()
    kpi_rows = _scope_proc(
        KpiData.query.join(ProcessKpi, ProcessKpi.id == KpiData.process_kpi_id)
        .join(Process, Process.id == ProcessKpi.process_id)
        .filter(Process.tenant_id == tenant_id, Process.is_active.is_(True), KpiData.is_active.is_(True))
    ).count()
    critical = int(base.get("critical_count") or 0)
    score = float(base.get("score") or 0.0)

    _mq = ProcessMaturity.query.filter_by(tenant_id=tenant_id, is_active=True)
    if _spids is not None:
        _mq = _mq.filter(ProcessMaturity.process_id.in_(_spids))
    maturity_rows = _mq.all()
    maturity_levels = [int(r.maturity_level or 0) for r in maturity_rows if r.maturity_level is not None]
    maturity_avg = round(sum(maturity_levels) / len(maturity_levels), 2) if maturity_levels else 0.0

    _bq = BottleneckLog.query.filter_by(tenant_id=tenant_id, is_active=True)
    if _spids is not None:
        _bq = _bq.filter(BottleneckLog.process_id.in_(_spids))
    bottlenecks = _bq.all()
    open_bottlenecks = [b for b in bottlenecks if b.resolved_at is None]
    severity_weight = {"low": 1, "medium": 2, "high": 3, "critical": 4}
    severity_points = sum(severity_weight.get(str((b.severity or "")).strip().lower(), 2) for b in open_bottlenecks)
    severity_index = min(100, severity_points * 8) if open_bottlenecks else min(100, critical * 20)

    _vq = ValueChainItem.query.filter_by(tenant_id=tenant_id, is_active=True)
    if _spids is not None:
        _vq = _vq.filter(ValueChainItem.linked_process_id.in_(_spids))
    value_items = _vq.all()
    mapped_process_ids = {int(v.linked_process_id) for v in value_items if v.linked_process_id}
    mapped_process_count = len(mapped_process_ids)
    waste_items = [v for v in value_items if (v.muda_type or "").strip()]
    waste_ratio = (len(waste_items) / len(value_items) * 100.0) if value_items else 0.0
    muda_risk = round(min(100.0, max(0.0, waste_ratio * 1.4)), 2) if value_items else round(max(0.0, 100.0 - score), 2)

    process_open_counts: dict[int, int] = {}
    for b in open_bottlenecks:
        pid = int(b.process_id or 0)
        if pid <= 0:
            continue
        process_open_counts[pid] = process_open_counts.get(pid, 0) + 1
    open_total = sum(process_open_counts.values())
    top3 = sorted(process_open_counts.values(), reverse=True)[:3]
    top_share = (sum(top3) / open_total * 100.0) if open_total else min(100.0, 20.0 + critical * 10.0)

    kpi_rows_all = _scope_proc(
        KpiData.query.join(ProcessKpi, ProcessKpi.id == KpiData.process_kpi_id)
        .join(Process, Process.id == ProcessKpi.process_id)
        .filter(Process.tenant_id == tenant_id, Process.is_active.is_(True), KpiData.is_active.is_(True))
    ).all()
    breach_count = 0
    ratio_pool: list[float] = []
    for row in kpi_rows_all:
        actual = _to_float(row.actual_value)
        target = _to_float(row.target_value)
        if actual is None or target is None or target <= 0:
            continue
        ratio = max(0.0, min(1.5, actual / target))
        ratio_pool.append(ratio)
        if ratio < 0.9:
            breach_count += 1
    observed_rows = len(ratio_pool)
    breach_risk = round((breach_count / observed_rows) * 100.0, 2) if observed_rows else min(100.0, critical * 15.0)

    kpi_row_counts = _scope_proc(
        db.session.query(ProcessKpi.id, func.count(KpiData.id))
        .join(Process, Process.id == ProcessKpi.process_id)
        .join(KpiData, KpiData.process_kpi_id == ProcessKpi.id, isouter=True)
        .filter(
            Process.tenant_id == tenant_id,
            Process.is_active.is_(True),
            ProcessKpi.is_active.is_(True),
            or_(KpiData.id.is_(None), KpiData.is_active.is_(True)),
        )
        .group_by(ProcessKpi.id)
    ).all()
    populated_series = sum(1 for _, cnt in kpi_row_counts if int(cnt or 0) >= 3)
    comparability_score = round((populated_series / max(1, int(kpi_count or 0))) * 100.0, 2) if kpi_count else 0.0
    period_row_count = observed_rows

    if ratio_pool:
        avg_ratio_pct = round((sum(ratio_pool) / len(ratio_pool)) * 100.0, 2)
        availability = round(min(100.0, max(0.0, avg_ratio_pct + 4.0)), 2)
        performance = round(min(100.0, max(0.0, avg_ratio_pct - 3.0)), 2)
        quality = round(min(100.0, max(0.0, avg_ratio_pct)), 2)
        oee_estimate = round((availability * performance * quality) / 10000.0, 2)
    else:
        availability = round(min(100.0, max(0.0, score + 5.0)), 2)
        performance = round(min(100.0, max(0.0, score - 5.0)), 2)
        quality = round(min(100.0, max(0.0, score)), 2)
        oee_estimate = round((availability * performance * quality) / 10000.0, 2)

    if value_items:
        value_added = len([v for v in value_items if not (v.muda_type or "").strip()])
        total_items = len(value_items)
        flow_efficiency = round((value_added / max(1, total_items)) * 100.0, 2)
        waste_pressure = round(100.0 - flow_efficiency, 2)
    else:
        flow_efficiency = round(min(100.0, max(0.0, score - 10.0)), 2)
        waste_pressure = round(100.0 - flow_efficiency, 2)

    active_process_with_kpi = (
        _scope_proc(
            db.session.query(Process.id)
            .join(ProcessKpi, ProcessKpi.process_id == Process.id)
            .filter(Process.tenant_id == tenant_id, Process.is_active.is_(True), ProcessKpi.is_active.is_(True))
        )
        .distinct()
        .count()
    )
    utilization_estimate = round((active_process_with_kpi / max(1, int(process_count or 0))) * 100.0, 2) if process_count else 0.0
    resource_pressure = round(min(100.0, max(0.0, 100.0 - utilization_estimate + (len(open_bottlenecks) * 2.0))), 2)

    today = date.today()
    prev_start = today - timedelta(days=60)
    curr_start = today - timedelta(days=30)
    curr_rows = [r for r in kpi_rows_all if r.data_date and r.data_date >= curr_start]
    prev_rows = [r for r in kpi_rows_all if r.data_date and prev_start <= r.data_date < curr_start]

    def _period_health(rows: list[Any]) -> float:
        vals: list[float] = []
        for row in rows:
            a = _to_float(row.actual_value)
            t = _to_float(row.target_value)
            if a is None or t is None or t <= 0:
                continue
            vals.append(max(0.0, min(1.5, a / t)) * 100.0)
        if not vals:
            return 0.0
        return round(sum(vals) / len(vals), 2)

    curr_health = _period_health(curr_rows)
    prev_health = _period_health(prev_rows)
    trend_delta = round(curr_health - prev_health, 2)
    trend_label = "stabil"
    if trend_delta > 1:
        trend_label = "iyilesiyor"
    elif trend_delta < -1:
        trend_label = "dusuyor"

    trend_meta = {
        "delta": trend_delta,
        "label": trend_label,
        "current_period_avg": curr_health,
        "previous_period_avg": prev_health,
    }

    return {
        "olgunluk": {
            "process_count": int(process_count or 0),
            "avg_level_estimate": round(maturity_avg, 2) if maturity_levels else max(1, min(5, round((score / 100.0) * 5))),
            "assessment_count": len(maturity_levels),
        },
        "darbogaz": {
            "critical_kpi_count": len(open_bottlenecks),
            "severity_index": round(severity_index, 2),
            "total_log_count": len(bottlenecks),
            "trend": trend_meta,
        },
        "deger_zinciri": {
            "mapped_process_count": mapped_process_count if mapped_process_count else int(process_count or 0),
            "muda_risk": muda_risk,
            "item_count": len(value_items),
            "trend": trend_meta,
        },
        "pareto": {
            "top_impact_slice": round(top_share, 2),
            "kpi_count": int(kpi_count or 0),
            "trend": trend_meta,
        },
        "sla": {
            "breach_risk": breach_risk,
            "observed_rows": observed_rows if observed_rows else int(kpi_rows or 0),
            "trend": trend_meta,
        },
        "benchmark": {
            "comparability_score": comparability_score,
            "period_row_count": period_row_count if period_row_count else int(kpi_rows or 0),
            "trend": trend_meta,
        },
        "oee": {
            "oee_estimate": oee_estimate,
            "availability": availability,
            "performance": performance,
            "quality": quality,
            "trend": trend_meta,
        },
        "vsm": {
            "flow_efficiency_estimate": flow_efficiency,
            "waste_pressure": waste_pressure,
            "trend": trend_meta,
        },
        "kapasite": {
            "utilization_estimate": utilization_estimate,
            "resource_pressure": resource_pressure,
            "trend": trend_meta,
        },
    }


@cache.memoize(timeout=300)
def get_kpr_data(tenant_id: int, scope_project_ids: tuple[int, ...] | None = None) -> dict[str, Any]:
    return _project_component(tenant_id, list(scope_project_ids) if scope_project_ids is not None else None)


@cache.memoize(timeout=300)
def get_kpr_extended_data(tenant_id: int, scope_project_ids: tuple[int, ...] | None = None) -> dict[str, Any]:
    # scope None → kurum geneli. Tuple → yalnız o projeler.
    # RiskHeatmapItem project_id taşımadığından kurum geneli kalır (teknik kısıt, belge §5).
    _sprids = list(scope_project_ids) if scope_project_ids is not None else None
    base = _project_component(tenant_id, _sprids)
    _projq = Project.query.filter_by(tenant_id=tenant_id, is_archived=False)
    if _sprids is not None:
        _projq = _projq.filter(Project.id.in_(_sprids))
    projects = _projq.all()
    project_ids = [p.id for p in projects]
    if not project_ids:
        return {
            "evm": {"snapshot_count": 0, "avg_spi": 0.0, "avg_cpi": 0.0},
            "risk": {"open_risk_count": 0, "avg_rpn": 0.0, "high_risk_count": 0},
            "kaynak_kapasite": {"resource_load": 0.0, "overdue_open_tasks": 0, "active_task_count": 0},
            "gantt": {"timeline_task_count": 0, "on_time_ratio": 0.0},
        }

    _evmq = EvmSnapshot.query.filter(EvmSnapshot.tenant_id == tenant_id, EvmSnapshot.is_active.is_(True))
    if _sprids is not None:
        _evmq = _evmq.filter(EvmSnapshot.project_id.in_(_sprids))
    evm_rows = _evmq.all()
    spi_vals = [float(r.spi) for r in evm_rows if r.spi is not None]
    cpi_vals = [float(r.cpi) for r in evm_rows if r.cpi is not None]
    avg_spi = round(sum(spi_vals) / len(spi_vals), 2) if spi_vals else 0.0
    avg_cpi = round(sum(cpi_vals) / len(cpi_vals), 2) if cpi_vals else 0.0

    # RiskHeatmapItem project_id taşımaz → scope'lanamaz, kurum geneli kalır (belge §5).
    risk_rows = RiskHeatmapItem.query.filter_by(tenant_id=tenant_id, is_active=True).all()
    open_risks = [r for r in risk_rows if (r.status or "").lower() not in {"closed", "done", "resolved"}]
    risk_points = [int(r.rpn or (int(r.probability or 0) * int(r.impact or 0))) for r in open_risks]
    avg_rpn = round(sum(risk_points) / len(risk_points), 2) if risk_points else 0.0
    high_risk_count = len([v for v in risk_points if v >= 15])

    tasks = Task.query.filter(Task.project_id.in_(project_ids), Task.is_archived.is_(False)).all()
    overdue_open = 0
    dated_tasks = 0
    on_time = 0
    for t in tasks:
        if t.due_date and t.status != "Tamamlandı" and t.due_date < today:
            overdue_open += 1
        if t.start_date or t.due_date:
            dated_tasks += 1
        if t.status == "Tamamlandı":
            on_time += 1
    active_task_count = len([t for t in tasks if t.status != "Tamamlandı"])
    resource_load = round((active_task_count / max(1, len(projects))) * 10.0, 2)
    on_time_ratio = round((on_time / max(1, dated_tasks)) * 100.0, 2) if dated_tasks else 0.0

    return {
        "evm": {"snapshot_count": len(evm_rows), "avg_spi": avg_spi, "avg_cpi": avg_cpi},
        "risk": {"open_risk_count": len(open_risks), "avg_rpn": avg_rpn, "high_risk_count": high_risk_count},
        "kaynak_kapasite": {
            "resource_load": resource_load,
            "overdue_open_tasks": overdue_open,
            "active_task_count": active_task_count,
        },
        "gantt": {"timeline_task_count": dated_tasks, "on_time_ratio": on_time_ratio},
        "summary": {"score": base.get("score", 0), "band": base.get("band", "red")},
    }


@cache.memoize(timeout=300)
def get_cross_heatmap_data(
    tenant_id: int,
    scope_process_ids: tuple[int, ...] | None = None,
    scope_project_ids: tuple[int, ...] | None = None,
) -> dict[str, Any]:
    hub = get_hub_summary(tenant_id, scope_process_ids, scope_project_ids)
    recommendations = get_recommendations_from_summary(hub)
    points = [
        {
            "name": "KS-Radar",
            "probability": 2 if hub["ks"]["score"] >= 80 else 3 if hub["ks"]["score"] >= 60 else 4,
            "impact": 2 if hub["ks"]["score"] >= 80 else 3 if hub["ks"]["score"] >= 60 else 4,
            "category": "strategy",
            "source": "ks",
            "recommendation": recommendations[0] if recommendations else None,
        },
        {
            "name": "KP-Radar",
            "probability": 2 if hub["kp"]["score"] >= 80 else 3 if hub["kp"]["score"] >= 60 else 5,
            "impact": 2 if hub["kp"]["score"] >= 80 else 4 if hub["kp"]["score"] >= 60 else 5,
            "category": "process",
            "source": "kp",
            "recommendation": recommendations[1] if len(recommendations) > 1 else None,
        },
        {
            "name": "KPR-Radar",
            "probability": 2 if hub["kpr"]["score"] >= 80 else 3 if hub["kpr"]["score"] >= 60 else 5,
            "impact": 2 if hub["kpr"]["score"] >= 80 else 3 if hub["kpr"]["score"] >= 60 else 5,
            "category": "project",
            "source": "kpr",
            "recommendation": recommendations[2] if len(recommendations) > 2 else None,
        },
        {
            "name": "Bireysel",
            "probability": 2 if hub["individual"]["score"] >= 80 else 3 if hub["individual"]["score"] >= 60 else 4,
            "impact": 2 if hub["individual"]["score"] >= 80 else 3 if hub["individual"]["score"] >= 60 else 4,
            "category": "individual",
            "source": "individual",
            "recommendation": recommendations[3] if len(recommendations) > 3 else None,
        },
    ]
    for p in points:
        p["rpn"] = p["probability"] * p["impact"]
    return {"points": points}


@cache.memoize(timeout=300)
def get_cross_extended_data(tenant_id: int) -> dict[str, Any]:
    comp_rows = CompetitorAnalysis.query.filter_by(tenant_id=tenant_id, is_active=True).all()
    gaps = [float((r.their_score or 0) - (r.our_score or 0)) for r in comp_rows]
    avg_gap = round(sum(gaps) / len(gaps), 2) if gaps else 0.0

    a3_rows = A3Report.query.filter_by(tenant_id=tenant_id, is_active=True).all()
    with_root_cause = len([r for r in a3_rows if (r.root_cause_json or "").strip()])

    survey_rows = StakeholderSurvey.query.filter_by(tenant_id=tenant_id, is_active=True).all()
    scores = [float(r.score) for r in survey_rows if r.score is not None]
    avg_score = round(sum(scores) / len(scores), 2) if scores else 0.0

    return {
        "rekabet": {"record_count": len(comp_rows), "avg_gap_against_competition": avg_gap},
        "a3_5neden": {"report_count": len(a3_rows), "root_cause_coverage": round((with_root_cause / max(1, len(a3_rows))) * 100.0, 2)},
        "anket": {"survey_count": len(survey_rows), "avg_score": avg_score},
    }


def get_recommendations_from_summary(summary: dict[str, Any]) -> list[str]:
    out: list[str] = []
    if summary.get("total_band") == "red":
        out.append("Kurum genel riski yuksek: haftalik yonetim gozlestirmesi baslatin.")

    kp = summary.get("kp", {})
    if int(kp.get("critical_count") or 0) >= 3:
        out.append("KP-Radar: kritik KPI'lar icin 30 gunluk iyilestirme plani olusturun.")

    kpr = summary.get("kpr", {})
    if int(kpr.get("critical_count") or 0) >= 2:
        out.append("KPR-Radar: kritik projeler icin EVM ve gecikme kok neden analizi yapin.")

    ind = summary.get("individual", {})
    if int(ind.get("critical_count") or 0) >= 4:
        out.append("Bireysel performansta dusus var: hedef-gozden-gecirme seansi planlayin.")

    ks = summary.get("ks", {})
    if float(ks.get("score") or 0) < 60:
        out.append("KS-Radar: strateji-surec hizalamasini yeniden degerlendirin.")

    if not out:
        out.append("Genel gorunum stabil: mevcut aksiyon planini izlemeye devam edin.")
    return out


def get_recommendation_triggers(summary: dict[str, Any]) -> list[dict[str, Any]]:
    kp = summary.get("kp", {})
    kpr = summary.get("kpr", {})
    ks = summary.get("ks", {})
    ind = summary.get("individual", {})
    out: list[dict[str, Any]] = []
    if summary.get("total_band") == "red":
        out.append({"rule_code": "RISK-GLOBAL-RED", "module": "hub", "severity": "high"})
    if int(kp.get("critical_count") or 0) >= 3:
        out.append({"rule_code": "KP-CRITICAL-COUNT", "module": "kp", "severity": "high"})
    if int(kpr.get("critical_count") or 0) >= 2:
        out.append({"rule_code": "KPR-CRITICAL-COUNT", "module": "kpr", "severity": "high"})
    if float(ks.get("score") or 0) < 60:
        out.append({"rule_code": "KS-ALIGNMENT-LOW", "module": "ks", "severity": "medium"})
    if int(ind.get("critical_count") or 0) >= 4:
        out.append({"rule_code": "IND-CRITICAL-COUNT", "module": "individual", "severity": "medium"})
    return out


def recommendation_key(item: str) -> str:
    return sha1((item or "").strip().encode("utf-8")).hexdigest()[:16]


def get_recommendation_states(tenant_id: int, user_id: int, items: list[str]) -> dict[str, str]:
    keys = [recommendation_key(item) for item in items]
    rows = (
        KRadarRecommendationAction.query.filter_by(tenant_id=tenant_id, user_id=user_id)
        .filter(KRadarRecommendationAction.recommendation_key.in_(keys))
        .all()
    )
    state_map = {r.recommendation_key: r.state for r in rows}
    out: dict[str, str] = {}
    for item in items:
        k = recommendation_key(item)
        out[k] = state_map.get(k, "pending")
    return out


def set_recommendation_state(tenant_id: int, user_id: int, item: str, state: str) -> dict[str, Any]:
    safe_state = (state or "").strip().lower()
    if safe_state not in {"approved", "rejected"}:
        raise ValueError("Gecersiz karar. approved/rejected olmali.")
    key = recommendation_key(item)
    row = KRadarRecommendationAction.query.filter_by(
        tenant_id=tenant_id,
        user_id=user_id,
        recommendation_key=key,
    ).first()
    if row is None:
        row = KRadarRecommendationAction(
            tenant_id=tenant_id,
            user_id=user_id,
            recommendation_key=key,
            recommendation_text=item,
            state=safe_state,
        )
        db.session.add(row)
    else:
        row.state = safe_state
        row.recommendation_text = item
    task_meta: dict[str, Any] | None = None
    if safe_state == "approved":
        task_meta = _create_action_task_for_recommendation(tenant_id, user_id, item)
    db.session.commit()
    return {"key": key, "state": safe_state, "action_task": task_meta}


def _create_action_task_for_recommendation(tenant_id: int, user_id: int, text: str) -> dict[str, Any] | None:
    project = (
        Project.query.filter_by(tenant_id=tenant_id, is_archived=False)
        .order_by(Project.updated_at.desc())
        .first()
    )
    if project is None:
        logger.info("K-Radar aksiyon gorevi olusturulamadi: aktif proje yok (tenant=%s)", tenant_id)
        return None
    title = (text or "").strip()
    if len(title) > 180:
        title = title[:177] + "..."
    lowered = (text or "").lower()
    priority = "Orta"
    if "kritik" in lowered or "yuksek" in lowered:
        priority = "Yüksek"
    if "stabil" in lowered:
        priority = "Düşük"
    existing = (
        Task.query.filter_by(project_id=project.id, is_archived=False)
        .filter(Task.title == f"[K-Radar] {title}")
        .first()
    )
    if existing:
        return {"task_id": existing.id, "project_id": project.id, "deduplicated": True}
    task = Task(
        project_id=project.id,
        title=f"[K-Radar] {title}",
        description="K-Radar onaylanan öneri aksiyonu.",
        reporter_id=user_id,
        assignee_id=user_id,
        status="Yapılacak",
        priority=priority,
        is_archived=False,
    )
    db.session.add(task)
    db.session.flush()
    return {"task_id": task.id, "project_id": project.id}


def list_recommendation_action_history(
    tenant_id: int,
    user_id: int,
    can_manage: bool,
    limit: int = 30,
    page: int = 1,
    state: str | None = None,
    actor_user_id: int | None = None,
) -> dict[str, Any]:
    q = KRadarRecommendationAction.query.filter_by(tenant_id=tenant_id)
    if not can_manage:
        q = q.filter_by(user_id=user_id)
    if state in {"approved", "rejected", "pending"}:
        q = q.filter(KRadarRecommendationAction.state == state)
    if actor_user_id is not None and can_manage:
        q = q.filter(KRadarRecommendationAction.user_id == actor_user_id)
    total = q.count()
    safe_page = max(1, int(page or 1))
    safe_limit = max(1, min(int(limit or 30), 200))
    pages = max(1, (total + safe_limit - 1) // safe_limit)
    if safe_page > pages:
        safe_page = pages
    offset = (safe_page - 1) * safe_limit
    rows = (
        q.order_by(KRadarRecommendationAction.updated_at.desc())
        .offset(offset)
        .limit(safe_limit)
        .all()
    )
    out: list[dict[str, Any]] = []
    for r in rows:
        out.append(
            {
                "id": r.id,
                "user_id": r.user_id,
                "recommendation_key": r.recommendation_key,
                "recommendation_text": r.recommendation_text,
                "state": r.state,
                "updated_at": (r.updated_at.isoformat() if r.updated_at else None),
            }
        )
    return {
        "items": out,
        "pagination": {
            "page": safe_page,
            "per_page": safe_limit,
            "total": total,
            "pages": pages,
        },
    }


# ══════════════════════════════════════════════════════════════════════════════
# KS-Radar — Gerçek DB Verisi Fonksiyonları
# ══════════════════════════════════════════════════════════════════════════════

import json as _json


def _parse_json_list(raw: str | None) -> list:
    """JSON string'i listeye çevirir, hata durumunda boş liste döner."""
    if not raw:
        return []
    try:
        result = _json.loads(raw)
        return result if isinstance(result, list) else []
    except Exception:
        return []


def _parse_json_obj(raw: str | None) -> dict:
    """JSON string'i dict'e çevirir, hata durumunda boş dict döner."""
    if not raw:
        return {}
    try:
        result = _json.loads(raw)
        return result if isinstance(result, dict) else {}
    except Exception:
        return {}


def _get_plan_year_for_tenant(tenant_id: int, year: int | None = None):
    """Tenant için plan year döner. year verilmezse en güncel yılı alır."""
    from app.models.plan_year import PlanYear
    if year:
        py = PlanYear.query.filter_by(tenant_id=tenant_id, year=year).first()
        if py:
            return py
    # En son yıl
    return PlanYear.query.filter_by(tenant_id=tenant_id).order_by(PlanYear.year.desc()).first()


@cache.memoize(timeout=300)
def get_ks_swot_real(tenant_id: int, year: int | None = None) -> dict:
    """Gerçek SWOT verisi — swot_analyses tablosundan."""
    from app.models.swot import SwotAnalysis
    from app.models.plan_year import PlanYear

    all_pys = PlanYear.query.filter_by(tenant_id=tenant_id).order_by(PlanYear.year.desc()).all()
    py_map = {py.id: py.year for py in all_pys}

    # Önce istenen yıl, yoksa verisi olan en son kayıt
    swot = None
    if year:
        target_py = next((py for py in all_pys if py.year == year), None)
        if target_py:
            swot = SwotAnalysis.query.filter_by(tenant_id=tenant_id, plan_year_id=target_py.id).first()

    if not swot or not any([swot.strengths, swot.weaknesses, swot.opportunities, swot.threats]):
        # Verisi olan en son SWOT'u bul (updated_at'e göre)
        swot = (SwotAnalysis.query
                .filter_by(tenant_id=tenant_id)
                .order_by(SwotAnalysis.updated_at.desc())
                .first())
        # Hâlâ boşsa None yap
        if swot and not any([swot.strengths, swot.weaknesses, swot.opportunities, swot.threats]):
            swot = None

    if not swot:
        return {
            "mevcut": False, "year": year,
            "strengths": [], "weaknesses": [], "opportunities": [], "threats": [],
            "ozet": {"S": 0, "W": 0, "O": 0, "T": 0},
            "yillar": [{"id": py.id, "year": py.year} for py in all_pys],
        }

    s_list = _parse_json_list(swot.strengths)
    w_list = _parse_json_list(swot.weaknesses)
    o_list = _parse_json_list(swot.opportunities)
    t_list = _parse_json_list(swot.threats)
    py_year = py_map.get(swot.plan_year_id, year)

    return {
        "mevcut": True,
        "swot_id": swot.id,
        "plan_year_id": swot.plan_year_id,
        "year": py_year,
        "guncelleme": str(swot.updated_at)[:10] if swot.updated_at else None,
        "strengths":     s_list,
        "weaknesses":    w_list,
        "opportunities": o_list,
        "threats":       t_list,
        "ozet": {"S": len(s_list), "W": len(w_list), "O": len(o_list), "T": len(t_list)},
        "yillar": [{"id": py.id, "year": py.year} for py in all_pys],
    }


@cache.memoize(timeout=300)
def get_ks_tows_real(tenant_id: int, year: int | None = None) -> dict:
    """Gerçek TOWS verisi — tows_analyses tablosundan."""
    from app.models.swot import TowsAnalysis
    from app.models.plan_year import PlanYear

    all_pys = PlanYear.query.filter_by(tenant_id=tenant_id).order_by(PlanYear.year.desc()).all()
    py_map = {py.id: py.year for py in all_pys}

    tows = None
    if year:
        target_py = next((py for py in all_pys if py.year == year), None)
        if target_py:
            tows = TowsAnalysis.query.filter_by(tenant_id=tenant_id, plan_year_id=target_py.id).first()

    if not tows or not any([tows.so_strategies, tows.st_strategies, tows.wo_strategies, tows.wt_strategies]):
        tows = (TowsAnalysis.query
                .filter_by(tenant_id=tenant_id)
                .order_by(TowsAnalysis.updated_at.desc())
                .first())
        if tows and not any([tows.so_strategies, tows.st_strategies, tows.wo_strategies, tows.wt_strategies]):
            tows = None

    if not tows:
        return {
            "mevcut": False, "year": year,
            "so": [], "st": [], "wo": [], "wt": [],
            "ozet": {"SO": 0, "ST": 0, "WO": 0, "WT": 0},
            "yillar": [{"id": py.id, "year": py.year} for py in all_pys],
        }

    so = _parse_json_list(tows.so_strategies)
    st = _parse_json_list(tows.st_strategies)
    wo = _parse_json_list(tows.wo_strategies)
    wt = _parse_json_list(tows.wt_strategies)
    py_year = py_map.get(tows.plan_year_id, year)

    return {
        "mevcut": True,
        "tows_id": tows.id,
        "plan_year_id": tows.plan_year_id,
        "year": py_year,
        "guncelleme": str(tows.updated_at)[:10] if tows.updated_at else None,
        "so": so, "st": st, "wo": wo, "wt": wt,
        "ozet": {"SO": len(so), "ST": len(st), "WO": len(wo), "WT": len(wt)},
        "yillar": [{"id": py.id, "year": py.year} for py in all_pys],
    }


@cache.memoize(timeout=300)
def get_ks_pestel_real(tenant_id: int, year: int | None = None) -> dict:
    """Gerçek PESTEL verisi — pestel_analyses tablosundan."""
    from app.models.swot import PestelAnalysis
    from app.models.plan_year import PlanYear

    all_pys = PlanYear.query.filter_by(tenant_id=tenant_id).order_by(PlanYear.year.desc()).all()
    py_map = {py.id: py.year for py in all_pys}

    pestel = None
    if year:
        target_py = next((py for py in all_pys if py.year == year), None)
        if target_py:
            pestel = PestelAnalysis.query.filter_by(tenant_id=tenant_id, plan_year_id=target_py.id).first()

    if not pestel or not any([pestel.political, pestel.economic, pestel.social, pestel.technological, pestel.environmental, pestel.legal]):
        pestel = (PestelAnalysis.query
                  .filter_by(tenant_id=tenant_id)
                  .order_by(PestelAnalysis.updated_at.desc())
                  .first())
        if pestel and not any([pestel.political, pestel.economic, pestel.social, pestel.technological, pestel.environmental, pestel.legal]):
            pestel = None

    if not pestel:
        return {
            "mevcut": False, "year": year,
            "political": [], "economic": [], "social": [],
            "technological": [], "environmental": [], "legal": [],
            "ozet": {"P": 0, "E": 0, "S": 0, "T": 0, "E2": 0, "L": 0},
            "yillar": [{"id": py.id, "year": py.year} for py in all_pys],
        }

    p_list  = _parse_json_list(pestel.political)
    e_list  = _parse_json_list(pestel.economic)
    s_list  = _parse_json_list(pestel.social)
    t_list  = _parse_json_list(pestel.technological)
    e2_list = _parse_json_list(pestel.environmental)
    l_list  = _parse_json_list(pestel.legal)
    py_year = py_map.get(pestel.plan_year_id, year)

    return {
        "mevcut": True,
        "pestel_id": pestel.id,
        "plan_year_id": pestel.plan_year_id,
        "year": py_year,
        "guncelleme": str(pestel.updated_at)[:10] if pestel.updated_at else None,
        "political": p_list, "economic": e_list, "social": s_list,
        "technological": t_list, "environmental": e2_list, "legal": l_list,
        "ozet": {"P": len(p_list), "E": len(e_list), "S": len(s_list),
                 "T": len(t_list), "E2": len(e2_list), "L": len(l_list)},
        "yillar": [{"id": py.id, "year": py.year} for py in all_pys],
    }


@cache.memoize(timeout=300)
def get_ks_porter_real(tenant_id: int, year: int | None = None) -> dict:
    """Gerçek Porter 5 Kuvvet verisi."""
    from app.models.swot import PorterFiveForcesAnalysis
    from app.models.plan_year import PlanYear

    all_pys = PlanYear.query.filter_by(tenant_id=tenant_id).order_by(PlanYear.year.desc()).all()
    py_map = {py.id: py.year for py in all_pys}
    target_py = _get_plan_year_for_tenant(tenant_id, year)

    porter = None
    if target_py:
        porter = PorterFiveForcesAnalysis.query.filter_by(tenant_id=tenant_id, plan_year_id=target_py.id).first()

    if not porter:
        all_p = PorterFiveForcesAnalysis.query.filter_by(tenant_id=tenant_id).order_by(PorterFiveForcesAnalysis.updated_at.desc()).all()
        for p in all_p:
            if any([p.rivalry_intensity, p.supplier_power, p.buyer_power, p.new_entrant_threat, p.substitute_threat]):
                porter = p
                break

    def _parse_force(raw):
        obj = _parse_json_obj(raw)
        return {"score": obj.get("score"), "items": obj.get("items", [])}

    if not porter:
        return {
            "mevcut": False, "year": year,
            "rivalry": {"score": None, "items": []},
            "supplier": {"score": None, "items": []},
            "buyer": {"score": None, "items": []},
            "new_entrant": {"score": None, "items": []},
            "substitute": {"score": None, "items": []},
            "yillar": [{"id": py.id, "year": py.year} for py in all_pys],
        }

    py_year = py_map.get(porter.plan_year_id, year)
    return {
        "mevcut": True,
        "porter_id": porter.id,
        "plan_year_id": porter.plan_year_id,
        "year": py_year,
        "guncelleme": str(porter.updated_at)[:10] if porter.updated_at else None,
        "rivalry":     _parse_force(porter.rivalry_intensity),
        "supplier":    _parse_force(porter.supplier_power),
        "buyer":       _parse_force(porter.buyer_power),
        "new_entrant": _parse_force(porter.new_entrant_threat),
        "substitute":  _parse_force(porter.substitute_threat),
        "yillar": [{"id": py.id, "year": py.year} for py in all_pys],
    }


@cache.memoize(timeout=300)
def get_ks_gap_real(tenant_id: int, year: int | None = None) -> dict:
    """GAP analizi — hedef vs gerçekleşen, süreç bazlı."""
    from app.models.process import Process, ProcessKpi, KpiData
    import datetime as _dt

    cur_year = year or _dt.date.today().year
    processes = Process.query.filter_by(tenant_id=tenant_id, is_active=True).order_by(Process.code).all()
    kpis = (
        ProcessKpi.query.join(Process)
        .filter(Process.tenant_id == tenant_id, Process.is_active == True, ProcessKpi.is_active == True)
        .all()
    )
    kpi_map = {k.id: k for k in kpis}
    proc_map = {p.id: p for p in processes}

    kpi_ids = [k.id for k in kpis]
    latest_data = {}
    if kpi_ids:
        rows = (
            KpiData.query
            .filter(KpiData.process_kpi_id.in_(kpi_ids), KpiData.year == cur_year, KpiData.is_active == True)
            .order_by(KpiData.data_date.desc())
            .all()
        )
        for d in rows:
            if d.process_kpi_id not in latest_data:
                latest_data[d.process_kpi_id] = d

    # Süreç bazlı gap hesapla
    proc_gaps = {}
    for kpi_id, d in latest_data.items():
        kpi = kpi_map.get(kpi_id)
        if not kpi:
            continue
        try:
            target = float(kpi.target_value or 0)
            actual = float(d.actual_value or 0)
            if target <= 0:
                continue
            if getattr(kpi, 'direction', 'Increasing') == 'lower_is_better':
                pct = round(min(100.0, target / actual * 100), 1) if actual > 0 else 0.0
            else:
                pct = round(min(100.0, actual / target * 100), 1)
            gap = round(pct - 100, 1)
            pid = kpi.process_id
            if pid not in proc_gaps:
                proc_gaps[pid] = {"scores": [], "kpi_count": 0}
            proc_gaps[pid]["scores"].append(pct)
            proc_gaps[pid]["kpi_count"] += 1
        except (ValueError, TypeError):
            pass

    gap_rows = []
    for pid, data in proc_gaps.items():
        proc = proc_map.get(pid)
        if not proc:
            continue
        scores = data["scores"]
        ort = round(sum(scores) / len(scores), 1) if scores else 0
        gap_rows.append({
            "process_id": pid,
            "code": proc.code or "",
            "name": proc.name,
            "kpi_count": data["kpi_count"],
            "ort_basari": ort,
            "gap": round(ort - 100, 1),
            "durum": "hedefte" if ort >= 80 else ("riskli" if ort >= 50 else "kritik"),
        })
    gap_rows.sort(key=lambda x: x["ort_basari"])

    toplam_kpi = len(kpi_ids)
    veri_girilen = len(latest_data)
    tum_skorlar = [r["ort_basari"] for r in gap_rows]
    genel_ort = round(sum(tum_skorlar) / len(tum_skorlar), 1) if tum_skorlar else 0

    return {
        "year": cur_year,
        "toplam_kpi": toplam_kpi,
        "veri_girilen": veri_girilen,
        "genel_ort_basari": genel_ort,
        "genel_gap": round(genel_ort - 100, 1),
        "hedefte": sum(1 for r in gap_rows if r["durum"] == "hedefte"),
        "riskli":  sum(1 for r in gap_rows if r["durum"] == "riskli"),
        "kritik":  sum(1 for r in gap_rows if r["durum"] == "kritik"),
        "surec_gap_listesi": gap_rows,
    }


@cache.memoize(timeout=300)
def get_ks_strateji_real(tenant_id: int, year: int | None = None) -> dict:
    """Strateji hiyerarşisi + süreç bağlantıları + skor (seçili plan yılına göre)."""
    from app.models.core import Strategy, SubStrategy
    from app.models.process import Process
    from app.models.plan_year import PlanYear

    from app.models.process import ProcessSubStrategyLink

    plan_year_id = None
    if year:
        py = PlanYear.query.filter_by(tenant_id=tenant_id, year=year).first()
        plan_year_id = py.id if py else None

    def _base_query():
        return Strategy.query.options(
            selectinload(Strategy.sub_strategies)
                .selectinload(SubStrategy.process_sub_strategy_links)
                .joinedload(ProcessSubStrategyLink.process)
        ).filter_by(tenant_id=tenant_id, is_active=True)

    strategies = []
    if year and plan_year_id:
        strategies = _base_query().filter(Strategy.plan_year_id == plan_year_id).order_by(Strategy.code).all()
    if not strategies:
        # Yıl seçilmemiş, o yıla ait strateji yok, veya plan_year_id ataması yapılmamış
        # legacy kayıtlar var — tüm aktif stratejileri göster (tekrarı önlemek için
        # yalnızca plan_year_id'si NULL olan veya seçili yıla ait olanlar alınır).
        fallback_query = _base_query()
        if plan_year_id:
            fallback_query = fallback_query.filter(
                db.or_(Strategy.plan_year_id.is_(None), Strategy.plan_year_id == plan_year_id)
            )
        strategies = fallback_query.order_by(Strategy.code).all()
    all_processes = Process.query.filter_by(tenant_id=tenant_id, is_active=True).all()
    proc_map = {p.id: p for p in all_processes}

    linked_proc_ids = set()
    strat_list = []
    for s in strategies:
        subs = [ss for ss in s.sub_strategies if getattr(ss, "is_active", True)]
        sub_list = []
        for ss in subs:
            linked = [pssl.process for pssl in ss.process_sub_strategy_links
                      if pssl.process and pssl.process.is_active and pssl.process.tenant_id == tenant_id]
            for p in linked:
                linked_proc_ids.add(p.id)
            sub_list.append({
                "id": ss.id,
                "code": ss.code or "",
                "title": ss.title,
                "surec_sayisi": len(linked),
            })
        strat_list.append({
            "id": s.id,
            "code": s.code or "",
            "title": s.title,
            "alt_strateji_sayisi": len(subs),
            "bagli_surec_sayisi": sum(ss["surec_sayisi"] for ss in sub_list),
            "alt_stratejiler": sub_list,
        })

    stratejisiz = [p for p in all_processes if p.id not in linked_proc_ids]
    kapsam_pct = round(len(linked_proc_ids) / len(all_processes) * 100, 1) if all_processes else 0

    return {
        "toplam_strateji": len(strategies),
        "toplam_alt_strateji": sum(s["alt_strateji_sayisi"] for s in strat_list),
        "toplam_surec": len(all_processes),
        "bagli_surec": len(linked_proc_ids),
        "stratejisiz_surec": len(stratejisiz),
        "kapsam_pct": kapsam_pct,
        "stratejiler": strat_list,
        "stratejisiz_surecler": [{"id": p.id, "code": p.code or "", "name": p.name} for p in stratejisiz],
    }
