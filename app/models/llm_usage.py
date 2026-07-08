"""LLM kullanım kaydı + tenant kotası modelleri.

Maliyet/abuse koruması için her LLM çağrısı log'lanır.
"""
from __future__ import annotations

from extensions import db
from app.utils.tenant_guard import TenantScopedMixin


class LLMUsageLog(TenantScopedMixin, db.Model):
    """Her LLM çağrısının ham kaydı."""

    __tablename__ = "llm_usage_logs"

    id = db.Column(db.BigInteger, primary_key=True)
    tenant_id = db.Column(
        db.Integer, db.ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    endpoint = db.Column(db.String(80), nullable=False, index=True)
    # ai_pivot / ai_coach / ai_summary / ai_early_warning

    provider = db.Column(db.String(40), nullable=False, default="gemini")
    model = db.Column(db.String(80), nullable=True)
    prompt_tokens = db.Column(db.Integer, nullable=False, default=0)
    output_tokens = db.Column(db.Integer, nullable=False, default=0)
    total_tokens = db.Column(db.Integer, nullable=False, default=0)
    cost_usd = db.Column(db.Numeric(10, 6), nullable=False, default=0)

    status = db.Column(db.String(20), nullable=False, default="ok")
    # ok / error / rate_limited / quota_exceeded
    error_msg = db.Column(db.String(500), nullable=True)
    duration_ms = db.Column(db.Integer, nullable=True)

    created_at = db.Column(
        db.DateTime, nullable=False,
        server_default=db.func.now(), index=True,
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "endpoint": self.endpoint,
            "provider": self.provider,
            "model": self.model,
            "prompt_tokens": self.prompt_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "cost_usd": float(self.cost_usd) if self.cost_usd else 0,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<LLMUsageLog {self.id} tenant={self.tenant_id}>"


class LLMQuotaOverride(TenantScopedMixin, db.Model):
    """Tenant'a özel kota overide (varsayılan paket limitlerini ezer)."""

    __tablename__ = "llm_quota_overrides"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(
        db.Integer, db.ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False, unique=True,
    )
    daily_call_limit = db.Column(db.Integer, nullable=True)
    monthly_call_limit = db.Column(db.Integer, nullable=True)
    monthly_cost_limit_usd = db.Column(db.Numeric(10, 2), nullable=True)
    is_paused = db.Column(db.Boolean, nullable=False, default=False)
    note = db.Column(db.Text, nullable=True)
    updated_at = db.Column(
        db.DateTime, nullable=False,
        server_default=db.func.now(), onupdate=db.func.now(),
    )

    def __repr__(self):
        return f"<LLMQuotaOverride {self.id} tenant={self.tenant_id}>"
