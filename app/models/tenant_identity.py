"""Kurumsal kimlik — çok-satırlı Değer / Etik / Kalite maddeleri.

L1 (2026-06): tenants.core_values/code_of_ethics/quality_policy tek-TEXT
alanlarından çok-satırlı yapıya geçiş. Her madde ayrı kayıt (başlık + açıklama)
→ KOE "Kimlik & Strateji Netliği" boyutu satır-bazlı ölçülebilir, onboarding
şablondan madde işaretleme yapabilir, AI danışman "X'in açıklaması boş" diyebilir.

Karar (2026-06): "temiz kesim" — yeni tablolar canonical olur; eski TEXT
kolonları DB'de KALIR (geri-dönüş ağı) ama okunmaz/yazılmaz.
"""
from __future__ import annotations

from datetime import datetime, timezone

from extensions import db


class _KimlikMaddesiMixin:
    """Değer/Etik/Kalite maddelerinin ortak alanları (başlık + açıklama + sıra)."""

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(
        db.Integer, db.ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    baslik = db.Column(db.String(200), nullable=False)
    aciklama = db.Column(db.Text, nullable=True)
    sira = db.Column(db.Integer, default=0)  # gösterim sırası

    # Soft delete (KURALLAR §3)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class TenantValue(_KimlikMaddesiMixin, db.Model):
    """Kurumsal Değer maddesi (eski tenants.core_values yerine)."""
    __tablename__ = "tenant_values"

    def __repr__(self):
        return f"<TenantValue t={self.tenant_id} {self.baslik!r}>"


class TenantEthicsCode(_KimlikMaddesiMixin, db.Model):
    """Etik Kural maddesi (eski tenants.code_of_ethics yerine)."""
    __tablename__ = "tenant_ethics_codes"

    def __repr__(self):
        return f"<TenantEthicsCode t={self.tenant_id} {self.baslik!r}>"


class TenantQualityPolicy(_KimlikMaddesiMixin, db.Model):
    """Kalite Politikası maddesi (eski tenants.quality_policy yerine)."""
    __tablename__ = "tenant_quality_policies"

    def __repr__(self):
        return f"<TenantQualityPolicy t={self.tenant_id} {self.baslik!r}>"
