"""Çeyreklik Review Servisi (Sprint 54 — Ö1).

Modern strateji cadence pattern'ı (ClearPoint/Atlassian önerileri):
- Yıllık plan = vizyon
- Çeyreklik review = strateji ayarlama
- Aylık check-in = roadmap iyileştirme

Bu servis: bir tenant+yıl+çeyrek için consolidate edilmiş review data üretir.
"""
from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field
from typing import Optional

from extensions import db
from sqlalchemy import text


QUARTER_MONTHS = {1: (1, 3), 2: (4, 6), 3: (7, 9), 4: (10, 12)}


@dataclass
class QuarterlyReviewData:
    tenant_id: int
    year: int
    quarter: int
    period_label: str  # "2026 Q2"

    # KPI durumu
    kpi_total: int = 0
    kpi_with_data: int = 0
    kpi_on_target_pct: float = 0.0
    kpi_avg_score: Optional[float] = None

    # Strateji
    strategy_count: int = 0
    sub_strategy_count: int = 0

    # OKR
    okr_objective_count: int = 0
    okr_avg_progress: Optional[float] = None

    # Süreç
    process_count: int = 0
    active_activities: int = 0
    overdue_activities: int = 0

    # Risk
    open_risks: int = 0
    critical_risks: int = 0

    # Anomali
    anomaly_high: int = 0
    anomaly_medium: int = 0

    # Önemli olaylar
    new_strategies_this_quarter: int = 0
    closed_activities_this_quarter: int = 0

    # Aksiyon önerileri (AI öncesi heuristic)
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "tenant_id": self.tenant_id,
            "year": self.year,
            "quarter": self.quarter,
            "period_label": self.period_label,
            "kpi": {
                "total": self.kpi_total,
                "with_data": self.kpi_with_data,
                "on_target_pct": round(self.kpi_on_target_pct, 1),
                "avg_score": round(self.kpi_avg_score, 2) if self.kpi_avg_score else None,
            },
            "strategy": {
                "count": self.strategy_count,
                "sub_count": self.sub_strategy_count,
                "new_this_quarter": self.new_strategies_this_quarter,
            },
            "okr": {
                "objective_count": self.okr_objective_count,
                "avg_progress_pct": round(self.okr_avg_progress, 1) if self.okr_avg_progress else None,
            },
            "process": {
                "count": self.process_count,
                "active_activities": self.active_activities,
                "overdue_activities": self.overdue_activities,
                "closed_this_quarter": self.closed_activities_this_quarter,
            },
            "risk": {
                "open": self.open_risks,
                "critical": self.critical_risks,
            },
            "anomaly": {
                "high": self.anomaly_high,
                "medium": self.anomaly_medium,
            },
            "recommendations": self.recommendations,
        }


def _quarter_date_range(year: int, quarter: int) -> tuple[_dt.date, _dt.date]:
    m_start, m_end = QUARTER_MONTHS[quarter]
    start = _dt.date(year, m_start, 1)
    end_month = m_end + 1 if m_end < 12 else 1
    end_year = year + 1 if m_end == 12 else year
    try:
        end = _dt.date(end_year, end_month, 1) - _dt.timedelta(days=1)
    except ValueError:
        end = _dt.date(year, m_end, 28)
    return start, end


