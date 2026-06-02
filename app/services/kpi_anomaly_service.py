"""KPI Anomali Tespit Servisi (Sprint 14.1).

Z-score tabanlı sapma tespiti — bir KPI'nın son ölçümü tarihsel ortalamadan
N standart sapma uzaktaysa anomali olarak işaretle.

Kullanım:
    from app.services.kpi_anomaly_service import detect_anomalies_for_tenant
    results = detect_anomalies_for_tenant(tenant_id=27, threshold=2.0)
    # [{kpi_id, kpi_name, latest_value, mean, std, z_score, severity}, ...]
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from math import sqrt

from extensions import db
from sqlalchemy import text


@dataclass
class AnomalyResult:
    kpi_id: int
    kpi_code: str
    kpi_name: str
    process_code: str
    latest_value: float
    latest_date: str
    mean: float
    std: float
    z_score: float
    severity: str  # "low", "medium", "high"
    direction: str  # "Increasing", "Decreasing"
    target_value: Optional[float]

    def to_dict(self) -> dict:
        return {
            "kpi_id": self.kpi_id,
            "kpi_code": self.kpi_code,
            "kpi_name": self.kpi_name,
            "process_code": self.process_code,
            "latest_value": self.latest_value,
            "latest_date": self.latest_date,
            "mean": round(self.mean, 2),
            "std": round(self.std, 2),
            "z_score": round(self.z_score, 2),
            "severity": self.severity,
            "direction": self.direction,
            "target_value": self.target_value,
        }


def _classify_severity(z_abs: float) -> str:
    if z_abs >= 3.0:
        return "high"
    if z_abs >= 2.0:
        return "medium"
    return "low"


def detect_anomalies_for_tenant(
    tenant_id: int,
    threshold: float = 2.0,
    min_samples: int = 5,
    limit: int = 100,
) -> list[AnomalyResult]:
    """Bir tenant'taki tüm KPI'lar için anomali tara.

    Args:
        tenant_id: Hedef tenant
        threshold: Z-score eşiği (default 2.0 → %95 CI dışı)
        min_samples: Anomali tespiti için minimum tarihsel veri sayısı
        limit: Maksimum anomali sayısı (sorted by |z_score| desc)
    """
    # Her KPI için son değer + tarihsel istatistik (mean, std, count)
    # Tek sorguda PostgreSQL window function ile
    sql = text("""
        WITH kpi_latest AS (
            SELECT DISTINCT ON (kd.process_kpi_id)
                kd.process_kpi_id,
                kd.actual_value::float AS latest_value,
                kd.data_date AS latest_date
            FROM kpi_data kd
            JOIN process_kpis k ON kd.process_kpi_id = k.id
            JOIN processes p ON k.process_id = p.id
            WHERE p.tenant_id = :tid
              AND kd.is_active = true
              AND k.is_active = true
              AND kd.actual_value ~ '^-?[0-9]+\\.?[0-9]*$'
            ORDER BY kd.process_kpi_id, kd.data_date DESC, kd.id DESC
        ),
        kpi_stats AS (
            SELECT
                kd.process_kpi_id,
                AVG(kd.actual_value::float) AS mean_val,
                STDDEV_SAMP(kd.actual_value::float) AS std_val,
                COUNT(*) AS sample_count
            FROM kpi_data kd
            JOIN process_kpis k ON kd.process_kpi_id = k.id
            JOIN processes p ON k.process_id = p.id
            WHERE p.tenant_id = :tid
              AND kd.is_active = true
              AND kd.actual_value ~ '^-?[0-9]+\\.?[0-9]*$'
            GROUP BY kd.process_kpi_id
        )
        SELECT
            k.id AS kpi_id,
            k.code AS kpi_code,
            k.name AS kpi_name,
            k.direction,
            k.target_value,
            p.code AS process_code,
            kl.latest_value,
            kl.latest_date,
            ks.mean_val,
            ks.std_val,
            ks.sample_count
        FROM process_kpis k
        JOIN processes p ON k.process_id = p.id
        JOIN kpi_latest kl ON kl.process_kpi_id = k.id
        JOIN kpi_stats ks ON ks.process_kpi_id = k.id
        WHERE p.tenant_id = :tid
          AND k.is_active = true
          AND ks.sample_count >= :min_samples
          AND ks.std_val > 0
    """)

    rows = db.session.execute(sql, {"tid": tenant_id, "min_samples": min_samples}).fetchall()
    results: list[AnomalyResult] = []
    for r in rows:
        mean_val = float(r.mean_val or 0)
        std_val = float(r.std_val or 0)
        latest = float(r.latest_value or 0)
        if std_val == 0:
            continue
        z = (latest - mean_val) / std_val
        if abs(z) < threshold:
            continue

        try:
            target_num = float(r.target_value) if r.target_value is not None else None
        except (ValueError, TypeError):
            target_num = None

        results.append(AnomalyResult(
            kpi_id=r.kpi_id,
            kpi_code=r.kpi_code or "",
            kpi_name=r.kpi_name or "",
            process_code=r.process_code or "",
            latest_value=latest,
            latest_date=r.latest_date.isoformat() if r.latest_date else "",
            mean=mean_val,
            std=std_val,
            z_score=z,
            severity=_classify_severity(abs(z)),
            direction=r.direction or "Increasing",
            target_value=target_num,
        ))

    # |z_score| büyükten küçüğe sırala, limit
    results.sort(key=lambda x: abs(x.z_score), reverse=True)
    return results[:limit]


def is_unfavorable_anomaly(result: AnomalyResult) -> bool:
    """Anomali kötü yönde mi?

    Direction=Increasing + latest < mean → kötü (target'tan uzaklaşma)
    Direction=Decreasing + latest > mean → kötü
    """
    if result.direction == "Increasing":
        return result.z_score < 0
    if result.direction == "Decreasing":
        return result.z_score > 0
    return abs(result.z_score) >= 2.5  # bilinmeyen yön → büyük sapma kötü kabul
