"""Marketing sitesi tanıtım formu kayıtları."""

from datetime import datetime, timezone

from extensions import db


class DemoRequest(db.Model):
    """/demo-talep formundan gelen kayıtlar."""

    __tablename__ = 'demo_requests'

    id = db.Column(db.Integer, primary_key=True)

    ad_soyad = db.Column(db.String(200), nullable=False)
    kurum = db.Column(db.String(200), nullable=False)
    gorev = db.Column(db.String(200))
    sektor = db.Column(db.String(100))
    calisan = db.Column(db.String(50))
    email = db.Column(db.String(200), nullable=False)
    telefon = db.Column(db.String(50))
    moduller = db.Column(db.String(500))
    mesaj = db.Column(db.Text)

    email_gonderildi = db.Column(db.Boolean, default=False, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        db.Index('idx_demo_request_created', 'created_at'),
    )

    def __repr__(self):
        return f'<DemoRequest {self.kurum} / {self.ad_soyad}>'
