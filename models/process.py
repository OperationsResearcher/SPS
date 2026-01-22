# -*- coding: utf-8 -*-
"""
Süreç Yönetimi Modelleri
------------------------
Süreç, Performans Göstergeleri (PG), Faaliyetler ve SWOT/PESTLE analiz modellerini içerir.
"""
from extensions import db
from datetime import datetime

# Association Tables (Many-to-Many İlişkiler için)
surec_uyeleri = db.Table('surec_uyeleri',
    db.Column('surec_id', db.Integer, db.ForeignKey('surec.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

surec_liderleri = db.Table('surec_liderleri',
    db.Column('surec_id', db.Integer, db.ForeignKey('surec.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

surec_alt_stratejiler = db.Table('surec_alt_stratejiler',
    db.Column('surec_id', db.Integer, db.ForeignKey('surec.id'), primary_key=True),
    db.Column('alt_strateji_id', db.Integer, db.ForeignKey('alt_strateji.id'), primary_key=True)
)

process_owners = db.Table('process_owners',
    db.Column('process_id', db.Integer, db.ForeignKey('surec.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)


class Surec(db.Model):
    """
    Süreç Modeli
    
    Kurumun iş süreçlerini tanımlar.
    V3.0 ile birlikte ağırlık, sahiplik ve kod alanları geliştirilmiştir.
    """
    __tablename__ = 'surec'
    
    id = db.Column(db.Integer, primary_key=True)
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'), nullable=False, index=True)
    
    # Tanımlama
    code = db.Column(db.String(20), nullable=True, index=True)  # Örn: SR1
    ad = db.Column(db.String(200), nullable=False, index=True)
    name = db.Column(db.String(200), nullable=True)  # İngilizce
    
    # Detaylar
    weight = db.Column(db.Float, default=0.0)  # Süreç Ağırlığı (0.0-1.0)
    dokuman_no = db.Column(db.String(50))
    rev_no = db.Column(db.String(20))
    rev_tarihi = db.Column(db.Date)
    ilk_yayin_tarihi = db.Column(db.Date)
    
    # Durum ve İlerleme
    durum = db.Column(db.String(50), default='Aktif')
    ilerleme = db.Column(db.Integer, default=0)
    
    # Kapsam
    baslangic_siniri = db.Column(db.Text)
    bitis_siniri = db.Column(db.Text)
    baslangic_tarihi = db.Column(db.Date)
    bitis_tarihi = db.Column(db.Date)
    aciklama = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Soft Delete
    silindi = db.Column(db.Boolean, default=False, nullable=False, index=True)
    deleted_at = db.Column(db.DateTime, nullable=True)
    deleted_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # İlişkiler
    kurum = db.relationship('Kurum', foreign_keys=[kurum_id], backref=db.backref('surecler', lazy=True))
    
    # Many-to-Many İlişkiler
    liderler = db.relationship('User', secondary=surec_liderleri, backref='liderlik_yaptigi_surecler')
    uyeler = db.relationship('User', secondary=surec_uyeleri, backref='uye_oldugu_surecler')
    owners = db.relationship('User', secondary=process_owners, backref='sahip_oldugu_surecler')
    alt_stratejiler = db.relationship('AltStrateji', secondary=surec_alt_stratejiler, backref='surecler')
    
    def __repr__(self):
        return f'<Surec {self.ad}>'


class SurecPerformansGostergesi(db.Model):
    """
    Süreç Performans Göstergesi (KPI) Modeli
    
    Süreçlerin performansını ölçmek için kullanılan metrikler.
    """
    __tablename__ = 'surec_performans_gostergesi'
    
    id = db.Column(db.Integer, primary_key=True)
    surec_id = db.Column(db.Integer, db.ForeignKey('surec.id'), nullable=False, index=True)
    
    # Temel Bilgiler
    ad = db.Column(db.String(200), nullable=False)
    aciklama = db.Column(db.Text)
    kodu = db.Column(db.String(50))  # Örn: PG-01
    
    # Hedefler
    hedef_deger = db.Column(db.String(100))
    olcum_birimi = db.Column(db.String(50))
    periyot = db.Column(db.String(50))  # Aylık, Çeyreklik, Yıllık
    
    # Yöntem
    veri_alinacak_yer = db.Column(db.String(200))
    hedef_belirleme_yontemi = db.Column(db.String(200))
    veri_toplama_yontemi = db.Column(db.String(50), default='Ortalama')
    calculation_method = db.Column(db.String(20), default='AVG')
    
    # Konfigürasyon
    agirlik = db.Column(db.Integer, default=0)
    onemli = db.Column(db.Boolean, default=False)
    direction = db.Column(db.String(20), default='Increasing')  # Increasing/Decreasing
    
    # Excel formatı için yeni alanlar
    gosterge_turu = db.Column(db.String(50), nullable=True)
    basari_puani = db.Column(db.Integer, nullable=True)
    agirlikli_basari_puani = db.Column(db.Float, nullable=True)
    basari_puani_araliklari = db.Column(db.Text, nullable=True)  # JSON
    onceki_yil_ortalamasi = db.Column(db.Float, nullable=True)
    target_method = db.Column(db.String(10), nullable=True)
    unit = db.Column(db.String(20), nullable=True)
    
    # İlişkiler
    alt_strateji_id = db.Column(db.Integer, db.ForeignKey('alt_strateji.id'), nullable=True, index=True)
    
    baslangic_tarihi = db.Column(db.Date)
    bitis_tarihi = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Backrefs
    surec = db.relationship('Surec', backref=db.backref('performans_gostergeleri', lazy=True, cascade='all, delete-orphan'))
    alt_strateji = db.relationship('AltStrateji', backref=db.backref('performans_gostergeleri', lazy=True))
    
    def __repr__(self):
        return f'<SurecPerformansGostergesi {self.ad}>'
    
class SurecFaaliyet(db.Model):
    """
    Süreç Faaliyet Modeli
    
    Süreç hedeflerine ulaşmak için yapılması gereken aksiyonlar.
    """
    __tablename__ = 'surec_faaliyet'
    
    id = db.Column(db.Integer, primary_key=True)
    surec_id = db.Column(db.Integer, db.ForeignKey('surec.id'), nullable=False, index=True)
    
    ad = db.Column(db.String(200), nullable=False)
    aciklama = db.Column(db.Text)
    
    baslangic_tarihi = db.Column(db.Date)
    bitis_tarihi = db.Column(db.Date)
    
    durum = db.Column(db.String(50), default='Planlandı')
    ilerleme = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    surec = db.relationship('Surec', backref=db.backref('faaliyetler', lazy=True, cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<SurecFaaliyet {self.ad}>'

class BireyselPerformansGostergesi(db.Model):
    """
    Bireysel Performans Göstergesi Modeli
    
    Kullanıcıların bireysel hedeflerini veya süreçlerden onlara atanan hedefleri tutar.
    Süreç karnesinde kullanıcı bazlı takip için kritik öneme sahiptir.
    """
    __tablename__ = 'bireysel_performans_gostergesi'
    
    __table_args__ = (
        db.Index('idx_bireysel_pg_user', 'user_id', 'kaynak'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    
    # Tanım
    ad = db.Column(db.String(200), nullable=False, index=True)
    aciklama = db.Column(db.Text)
    kodu = db.Column(db.String(50))
    
    # Değerler
    hedef_deger = db.Column(db.String(100))
    gerceklesen_deger = db.Column(db.String(100))
    olcum_birimi = db.Column(db.String(50))
    
    # Konfigürasyon
    periyot = db.Column(db.String(50))
    agirlik = db.Column(db.Integer, default=0)
    onemli = db.Column(db.Boolean, default=False)
    
    # Durum ve Tarih
    baslangic_tarihi = db.Column(db.Date)
    bitis_tarihi = db.Column(db.Date)
    durum = db.Column(db.String(50), default='Devam Ediyor')
    
    # Kaynak (Süreçten mi geldi yoksa bireysel mi?)
    kaynak = db.Column(db.String(50), default='Bireysel')  # 'Bireysel' veya 'Süreç'
    kaynak_surec_id = db.Column(db.Integer, db.ForeignKey('surec.id'), nullable=True, index=True)
    kaynak_surec_pg_id = db.Column(db.Integer, db.ForeignKey('surec_performans_gostergesi.id'), nullable=True, index=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    user = db.relationship('User', backref=db.backref('bireysel_performans_gostergeleri', lazy=True))
    kaynak_surec = db.relationship('Surec', foreign_keys=[kaynak_surec_id], backref='atanan_performans_gostergeleri')
    kaynak_pg = db.relationship('SurecPerformansGostergesi', foreign_keys=[kaynak_surec_pg_id])
    
    def __repr__(self):
        return f'<BireyselPerformansGostergesi {self.ad}>'

class BireyselFaaliyet(db.Model):
    """
    Bireysel Faaliyet Modeli
    
    Kullanıcının kendine atadığı veya süreçten gelen aksiyonlar.
    """
    __tablename__ = 'bireysel_faaliyet'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    
    ad = db.Column(db.String(200), nullable=False)
    aciklama = db.Column(db.Text)
    
    baslangic_tarihi = db.Column(db.Date)
    bitis_tarihi = db.Column(db.Date)
    
    durum = db.Column(db.String(50), default='Planlandı')
    ilerleme = db.Column(db.Integer, default=0)
    
    # Kaynak
    kaynak = db.Column(db.String(50), default='Bireysel')  # 'Bireysel' veya 'Süreç'
    kaynak_surec_id = db.Column(db.Integer, db.ForeignKey('surec.id'), nullable=True, index=True)
    kaynak_surec_faaliyet_id = db.Column(db.Integer, db.ForeignKey('surec_faaliyet.id'), nullable=True, index=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    user = db.relationship('User', backref=db.backref('bireysel_faaliyetler', lazy=True))
    kaynak_surec = db.relationship('Surec', foreign_keys=[kaynak_surec_id], backref='atanan_faaliyetler')
    kaynak_faaliyet = db.relationship('SurecFaaliyet', foreign_keys=[kaynak_surec_faaliyet_id])
    
    def __repr__(self):
        return f'<BireyselFaaliyet {self.ad}>'

class PerformansGostergeVeri(db.Model):
    """
    Performans Gösterge Veri Modeli
    
    PG'lerin gerçekleşen değerlerini tutar. Periyodik veri girişi için kullanılır.
    """
    __tablename__ = 'performans_gosterge_veri'
    
    __table_args__ = (
        db.Index('idx_pg_veri_lookup', 'bireysel_pg_id', 'yil', 'veri_tarihi'),
        db.Index('idx_pg_veri_user', 'user_id', 'yil'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    bireysel_pg_id = db.Column(db.Integer, db.ForeignKey('bireysel_performans_gostergesi.id'), nullable=False, index=True)
    
    # Zaman Bilgisi
    yil = db.Column(db.Integer, nullable=False, index=True)
    veri_tarihi = db.Column(db.Date, nullable=False, index=True)
    
    # Giriş Detayları
    giris_periyot_tipi = db.Column(db.String(20))  # yillik, ceyrek, aylik
    giris_periyot_no = db.Column(db.Integer)
    giris_periyot_ay = db.Column(db.Integer)
    
    # Legacy Alanlar (Geriye uyumluluk)
    ceyrek = db.Column(db.Integer)
    ay = db.Column(db.Integer)
    hafta = db.Column(db.Integer)
    gun = db.Column(db.Integer)
    
    # Değerler
    hedef_deger = db.Column(db.String(100))
    gerceklesen_deger = db.Column(db.String(100), nullable=False)
    durum = db.Column(db.String(50))
    durum_yuzdesi = db.Column(db.Float)
    aciklama = db.Column(db.Text)
    
    # İzlenebilirlik
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Veriyi giren
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    bireysel_pg = db.relationship('BireyselPerformansGostergesi', backref=db.backref('veriler', lazy=True))
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('pg_verileri', lazy=True))
    olusturan = db.relationship('User', foreign_keys=[created_by])
    guncelleyen = db.relationship('User', foreign_keys=[updated_by])

class PerformansGostergeVeriAudit(db.Model):
    """PG Veri Değişiklik Geçmişi (Audit Log)"""
    __tablename__ = 'performans_gosterge_veri_audit'
    
    id = db.Column(db.Integer, primary_key=True)
    pg_veri_id = db.Column(db.Integer, db.ForeignKey('performans_gosterge_veri.id'), nullable=False, index=True)
    
    islem_tipi = db.Column(db.String(20), nullable=False) # OLUSTUR, GUNCELLE, SIL
    eski_deger = db.Column(db.Text)
    yeni_deger = db.Column(db.Text)
    degisiklik_aciklama = db.Column(db.Text)
    
    islem_yapan_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    islem_tarihi = db.Column(db.DateTime, default=datetime.utcnow)
    
    pg_veri = db.relationship('PerformansGostergeVeri', backref=db.backref('audit_log', lazy=True, passive_deletes=True))
    islem_yapan = db.relationship('User', backref=db.backref('pg_veri_audit_islemleri', lazy=True))

class FaaliyetTakip(db.Model):
    """Faaliyet Takip Modeli"""
    __tablename__ = 'faaliyet_takip'
    
    id = db.Column(db.Integer, primary_key=True)
    bireysel_faaliyet_id = db.Column(db.Integer, db.ForeignKey('bireysel_faaliyet.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    yil = db.Column(db.Integer, nullable=False)
    ay = db.Column(db.Integer, nullable=False)
    gerceklesti = db.Column(db.Boolean, default=False)
    not_text = db.Column(db.Text)
    tamamlanma_tarihi = db.Column(db.Date)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    bireysel_faaliyet = db.relationship('BireyselFaaliyet', backref=db.backref('takip', lazy=True))
    user = db.relationship('User', backref=db.backref('faaliyet_takipleri', lazy=True))

class FavoriKPI(db.Model):
    """Favori KPI Modeli"""
    __tablename__ = 'favori_kpi'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    surec_pg_id = db.Column(db.Integer, db.ForeignKey('surec_performans_gostergesi.id'), nullable=False)
    sira = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('favori_kpiler', lazy=True))
    surec_pg = db.relationship('SurecPerformansGostergesi', backref=db.backref('favori_olanlar', lazy=True))

# Aliases for English compatibility
Process = Surec
PerformanceIndicator = SurecPerformansGostergesi
