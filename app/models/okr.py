"""OKR (Objectives and Key Results) modeli."""
from datetime import datetime, timezone
from extensions import db


class OkrObjective(db.Model):
    """
    OKR Hedefi (Objective).
    Bir plan year + tenant kombinasyonu için birden fazla hedef olabilir.
    """
    __tablename__ = "okr_objectives"

    id            = db.Column(db.Integer, primary_key=True)
    tenant_id     = db.Column(db.Integer, db.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_year_id  = db.Column(db.Integer, db.ForeignKey("plan_years.id", ondelete="CASCADE"), nullable=False, index=True)

    title         = db.Column(db.String(300), nullable=False)          # Hedef başlığı
    description   = db.Column(db.Text, nullable=True)                  # Açıklama
    quarter       = db.Column(db.Integer, nullable=True)               # 1-4 arası çeyrek, None = yıllık
    owner         = db.Column(db.String(200), nullable=True)           # Sorumlu kişi/ekip
    order_no      = db.Column(db.Integer, default=0)

    is_active     = db.Column(db.Boolean, default=True, nullable=False)
    created_at    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                              onupdate=lambda: datetime.now(timezone.utc))

    key_results   = db.relationship("OkrKeyResult", backref="objective",
                                    lazy="dynamic", cascade="all, delete-orphan",
                                    order_by="OkrKeyResult.order_no")

    plan_year     = db.relationship("PlanYear", backref=db.backref("okr_objectives", lazy="dynamic"))
    tenant        = db.relationship("Tenant",   backref=db.backref("okr_objectives", lazy="dynamic"))

    def __repr__(self):
        return f"<OkrObjective {self.id} {self.title[:40]}>"


class OkrKeyResult(db.Model):
    """
    Anahtar Sonuç (Key Result).
    Her Objective'e bağlı, ölçülebilir sonuçlar.
    """
    __tablename__ = "okr_key_results"

    id            = db.Column(db.Integer, primary_key=True)
    objective_id  = db.Column(db.Integer, db.ForeignKey("okr_objectives.id", ondelete="CASCADE"), nullable=False, index=True)

    title         = db.Column(db.String(300), nullable=False)          # KR başlığı
    metric        = db.Column(db.String(100), nullable=True)           # Ölçüm birimi (%, sayı, vb.)
    start_value   = db.Column(db.Float, nullable=True)                 # Başlangıç değeri
    target_value  = db.Column(db.Float, nullable=True)                 # Hedef değer
    current_value = db.Column(db.Float, nullable=True)                 # Güncel değer
    order_no      = db.Column(db.Integer, default=0)

    is_active     = db.Column(db.Boolean, default=True, nullable=False)
    created_at    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                              onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<OkrKeyResult {self.id} {self.title[:40]}>"

    @property
    def progress(self) -> float | None:
        """0.0 – 1.0 arası ilerleme skoru."""
        if self.target_value is None or self.start_value is None:
            return None
        span = self.target_value - self.start_value
        if span == 0:
            return 1.0 if self.current_value == self.target_value else 0.0
        cur = self.current_value if self.current_value is not None else self.start_value
        return max(0.0, min(1.0, (cur - self.start_value) / span))

    @property
    def progress_pct(self) -> float | None:
        p = self.progress
        return round(p * 100, 1) if p is not None else None
