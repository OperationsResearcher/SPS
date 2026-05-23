"""ESG / Sürdürülebilirlik modelleri (Sprint 49).

Kategori (category):
  E — Environment (karbon, su, atık, enerji)
  S — Social (çeşitlilik, eğitim, sağlık)
  G — Governance (yönetişim, denetim)

Scope (carbon için):
  scope1 — Direkt emisyon (yakıt, sızıntı)
  scope2 — Satın alınan enerji (elektrik)
  scope3 — Indirect (tedarik zinciri, ulaşım)

SDG codes: BM Sürdürülebilir Kalkınma Hedefleri (SDG1-SDG17)
"""
from __future__ import annotations

from datetime import datetime, timezone

from extensions import db


class EsgMetric(db.Model):
    """ESG metric tanımı (tenant başına)."""

    __tablename__ = "esg_metrics"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    code = db.Column(db.String(50), nullable=True)  # örn. "CARBON-SC1-FUEL"
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=True, index=True)  # E/S/G
    scope = db.Column(db.String(20), nullable=True)  # scope1/scope2/scope3
    unit = db.Column(db.String(50), nullable=True)  # tCO2e, m3, kWh, %
    sdg_codes = db.Column(db.String(100), nullable=True)  # virgülle ayrılmış
    target_value = db.Column(db.Float, nullable=True)
    baseline_year = db.Column(db.Integer, nullable=True)
    baseline_value = db.Column(db.Float, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    values = db.relationship("EsgMetricValue", backref="metric", lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<EsgMetric {self.code or ''} {self.name}>"


class EsgMetricValue(db.Model):
    """ESG metric ölçüm (aylık/yıllık)."""

    __tablename__ = "esg_metric_values"

    id = db.Column(db.Integer, primary_key=True)
    metric_id = db.Column(db.Integer, db.ForeignKey("esg_metrics.id", ondelete="CASCADE"), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    period_type = db.Column(db.String(20), nullable=True)  # Aylık/Yıllık
    period_no = db.Column(db.Integer, nullable=True)
    value = db.Column(db.Float, nullable=True)
    source = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