def build_quarterly_review(tenant_id: int, year: int, quarter: int) -> QuarterlyReviewData:
    """Bir çeyreklik review için tüm metrikleri topla."""
    if quarter not in (1, 2, 3, 4):
        raise ValueError("quarter 1-4 arası olmalı")

    q_start, q_end = _quarter_date_range(year, quarter)
    data = QuarterlyReviewData(
        tenant_id=tenant_id, year=year, quarter=quarter,
        period_label=f"{year} Q{quarter}",
    )

    # İlgili plan_year'ı çöz — yoksa tüm verilere düş
    py_id = None
    try:
        from app.services.plan_year_service import get_plan_year
        py = get_plan_year(tenant_id, year)
        py_id = py.id if py else None
    except Exception:
        py_id = None

    # KPI (plan_year_id varsa o yıla ait süreçlerin KPI'larını say)
    py_clause = "AND p.plan_year_id = :py" if py_id else ""
    py_params = {"py": py_id} if py_id else {}
    kpi_total = db.session.execute(text(f"""
        SELECT count(*) FROM process_kpis k JOIN processes p ON k.process_id=p.id
        WHERE p.tenant_id=:t AND k.is_active=true AND p.is_active=true {py_clause}
    """), {"t": tenant_id, **py_params}).scalar() or 0
    data.kpi_total = kpi_total

    kpi_with_data = db.session.execute(text("""
        SELECT count(DISTINCT k.id) FROM process_kpis k
        JOIN processes p ON k.process_id=p.id
        JOIN kpi_data kd ON kd.process_kpi_id=k.id
        WHERE p.tenant_id=:t AND kd.year=:y
          AND kd.data_date BETWEEN :s AND :e
          AND kd.is_active=true
    """), {"t": tenant_id, "y": year, "s": q_start, "e": q_end}).scalar() or 0
    data.kpi_with_data = kpi_with_data

    # On-target pct (actual_value >= target_value sayısı / toplam veri)
    on_target_rows = db.session.execute(text("""
        SELECT
            sum(CASE WHEN kd.actual_value::float >= kd.target_value::float THEN 1 ELSE 0 END) as on_target,
            count(*) as total
        FROM kpi_data kd
        JOIN process_kpis k ON kd.process_kpi_id=k.id
        JOIN processes p ON k.process_id=p.id
        WHERE p.tenant_id=:t AND kd.year=:y
          AND kd.data_date BETWEEN :s AND :e
          AND kd.is_active=true
          AND kd.actual_value ~ '^-?[0-9]+\\.?[0-9]*$'
          AND kd.target_value ~ '^-?[0-9]+\\.?[0-9]*$'
    """), {"t": tenant_id, "y": year, "s": q_start, "e": q_end}).fetchone()
    if on_target_rows and on_target_rows.total:
        data.kpi_on_target_pct = (on_target_rows.on_target / on_target_rows.total) * 100

    # Strateji (plan_year filtre)
    strat_py_clause = "AND plan_year_id = :py" if py_id else ""
    data.strategy_count = db.session.execute(text(
        f"SELECT count(*) FROM strategies WHERE tenant_id=:t AND is_active=true {strat_py_clause}"
    ), {"t": tenant_id, **py_params}).scalar() or 0
    data.sub_strategy_count = db.session.execute(text(
        f"SELECT count(*) FROM sub_strategies WHERE strategy_id IN "
        f"(SELECT id FROM strategies WHERE tenant_id=:t {strat_py_clause}) AND is_active=true"
    ), {"t": tenant_id, **py_params}).scalar() or 0
    data.new_strategies_this_quarter = db.session.execute(text(
        "SELECT count(*) FROM strategies WHERE tenant_id=:t "
        "AND created_at BETWEEN :s AND :e"
    ), {"t": tenant_id, "s": q_start, "e": q_end}).scalar() or 0

    # OKR (plan_year filtre)
    try:
        from app.models.okr import OkrObjective
        _okr_q = OkrObjective.query.filter_by(tenant_id=tenant_id, is_active=True)
        if py_id and hasattr(OkrObjective, 'plan_year_id'):
            _okr_q = _okr_q.filter(OkrObjective.plan_year_id == py_id)
        objectives = _okr_q.all()
        data.okr_objective_count = len(objectives)
        progresses = []
        for o in objectives:
            krs = [k for k in o.key_results if k.is_active]
            pcts = [k.progress_pct for k in krs if k.progress_pct is not None]
            if pcts:
                progresses.append(sum(pcts) / len(pcts))
        if progresses:
            data.okr_avg_progress = sum(progresses) / len(progresses)
    except Exception:
        pass

    # Süreç + Faaliyet (plan_year filtre)
    proc_py_clause = "AND plan_year_id = :py" if py_id else ""
    data.process_count = db.session.execute(text(
        f"SELECT count(*) FROM processes WHERE tenant_id=:t AND is_active=true {proc_py_clause}"
    ), {"t": tenant_id, **py_params}).scalar() or 0
    act_py_clause = "AND p.plan_year_id = :py" if py_id else ""
    data.active_activities = db.session.execute(text(
        f"SELECT count(*) FROM process_activities a JOIN processes p ON a.process_id=p.id "
        f"WHERE p.tenant_id=:t AND a.is_active=true AND a.status IN ('Planlandı', 'Devam Ediyor') {act_py_clause}"
    ), {"t": tenant_id, **py_params}).scalar() or 0
    data.overdue_activities = db.session.execute(text(
        "SELECT count(*) FROM process_activities a JOIN processes p ON a.process_id=p.id "
        "WHERE p.tenant_id=:t AND a.is_active=true "
        "AND a.status != 'Tamamlandı' AND a.end_date < CURRENT_DATE"
    ), {"t": tenant_id}).scalar() or 0
    data.closed_activities_this_quarter = db.session.execute(text(
        "SELECT count(*) FROM process_activities a JOIN processes p ON a.process_id=p.id "
        "WHERE p.tenant_id=:t AND a.status='Tamamlandı' "
        "AND a.completed_at BETWEEN :s AND :e"
    ), {"t": tenant_id, "s": q_start, "e": q_end}).scalar() or 0

    # Risk
    try:
        from app.models.k_radar_domain import RiskHeatmapItem
        risks = RiskHeatmapItem.query.filter_by(
            tenant_id=tenant_id, is_active=True
        ).all()
        data.open_risks = sum(1 for r in risks if r.status != "Closed")
        data.critical_risks = sum(
            1 for r in risks
            if (r.probability or 0) * (r.impact or 0) >= 16
        )
    except Exception:
        pass

    # Anomali
    try:
        from app.services.kpi_anomaly_service import detect_anomalies_for_tenant
        anomalies = detect_anomalies_for_tenant(tenant_id, threshold=2.0, limit=100)
        data.anomaly_high = sum(1 for a in anomalies if a.severity == "high")
        data.anomaly_medium = sum(1 for a in anomalies if a.severity == "medium")
    except Exception:
        pass

    # Heuristik öneriler
    if data.kpi_on_target_pct < 50:
        data.recommendations.append(
            f"⚠️ KPI'ların yalnızca %{data.kpi_on_target_pct:.0f}'ı hedef üstünde — "
            "stratejik öncelikleri gözden geçirmeyi düşünün."
        )
    if data.overdue_activities > 5:
        data.recommendations.append(
            f"🔴 {data.overdue_activities} gecikmiş faaliyet var — kapasite planlaması gerekebilir."
        )
    if data.critical_risks > 0:
        data.recommendations.append(
            f"🛡️ {data.critical_risks} kritik risk var — mitigasyon planları aktif mi?"
        )
    if data.anomaly_high > 0:
        data.recommendations.append(
            f"📊 {data.anomaly_high} yüksek-severity KPI anomalisi — kök neden analizi başlat."
        )
    if data.kpi_with_data < data.kpi_total * 0.6:
        data.recommendations.append(
            f"📥 Bu çeyrekte KPI'ların yalnızca %{(data.kpi_with_data/max(data.kpi_total,1))*100:.0f}'ı için "
            "veri girilmiş — veri girişi disiplinini güçlendirin."
        )
    if not data.recommendations:
        data.recommendations.append(
            "✅ Genel durum sağlıklı görünüyor. Bir sonraki çeyreğe geçebilirsiniz."
        )

    return data
