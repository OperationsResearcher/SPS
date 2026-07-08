"""Stratejik analiz modelleri — plan year bazlı (SWOT, TOWS, PESTEL, Porter)."""
from datetime import datetime, timezone
from extensions import db
from app.utils.tenant_guard import TenantScopedMixin


class SwotAnalysis(TenantScopedMixin, db.Model):
    """
    SWOT Analizi. Her PlanYear / Tenant kombinasyonu için bir kayıt.
    Güçlü/Zayıf yönler, Fırsatlar ve Tehditler JSON dizisi olarak saklanır.
    """
    __tablename__ = "swot_analyses"

    id = db.Column(db.Integer, primary_key=True)
    plan_year_id = db.Column(
        db.Integer, db.ForeignKey("plan_years.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    tenant_id = db.Column(
        db.Integer, db.ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    source_swot_id = db.Column(
        db.Integer, db.ForeignKey("swot_analyses.id", ondelete="SET NULL"),
        nullable=True
    )

    # Her alan: JSON dizisi — [{"id": 1, "text": "...", "order": 1}, ...]
    strengths = db.Column(db.Text, nullable=True)      # Güçlü Yönler (S)
    weaknesses = db.Column(db.Text, nullable=True)     # Zayıf Yönler (W)
    opportunities = db.Column(db.Text, nullable=True)  # Fırsatlar (O)
    threats = db.Column(db.Text, nullable=True)        # Tehditler (T)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    plan_year = db.relationship(
        "PlanYear",
        backref=db.backref("swot_analyses", lazy="dynamic", cascade="all, delete-orphan")
    )
    tenant = db.relationship(
        "Tenant",
        backref=db.backref("swot_analyses", lazy="dynamic")
    )
    source_swot = db.relationship(
        "SwotAnalysis", remote_side=[id], foreign_keys=[source_swot_id]
    )

    __table_args__ = (
        db.UniqueConstraint("plan_year_id", "tenant_id", name="uq_swot_plan_year_tenant"),
    )

    def __repr__(self):
        return f"<SwotAnalysis plan_year={self.plan_year_id} tenant={self.tenant_id}>"


class TowsAnalysis(TenantScopedMixin, db.Model):
    """
    TOWS Matrisi. Her PlanYear / Tenant için SWOT'tan türetilen stratejiler.
    SO, ST, WO, WT strateji grupları JSON dizisi olarak saklanır.
    """
    __tablename__ = "tows_analyses"

    id = db.Column(db.Integer, primary_key=True)
    plan_year_id = db.Column(
        db.Integer, db.ForeignKey("plan_years.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    tenant_id = db.Column(
        db.Integer, db.ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    source_tows_id = db.Column(
        db.Integer, db.ForeignKey("tows_analyses.id", ondelete="SET NULL"),
        nullable=True
    )

    # Her alan: JSON dizisi — [{"id": 1, "text": "...", "order": 1}, ...]
    so_strategies = db.Column(db.Text, nullable=True)  # S+O: Güçlü yönler × Fırsatlar
    st_strategies = db.Column(db.Text, nullable=True)  # S+T: Güçlü yönler × Tehditler
    wo_strategies = db.Column(db.Text, nullable=True)  # W+O: Zayıf yönler × Fırsatlar
    wt_strategies = db.Column(db.Text, nullable=True)  # W+T: Zayıf yönler × Tehditler

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    plan_year = db.relationship(
        "PlanYear",
        backref=db.backref("tows_analyses", lazy="dynamic", cascade="all, delete-orphan")
    )
    tenant = db.relationship(
        "Tenant",
        backref=db.backref("tows_analyses", lazy="dynamic")
    )
    source_tows = db.relationship(
        "TowsAnalysis", remote_side=[id], foreign_keys=[source_tows_id]
    )

    __table_args__ = (
        db.UniqueConstraint("plan_year_id", "tenant_id", name="uq_tows_plan_year_tenant"),
    )

    def __repr__(self):
        return f"<TowsAnalysis plan_year={self.plan_year_id} tenant={self.tenant_id}>"


class PestelAnalysis(TenantScopedMixin, db.Model):
    """
    PESTEL Analizi. Her PlanYear / Tenant için bir kayıt.
    Her kategori JSON dizisi: [{"id":1,"text":"...","impact":"positive","order":1}, ...]
    """
    __tablename__ = "pestel_analyses"

    id = db.Column(db.Integer, primary_key=True)
    plan_year_id = db.Column(
        db.Integer, db.ForeignKey("plan_years.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    tenant_id = db.Column(
        db.Integer, db.ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    source_pestel_id = db.Column(
        db.Integer, db.ForeignKey("pestel_analyses.id", ondelete="SET NULL"),
        nullable=True
    )

    political     = db.Column(db.Text, nullable=True)   # Siyasi
    economic      = db.Column(db.Text, nullable=True)   # Ekonomik
    social        = db.Column(db.Text, nullable=True)   # Sosyal
    technological = db.Column(db.Text, nullable=True)   # Teknolojik
    environmental = db.Column(db.Text, nullable=True)   # Çevresel
    legal         = db.Column(db.Text, nullable=True)   # Yasal

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    plan_year = db.relationship(
        "PlanYear",
        backref=db.backref("pestel_analyses", lazy="dynamic", cascade="all, delete-orphan")
    )
    tenant = db.relationship(
        "Tenant",
        backref=db.backref("pestel_analyses", lazy="dynamic")
    )
    source_pestel = db.relationship(
        "PestelAnalysis", remote_side=[id], foreign_keys=[source_pestel_id]
    )

    __table_args__ = (
        db.UniqueConstraint("plan_year_id", "tenant_id", name="uq_pestel_plan_year_tenant"),
    )

    def __repr__(self):
        return f"<PestelAnalysis plan_year={self.plan_year_id} tenant={self.tenant_id}>"


class PorterFiveForcesAnalysis(TenantScopedMixin, db.Model):
    """
    Porter's Five Forces Analizi.
    Her kuvvet: {"score": 1-5, "items": [{"id":1,"text":"...","order":1}, ...]}
    """
    __tablename__ = "porter_analyses"

    id = db.Column(db.Integer, primary_key=True)
    plan_year_id = db.Column(
        db.Integer, db.ForeignKey("plan_years.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    tenant_id = db.Column(
        db.Integer, db.ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    source_porter_id = db.Column(
        db.Integer, db.ForeignKey("porter_analyses.id", ondelete="SET NULL"),
        nullable=True
    )

    rivalry_intensity   = db.Column(db.Text, nullable=True)   # Sektör Rekabet Yoğunluğu
    supplier_power      = db.Column(db.Text, nullable=True)   # Tedarikçi Gücü
    buyer_power         = db.Column(db.Text, nullable=True)   # Alıcı Gücü
    new_entrant_threat  = db.Column(db.Text, nullable=True)   # Yeni Giriş Tehdidi
    substitute_threat   = db.Column(db.Text, nullable=True)   # İkame Ürün Tehdidi

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    plan_year = db.relationship(
        "PlanYear",
        backref=db.backref("porter_analyses", lazy="dynamic", cascade="all, delete-orphan")
    )
    tenant = db.relationship(
        "Tenant",
        backref=db.backref("porter_analyses", lazy="dynamic")
    )
    source_porter = db.relationship(
        "PorterFiveForcesAnalysis", remote_side=[id], foreign_keys=[source_porter_id]
    )

    __table_args__ = (
        db.UniqueConstraint("plan_year_id", "tenant_id", name="uq_porter_plan_year_tenant"),
    )

    def __repr__(self):
        return f"<PorterFiveForcesAnalysis plan_year={self.plan_year_id} tenant={self.tenant_id}>"
