"""KPI Trend Forecasting (Sprint 46).

Basit linear regression + güven aralığı tahmini.
Tarihsel KpiData → gelecek N dönem projeksiyon.

Kullanım:
    from app.services.forecast_service import forecast_kpi
    result = forecast_kpi(kpi_id=100, periods_ahead=3)
    # {history: [...], forecast: [...], slope, r_squared, confidence_low/high}
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from extensions import db
from app.models.process import KpiData


@dataclass
class ForecastPoint:
    period: int  # 0=ilk, 1=ikinci ...
    label: str
    value: float
    confidence_low: Optional[float] = None
    confidence_high: Optional[float] = None
    is_forecast: bool = False

    def to_dict(self) -> dict:
        return {
            "period": self.period,
            "label": self.label,
            "value": round(self.value, 2),
            "confidence_low": round(self.confidence_low, 2) if self.confidence_low is not None else None,
            "confidence_high": round(self.confidence_high, 2) if self.confidence_high is not None else None,
            "is_forecast": self.is_forecast,
        }


def _linear_regression(xs: list[float], ys: list[float]) -> tuple[float, float, float]:
    """Linear regression — döner (slope, intercept, r_squared)."""
    n = len(xs)
    if n < 2:
        return 0.0, ys[0] if ys else 0.0, 0.0
    x_mean = sum(xs) / n
    y_mean = sum(ys) / n
    num = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    den_x = sum((x - x_mean) ** 2 for x in xs)
    den_y = sum((y - y_mean) ** 2 for y in ys)
    if den_x == 0:
        return 0.0, y_mean, 0.0
    slope = num / den_x
    intercept = y_mean - slope * x_mean
    r_sq = (num * num) / (den_x * den_y) if den_y else 0.0
    return slope, intercept, r_sq


def _standard_error(xs: list[float], ys: list[float], slope: float, intercept: float) -> float:
    """Tahmin standart hatası."""
    n = len(xs)
    if n < 3:
        return 0.0
    residuals = [y - (slope * x + intercept) for x, y in zip(xs, ys)]
    sse = sum(r ** 2 for r in residuals)
    return (sse / (n - 2)) ** 0.5


def forecast_kpi(
    kpi_id: int,
    periods_ahead: int = 3,
    confidence: float = 1.96,  # ~%95 CI
) -> dict:
    """Linear regression ile KPI projeksiyonu.

    Args:
        kpi_id: ProcessKpi.id
        periods_ahead: kaç gelecek dönem (period_no/data_date sırasıyla)
        confidence: standart hata çarpanı (1.96 = %95)

    Returns:
        {
            "kpi_id": int,
            "history": [{period, label, value}, ...],
            "forecast": [{period, label, value, confidence_low/high, is_forecast: True}],
            "slope": float,
            "intercept": float,
            "r_squared": float,
            "trend_direction": "up"/"down"/"flat",
        }
    """
    # Son 24 veri noktasını al (yeni → eski sıralanmış olarak iter)
    rows = (
        KpiData.query
        .filter_by(process_kpi_id=kpi_id, is_active=True)
        .order_by(KpiData.data_date.desc(), KpiData.id.desc())
        .limit(24)
        .all()
    )
    rows = list(reversed(rows))  # eski → yeni

    # Sayısal değerleri çıkar
    history: list[ForecastPoint] = []
    xs: list[float] = []
    ys: list[float] = []
    for i, r in enumerate(rows):
        try:
            val = float(r.actual_value)
        except (ValueError, TypeError):
            continue
        label = (
            f"{r.year} {r.period_type or ''} {r.period_no or ''}".strip()
            if r.year else (r.data_date.isoformat() if r.data_date else f"#{i}")
        )
        history.append(ForecastPoint(period=i, label=label, value=val, is_forecast=False))
        xs.append(float(i))
        ys.append(val)

    if len(xs) < 3:
        return {
            "success": False,
            "message": f"En az 3 veri noktası gerekli (mevcut: {len(xs)})",
            "history": [p.to_dict() for p in history],
            "forecast": [],
        }

    slope, intercept, r_sq = _linear_regression(xs, ys)
    se = _standard_error(xs, ys, slope, intercept)

    forecast: list[ForecastPoint] = []
    next_period = len(xs)
    for k in range(periods_ahead):
        x = float(next_period + k)
        pred = slope * x + intercept
        ci = confidence * se
        forecast.append(ForecastPoint(
            period=int(x),
            label=f"T+{k + 1}",
            value=pred,
            confidence_low=pred - ci,
            confidence_high=pred + ci,
            is_forecast=True,
        ))

    direction = "up" if slope > 0.01 else "down" if slope < -0.01 else "flat"

    return {
        "success": True,
        "kpi_id": kpi_id,
        "history": [p.to_dict() for p in history],
        "forecast": [p.to_dict() for p in forecast],
        "slope": round(slope, 4),
        "intercept": round(intercept, 4),
        "r_squared": round(r_sq, 4),
        "standard_error": round(se, 4),
        "trend_direction": direction,
        "samples": len(xs),
    }
