"""BSC (Balanced Scorecard) modeli."""
from datetime import datetime, timezone
from extensions import db

# 4 klasik BSC perspektifi
BSC_PERSPECTIVES = [
    ("finansal",    "Finansal"),
    ("musteri",     "Müşteri"),
    ("ic_surec",    "İç Süreçler"),
    ("ogrenme",     "Öğrenme & Gelişim"),
]


class BscKpiPerspective(db.Model):
    """
    ProcessKpi → BSC Perspektif ataması.
    Her KPI bir perspektife atanabilir.
    Aynı KPI farklı plan year'larda farklı perspektifte olabilir.
    """
    __tablename__ = "bsc_kpi_perspectives"

    id             = db.Column(db.Integer, primary_key=True)
    tenant_id      = db.Column(db.Integer, db.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_year_id   = db.Column(db.Integer, db.ForeignKey("plan_years.id", ondelete="CASCADE"), nullable=False, index=True)
    process_kpi_id = db.Column(db.Integer, db.ForeignKey("process_kpis.id", ondelete="CASCADE"), nullable=False, index=True)

    # finansal | musteri | ic_surec | ogrenme
    perspective    = db.Column(db.String(30), nullable=False)

    created_at     = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at     = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                               onupdate=lambda: datetime.now(timezone.utc))

    plan_year      = db.relationship("PlanYear",   backref=db.backref("bsc_kpi_perspectives", lazy="dynamic"))
    tenant         = db.relationship("Tenant",     backref=db.backref("bsc_kpi_perspectives", lazy="dynamic"))
    process_kpi    = db.relationship("ProcessKpi", backref=db.backref("bsc_perspective", uselist=False))

    __table_args__ = (
        db.UniqueConstraint("plan_year_id", "process_kpi_id", name="uq_bsc_kpi_perspective"),
        db.Index("idx_bsc_kpi_persp_lookup", "tenant_id", "plan_year_id", "perspective"),
    )

    def __repr__(self):
        return f"<BscKpiPerspective kpi={self.process_kpi_id} persp={self.perspective}>"
