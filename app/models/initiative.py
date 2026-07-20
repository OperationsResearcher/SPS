"""Multi-Year Initiative (Sprint 55 — Ö4).

Stratejik initiatives birden çok yıla yayılabilir. Her initiative
yıllık plan year'lardan bağımsız bir yaşam döngüsüne sahiptir ama
hangi strateji/alt strateji ile bağlı olduğunu gösterir.
"""
from __future__ import annotations

from extensions import db
from app.utils.tenant_guard import TenantScopedMixin


class Initiative(TenantScopedMixin, db.Model):
    """Çok yıllık stratejik girişim (initiative)."""

    __tablename__ = "initiatives"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(
        db.Integer, db.ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )

    code = db.Column(db.String(40), nullable=True)
    name = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Bağlı strateji (opsiyonel — pure cross-strategy initiatives mümkün)
    strategy_id = db.Column(
        db.Integer, db.ForeignKey("strategies.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )
    sub_strategy_id = db.Column(
        db.Integer, db.ForeignKey("sub_strategies.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Yıl bazlı Faz 1.1 (T3/T9): girişimin ait olduğu plan yılı.
    # start_year/end_year KALDIRILMADI — halen okuyan route'lar var
    # (routes_initiative.py:35-37). Faz 3'te okuma yolları plan_year_id'ye
    # geçince ayrı migration'da düşürülecek (migration a1f2c3d4e5b6 docstring).
    plan_year_id = db.Column(
        db.Integer, db.ForeignKey("plan_years.id", ondelete="CASCADE"),
        nullable=True, index=True,
    )

    # Çok yıllık zaman aralığı
    start_year = db.Column(db.Integer, nullable=False)
    end_year = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)

    # Durum & finansal
    status = db.Column(db.String(30), nullable=False, default="planned")
    # planned / in_progress / on_hold / completed / cancelled
    priority = db.Column(db.String(20), nullable=False, default="medium")
    # critical / high / medium / low

    budget_total = db.Column(db.Numeric(18, 2), nullable=True)
    budget_spent = db.Column(db.Numeric(18, 2), nullable=True, default=0)

    progress_pct = db.Column(db.Float, nullable=False, default=0.0)

    owner_user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime, nullable=False,
        server_default=db.func.now(), onupdate=db.func.now(),
    )

    milestones = db.relationship(
        "InitiativeMilestone", backref="initiative",
        cascade="all, delete-orphan", lazy="selectin",
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "strategy_id": self.strategy_id,
            "sub_strategy_id": self.sub_strategy_id,
            "start_year": self.start_year,
            "end_year": self.end_year,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "status": self.status,
            "priority": self.priority,
            "budget_total": float(self.budget_total) if self.budget_total else None,
            "budget_spent": float(self.budget_spent) if self.budget_spent else 0.0,
            "progress_pct": self.progress_pct,
            "owner_user_id": self.owner_user_id,
            "milestone_count": len(self.milestones) if self.milestones else 0,
        }

    def __repr__(self):
        return f'<Initiative {self.id}, self.name[:20]>'


class InitiativeMilestone(db.Model):
    """Initiative kilometre taşı."""

    __tablename__ = "initiative_milestones"

    id = db.Column(db.Integer, primary_key=True)
    initiative_id = db.Column(
        db.Integer, db.ForeignKey("initiatives.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    name = db.Column(db.String(300), nullable=False)
    target_date = db.Column(db.Date, nullable=True)
    completed_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(30), nullable=False, default="pending")
    # pending / in_progress / done / missed
    note = db.Column(db.Text, nullable=True)
    order_index = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    def __repr__(self):
        return f'<InitiativeMilestone {self.id} {(self.name or "")[:20]}>'

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "initiative_id": self.initiative_id,
            "name": self.name,
            "target_date": self.target_date.isoformat() if self.target_date else None,
            "completed_date": self.completed_date.isoformat() if self.completed_date else None,
            "status": self.status,
            "note": self.note,
            "order_index": self.order_index,
        }
