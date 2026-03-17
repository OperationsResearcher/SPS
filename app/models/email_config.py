"""Tenant e-posta yapılandırma modeli."""

from datetime import datetime, timezone
from app.models import db


class TenantEmailConfig(db.Model):
    """
    Tenant başına özel SMTP ayarları.
    Boş bırakılırsa sistem varsayılan SMTP'si (kokpitim.com) kullanılır.
    """

    __tablename__ = "tenant_email_configs"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(
        db.Integer, db.ForeignKey("tenants.id"), nullable=False, unique=True, index=True
    )

    # Özel SMTP aktif mi?
    use_custom_smtp = db.Column(db.Boolean, default=False, nullable=False)

    # SMTP bağlantı bilgileri
    smtp_host = db.Column(db.String(255), nullable=True)
    smtp_port = db.Column(db.Integer, default=587, nullable=True)
    smtp_use_tls = db.Column(db.Boolean, default=True, nullable=False)
    smtp_use_ssl = db.Column(db.Boolean, default=False, nullable=False)
    smtp_username = db.Column(db.String(255), nullable=True)
    smtp_password = db.Column(db.String(512), nullable=True)   # üretimde şifreli saklanmalı

    # Gönderici bilgisi
    sender_name = db.Column(db.String(128), nullable=True)     # "Kokpitim - Firma Adı"
    sender_email = db.Column(db.String(255), nullable=True)    # bildirim@firma.com

    # Bildirim tercihleri — hangi olaylar için mail gitsin
    notify_on_process_assign = db.Column(db.Boolean, default=True, nullable=False)
    notify_on_kpi_change = db.Column(db.Boolean, default=True, nullable=False)
    notify_on_activity_add = db.Column(db.Boolean, default=True, nullable=False)
    notify_on_task_assign = db.Column(db.Boolean, default=True, nullable=False)

    # Meta
    updated_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    tenant = db.relationship("Tenant", backref=db.backref("email_config", uselist=False))
    updater = db.relationship("User", foreign_keys=[updated_by])

    def __repr__(self):
        return f"<TenantEmailConfig tenant={self.tenant_id} custom={self.use_custom_smtp}>"
