"""Strategy models - SWOT Analysis."""

from datetime import datetime, timezone

from app.models import db


class SwotAnalysis(db.Model):
    """SWOT analysis item per tenant."""

    __tablename__ = "swot_analyses"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False)
    category = db.Column(db.String(32), nullable=False)  # strength, weakness, opportunity, threat
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
