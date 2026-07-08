"""TenantYearIdentity — Misyon/Vizyon/Değerler yıllık versiyonlaması."""
from datetime import datetime, timezone
from extensions import db
from app.utils.tenant_guard import TenantScopedMixin


class TenantYearIdentity(TenantScopedMixin, db.Model):
    """
    Kurumun stratejik kimlik alanlarının (misyon, vizyon, değerler vb.)
    yıl bazlı kopyası. Her PlanYear için bir kayıt.
    """
    __tablename__ = "tenant_year_identities"

    id = db.Column(db.Integer, primary_key=True)
    plan_year_id = db.Column(
        db.Integer, db.ForeignKey("plan_years.id", ondelete="CASCADE"),
        nullable=False, unique=True, index=True
    )
    tenant_id = db.Column(
        db.Integer, db.ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False, index=True
    )

    purpose = db.Column(db.Text, nullable=True)         # Amaç
    vision = db.Column(db.Text, nullable=True)          # Vizyon
    core_values = db.Column(db.Text, nullable=True)     # Değerler
    code_of_ethics = db.Column(db.Text, nullable=True)  # Etik Kurallar
    quality_policy = db.Column(db.Text, nullable=True)  # Kalite Politikası

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    plan_year = db.relationship(
        "PlanYear",
        backref=db.backref("tenant_year_identity", uselist=False, cascade="all, delete-orphan")
    )
    tenant = db.relationship(
        "Tenant",
        backref=db.backref("year_identities", lazy="dynamic")
    )

    def __repr__(self):
        return f"<TenantYearIdentity plan_year={self.plan_year_id} tenant={self.tenant_id}>"
