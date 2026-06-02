"""Uygulama geneli anahtar-değer ayarları (tenant bağımsız)."""

from datetime import datetime, timezone

from app.models import db


class SystemSetting(db.Model):
    """Örn. maintenance_mode — tek satır key/value."""

    __tablename__ = "system_settings"

    key = db.Column(db.String(64), primary_key=True)
    value = db.Column(db.Text, nullable=False)
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self):
        return f"<SystemSetting {self.key}={str(self.value or '')[:20]}>"
