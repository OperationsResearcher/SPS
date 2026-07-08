"""Replan Trigger model (Sprint 57 — Ö8).

Trigger-based replan: belirli koşullar gerçekleştiğinde
("KPI 2 ardışık dönem hedef altında", "Risk skoru > X", "Dış olay") otomatik
strateji ayarlama önerisi tetiklenir.
"""
from __future__ import annotations

from extensions import db
from app.utils.tenant_guard import TenantScopedMixin


class ReplanTrigger(TenantScopedMixin, db.Model):
    """Stratejik yeniden planlama tetikleyicisi."""

    __tablename__ = "replan_triggers"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(
        db.Integer, db.ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Tetik tipi
    trigger_type = db.Column(db.String(40), nullable=False)
    # kpi_below_target / risk_score / overdue_activity_pct /
    # anomaly_high / manual / external_event

    # Ölçüm parametreleri
    target_kpi_id = db.Column(
        db.Integer, db.ForeignKey("process_kpis.id", ondelete="CASCADE"),
        nullable=True,
    )
    threshold_value = db.Column(db.Float, nullable=True)
    threshold_operator = db.Column(db.String(5), nullable=True)  # < <= > >= == !=
    consecutive_periods = db.Column(db.Integer, nullable=False, default=1)

    # Aksiyon
    action = db.Column(db.String(40), nullable=False, default="notify")
    # notify / suggest_pivot / create_review / pause_initiative

    severity = db.Column(db.String(20), nullable=False, default="medium")

    is_active = db.Column(db.Boolean, nullable=False, default=True)
    last_fired_at = db.Column(db.DateTime, nullable=True)
    fire_count = db.Column(db.Integer, nullable=False, default=0)

    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime, nullable=False,
        server_default=db.func.now(), onupdate=db.func.now(),
    )

    def __repr__(self):
        return f"<ReplanTrigger {self.id} {(self.name or '')[:20]}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "trigger_type": self.trigger_type,
            "target_kpi_id": self.target_kpi_id,
            "threshold_value": self.threshold_value,
            "threshold_operator": self.threshold_operator,
            "consecutive_periods": self.consecutive_periods,
            "action": self.action,
            "severity": self.severity,
            "is_active": self.is_active,
            "last_fired_at": self.last_fired_at.isoformat() if self.last_fired_at else None,
            "fire_count": self.fire_count,
        }


class ReplanTriggerEvent(TenantScopedMixin, db.Model):
    """Bir trigger'ın tetiklendiği olayın günlüğü."""

    __tablename__ = "replan_trigger_events"

    id = db.Column(db.Integer, primary_key=True)
    trigger_id = db.Column(
        db.Integer, db.ForeignKey("replan_triggers.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    tenant_id = db.Column(db.Integer, nullable=False, index=True)
    fired_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    payload = db.Column(db.Text, nullable=True)  # JSON string: detay
    action_taken = db.Column(db.String(40), nullable=True)
    acknowledged_at = db.Column(db.DateTime, nullable=True)
    acknowledged_by_user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    def __repr__(self):
        return f"<ReplanTriggerEvent {self.id} trigger={self.trigger_id}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "trigger_id": self.trigger_id,
            "fired_at": self.fired_at.isoformat() if self.fired_at else None,
            "payload": self.payload,
            "action_taken": self.action_taken,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
        }
