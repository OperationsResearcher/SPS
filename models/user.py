# -*- coding: utf-8 -*-
"""
Kullanıcı ve Yetkilendirme Modelleri
-----------------------------------
Kullanıcı, rol, yetki matrisi, organizasyonel yapı, bildirimler ve loglar.
"""
from extensions import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    """
    Kullanıcı Modeli
    
    Sistemdeki tüm kullanıcıların temel bilgilerini, kimlik doğrulama verilerini
    ve sistem tercihlerini saklar. SQL Server uyumluluğu için tablo adı 'user' olarak belirtilmiştir.
    """
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(120), nullable=False)
    
    # Kişisel Bilgiler
    first_name = db.Column(db.String(50))  # Ad
    last_name = db.Column(db.String(50))   # Soyad
    phone = db.Column(db.String(20))       # Telefon
    title = db.Column(db.String(100))      # Unvan
    department = db.Column(db.String(100)) # Departman
    
    # Rol ve Yetkiler
    sistem_rol = db.Column(db.String(50), nullable=False, default='kurum_kullanici', index=True)
    # Roller: admin, kurum_yoneticisi, ust_yonetim, kurum_kullanici
    
    surec_rol = db.Column(db.String(50), default=None)  # surec_lideri, surec_uyesi, None
    
    # İlişkiler
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'), nullable=False, index=True)
    kurum = db.relationship('Kurum', backref=db.backref('users', lazy=True), foreign_keys=[kurum_id])
    
    # Görsel ve Tercihler
    profile_photo = db.Column(db.String(500))  # Profil fotoğrafı URL'si
    theme_preferences = db.Column(db.Text)     # JSON: {"theme": "dark", "color": "blue"}
    layout_preference = db.Column(db.String(20), default='classic')  # 'classic' veya 'sidebar'
    
    # Guide/Yardım Sistemi Tercihleri
    guide_character_style = db.Column(db.String(50), default='professional')  # professional, friendly, minimal
    show_page_guides = db.Column(db.Boolean, default=True, nullable=False)  # Sayfa yardımlarını göster
    completed_walkthroughs = db.Column(db.Text)  # JSON: {"dashboard": true, "projects": true}
    
    # Meta Veriler
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Soft Delete (Silinmiş gibi gösterme)
    silindi = db.Column(db.Boolean, default=False, nullable=False, index=True)
    deleted_at = db.Column(db.DateTime, nullable=True)
    deleted_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # İlişki tanımları
    deleter = db.relationship('User', remote_side=[id], foreign_keys=[deleted_by])
    
    def __repr__(self):
        return f'<User {self.username}>'

class Kurum(db.Model):
    """
    Kurum Modeli
    
    Sistemi kullanan firmaların/kurumların bilgilerini saklar.
    """
    __tablename__ = 'kurum'

    id = db.Column(db.Integer, primary_key=True)
    kisa_ad = db.Column(db.String(100), nullable=False, index=True)
    ticari_unvan = db.Column(db.String(200), nullable=False)
    faaliyet_alani = db.Column(db.String(200))
    
    # İletişim
    adres = db.Column(db.Text)
    il = db.Column(db.String(100))
    ilce = db.Column(db.String(100))
    email = db.Column(db.String(120))
    web_adresi = db.Column(db.String(200))
    telefon = db.Column(db.String(20))
    
    # Vergi Bilgileri
    calisan_sayisi = db.Column(db.Integer)
    sektor = db.Column(db.String(100))
    vergi_dairesi = db.Column(db.String(100))
    vergi_numarasi = db.Column(db.String(20))
    
    # Kurumsal Kimlik
    logo_url = db.Column(db.String(500))
    amac = db.Column(db.Text)
    vizyon = db.Column(db.Text)
    stratejik_profil = db.Column(db.Text)
    stratejik_durum = db.Column(db.String(50), default='eksik')
    stratejik_son_guncelleme = db.Column(db.DateTime)
    
    # Rehber Sistemi (Guide System)
    show_guide_system = db.Column(db.Boolean, default=True, nullable=False)  # Kurum için rehber sistemi aktif mi?
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Soft Delete
    silindi = db.Column(db.Boolean, default=False, nullable=False, index=True)
    deleted_at = db.Column(db.DateTime, nullable=True)
    deleted_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # İlişkiler
    # users = db.relationship('User', backref='kurum', lazy=True)  # User modelinde backref var
    deleter = db.relationship('User', foreign_keys=[deleted_by], backref='deleted_kurumlar')
    
    def __repr__(self):
        return f'<Kurum {self.kisa_ad}>'

