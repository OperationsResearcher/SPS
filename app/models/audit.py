"""
Audit Log Model
Sprint 5-6: Güvenlik ve Stabilite
Kullanıcı aktivitelerini loglama
"""

from app.models import db
from datetime import datetime

class AuditLog(db.Model):
    """Audit log tablosu"""
    
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Kullanıcı bilgisi
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    username = db.Column(db.String(100))
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=True)
    
    # Aksiyon bilgisi
    action = db.Column(db.String(50), nullable=False)  # CREATE, UPDATE, DELETE, LOGIN, LOGOUT
    resource_type = db.Column(db.String(50))  # Process, KPI, User, etc.
    resource_id = db.Column(db.Integer)
    
    # Detaylar
    description = db.Column(db.Text)
    old_values = db.Column(db.JSON)  # Eski değerler
    new_values = db.Column(db.JSON)  # Yeni değerler
    
    # Request bilgisi
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    request_method = db.Column(db.String(10))
    request_path = db.Column(db.String(500))
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # İndeksler
    __table_args__ = (
        db.Index('idx_audit_user', 'user_id', 'created_at'),
        db.Index('idx_audit_tenant', 'tenant_id', 'created_at'),
        db.Index('idx_audit_action', 'action', 'created_at'),
        db.Index('idx_audit_resource', 'resource_type', 'resource_id'),
    )
    
    def __repr__(self):
        return f'<AuditLog {self.action} by {self.username} at {self.created_at}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'description': self.description,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
