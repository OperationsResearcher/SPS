"""K-Radar hesaplama servisi (Faz-1 temel sürüm)."""

from __future__ import annotations

import logging
from typing import Any
from hashlib import sha1
from datetime import date, timedelta

from sqlalchemy import func, or_

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
from models.project import Project, Task
from app.models.k_radar import KRadarRecommendationAction

logger = logging.getLogger(__name__)


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


def _process_component(tenant_id: int) -> dict[str, Any]:
    kpis = (
        ProcessKpi.query.join(Process, Process.id == ProcessKpi.process_id)
        .filter(
            Process.tenant_id == tenant_id,
            Process.is_active.is_(True),
            ProcessKpi.is_active.is_(True),
        )
        .all()
    )
    rows: list[tuple[float, float]] = []
    critical_count = 0
    for kpi in kpis:
        latest = (
            KpiData.query.filter_by(process_kpi_id=kpi.id, is_active=True)
            .order_by(KpiData.data_date.desc())
            .first()
        )
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


def _project_component(tenant_id: int) -> dict[str, Any]:
    active_projects = (
        Project.query.filter_by(tenant_id=tenant_id, is_archived=False).all()
    )
    if not active_projects:
        return {"score": 0.0, "band": "red", "critical_count": 0, "project_count": 0}
    rows: list[tuple[float, float]] = []
    critical_count = 0
    for project in active_projects:
        health = float(project.health_score or 0.0)
        delayed_tasks = (
            Task.query.filter_by(project_id=project.id, is_archived=False)
            .filter(Task.due_date.isnot(None))
            .filter(Task.status != "Tamamlandı")
            .filter(Task.due_date < func.current_date())
            .count()
        )
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
    rows: list[tuple[float, float]] = []
    critical_count = 0
    for indicator in indicators:
        latest = (
            IndividualKpiData.query.filter_by(individual_pg_id=indicator.id)
            .order_by(IndividualKpiData.data_date.desc())
            .first()
        )
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


def get_hub_summary(tenant_id: int) -> dict[str, Any]:
    ks = _ks_component(tenant_id)
    kp = _process_component(tenant_id)
    kpr = _project_component(tenant_id)
    ind = _individual_component(tenant_id)

    total = _weighted_score(
        [
            (ks["score"], 2.0),
            (kp["score"], 3.0),
            (kpr["score"], 3.0),
            (ind["score"], 2.0),
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


def get_ks_data(tenant_id: int) -> dict[str, Any]:
    return _ks_component(tenant_id)


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


def get_kp_data(tenant_id: int) -> dict[str, Any]:
    return _process_component(tenant_id)


def get_kp_extended_data(tenant_id: int) -> dict[str, Any]:
    base = _process_component(tenant_id)
    process_count = Process.query.filter_by(tenant_id=tenant_id, is_active=True).count()
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
    critical = int(base.get("critical_count") or 0)
    score = float(base.get("score") or 0.0)

    maturity_rows = ProcessMaturity.query.filter_by(tenant_id=tenant_id, is_active=True).all()
    maturity_levels = [int(r.maturity_level or 0) for r in maturity_rows if r.maturity_level is not None]
    maturity_avg = round(sum(maturity_levels) / len(maturity_levels), 2) if maturity_levels else 0.0

    bottlenecks = BottleneckLog.query.filter_by(tenant_id=tenant_id, is_active=True).all()
    open_bottlenecks = [b for b in bottlenecks if b.resolved_at is None]
    severity_weight = {"low": 1, "medium": 2, "high": 3, "critical": 4}
    severity_points = sum(severity_weight.get(str((b.severity or "")).strip().lower(), 2) for b in open_bottlenecks)
    severity_index = min(100, severity_points * 8) if open_bottlenecks else min(100, critical * 20)

    value_items = ValueChainItem.query.filter_by(tenant_id=tenant_id, is_active=True).all()
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

    kpi_rows_all = (
        KpiData.query.join(ProcessKpi, ProcessKpi.id == KpiData.process_kpi_id)
        .join(Process, Process.id == ProcessKpi.process_id)
        .filter(Process.tenant_id == tenant_id, Process.is_active.is_(True), KpiData.is_active.is_(True))
        .all()
    )
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

    kpi_row_counts = (
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
        .all()
    )
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
        db.session.query(Process.id)
        .join(ProcessKpi, ProcessKpi.process_id == Process.id)
        .filter(Process.tenant_id == tenant_id, Process.is_active.is_(True), ProcessKpi.is_active.is_(True))
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


def get_kpr_data(tenant_id: int) -> dict[str, Any]:
    return _project_component(tenant_id)


def get_kpr_extended_data(tenant_id: int) -> dict[str, Any]:
    base = _project_component(tenant_id)
    projects = Project.query.filter_by(tenant_id=tenant_id, is_archived=False).all()
    project_ids = [p.id for p in projects]
    if not project_ids:
        return {
            "evm": {"snapshot_count": 0, "avg_spi": 0.0, "avg_cpi": 0.0},
            "risk": {"open_risk_count": 0, "avg_rpn": 0.0, "high_risk_count": 0},
            "kaynak_kapasite": {"resource_load": 0.0, "overdue_open_tasks": 0, "active_task_count": 0},
            "gantt": {"timeline_task_count": 0, "on_time_ratio": 0.0},
        }

    evm_rows = EvmSnapshot.query.filter(EvmSnapshot.tenant_id == tenant_id, EvmSnapshot.is_active.is_(True)).all()
    spi_vals = [float(r.spi) for r in evm_rows if r.spi is not None]
    cpi_vals = [float(r.cpi) for r in evm_rows if r.cpi is not None]
    avg_spi = round(sum(spi_vals) / len(spi_vals), 2) if spi_vals else 0.0
    avg_cpi = round(sum(cpi_vals) / len(cpi_vals), 2) if cpi_vals else 0.0

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


def get_cross_heatmap_data(tenant_id: int) -> dict[str, Any]:
    hub = get_hub_summary(tenant_id)
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
