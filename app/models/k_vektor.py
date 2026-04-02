"""K-Vektör ağırlık ve denetim kayıtları."""

from datetime import datetime, timezone

from app.models import db


class KVektorStrategyWeight(db.Model):
    """Ana strateji ham ağırlığı (K-Vektör kota bölüşümü)."""

    __tablename__ = "k_vektor_strategy_weights"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    strategy_id = db.Column(db.Integer, db.ForeignKey("strategies.id", ondelete="CASCADE"), nullable=False)
    weight_raw = db.Column(db.Float, nullable=True)

    tenant = db.relationship("Tenant", backref=db.backref("k_vektor_strategy_weights", lazy=True, cascade="all, delete-orphan"))
    strategy = db.relationship("Strategy", backref=db.backref("k_vektor_weight_row", uselist=False, lazy=True))

    __table_args__ = (db.UniqueConstraint("tenant_id", "strategy_id", name="uq_kv_strat_w_tenant_strategy"),)


class KVektorSubStrategyWeight(db.Model):
    """Alt strateji ham ağırlığı (ebeveyn ana strateji kotası içinde)."""

    __tablename__ = "k_vektor_sub_strategy_weights"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    sub_strategy_id = db.Column(db.Integer, db.ForeignKey("sub_strategies.id", ondelete="CASCADE"), nullable=False)
    weight_raw = db.Column(db.Float, nullable=True)

    tenant = db.relationship("Tenant", backref=db.backref("k_vektor_sub_strategy_weights", lazy=True, cascade="all, delete-orphan"))
    sub_strategy = db.relationship("SubStrategy", backref=db.backref("k_vektor_weight_row", uselist=False, lazy=True))

    __table_args__ = (db.UniqueConstraint("tenant_id", "sub_strategy_id", name="uq_kv_sub_w_tenant_sub"),)


class KVektorConfigSnapshot(db.Model):
    """Yapılandırma / ağırlık değişikliği anı (denetim)."""

    __tablename__ = "k_vektor_config_snapshots"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    snapshot_type = db.Column(db.String(64), nullable=False)
    payload_json = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    tenant = db.relationship("Tenant", backref=db.backref("k_vektor_snapshots", lazy=True))
    user = db.relationship("User", foreign_keys=[user_id], backref=db.backref("k_vektor_snapshots", lazy=True))
