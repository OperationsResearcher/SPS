"""
Notification Model
Sprint 7-9: Real-Time ve Bildirimler
"""

from app.extensions import db
from datetime import datetime

class Notification(db.Model):
    """Bildirim tablosu"""
    
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Kullanıcı
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Bildirim bilgisi
    type = db.Column(db.String(50), nullable=False)  # performance_alert, task_reminder, etc.
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    
    # Aksiyon
    action_url = db.Column(db.String(500))
    
    # Extra data (JSON) - renamed from metadata to avoid SQLAlchemy reserved word
    extra_data = db.Column(db.JSON)
    
    # Durum
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    read_at = db.Column(db.DateTime)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # İndeksler
    __table_args__ = (
        db.Index('idx_notification_user_read', 'user_id', 'is_read', 'created_at'),
        db.Index('idx_notification_type', 'type', 'created_at'),
        db.Index('idx_notification_priority', 'priority', 'is_read'),
    )
    
    def __repr__(self):
        return f'<Notification {self.type} for user {self.user_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'title': self.title,
            'message': self.message,
            'priority': self.priority,
            'action_url': self.action_url,
            'extra_data': self.extra_data,
            'is_read': self.is_read,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class NotificationPreference(db.Model):
    """Bildirim tercihleri tablosu"""
    
    __tablename__ = 'notification_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Email bildirimleri
    email_performance_alerts = db.Column(db.Boolean, default=True)
    email_task_reminders = db.Column(db.Boolean, default=True)
    email_collaboration = db.Column(db.Boolean, default=True)
    email_achievements = db.Column(db.Boolean, default=False)
    email_system = db.Column(db.Boolean, default=True)
    
    # In-app bildirimleri
    inapp_performance_alerts = db.Column(db.Boolean, default=True)
    inapp_task_reminders = db.Column(db.Boolean, default=True)
    inapp_collaboration = db.Column(db.Boolean, default=True)
    inapp_achievements = db.Column(db.Boolean, default=True)
    inapp_system = db.Column(db.Boolean, default=True)
    
    # Push bildirimleri
    push_enabled = db.Column(db.Boolean, default=False)
    push_performance_alerts = db.Column(db.Boolean, default=True)
    push_task_reminders = db.Column(db.Boolean, default=True)
    
    # Özet email
    daily_digest = db.Column(db.Boolean, default=False)
    weekly_digest = db.Column(db.Boolean, default=True)
    
    # Timestamp
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<NotificationPreference for user {self.user_id}>'


class PushSubscription(db.Model):
    """Push notification subscription model"""
    __tablename__ = 'push_subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    endpoint = db.Column(db.Text, nullable=False)
    p256dh = db.Column(db.String(255), nullable=False)
    auth = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İndeksler
    __table_args__ = (
        db.Index('idx_push_subscription_user', 'user_id', 'is_active'),
        db.Index('idx_push_subscription_endpoint', 'endpoint'),
    )
    
    def __repr__(self):
        return f'<PushSubscription {self.id} - User {self.user_id}>'
