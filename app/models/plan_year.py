"""Plan Year models — yıllık stratejik planlama dönem sistemi (Faz 1-6).

EDGE CASE NOTU:
  plan_year=None durumu normaldir (feature flag kapalı veya yeni tenant).
  Route'larda MUTLAKA `if active_py:` kontrolü yapılmalı, active_py.id/year
  direkt erişilmemelidir. Güvenli pattern:
      py_id = active_py.id if active_py else None
      year  = active_py.year if active_py else datetime.now().year
"""
from datetime import datetime, timezone

from extensions import db


class PlanYear(db.Model):
    """
    Stratejik Plan Yılı.
    Her tenant için yıl başına bir kayıt. Tüm yıllık config tabloları buraya FK verir.
    Status: draft → active → closed → archived
    """
    __tablename__ = "plan_years"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(
        db.Integer, db.ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    year = db.Column(db.Integer, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=True)   # Ör: "2025 Stratejik Planı"
    status = db.Column(db.String(20), default="active", nullable=False)  # draft|active|closed|archived
    template_source_id = db.Column(
        db.Integer, db.ForeignKey("plan_years.id", ondelete="SET NULL"),
        nullable=True
    )
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    closed_at = db.Column(db.DateTime, nullable=True)

    # Sprint 56 (Ö5): Scenario branching
    scenario_of_id = db.Column(
        db.Integer, db.ForeignKey("plan_years.id", ondelete="CASCADE"),
        nullable=True, index=True,
    )
    scenario_label = db.Column(db.String(80), nullable=True)
    # "baseline" / "optimistic" / "pessimistic" / custom

    tenant = db.relationship(
        "Tenant", backref=db.backref("plan_years", lazy="dynamic")
    )
    template_source = db.relationship(
        "PlanYear", remote_side=[id], foreign_keys=[template_source_id],
        backref=db.backref("derived_years", lazy="dynamic")
    )

    __table_args__ = (
        # Sprint 56: scenarios bypass tenant+year uniqueness via partial index (migration)
        db.UniqueConstraint("tenant_id", "year", name="uq_plan_year_tenant_year"),
        db.Index("idx_plan_year_tenant_status", "tenant_id", "status"),
        db.Index("idx_plan_year_scenario_of", "scenario_of_id"),
    )

    def __repr__(self):
        return f"<PlanYear {self.year} tenant={self.tenant_id} status={self.status}>"


class KpiYearConfig(db.Model):
    """
    Yıllık KPI konfigürasyonu.
    ProcessKpi'daki tüm konfigürasyon alanlarının yıla özgü kopyası.
    Kayıt yoksa ProcessKpi'ın orijinal değerleri fallback olarak kullanılır.
    Hedef değişirse tüm o yılın dönemleri yeni hedefe göre dinamik hesaplanır.
    """
    __tablename__ = "kpi_year_configs"

    id = db.Column(db.Integer, primary_key=True)
    plan_year_id = db.Column(
        db.Integer, db.ForeignKey("plan_years.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    process_kpi_id = db.Column(
        db.Integer, db.ForeignKey("process_kpis.id", ondelete="CASCADE"),
        nullable=False, index=True
    )

    # Hedef & Yöntem (ProcessKpi'dan kopyalanır, değiştirilebilir)
    target_value = db.Column(db.String(100), nullable=True)
    unit = db.Column(db.String(50), nullable=True)
    period = db.Column(db.String(50), nullable=True)          # Aylık, Çeyreklik, Yıllık
    direction = db.Column(db.String(20), nullable=True)       # Increasing / Decreasing
    target_method = db.Column(db.String(10), nullable=True)   # RG, HKY, HK, SH, DH, SGH
    calculation_method = db.Column(db.String(20), nullable=True)  # Ortalama, Toplama, Son Değer
    basari_puani_araliklari = db.Column(db.Text, nullable=True)   # JSON (mevcut format korunur)
    onceki_yil_ortalamasi = db.Column(db.Float, nullable=True)

    # Plan dahiliyeti ve ağırlık
    weight = db.Column(db.Float, nullable=True)
    is_included = db.Column(db.Boolean, default=True, nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    plan_year = db.relationship(
        "PlanYear",
        backref=db.backref("kpi_year_configs", lazy="dynamic", cascade="all, delete-orphan")
    )
    process_kpi = db.relationship(
        "ProcessKpi",
        backref=db.backref("year_configs", lazy="dynamic")
    )

    __table_args__ = (
        db.UniqueConstraint("plan_year_id", "process_kpi_id", name="uq_kpi_year_config"),
        db.Index("idx_kpi_year_config_lookup", "plan_year_id", "process_kpi_id"),
    )

    def __repr__(self):
        return f"<KpiYearConfig plan_year={self.plan_year_id} kpi={self.process_kpi_id}>"


class StrategyYearConfig(db.Model):
    """Yıllık strateji override (başlık, kod, açıklama, dahiliyet, ağırlık).
    Boş alan varsa strategies tablosundan fallback kullanılır."""
    __tablename__ = "strategy_year_configs"

    id = db.Column(db.Integer, primary_key=True)
    plan_year_id = db.Column(
        db.Integer, db.ForeignKey("plan_years.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    strategy_id = db.Column(
        db.Integer, db.ForeignKey("strategies.id", ondelete="CASCADE"),
        nullable=False, index=True
    )

    title = db.Column(db.String(200), nullable=True)
    code = db.Column(db.String(20), nullable=True)
    description = db.Column(db.Text, nullable=True)
    is_included = db.Column(db.Boolean, default=True, nullable=False)
    weight = db.Column(db.Float, nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    plan_year = db.relationship(
        "PlanYear",
        backref=db.backref("strategy_year_configs", lazy="dynamic", cascade="all, delete-orphan")
    )
    strategy = db.relationship(
        "Strategy",
        backref=db.backref("year_configs", lazy="dynamic")
    )

    __table_args__ = (
        db.UniqueConstraint("plan_year_id", "strategy_id", name="uq_strategy_year_config"),
        db.Index("idx_strategy_year_config", "plan_year_id", "strategy_id"),
    )

    def __repr__(self):
        return f"<StrategyYearConfig plan_year={self.plan_year_id} strategy={self.strategy_id}>"


class SubStrategyYearConfig(db.Model):
    """Yıllık alt strateji override."""
    __tablename__ = "sub_strategy_year_configs"

    id = db.Column(db.Integer, primary_key=True)
    plan_year_id = db.Column(
        db.Integer, db.ForeignKey("plan_years.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    sub_strategy_id = db.Column(
        db.Integer, db.ForeignKey("sub_strategies.id", ondelete="CASCADE"),
        nullable=False, index=True
    )

    title = db.Column(db.String(200), nullable=True)
    code = db.Column(db.String(20), nullable=True)
    description = db.Column(db.Text, nullable=True)
    is_included = db.Column(db.Boolean, default=True, nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    plan_year = db.relationship(
        "PlanYear",
        backref=db.backref("sub_strategy_year_configs", lazy="dynamic", cascade="all, delete-orphan")
    )
    sub_strategy = db.relationship(
        "SubStrategy",
        backref=db.backref("year_configs", lazy="dynamic")
    )

    __table_args__ = (
        db.UniqueConstraint("plan_year_id", "sub_strategy_id", name="uq_sub_strategy_year_config"),
        db.Index("idx_sub_strategy_year_config", "plan_year_id", "sub_strategy_id"),
    )

    def __repr__(self):
        return f"<SubStrategyYearConfig plan_year={self.plan_year_id} sub={self.sub_strategy_id}>"


class ProcessYearConfig(db.Model):
    """Yıllık süreç override (ad, ağırlık, dahiliyet).
    Boş alan varsa processes tablosundan fallback kullanılır."""
    __tablename__ = "process_year_configs"

    id = db.Column(db.Integer, primary_key=True)
    plan_year_id = db.Column(
        db.Integer, db.ForeignKey("plan_years.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    process_id = db.Column(
        db.Integer, db.ForeignKey("processes.id", ondelete="CASCADE"),
        nullable=False, index=True
    )

    name = db.Column(db.String(200), nullable=True)
    weight = db.Column(db.Float, nullable=True)
    is_included = db.Column(db.Boolean, default=True, nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    plan_year = db.relationship(
        "PlanYear",
        backref=db.backref("process_year_configs", lazy="dynamic", cascade="all, delete-orphan")
    )
    process = db.relationship(
        "Process",
        backref=db.backref("year_configs", lazy="dynamic")
    )

    __table_args__ = (
        db.UniqueConstraint("plan_year_id", "process_id", name="uq_process_year_config"),
        db.Index("idx_process_year_config", "plan_year_id", "process_id"),
    )

    def __repr__(self):
        return f"<ProcessYearConfig plan_year={self.plan_year_id} process={self.process_id}>"


class IndividualKpiYearConfig(db.Model):
    """Yıllık bireysel PG konfigürasyonu."""
    __tablename__ = "individual_kpi_year_configs"

    id = db.Column(db.Integer, primary_key=True)
    plan_year_id = db.Column(
        db.Integer, db.ForeignKey("plan_years.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    individual_performance_id = db.Column(
        db.Integer,
        db.ForeignKey("individual_performance_indicators.id", ondelete="CASCADE"),
        nullable=False, index=True
    )

    target_value = db.Column(db.String(100), nullable=True)
    unit = db.Column(db.String(50), nullable=True)
    period = db.Column(db.String(50), nullable=True)
    direction = db.Column(db.String(20), nullable=True)
    target_method = db.Column(db.String(10), nullable=True)
    calculation_method = db.Column(db.String(20), nullable=True)
    basari_puani_araliklari = db.Column(db.Text, nullable=True)
    weight = db.Column(db.Float, nullable=True)
    is_included = db.Column(db.Boolean, default=True, nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    plan_year = db.relationship(
        "PlanYear",
        backref=db.backref(
            "individual_kpi_year_configs", lazy="dynamic", cascade="all, delete-orphan"
        )
    )
    individual_performance = db.relationship(
        "IndividualPerformanceIndicator",
        backref=db.backref("year_configs", lazy="dynamic")
    )

    __table_args__ = (
        db.UniqueConstraint(
            "plan_year_id", "individual_performance_id",
            name="uq_indiv_kpi_year_config"
        ),
        db.Index("idx_indiv_kpi_year_config", "plan_year_id", "individual_performance_id"),
    )

    def __repr__(self):
        return (
            f"<IndividualKpiYearConfig plan_year={self.plan_year_id} "
            f"ind={self.individual_performance_id}>"
        )
