"""K-Radar domain tablolari (Faz-B paket-1)."""

from datetime import datetime, timezone

from extensions import db


class ProcessMaturity(db.Model):
    __tablename__ = "process_maturity"
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    process_id = db.Column(db.Integer, db.ForeignKey("processes.id"), nullable=False, index=True)
    maturity_level = db.Column(db.Integer, nullable=False)
    dimension = db.Column(db.String(100), nullable=True)
    assessed_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    assessed_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class BottleneckLog(db.Model):
    __tablename__ = "bottleneck_log"
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    process_id = db.Column(db.Integer, db.ForeignKey("processes.id"), nullable=False, index=True)
    kpi_id = db.Column(db.Integer, db.ForeignKey("process_kpis.id"), nullable=True, index=True)
    severity = db.Column(db.String(20), nullable=True)
    note = db.Column(db.Text, nullable=True)
    triggered_at = db.Column(db.DateTime, nullable=True, index=True)
    resolved_at = db.Column(db.DateTime, nullable=True, index=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class ValueChainItem(db.Model):
    __tablename__ = "value_chain_items"
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    category = db.Column(db.String(20), nullable=False)  # primary/support
    linked_process_id = db.Column(db.Integer, db.ForeignKey("processes.id"), nullable=True, index=True)
    muda_type = db.Column(db.String(50), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    note = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class EvmSnapshot(db.Model):
    __tablename__ = "evm_snapshots"
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False, index=True)
    snapshot_date = db.Column(db.Date, nullable=False, index=True)
    pv = db.Column(db.Float, nullable=True)
    ev = db.Column(db.Float, nullable=True)
    ac = db.Column(db.Float, nullable=True)
    spi = db.Column(db.Float, nullable=True)
    cpi = db.Column(db.Float, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class RiskHeatmapItem(db.Model):
    __tablename__ = "risk_heatmap_items"
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    probability = db.Column(db.Integer, nullable=False)
    impact = db.Column(db.Integer, nullable=False)
    rpn = db.Column(db.Integer, nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    status = db.Column(db.String(50), nullable=True)
    source_type = db.Column(db.String(50), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class StakeholderMap(db.Model):
    __tablename__ = "stakeholder_maps"
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(100), nullable=True)
    influence = db.Column(db.Integer, nullable=True)
    interest = db.Column(db.Integer, nullable=True)
    strategy = db.Column(db.String(200), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class StakeholderSurvey(db.Model):
    __tablename__ = "stakeholder_surveys"
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    stakeholder_type = db.Column(db.String(100), nullable=False)
    period = db.Column(db.String(50), nullable=True)
    score = db.Column(db.Float, nullable=True)
    comment = db.Column(db.Text, nullable=True)
    source = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class A3Report(db.Model):
    __tablename__ = "a3_reports"
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    source_type = db.Column(db.String(50), nullable=True)
    source_id = db.Column(db.Integer, nullable=True)
    problem = db.Column(db.Text, nullable=True)
    root_cause_json = db.Column(db.Text, nullable=True)
    countermeasures = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class CompetitorAnalysis(db.Model):
    __tablename__ = "competitor_analyses"
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    competitor_name = db.Column(db.String(200), nullable=False)
    dimension = db.Column(db.String(100), nullable=True)
    our_score = db.Column(db.Float, nullable=True)
    their_score = db.Column(db.Float, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
