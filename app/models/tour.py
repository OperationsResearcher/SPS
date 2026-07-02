"""Kule yardımcı sistemi — kullanıcı tur durum modeli."""

from datetime import datetime, timezone

from extensions import db


class UserTourProgress(db.Model):
    """Bir kullanıcı + tur_key için durum kaydı.

    status: 'pending' | 'completed' | 'dismissed'
    """

    __tablename__ = "user_tour_progress"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tour_key = db.Column(db.String(64), nullable=False)
    status = db.Column(db.String(16), nullable=False, default="pending")
    seen_count = db.Column(db.Integer, nullable=False, default=0)
    completed_at = db.Column(db.DateTime, nullable=True)
    dismissed_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=False,
                           default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint("user_id", "tour_key", name="uq_user_tour"),
    )

    def __repr__(self):
        return f"<UserTourProgress user={self.user_id} tour={self.tour_key} status={self.status}>"

    def to_dict(self) -> dict:
        return {
            "tour_key": self.tour_key,
            "status": self.status,
            "seen_count": self.seen_count,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "dismissed_at": self.dismissed_at.isoformat() if self.dismissed_at else None,
        }