class YetkiMatrisi(db.Model):
    """Rol bazlı yetki tanımlamaları"""
    __tablename__ = 'yetki_matrisi'
    
    id = db.Column(db.Integer, primary_key=True)
    rol = db.Column(db.String(50), nullable=False, index=True)
    yetki_kodu = db.Column(db.String(100), nullable=False)
    aktif = db.Column(db.Boolean, default=True)
    aciklama = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<YetkiMatrisi {self.rol}:{self.yetki_kodu}>'

class OzelYetki(db.Model):
    """Kullanıcıya özel yetkiler"""
    __tablename__ = 'ozel_yetki'
    
    id = db.Column(db.Integer, primary_key=True)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    yetki_kodu = db.Column(db.String(100), nullable=False)
    aktif = db.Column(db.Boolean, default=True)
    veren_kullanici_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    kullanici = db.relationship('User', foreign_keys=[kullanici_id], backref=db.backref('ozel_yetkiler', lazy=True))
    veren_kullanici = db.relationship('User', foreign_keys=[veren_kullanici_id])

class KullaniciYetki(db.Model):
    """Matris tabanlı yetki atamaları"""
    __tablename__ = 'kullanici_yetki'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    yetki_kodu = db.Column(db.String(100), nullable=False)
    aktif = db.Column(db.Boolean, default=True)
    atayan_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', foreign_keys=[user_id], backref='yetkiler')
    atayan = db.relationship('User', foreign_keys=[atayan_user_id])

class DashboardLayout(db.Model):
    """Kullanıcı bazlı dashboard düzeni"""
    __tablename__ = 'dashboard_layout'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    layout_name = db.Column(db.String(100), default='Varsayılan')
    is_default = db.Column(db.Boolean, default=False)
    layout_data = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('dashboard_layouts', lazy=True))

class Deger(db.Model):
    """Kurum Değerleri"""
    __tablename__ = 'deger'
    id = db.Column(db.Integer, primary_key=True)
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'), nullable=False)
    baslik = db.Column(db.String(200), nullable=False)
    aciklama = db.Column(db.Text)
    kurum = db.relationship('Kurum', backref=db.backref('degerler', lazy=True))

class EtikKural(db.Model):
    """Kurum Etik Kuralları"""
    __tablename__ = 'etik_kural'
    id = db.Column(db.Integer, primary_key=True)
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'), nullable=False)
    baslik = db.Column(db.String(200), nullable=False)
    aciklama = db.Column(db.Text)
    kurum = db.relationship('Kurum', backref=db.backref('etik_kurallari', lazy=True))

class KalitePolitikasi(db.Model):
    """Kurum Kalite Politikası"""
    __tablename__ = 'kalite_politikasi'
    id = db.Column(db.Integer, primary_key=True)
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'), nullable=False)
    baslik = db.Column(db.String(200), nullable=False)
    aciklama = db.Column(db.Text)
    kurum = db.relationship('Kurum', backref=db.backref('kalite_politikalari', lazy=True))

class Notification(db.Model):
    """Sistem Bildirimleri"""
    __tablename__ = 'notification'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    tip = db.Column(db.String(50), nullable=False)
    baslik = db.Column(db.String(200), nullable=False)
    mesaj = db.Column(db.Text)
    link = db.Column(db.String(500))
    okundu = db.Column(db.Boolean, default=False)
    email_sent = db.Column(db.Boolean, default=False)
    
    # İlişkiler (Circular import önlemek için string referans veya sonradan tanımlama gerekli olabilir)
    # Şimdilik basit ID'ler
    surec_id = db.Column(db.Integer, nullable=True)
    project_id = db.Column(db.Integer, nullable=True)
    task_id = db.Column(db.Integer, nullable=True)
    ilgili_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('bildirimler', lazy=True))

class UserActivityLog(db.Model):
    """Kullanıcı Aktivite Logları"""
    __tablename__ = 'user_activity_log'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    tip = db.Column(db.String(50), nullable=False)
    baslik = db.Column(db.String(200), nullable=False)
    aciklama = db.Column(db.Text)
    link = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Opsiyonel referanslar
    surec_id = db.Column(db.Integer, nullable=True)
    ilgili_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    bireysel_pg_id = db.Column(db.Integer, nullable=True)
    surec_pg_id = db.Column(db.Integer, nullable=True)
    
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('aktivite_loglari', lazy=True))

class Note(db.Model):
    """
    Karalama Defteri (Scratchpad) Modeli
    Kullanıcıların hızlı notlar alması için.
    """
    __tablename__ = 'note'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # İlişki
    user = db.relationship('User', backref=db.backref('notes', lazy='dynamic', order_by='Note.created_at.desc()'))

