# -*- coding: utf-8 -*-
"""
Geri Bildirim Sistemi (Kule Modülü) Modeli
-------------------------------------------
Kullanıcıların sistem hakkında geri bildirim göndermesi için.
"""
from extensions import db
from datetime import datetime

class Feedback(db.Model):
    """
    Geri Bildirim Modeli
    
    Kullanıcıların sistem hakkında hata bildirimi, öneri veya talep göndermesi için.
    """
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    page_url = db.Column(db.String(500), nullable=True)  # Hatanın alındığı sayfa adresi
    category = db.Column(db.String(50), nullable=False)  # 'Hata', 'Öneri', 'Talep'
    description = db.Column(db.Text, nullable=False)  # Kullanıcının yazdığı mesaj
    screenshot_path = db.Column(db.String(500), nullable=True)  # Resim yüklenirse dosya yolu
    status = db.Column(db.String(50), default='Bekliyor', nullable=False)  # 'Bekliyor', 'İnceleniyor', 'Çözüldü', 'Reddedildi'
    admin_note = db.Column(db.Text, nullable=True)  # Yöneticinin cevabı/notu
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # İlişki
    user = db.relationship('User', backref=db.backref('feedbacks', lazy=True))
    
    def __repr__(self):
        return f'<Feedback {self.id} - {self.category} - {self.status}>'
