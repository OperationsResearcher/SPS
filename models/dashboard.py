from extensions import db
from datetime import datetime

class UserDashboardSettings(db.Model):
    """
    V3 Dashboard için kullanıcıya özel widget yerleşim ayarları.
    """
    __tablename__ = 'user_dashboard_settings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    layout_config = db.Column(db.Text, nullable=True) # JSON string olarak widget sıralamasını tutar
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # User ilişkisi (models/user.py içindeki User modeline referans)
    # backref eklemek yerine sadece ForeignKey tutuyoruz, gerekirse User modeline relationship eklenir.
    user = db.relationship('User', backref=db.backref('dashboard_settings_v3', uselist=False))

    def __repr__(self):
        return f'<UserDashboardSettings User:{self.user_id}>'
