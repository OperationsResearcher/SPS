"""K-Radar kalici aksiyon modelleri."""

from datetime import datetime, timezone

from extensions import db


class KRadarRecommendationAction(db.Model):
    __tablename__ = "k_radar_recommendation_actions"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    recommendation_key = db.Column(db.String(64), nullable=False, index=True)
    recommendation_text = db.Column(db.Text, nullable=False)
    state = db.Column(db.String(20), nullable=False, default="pending")  # approved|rejected

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    tenant = db.relationship("Tenant", backref=db.backref("k_radar_actions", lazy=True))
    user = db.relationship("User", backref=db.backref("k_radar_actions", lazy=True))

    __table_args__ = (
        db.UniqueConstraint(
            "tenant_id", "user_id", "recommendation_key", name="uq_k_radar_action_user_key"
        ),
    )
