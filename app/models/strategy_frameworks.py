"""Akademik strateji çerçeveleri — Blue Ocean & VRIO modelleri.

S60-S61: AntiGravity raporundan seçilen, mevcut SWOT/PESTLE'a tamamlayıcı modeller.
"""
from __future__ import annotations

from extensions import db


# ─── Blue Ocean Strategy ─────────────────────────────────────────────────────

class BlueOceanCanvas(db.Model):
    """Bir sektör/pazar için Strategy Canvas (Value Curve) ana kaydı."""

    __tablename__ = "blue_ocean_canvases"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(
        db.Integer, db.ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    name = db.Column(db.String(200), nullable=False)
    industry = db.Column(db.String(120), nullable=True)
    description = db.Column(db.Text, nullable=True)
    competitor_names = db.Column(db.Text, nullable=True)  # comma-separated
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime, nullable=False,
        server_default=db.func.now(), onupdate=db.func.now(),
    )

    factors = db.relationship(
        "BlueOceanFactor", backref="canvas",
        cascade="all, delete-orphan", lazy="selectin",
    )
    errc_items = db.relationship(
        "BlueOceanERRC", backref="canvas",
        cascade="all, delete-orphan", lazy="selectin",
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "industry": self.industry,
            "description": self.description,
            "competitor_names": [c.strip() for c in (self.competitor_names or "").split(",") if c.strip()],
            "factor_count": len(self.factors) if self.factors else 0,
            "errc_count": len(self.errc_items) if self.errc_items else 0,
        }


class BlueOceanFactor(db.Model):
    """Rekabet faktörü (Fiyat, Kalite, Hız vb.) + kendi & rakip puanları (1-10)."""

    __tablename__ = "blue_ocean_factors"

    id = db.Column(db.Integer, primary_key=True)
    canvas_id = db.Column(
        db.Integer, db.ForeignKey("blue_ocean_canvases.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    name = db.Column(db.String(150), nullable=False)
    order_index = db.Column(db.Integer, nullable=False, default=0)
    self_score = db.Column(db.Float, nullable=False, default=5.0)
    # Rakip puanları: JSON string "{'rakip1': 7, 'rakip2': 4}"
    competitor_scores = db.Column(db.Text, nullable=True)

    def to_dict(self) -> dict:
        import json
        try:
            comp = json.loads(self.competitor_scores) if self.competitor_scores else {}
        except Exception:
            comp = {}
        return {
            "id": self.id,
            "name": self.name,
            "order_index": self.order_index,
            "self_score": self.self_score,
            "competitor_scores": comp,
        }


class BlueOceanERRC(db.Model):
    """ERRC (Eliminate / Reduce / Raise / Create) öğesi."""

    __tablename__ = "blue_ocean_errc_items"

    id = db.Column(db.Integer, primary_key=True)
    canvas_id = db.Column(
        db.Integer, db.ForeignKey("blue_ocean_canvases.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    action = db.Column(db.String(20), nullable=False)
    # eliminate / reduce / raise / create
    text = db.Column(db.Text, nullable=False)
    rationale = db.Column(db.Text, nullable=True)
    impact = db.Column(db.String(20), nullable=True)  # high/medium/low
    order_index = db.Column(db.Integer, nullable=False, default=0)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "action": self.action,
            "text": self.text,
            "rationale": self.rationale,
            "impact": self.impact,
            "order_index": self.order_index,
        }


# ─── VRIO ────────────────────────────────────────────────────────────────────

class VRIOResource(db.Model):
    """Kurumsal kaynak/yetenek + VRIO değerlendirmesi."""

    __tablename__ = "vrio_resources"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(
        db.Integer, db.ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(80), nullable=True)
    # tangible / intangible / human / financial / organizational
    description = db.Column(db.Text, nullable=True)

    is_valuable = db.Column(db.Boolean, nullable=False, default=False)
    is_rare = db.Column(db.Boolean, nullable=False, default=False)
    is_inimitable = db.Column(db.Boolean, nullable=False, default=False)
    is_organized = db.Column(db.Boolean, nullable=False, default=False)

    note = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime, nullable=False,
        server_default=db.func.now(), onupdate=db.func.now(),
    )

    @property
    def competitive_label(self) -> str:
        """VRIO yorumu — Barney karar ağacı."""
        if not self.is_valuable:
            return "Rekabetçi Dezavantaj"
        if not self.is_rare:
            return "Rekabet Paritesi"
        if not self.is_inimitable:
            return "Geçici Rekabet Avantajı"
        if not self.is_organized:
            return "Kullanılmayan Avantaj"
        return "Sürdürülebilir Rekabet Avantajı"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "is_valuable": self.is_valuable,
            "is_rare": self.is_rare,
            "is_inimitable": self.is_inimitable,
            "is_organized": self.is_organized,
            "note": self.note,
            "competitive_label": self.competitive_label,
        }
