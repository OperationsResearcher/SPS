# -*- coding: utf-8 -*-
"""
Database Models
Tüm veritabanı modelleri bu dosyada toplanmıştır.
"""
from extensions import db
from flask_login import UserMixin
from datetime import datetime

# Association Tables
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

# Proje Yönetimi Association Tables
project_members = db.Table('project_members',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

project_observers = db.Table('project_observers',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

project_related_processes = db.Table('project_related_processes',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True),
    db.Column('surec_id', db.Integer, db.ForeignKey('surec.id'), primary_key=True)
)

task_predecessors = db.Table('task_predecessors',
    db.Column('task_id', db.Integer, db.ForeignKey('task.id'), primary_key=True),
    db.Column('predecessor_id', db.Integer, db.ForeignKey('task.id'), primary_key=True)
)

# Stratejik Planlama V3.0 Association Tables
process_owners = db.Table('process_owners',
    db.Column('process_id', db.Integer, db.ForeignKey('surec.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class StrategyProcessMatrix(db.Model):
    """Strateji-Süreç Matrisi Modeli - İlişki skorlarını yönetmek için"""
    __tablename__ = 'strategy_process_matrix'
    
    id = db.Column(db.Integer, primary_key=True)
    sub_strategy_id = db.Column(db.Integer, db.ForeignKey('alt_strateji.id'), nullable=False, index=True)
    process_id = db.Column(db.Integer, db.ForeignKey('surec.id'), nullable=False, index=True)
    relationship_strength = db.Column(db.Integer, default=0)  # 0-9 arası ilişki gücü (9=Güçlü, 3=Zayıf)
    relationship_score = db.Column(db.Integer, default=0)  # V3.0: Excel'deki A/B ilişkileri için (A=9, B=3)
    
    # İlişkiler
    sub_strategy = db.relationship('AltStrateji', backref=db.backref('matrix_relations', lazy=True))
    process = db.relationship('Surec', backref=db.backref('strategy_matrix_relations', lazy=True))
    
    # Unique constraint: Aynı alt strateji ve süreç çifti sadece bir kez olabilir
    __table_args__ = (db.UniqueConstraint('sub_strategy_id', 'process_id', name='uq_strategy_process_matrix'),)
    
    def __repr__(self):
        return f'<StrategyProcessMatrix Sub:{self.sub_strategy_id} Proc:{self.process_id} Score:{self.relationship_score}>'


# Models
class User(UserMixin, db.Model):
    """Kullanıcı modeli - SQL Server uyumluluğu için __tablename__ belirtildi"""
    __tablename__ = 'user'  # SQL Server'da reserved keyword olabilir, açıkça belirtildi
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(120), nullable=False)
    first_name = db.Column(db.String(50))  # Ad
    last_name = db.Column(db.String(50))  # Soyad
    phone = db.Column(db.String(20))  # Telefon
    title = db.Column(db.String(100))  # Unvan
    department = db.Column(db.String(100))  # Departman
    sistem_rol = db.Column(db.String(50), nullable=False, default='kurum_kullanici', index=True)  # admin, kurum_yoneticisi, ust_yonetim, kurum_kullanici
    surec_rol = db.Column(db.String(50), default=None)  # surec_lideri, surec_uyesi, None
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'), nullable=False, index=True)
    profile_photo = db.Column(db.String(500))  # Profil fotoğrafı URL'si veya dosya yolu
    theme_preferences = db.Column(db.Text)  # JSON: {"theme": "...", "color": "..."}
    layout_preference = db.Column(db.String(20), default='classic')  # 'classic' veya 'sidebar'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Soft delete kolonları
    silindi = db.Column(db.Boolean, default=False, nullable=False, index=True)
    deleted_at = db.Column(db.DateTime, nullable=True)
    deleted_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    kurum = db.relationship('Kurum', foreign_keys=[kurum_id], backref=db.backref('users', lazy=True))
    deleter = db.relationship('User', remote_side=[id], foreign_keys=[deleted_by])
    
    def __repr__(self):
        return f'<User {self.username}>'


class DashboardLayout(db.Model):
    """Kullanıcı bazlı özelleştirilebilir dashboard layout'ları"""
    __tablename__ = 'dashboard_layout'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    layout_name = db.Column(db.String(100), nullable=False, default='Varsayılan Görünüm')
    is_default = db.Column(db.Boolean, default=False)  # Varsayılan görünüm mü?
    layout_data = db.Column(db.Text)  # JSON formatında kart pozisyonları ve ayarları
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('dashboard_layouts', lazy=True))
    
    def __repr__(self):
        return f'<DashboardLayout User:{self.user_id} - {self.layout_name}>'


class Kurum(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kisa_ad = db.Column(db.String(100), nullable=False, index=True)
    ticari_unvan = db.Column(db.String(200), nullable=False)
    faaliyet_alani = db.Column(db.String(200))
    adres = db.Column(db.Text)
    il = db.Column(db.String(100))
    ilce = db.Column(db.String(100))
    calisan_sayisi = db.Column(db.Integer)
    sektor = db.Column(db.String(100))
    vergi_dairesi = db.Column(db.String(100))
    vergi_numarasi = db.Column(db.String(20))
    email = db.Column(db.String(120))
    web_adresi = db.Column(db.String(200))
    telefon = db.Column(db.String(20))
    logo_url = db.Column(db.String(500))  # Logo URL'si veya dosya yolu
    amac = db.Column(db.Text)
    vizyon = db.Column(db.Text)
    stratejik_profil = db.Column(db.Text)
    stratejik_durum = db.Column(db.String(50), default='eksik')
    stratejik_son_guncelleme = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Soft delete kolonları
    silindi = db.Column(db.Boolean, default=False, nullable=False, index=True)
    deleted_at = db.Column(db.DateTime, nullable=True)
    deleted_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    deleter = db.relationship('User', foreign_keys=[deleted_by], backref='deleted_kurumlar')
    
    def __repr__(self):
        return f'<Kurum {self.kisa_ad}>'


class Deger(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'), nullable=False, index=True)
    baslik = db.Column(db.String(200), nullable=False)
    aciklama = db.Column(db.Text)
    
    kurum = db.relationship('Kurum', backref=db.backref('degerler', lazy=True, cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<Deger {self.baslik}>'


class EtikKural(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'), nullable=False, index=True)
    baslik = db.Column(db.String(200), nullable=False)
    aciklama = db.Column(db.Text)
    
    kurum = db.relationship('Kurum', backref=db.backref('etik_kurallari', lazy=True, cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<EtikKural {self.baslik}>'


class KalitePolitikasi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'), nullable=False, index=True)
    baslik = db.Column(db.String(200), nullable=False)
    aciklama = db.Column(db.Text)
    
    kurum = db.relationship('Kurum', backref=db.backref('kalite_politikalari', lazy=True, cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<KalitePolitikasi {self.baslik}>'


# ============================================================================
# STRATEJİK PLANLAMA V3.0 MODELLERİ
# ============================================================================

class CorporateIdentity(db.Model):
    """Kurumsal Kimlik - Singleton (Kurum başına tek kayıt) - Excel: Misyon, Vizyon, Değerler"""
    __tablename__ = 'corporate_identity'
    
    id = db.Column(db.Integer, primary_key=True)
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'), nullable=False, unique=True, index=True)
    vizyon = db.Column(db.Text)  # Excel: Vizyon
    misyon = db.Column(db.Text)  # Excel: Misyon
    kalite_politikasi = db.Column(db.Text)  # Excel: Kalite Politikası
    degerler = db.Column(db.Text)  # JSON formatında: ["Şeffaflık", "Verimlilik", ...]
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    kurum = db.relationship('Kurum', backref=db.backref('corporate_identity', uselist=False, cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<CorporateIdentity Kurum:{self.kurum_id}>'


class Surec(db.Model):
    """Süreç Modeli - V3.0 ile code, name, weight ve process_owners eklendi"""
    __tablename__ = 'surec'
    
    id = db.Column(db.Integer, primary_key=True)
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'), nullable=False, index=True)
    code = db.Column(db.String(20), nullable=True, index=True)  # V3.0: Örn: SR1
    ad = db.Column(db.String(200), nullable=False, index=True)
    name = db.Column(db.String(200), nullable=True)  # V3.0: İngilizce tanım (opsiyonel)
    weight = db.Column(db.Float, default=0.0)  # V3.0: Süreç Ağırlığı (0.0-1.0 arası)
    dokuman_no = db.Column(db.String(50))
    rev_no = db.Column(db.String(20))
    rev_tarihi = db.Column(db.Date)  # YENİ
    ilk_yayin_tarihi = db.Column(db.Date)  # YENİ
    lider_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Geriye uyumluluk için - artık kullanılmayacak
    durum = db.Column(db.String(50), default='Aktif')
    ilerleme = db.Column(db.Integer, default=0)
    baslangic_siniri = db.Column(db.Text)  # YENİ: Süreç başlangıç sınırı açıklaması
    bitis_siniri = db.Column(db.Text)  # YENİ: Süreç bitiş sınırı açıklaması
    baslangic_tarihi = db.Column(db.Date)  # Süreç başlangıç tarihi (proje timeline için)
    bitis_tarihi = db.Column(db.Date)  # Süreç bitiş tarihi (proje timeline için)
    aciklama = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Soft delete kolonları
    silindi = db.Column(db.Boolean, default=False, nullable=False, index=True)
    deleted_at = db.Column(db.DateTime, nullable=True)
    deleted_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    kurum = db.relationship('Kurum', foreign_keys=[kurum_id], backref=db.backref('surecler', lazy=True))
    deleter = db.relationship('User', foreign_keys=[deleted_by], backref='deleted_surecler')
    lider = db.relationship('User', foreign_keys=[lider_id], backref='eski_liderlik_yaptigi_surecler')  # Deprecated
    liderler = db.relationship('User', secondary=surec_liderleri, backref='liderlik_yaptigi_surecler')  # YENİ: Birden fazla lider
    uyeler = db.relationship('User', secondary=surec_uyeleri, backref='uye_oldugu_surecler')
    alt_stratejiler = db.relationship('AltStrateji', secondary=surec_alt_stratejiler, backref='surecler')  # YENİ: Birden fazla alt strateji
    owners = db.relationship('User', secondary=process_owners, backref='sahip_oldugu_surecler')  # V3.0: Çoklu sahiplik
    
    def to_dict(self):
        """Süreç nesnesini dictionary'ye çevir"""
        return {
            'id': self.id,
            'ad': self.ad,
            'dokuman_no': self.dokuman_no,
            'rev_no': self.rev_no,
            'rev_tarihi': self.rev_tarihi.strftime('%Y-%m-%d') if self.rev_tarihi else None,
            'ilk_yayin_tarihi': self.ilk_yayin_tarihi.strftime('%Y-%m-%d') if self.ilk_yayin_tarihi else None,
            'durum': self.durum,
            'ilerleme': self.ilerleme,
            'baslangic_siniri': self.baslangic_siniri,
            'bitis_siniri': self.bitis_siniri,
            'baslangic_tarihi': self.baslangic_tarihi.strftime('%Y-%m-%d') if self.baslangic_tarihi else None,
            'bitis_tarihi': self.bitis_tarihi.strftime('%Y-%m-%d') if self.bitis_tarihi else None,
            'aciklama': self.aciklama,
            'kurum': self.kurum.ad if self.kurum else None,
            'kurum_id': self.kurum_id,
            'liderler': [{'id': u.id, 'ad': u.ad, 'soyad': u.soyad} for u in self.liderler],
            'uyeler': [{'id': u.id, 'ad': u.ad, 'soyad': u.soyad} for u in self.uyeler],
            'alt_stratejiler': [{'id': s.id, 'ad': s.ad} for s in self.alt_stratejiler]
        }
    
    def __repr__(self):
        return f'<Surec {self.ad}>'


# Alias for Surec (English name)
Process = Surec


class AnaStrateji(db.Model):
    """Ana Strateji Modeli - V3.0 ile code alanı eklendi"""
    id = db.Column(db.Integer, primary_key=True)
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'), nullable=False, index=True)
    code = db.Column(db.String(20), nullable=True, unique=True, index=True)  # V3.0: Örn: ST1 (UNIQUE eklendi)
    ad = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(200), nullable=True)  # V3.0: İngilizce tanım (opsiyonel)
    aciklama = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    kurum = db.relationship('Kurum', backref=db.backref('ana_stratejiler', lazy=True, cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<AnaStrateji {self.code or ""} - {self.ad}>'


# Alias for AnaStrateji (English name)
MainStrategy = AnaStrateji


class AltStrateji(db.Model):
    """Alt Strateji Modeli - V3.0 ile code, target_method alanı ve Süreç ilişkisi eklendi"""
    id = db.Column(db.Integer, primary_key=True)
    ana_strateji_id = db.Column(db.Integer, db.ForeignKey('ana_strateji.id'), nullable=False, index=True)
    code = db.Column(db.String(20), nullable=True, index=True)  # V3.0: Örn: ST1.1
    ad = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(200), nullable=True)  # V3.0: İngilizce tanım (opsiyonel)
    target_method = db.Column(db.String(10), nullable=True)  # V3.0: HKY, RG, SH, DH, HK, SGH
    aciklama = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    ana_strateji = db.relationship('AnaStrateji', backref=db.backref('alt_stratejiler', lazy=True, cascade='all, delete-orphan'))
    # V3.0: StrategyProcessMatrix üzerinden süreçlerle ilişki (relationship_strength ile)
    # Not: Artık StrategyProcessMatrix tam bir model olduğu için secondary kullanmıyoruz
    # İlişki StrategyProcessMatrix modeli üzerinden yönetiliyor
    
    def __repr__(self):
        return f'<AltStrateji {self.code or ""} - {self.ad}>'


# Alias for AltStrateji (English name)
SubStrategy = AltStrateji


class SurecPerformansGostergesi(db.Model):
    """Süreç bazlı performans göstergeleri - V3.0 ile calculation_method, target_method, unit, direction eklendi"""
    __tablename__ = 'surec_performans_gostergesi'
    
    id = db.Column(db.Integer, primary_key=True)
    surec_id = db.Column(db.Integer, db.ForeignKey('surec.id'), nullable=False, index=True)
    ad = db.Column(db.String(200), nullable=False)
    aciklama = db.Column(db.Text)
    hedef_deger = db.Column(db.String(100))
    olcum_birimi = db.Column(db.String(50))
    periyot = db.Column(db.String(50))  # Aylık, Çeyreklik, Yıllık
    veri_alinacak_yer = db.Column(db.String(200))  # YENİ: Veri nereden alınacak
    hedef_belirleme_yontemi = db.Column(db.String(200))  # YENİ: Hedef nasıl belirlendi
    veri_toplama_yontemi = db.Column(db.String(50), default='Ortalama')  # YENİ: 'Toplam' veya 'Ortalama'
    # Süreç Karnesi için yeni kolonlar
    agirlik = db.Column(db.Integer, default=0)  # 0-100 arası ağırlık yüzdesi
    onemli = db.Column(db.Boolean, default=False)  # True ise Excel'de sarı vurgu
    kodu = db.Column(db.String(50))  # PG Kodu (örn: "PG-01", "PG-02")
    baslangic_tarihi = db.Column(db.Date)
    bitis_tarihi = db.Column(db.Date)
    # V3.0: Yeni alanlar
    calculation_method = db.Column(db.String(20), default='AVG')  # SUM, AVG, LAST_VALUE
    target_method = db.Column(db.String(10), nullable=True)  # HKY, RG, SH, DH, HK, SGH
    unit = db.Column(db.String(20), nullable=True)  # %, Adet, TL, vb.
    direction = db.Column(db.String(20), default='Increasing')  # Increasing (Arttırmak iyi), Decreasing (Azaltmak iyi)
    # Excel formatı için yeni alanlar (Süreç Karnesi Excel formatına uyum)
    alt_strateji_id = db.Column(db.Integer, db.ForeignKey('alt_strateji.id'), nullable=True, index=True)  # Excel: Alt Strateji bağlantısı
    gosterge_turu = db.Column(db.String(50), nullable=True)  # Excel: Göst. Türü (iyileştirme, istatistik)
    basari_puani = db.Column(db.Integer, nullable=True)  # Excel: Başarı Puanı (1-5 arası)
    agirlikli_basari_puani = db.Column(db.Float, nullable=True)  # Excel: Ağırlıklı Başarı Puanı (Ağırlık × Başarı Puanı)
    basari_puani_araliklari = db.Column(db.Text, nullable=True)  # Excel: Başarı Puanı Aralıkları (JSON formatında: {1: "...", 2: "...", 3: "...", 4: "...", 5: "..."})
    onceki_yil_ortalamasi = db.Column(db.Float, nullable=True)  # Excel: Önceki Yıl Ortalaması
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    surec = db.relationship('Surec', backref=db.backref('performans_gostergeleri', lazy=True, cascade='all, delete-orphan'))
    alt_strateji = db.relationship('AltStrateji', backref=db.backref('performans_gostergeleri', lazy=True))
    
    def __repr__(self):
        return f'<SurecPerformansGostergesi {self.ad}>'


# Alias for SurecPerformansGostergesi (English name)
PerformanceIndicator = SurecPerformansGostergesi


class SurecFaaliyet(db.Model):
    """Süreç bazlı faaliyetler - otomatik olarak süreç liderleri ve üyelerine atanır"""
    __tablename__ = 'surec_faaliyet'
    
    id = db.Column(db.Integer, primary_key=True)
    surec_id = db.Column(db.Integer, db.ForeignKey('surec.id'), nullable=False, index=True)
    ad = db.Column(db.String(200), nullable=False)
    aciklama = db.Column(db.Text)
    baslangic_tarihi = db.Column(db.Date)
    bitis_tarihi = db.Column(db.Date)
    durum = db.Column(db.String(50), default='Planlandı')  # Planlandı, Devam Ediyor, Tamamlandı, İptal
    ilerleme = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    surec = db.relationship('Surec', backref=db.backref('faaliyetler', lazy=True, cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<SurecFaaliyet {self.ad}>'


class SwotAnalizi(db.Model):
    """SWOT Analizi - Kurum bazlı"""
    __tablename__ = 'swot_analizi'
    
    id = db.Column(db.Integer, primary_key=True)
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'), nullable=False, index=True)
    kategori = db.Column(db.String(20), nullable=False)  # strengths, weaknesses, opportunities, threats
    baslik = db.Column(db.String(200), nullable=False)
    aciklama = db.Column(db.Text)
    oncelik = db.Column(db.Integer, default=1)  # 1-5 arası öncelik
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    kurum = db.relationship('Kurum', backref=db.backref('swot_analizleri', lazy=True, cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<SwotAnalizi {self.baslik}>'


class PestleAnalizi(db.Model):
    """PESTLE Analizi - Kurum bazlı"""
    __tablename__ = 'pestle_analizi'
    
    id = db.Column(db.Integer, primary_key=True)
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'), nullable=False, index=True)
    kategori = db.Column(db.String(20), nullable=False)  # political, economic, social, technological, legal, environmental
    baslik = db.Column(db.String(200), nullable=False)
    aciklama = db.Column(db.Text)
    etki = db.Column(db.String(20), default='Orta')  # Düşük, Orta, Yüksek
    oncelik = db.Column(db.Integer, default=1)  # 1-5 arası öncelik
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    kurum = db.relationship('Kurum', backref=db.backref('pestle_analizleri', lazy=True, cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<PestleAnalizi {self.baslik}>'


class BireyselPerformansGostergesi(db.Model):
    """Kullanıcının bireysel performans göstergeleri (hem süreçten gelen hem kendi eklediği)"""
    __tablename__ = 'bireysel_performans_gostergesi'
    
    __table_args__ = (
        db.Index('idx_bireysel_pg_user', 'user_id', 'kaynak'),  # User performance query optimization
    )
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    ad = db.Column(db.String(200), nullable=False, index=True)
    aciklama = db.Column(db.Text)
    hedef_deger = db.Column(db.String(100))
    gerceklesen_deger = db.Column(db.String(100))  # Kullanıcı günceller
    olcum_birimi = db.Column(db.String(50))
    periyot = db.Column(db.String(50))
    baslangic_tarihi = db.Column(db.Date)
    bitis_tarihi = db.Column(db.Date)
    durum = db.Column(db.String(50), default='Devam Ediyor')  # Devam Ediyor, Tamamlandı, İptal
    kaynak = db.Column(db.String(50), default='Bireysel')  # 'Bireysel' veya 'Süreç'
    kaynak_surec_id = db.Column(db.Integer, db.ForeignKey('surec.id'), nullable=True, index=True)
    kaynak_surec_pg_id = db.Column(db.Integer, db.ForeignKey('surec_performans_gostergesi.id'), nullable=True, index=True)
    # YENİ: Süreç Karnesi için eklenen kolonlar
    agirlik = db.Column(db.Integer, default=0)  # 0-100 arası ağırlık yüzdesi
    onemli = db.Column(db.Boolean, default=False)  # True ise Excel'de sarı vurgu
    kodu = db.Column(db.String(50))  # PG Kodu (örn: "PG-01", "PG-02")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('bireysel_performans_gostergeleri', lazy=True))
    kaynak_surec = db.relationship('Surec', foreign_keys=[kaynak_surec_id], backref='atanan_performans_gostergeleri')
    kaynak_pg = db.relationship('SurecPerformansGostergesi', foreign_keys=[kaynak_surec_pg_id])
    
    def __repr__(self):
        return f'<BireyselPerformansGostergesi {self.ad}>'


class BireyselFaaliyet(db.Model):
    """Kullanıcının bireysel faaliyetleri (hem süreçten gelen hem kendi eklediği)"""
    __tablename__ = 'bireysel_faaliyet'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    ad = db.Column(db.String(200), nullable=False)
    aciklama = db.Column(db.Text)
    baslangic_tarihi = db.Column(db.Date)
    bitis_tarihi = db.Column(db.Date)
    durum = db.Column(db.String(50), default='Planlandı')  # Planlandı, Devam Ediyor, Tamamlandı, İptal
    ilerleme = db.Column(db.Integer, default=0)
    kaynak = db.Column(db.String(50), default='Bireysel')  # 'Bireysel' veya 'Süreç'
    kaynak_surec_id = db.Column(db.Integer, db.ForeignKey('surec.id'), nullable=True, index=True)
    kaynak_surec_faaliyet_id = db.Column(db.Integer, db.ForeignKey('surec_faaliyet.id'), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('bireysel_faaliyetler', lazy=True))
    kaynak_surec = db.relationship('Surec', foreign_keys=[kaynak_surec_id], backref='atanan_faaliyetler')
    kaynak_faaliyet = db.relationship('SurecFaaliyet', foreign_keys=[kaynak_surec_faaliyet_id])
    
    def __repr__(self):
        return f'<BireyselFaaliyet {self.ad}>'


class OzelYetki(db.Model):
    """Özel yetki tablosu - Kullanıcılara özel yetkiler vermek için"""
    __tablename__ = 'ozel_yetki'
    
    id = db.Column(db.Integer, primary_key=True)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    yetki_kodu = db.Column(db.String(100), nullable=False)  # kurum_ozluk, surec_performans, vb.
    aktif = db.Column(db.Boolean, default=True)
    veren_kullanici_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    kullanici = db.relationship('User', foreign_keys=[kullanici_id], backref=db.backref('ozel_yetkiler', lazy=True))
    veren_kullanici = db.relationship('User', foreign_keys=[veren_kullanici_id], backref=db.backref('verilen_yetkiler', lazy=True))
    
    __table_args__ = (db.UniqueConstraint('kullanici_id', 'yetki_kodu', name='unique_kullanici_yetki'),)
    
    def __repr__(self):
        return f'<OzelYetki User:{self.kullanici_id} - {self.yetki_kodu}>'


class Notification(db.Model):
    """Bildirim sistemi - Kullanıcılara gönderilen bildirimler"""
    __tablename__ = 'notification'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    tip = db.Column(db.String(50), nullable=False, index=True)  # pg_veri_girisi, faaliyet_guncelleme, surec_degisiklik, proje_gorev_mention, task_assigned, task_deadline, vb.
    baslik = db.Column(db.String(200), nullable=False)
    mesaj = db.Column(db.Text)
    link = db.Column(db.String(500))  # Bildirime tıklandığında gidilecek URL
    okundu = db.Column(db.Boolean, default=False, index=True)
    surec_id = db.Column(db.Integer, db.ForeignKey('surec.id'), nullable=True, index=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True, index=True)  # Proje bildirimleri için
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=True, index=True)  # Görev bildirimleri için
    ilgili_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # İşlemi yapan kullanıcı
    email_sent = db.Column(db.Boolean, default=False)  # E-posta gönderildi mi?
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('bildirimler', lazy=True, order_by='desc(Notification.created_at)'))
    surec = db.relationship('Surec', backref=db.backref('bildirimler', lazy=True))
    project = db.relationship('Project', backref=db.backref('notifications', lazy=True))
    task = db.relationship('Task', backref=db.backref('notifications', lazy=True))
    ilgili_user = db.relationship('User', foreign_keys=[ilgili_user_id])
    
    def __repr__(self):
        return f'<Notification {self.id} - {self.baslik} - {self.user.username}>'


class UserActivityLog(db.Model):
    """Kullanıcı aktivite logları - Dashboard'da Son Aktiviteler için"""
    __tablename__ = 'user_activity_log'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    tip = db.Column(db.String(50), nullable=False, index=True)  # login, pg_veri_girisi, pg_veri_guncelleme, pg_veri_silme, faaliyet_girisi, faaliyet_guncelleme, pg_ekleme, pg_guncelleme, pg_silme, faaliyet_ekleme, faaliyet_guncelleme, faaliyet_silme
    baslik = db.Column(db.String(200), nullable=False)
    aciklama = db.Column(db.Text)
    link = db.Column(db.String(500))  # Aktiviteye tıklandığında gidilecek URL
    surec_id = db.Column(db.Integer, db.ForeignKey('surec.id'), nullable=True, index=True)
    ilgili_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # İşlem yapılan kullanıcı (ör: başkasının verisi güncellendi)
    bireysel_pg_id = db.Column(db.Integer, db.ForeignKey('bireysel_performans_gostergesi.id'), nullable=True, index=True)
    surec_pg_id = db.Column(db.Integer, db.ForeignKey('surec_performans_gostergesi.id'), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('aktivite_loglari', lazy=True, order_by='desc(UserActivityLog.created_at)'))
    surec = db.relationship('Surec', backref=db.backref('aktivite_loglari', lazy=True))
    ilgili_user = db.relationship('User', foreign_keys=[ilgili_user_id])
    bireysel_pg = db.relationship('BireyselPerformansGostergesi', foreign_keys=[bireysel_pg_id])
    surec_pg = db.relationship('SurecPerformansGostergesi', foreign_keys=[surec_pg_id])
    
    def __repr__(self):
        return f'<UserActivityLog {self.id} - {self.tip} - {self.user.username}>'


class PerformansGostergeVeri(db.Model):
    """Performans gösterge verileri - Temiz veri sistemi"""
    __tablename__ = 'performans_gosterge_veri'
    
    __table_args__ = (
        db.Index('idx_pg_veri_lookup', 'bireysel_pg_id', 'yil', 'veri_tarihi'),  # Composite index for fast lookups
        db.Index('idx_pg_veri_user', 'user_id', 'yil'),  # User query optimization
    )
    
    id = db.Column(db.Integer, primary_key=True)
    bireysel_pg_id = db.Column(db.Integer, db.ForeignKey('bireysel_performans_gostergesi.id'), nullable=False, index=True)
    yil = db.Column(db.Integer, nullable=False, index=True)
    
    # VERİ TARİHİ - Periyodun son Cuması (Akıllı gösterim için kullanılır)
    veri_tarihi = db.Column(db.Date, nullable=False, index=True)
    
    # GİRİŞ BİLGİLERİ - Bilgi amaçlı (hangi periyotla girildiği)
    giris_periyot_tipi = db.Column(db.String(20))  # 'yillik', 'ceyrek', 'aylik', 'haftalik', 'gunluk'
    giris_periyot_no = db.Column(db.Integer)  # Çeyrek: 1-4, Ay: 1-12, Hafta: 1-5, Gün: 1-31
    giris_periyot_ay = db.Column(db.Integer)  # Haftalık ve günlük için ay bilgisi
    
    # ESKI ALANLAR - Geriye dönük uyumluluk için
    ceyrek = db.Column(db.Integer)
    ay = db.Column(db.Integer)
    hafta = db.Column(db.Integer)  # Ekledik
    gun = db.Column(db.Integer)    # Ekledik
    hedef_deger = db.Column(db.String(100))
    durum = db.Column(db.String(50))
    durum_yuzdesi = db.Column(db.Float)
    
    # VERİ
    gerceklesen_deger = db.Column(db.String(100), nullable=False)
    aciklama = db.Column(db.Text)
    
    # KİMLİK BİLGİLERİ
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)  # Veriyi giren kullanıcı
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))  # İlk oluşturan
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))  # Son güncelleyen
    
    # ZAMAN DAMGALARI
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # VERİ GİRİŞ TARİHİ
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İLİŞKİLER
    bireysel_pg = db.relationship('BireyselPerformansGostergesi', backref=db.backref('veriler', lazy=True))
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('pg_verileri', lazy=True))
    olusturan = db.relationship('User', foreign_keys=[created_by])
    guncelleyen = db.relationship('User', foreign_keys=[updated_by])
    
    def __repr__(self):
        return f'<PerformansGostergeVeri ID:{self.id} PG:{self.bireysel_pg_id} Tarih:{self.veri_tarihi}>'


class PerformansGostergeVeriAudit(db.Model):
    """PG veri değişiklik geçmişi (Audit Log)"""
    __tablename__ = 'performans_gosterge_veri_audit'
    
    id = db.Column(db.Integer, primary_key=True)
    pg_veri_id = db.Column(db.Integer, db.ForeignKey('performans_gosterge_veri.id'), nullable=False, index=True)
    
    # İŞLEM BİLGİLERİ
    islem_tipi = db.Column(db.String(20), nullable=False)  # 'OLUSTUR', 'GUNCELLE', 'SIL'
    eski_deger = db.Column(db.Text)  # JSON formatında eski değer
    yeni_deger = db.Column(db.Text)  # JSON formatında yeni değer
    degisiklik_aciklama = db.Column(db.Text)  # Ne değişti özet
    
    # KİM, NE ZAMAN
    islem_yapan_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    islem_tarihi = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # İLİŞKİLER
    # passive_deletes=True: Veri silindiğinde audit log kayıtları silinmemeli (geçmişi sakla)
    pg_veri = db.relationship('PerformansGostergeVeri', backref=db.backref('audit_log', lazy=True, passive_deletes=True))
    islem_yapan = db.relationship('User', backref=db.backref('pg_veri_audit_islemleri', lazy=True))
    
    def __repr__(self):
        return f'<PGVeriAudit ID:{self.id} Veri:{self.pg_veri_id} İşlem:{self.islem_tipi}>'


class FaaliyetTakip(db.Model):
    """Faaliyetin aylık takibi (X işaretleme)"""
    __tablename__ = 'faaliyet_takip'
    
    id = db.Column(db.Integer, primary_key=True)
    bireysel_faaliyet_id = db.Column(db.Integer, db.ForeignKey('bireysel_faaliyet.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    yil = db.Column(db.Integer, nullable=False, index=True)
    ay = db.Column(db.Integer, nullable=False)  # 1-12
    gerceklesti = db.Column(db.Boolean, default=False)  # True = X işareti
    not_text = db.Column(db.Text)  # Opsiyonel not
    tamamlanma_tarihi = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    bireysel_faaliyet = db.relationship('BireyselFaaliyet', backref=db.backref('takip', lazy=True))
    user = db.relationship('User', backref=db.backref('faaliyet_takipleri', lazy=True))
    
    def __repr__(self):
        return f'<FaaliyetTakip Faaliyet:{self.bireysel_faaliyet_id} {self.yil}/{self.ay} Gerç:{self.gerceklesti}>'


class FavoriKPI(db.Model):
    """Kullanıcının dashboard'da görmek istediği favori KPI'lar"""
    __tablename__ = 'favori_kpi'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    surec_pg_id = db.Column(db.Integer, db.ForeignKey('surec_performans_gostergesi.id'), nullable=False, index=True)
    sira = db.Column(db.Integer, default=0)  # Dashboard'da gösterilme sırası
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('favori_kpiler', lazy=True))
    surec_pg = db.relationship('SurecPerformansGostergesi', backref=db.backref('favori_olanlar', lazy=True))
    
    def __repr__(self):
        return f'<FavoriKPI User:{self.user_id} PG:{self.surec_pg_id}>'


class YetkiMatrisi(db.Model):
    """Rol bazlı yetki tanımlamaları"""
    __tablename__ = 'yetki_matrisi'
    
    id = db.Column(db.Integer, primary_key=True)
    rol = db.Column(db.String(50), nullable=False, index=True)  # sistem_admin, kurum_admin, kurum_user
    yetki_kodu = db.Column(db.String(100), nullable=False)  # kurum_ozluk_goruntule, kurum_ozluk_duzenle, vb.
    aktif = db.Column(db.Boolean, default=True)
    aciklama = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<YetkiMatrisi {self.rol}:{self.yetki_kodu}>'


class KullaniciYetki(db.Model):
    """Kullanıcı bazlı yetki atamaları - 2 boyutlu matris için"""
    __tablename__ = 'kullanici_yetki'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    yetki_kodu = db.Column(db.String(100), nullable=False)
    aktif = db.Column(db.Boolean, default=True)
    atayan_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Kim bu yetkiyi verdi
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', foreign_keys=[user_id], backref='yetkiler')
    atayan = db.relationship('User', foreign_keys=[atayan_user_id])
    
    def __repr__(self):
        return f'<KullaniciYetki User:{self.user_id} - {self.yetki_kodu}>'


# ============================================================================
# PROJE YÖNETİMİ MODÜLÜ MODELLERİ
# ============================================================================

class Project(db.Model):
    """Proje modeli - Çoklu süreç ve kullanıcı bağlantısı"""
    __tablename__ = 'project'
    
    id = db.Column(db.Integer, primary_key=True)
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'), nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date, nullable=True, index=True)  # Proje başlangıç tarihi
    end_date = db.Column(db.Date, nullable=True, index=True)  # Proje bitiş tarihi
    priority = db.Column(db.String(50), default='Orta')  # Düşük, Orta, Yüksek, Kritik
    is_archived = db.Column(db.Boolean, default=False, index=True)  # Arşivlenmiş proje mi?
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # V67: Proje Sağlık Skoru Sistemi
    health_score = db.Column(db.Integer, default=100)  # 0-100 arası sağlık skoru
    health_status = db.Column(db.String(50), default='İyi')  # İyi, Riskte, Uyuyor, Kritik
    
    kurum = db.relationship('Kurum', backref=db.backref('projeler', lazy=True))
    manager = db.relationship('User', foreign_keys=[manager_id], backref='yonettigi_projeler')
    members = db.relationship('User', secondary=project_members, backref='uye_oldugu_projeler')
    observers = db.relationship('User', secondary=project_observers, backref='gozlemci_oldugu_projeler')
    related_processes = db.relationship('Surec', secondary=project_related_processes, backref='bagli_projeler')
    # V3.0: processes alias (related_processes ile aynı ilişkiyi kullanıyoruz)
    processes = db.relationship('Surec', secondary=project_related_processes, backref='projeler')  # Alias for related_processes
    tasks = db.relationship('Task', backref='project', lazy=True, cascade='all, delete-orphan')
    
    # Şablon ilişkisi (şablondan oluşturulduysa)
    template_id = db.Column(db.Integer, db.ForeignKey('project_template.id'), nullable=True, index=True)
    template = db.relationship('ProjectTemplate', backref='instances')
    
    def get_health_score(self):
        """Projenin sağlık durumunu hesaplar (100 üzerinden).
        Her 'High' öncelikli ve 'Açık' iş 20 puan düşürür.
        Template'lerde kullanım için optimize edilmiş versiyon."""
        try:
            # Activity modelini import et (circular import önlemi için)
            # Activity modeli bu dosyada tanımlı olduğu için direkt kullanabiliriz
            from models import Activity
            
            # Riskli işleri say (Proje adı veya ID eşleşen, High priority ve Açık/Beklemede/Devam olanlar)
            risk_count = Activity.query.filter(
                db.or_(
                    Activity.project_name == self.name,  # project_name ile eşleşme
                    Activity.project_id == self.id       # veya project_id ile eşleşme
                ),
                Activity.priority == 'High',
                Activity.status.in_(['Açık', 'Beklemede', 'Devam'])
            ).count()
            
            # Puan hesabı: Başlangıç 100, her risk -20
            score = 100 - (risk_count * 20)
            return max(0, score)  # Eksiye düşmesin
        except Exception as e:
            # Hata durumunda varsayılan tam puan döndür
            return 100
    
    def update_health(self):
        """V67: Proje sağlık skorunu faaliyetlere göre güncelle (veritabanına kaydet)"""
        from datetime import timedelta
        
        # Başlangıç puanı
        score = 100
        
        # Açık faaliyetleri say
        open_activities = [a for a in self.activities if a.status not in ['Tamamlandı', 'Kapalı']]
        
        # Öncelik bazlı puan düşüşü
        for activity in open_activities:
            if activity.priority == 'High':
                score -= 15
            elif activity.priority == 'Normal':
                score -= 5
            elif activity.priority == 'Low':
                score -= 2
        
        # Son 7 gün içinde faaliyet var mı kontrol et
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_activities = [a for a in self.activities if a.date and a.date >= seven_days_ago]
        if not recent_activities and open_activities:
            # Son 7 günde faaliyet yoksa "Uyuyor" durumu
            self.health_status = 'Uyuyor'
            score = min(score, 40)  # Uyuyan projeler maksimum 40 puan alabilir
        
        # Skoru 0-100 aralığına sınırla
        score = max(0, min(100, score))
        self.health_score = score
        
        # Durum belirleme
        if score < 50:
            self.health_status = 'Kritik'
        elif score < 70:
            self.health_status = 'Riskte'
        elif not recent_activities and open_activities:
            self.health_status = 'Uyuyor'
        else:
            self.health_status = 'İyi'
        
        return self.health_score, self.health_status
    
    def __repr__(self):
        return f'<Project {self.name}>'


class Task(db.Model):
    """Görev modeli - Hiyerarşik yapı ve durum takibi"""
    __tablename__ = 'task'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=True, index=True)  # Hiyerarşik yapı
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, index=True)  # Atanan kullanıcı
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.Date, index=True)
    priority = db.Column(db.String(50), default='Orta')  # Düşük, Orta, Yüksek, Acil
    status = db.Column(db.String(50), default='Yapılacak', index=True)  # Yapılacak, Devam Ediyor, Tamamlandı, Beklemede
    estimated_time = db.Column(db.Float)  # Tahmini süre (saat)
    actual_time = db.Column(db.Float)  # Gerçekleşen süre (saat)
    completed_at = db.Column(db.DateTime, index=True)  # Tamamlanma tarihi
    is_archived = db.Column(db.Boolean, default=False, index=True)  # Arşivlenmiş görev mi?
    
    # PG OTOMASYON ALANLARI (V2.5.0)
    is_measurable = db.Column(db.Boolean, default=False, index=True)  # Ölçülebilir faaliyet mi?
    planned_output_value = db.Column(db.Float, nullable=True)  # Planlanan çıktı değeri
    related_indicator_id = db.Column(db.Integer, db.ForeignKey('bireysel_performans_gostergesi.id'), nullable=True, index=True)  # İlişkili PG
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Hiyerarşik ilişkiler
    parent = db.relationship('Task', remote_side=[id], backref='children')
    predecessors = db.relationship('Task', secondary=task_predecessors,
                                   primaryjoin=(task_predecessors.c.task_id == id),
                                   secondaryjoin=(task_predecessors.c.predecessor_id == id),
                                   backref='successors')
    
    # Atama ilişkisi
    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id], backref='assigned_tasks')
    
    # Impact ilişkileri
    impacts = db.relationship('TaskImpact', backref='task', lazy=True, cascade='all, delete-orphan')
    
    # PG ilişkisi (otomasyon için)
    related_indicator = db.relationship('BireyselPerformansGostergesi', foreign_keys=[related_indicator_id], backref='related_tasks')
    
    def __repr__(self):
        return f'<Task {self.title}>'


class TaskImpact(db.Model):
    """Görev etkisi - Görev tamamlandığında PG'ye eklenecek değer"""
    __tablename__ = 'task_impact'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False, index=True)
    related_pg_id = db.Column(db.Integer, db.ForeignKey('bireysel_performans_gostergesi.id'), nullable=True, index=True)
    related_faaliyet_id = db.Column(db.Integer, db.ForeignKey('bireysel_faaliyet.id'), nullable=True, index=True)
    impact_value = db.Column(db.String(100), nullable=False)  # Görev bittiğinde PG'ye eklenecek değer
    is_processed = db.Column(db.Boolean, default=False, index=True)  # Bu impact işlendi mi? (Mükerrer veri kontrolü)
    processed_at = db.Column(db.DateTime, nullable=True)  # İşlenme tarihi
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    related_pg = db.relationship('BireyselPerformansGostergesi', foreign_keys=[related_pg_id], backref='task_impacts')
    related_faaliyet = db.relationship('BireyselFaaliyet', foreign_keys=[related_faaliyet_id], backref='task_impacts')
    
    def __repr__(self):
        return f'<TaskImpact Task:{self.task_id} PG:{self.related_pg_id} Value:{self.impact_value} Processed:{self.is_processed}>'


class TaskComment(db.Model):
    """Görev yorumları/tartışma alanı"""
    __tablename__ = 'task_comment'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    comment_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    task = db.relationship('Task', backref=db.backref('comments', lazy=True, cascade='all, delete-orphan'))
    user = db.relationship('User', backref=db.backref('task_comments', lazy=True))
    
    def __repr__(self):
        return f'<TaskComment Task:{self.task_id} User:{self.user_id}>'


class TaskMention(db.Model):
    """Görev yorumlarında @etiketleme"""
    __tablename__ = 'task_mention'
    
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('task_comment.id'), nullable=False, index=True)
    mentioned_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    comment = db.relationship('TaskComment', backref=db.backref('mentions', lazy=True, cascade='all, delete-orphan'))
    mentioned_user = db.relationship('User', foreign_keys=[mentioned_user_id], backref='task_mentions')
    
    def __repr__(self):
        return f'<TaskMention Comment:{self.comment_id} User:{self.mentioned_user_id}>'


class ProjectFile(db.Model):
    """Proje ve Kurumsal dosya havuzu - Versiyonlama, soft-delete ve ikili dosya sunucusu desteği"""
    __tablename__ = 'project_file'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True, index=True)  # NULL olabilir (kurumsal dosyalar için)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)  # Bytes
    file_type = db.Column(db.String(100))  # MIME type veya extension
    description = db.Column(db.Text)
    version = db.Column(db.Integer, default=1)  # Dosya versiyonu
    parent_file_id = db.Column(db.Integer, db.ForeignKey('project_file.id'), nullable=True, index=True)  # Önceki versiyon
    is_active = db.Column(db.Boolean, default=True, index=True)  # Soft-delete için
    deleted_at = db.Column(db.DateTime, nullable=True)  # Silme tarihi
    deleted_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Silen kullanıcı
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # İkili Dosya Sunucusu Alanları
    scope = db.Column(db.String(20), default='PROJECT', index=True)  # 'PROJECT' veya 'CORPORATE'
    category = db.Column(db.String(100), nullable=True, index=True)  # Kategori: 'Yönetmelik', 'Şablon', 'Rapor', 'IT Politikaları', vb.
    folder_path = db.Column(db.String(500), nullable=True)  # Klasör yolu (hierarchical yapı için)
    
    project = db.relationship('Project', backref=db.backref('files', lazy=True, cascade='all, delete-orphan'))
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('uploaded_project_files', lazy=True))
    parent_file = db.relationship('ProjectFile', remote_side=[id], backref='child_versions')
    deleted_by = db.relationship('User', foreign_keys=[deleted_by_id])
    
    def __repr__(self):
        scope_label = 'CORP' if self.scope == 'CORPORATE' else f'PROJ:{self.project_id}'
        return f'<ProjectFile {scope_label} File:{self.file_name} v{self.version}>'


# Association Tables - Yeni
task_tags = db.Table('task_tags',
    db.Column('task_id', db.Integer, db.ForeignKey('task.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)


class Tag(db.Model):
    """Görev etiketleri"""
    __tablename__ = 'tag'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(7), default='#007bff')  # Hex color
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True, index=True)  # Proje bazlı etiketler
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    project = db.relationship('Project', backref=db.backref('tags', lazy=True))
    
    def __repr__(self):
        return f'<Tag {self.name}>'


class TaskSubtask(db.Model):
    """Görev alt görevleri (checklist)"""
    __tablename__ = 'task_subtask'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    is_completed = db.Column(db.Boolean, default=False, index=True)
    order = db.Column(db.Integer, default=0)  # Sıralama
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    task = db.relationship('Task', backref=db.backref('subtasks', lazy=True, cascade='all, delete-orphan', order_by='TaskSubtask.order'))
    
    def __repr__(self):
        return f'<TaskSubtask {self.title}>'


class TimeEntry(db.Model):
    """Zaman takibi kayıtları"""
    __tablename__ = 'time_entry'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    start_time = db.Column(db.DateTime, nullable=False, index=True)
    end_time = db.Column(db.DateTime, nullable=True)
    duration_minutes = db.Column(db.Integer)  # Otomatik hesaplanır
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    task = db.relationship('Task', backref=db.backref('time_entries', lazy=True, cascade='all, delete-orphan'))
    user = db.relationship('User', backref=db.backref('time_entries', lazy=True))
    
    def __repr__(self):
        return f'<TimeEntry Task:{self.task_id} User:{self.user_id}>'


class TaskActivity(db.Model):
    """Görev aktivite log'u (audit trail)"""
    __tablename__ = 'task_activity'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    action = db.Column(db.String(50), nullable=False)  # created, updated, deleted, status_changed, assigned, etc.
    field_name = db.Column(db.String(50), nullable=True)  # Hangi alan değiştirildi
    old_value = db.Column(db.Text, nullable=True)  # Eski değer (JSON string)
    new_value = db.Column(db.Text, nullable=True)  # Yeni değer (JSON string)
    description = db.Column(db.Text)  # İnsan okunabilir açıklama
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    task = db.relationship('Task', backref=db.backref('activities', lazy=True, cascade='all, delete-orphan', order_by='TaskActivity.created_at.desc()'))
    user = db.relationship('User', backref=db.backref('task_activities', lazy=True))
    
    def __repr__(self):
        return f'<TaskActivity Task:{self.task_id} Action:{self.action}>'


class Activity(db.Model):
    """Faaliyet modeli - V67: Redmine/Jira/CRM entegrasyonu için merkezi aktivite kayıtları"""
    __tablename__ = 'activity'
    
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(50), nullable=False, index=True)  # Redmine, Jira, CRM, Dahili
    subject = db.Column(db.String(200), nullable=False)
    priority = db.Column(db.String(20), nullable=False, index=True)  # High, Normal, Low
    status = db.Column(db.String(50), nullable=False, index=True)  # Açık, Beklemede, Devam, Tamamlandı, Kapalı
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True, index=True)  # Opsiyonel: Projeye bağlı olabilir
    project_name = db.Column(db.String(200))  # V67: Proje adı (project_id yoksa bu kullanılır)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    project = db.relationship('Project', backref=db.backref('activities', lazy=True, cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<Activity {self.id} - {self.source}:{self.subject}>'
    
    def to_dict(self):
        """Activity nesnesini dictionary'ye çevir (templates için)"""
        return {
            'id': self.id,
            'source': self.source,
            'project': self.project.name if self.project else self.project_name or 'N/A',
            'subject': self.subject,
            'status': self.status,
            'priority': self.priority,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None
        }


class ProjectTemplate(db.Model):
    """Proje şablonları"""
    __tablename__ = 'project_template'
    
    id = db.Column(db.Integer, primary_key=True)
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'), nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    is_public = db.Column(db.Boolean, default=False)  # Kurum genelinde kullanılabilir mi?
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    kurum = db.relationship('Kurum', backref=db.backref('project_templates', lazy=True))
    created_by = db.relationship('User', foreign_keys=[created_by_id], backref='created_project_templates')
    
    def __repr__(self):
        return f'<ProjectTemplate {self.name}>'


class TaskTemplate(db.Model):
    """Görev şablonları (proje şablonlarına bağlı)"""
    __tablename__ = 'task_template'
    
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('project_template.id'), nullable=False, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('task_template.id'), nullable=True)  # Hiyerarşik yapı
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    estimated_time = db.Column(db.Float)
    priority = db.Column(db.String(50), default='Orta')
    order = db.Column(db.Integer, default=0)
    
    template = db.relationship('ProjectTemplate', backref=db.backref('task_templates', lazy=True, cascade='all, delete-orphan'))
    parent = db.relationship('TaskTemplate', remote_side=[id], backref='children')
    
    def __repr__(self):
        return f'<TaskTemplate {self.title}>'


class Sprint(db.Model):
    """Sprint (Agile metodoloji)"""
    __tablename__ = 'sprint'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    goal = db.Column(db.Text)
    start_date = db.Column(db.Date, nullable=False, index=True)
    end_date = db.Column(db.Date, nullable=False, index=True)
    status = db.Column(db.String(20), default='Planned')  # Planned, Active, Completed, Cancelled
    velocity = db.Column(db.Float)  # Sprint hızı (story points veya görev sayısı)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    project = db.relationship('Project', backref=db.backref('sprints', lazy=True, cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<Sprint {self.name}>'


class TaskSprint(db.Model):
    """Görev-Sprint ilişkisi"""
    __tablename__ = 'task_sprint'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False, index=True)
    sprint_id = db.Column(db.Integer, db.ForeignKey('sprint.id'), nullable=False, index=True)
    story_points = db.Column(db.Integer, default=0)  # Story points (opsiyonel)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    task = db.relationship('Task', backref=db.backref('sprint_assignments', lazy=True, cascade='all, delete-orphan'))
    sprint = db.relationship('Sprint', backref=db.backref('tasks', lazy=True, cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<TaskSprint Task:{self.task_id} Sprint:{self.sprint_id}>'


class ProjectRisk(db.Model):
    """Proje riskleri - Risk yönetimi ve ısı haritası"""
    __tablename__ = 'project_risk'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    impact = db.Column(db.Integer, nullable=False)  # 1-5 arası (Düşük-Yüksek)
    probability = db.Column(db.Integer, nullable=False)  # 1-5 arası (Düşük-Yüksek)
    mitigation_plan = db.Column(db.Text)  # Azaltma planı
    status = db.Column(db.String(50), default='Aktif')  # Aktif, Azaltıldı, Kapatıldı
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    project = db.relationship('Project', backref=db.backref('risks', lazy=True, cascade='all, delete-orphan'))
    created_by = db.relationship('User', foreign_keys=[created_by_id], backref='created_project_risks')
    
    @property
    def risk_score(self):
        """Risk skoru: impact * probability (1-25 arası)"""
        return self.impact * self.probability
    
    @property
    def risk_level(self):
        """Risk seviyesi: Düşük, Orta, Yüksek, Kritik"""
        score = self.risk_score
        if score <= 6:
            return 'Düşük'
        elif score <= 12:
            return 'Orta'
        elif score < 20:
            return 'Yüksek'
        else:  # score >= 20
            return 'Kritik'
    
    def __repr__(self):
        return f'<ProjectRisk Project:{self.project_id} {self.title} Score:{self.risk_score}>'


# ============================================
# FAZ 2: OPERASYONEL MÜKEMMELLİK MODELLERİ
# ============================================

# V59.0 - Hoshin Kanri Paketi
class ObjectiveComment(db.Model):
    """OKR/Hedef Yorum Modeli - Hoshin Catchball için"""
    __tablename__ = 'objective_comment'
    
    id = db.Column(db.Integer, primary_key=True)
    objective_id = db.Column(db.Integer, db.ForeignKey('alt_strateji.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    comment_text = db.Column(db.Text, nullable=False)
    comment_type = db.Column(db.String(50), default='feedback')  # feedback, question, approval, concern
    status = db.Column(db.String(50), default='active')  # active, resolved, archived
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    objective = db.relationship('AltStrateji', backref=db.backref('comments', lazy=True))
    user = db.relationship('User', backref=db.backref('objective_comments', lazy=True))
    
    def __repr__(self):
        return f'<ObjectiveComment Objective:{self.objective_id} User:{self.user_id} Type:{self.comment_type}>'


class StrategicPlan(db.Model):
    """Stratejik Plan Modeli - MTBP (Mid-Term Business Plan) için"""
    __tablename__ = 'strategic_plan'
    
    id = db.Column(db.Integer, primary_key=True)
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'), nullable=False, index=True)
    plan_name = db.Column(db.String(200), nullable=False)
    plan_type = db.Column(db.String(50), default='mtbp')  # mtbp, annual, quarterly
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='draft')  # draft, active, completed, archived
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    kurum = db.relationship('Kurum', backref=db.backref('strategic_plans', lazy=True))
    creator = db.relationship('User', foreign_keys=[created_by], backref=db.backref('created_plans', lazy=True))
    
    def __repr__(self):
        return f'<StrategicPlan {self.plan_name} ({self.plan_type})>'


class PlanItem(db.Model):
    """Plan Maddesi Modeli - StrategicPlan'e bağlı hedefler ve faaliyetler"""
    __tablename__ = 'plan_item'
    
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('strategic_plan.id'), nullable=False, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('plan_item.id'), nullable=True, index=True)  # Hiyerarşi için
    item_type = db.Column(db.String(50), nullable=False)  # objective, key_result, initiative, action
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    target_value = db.Column(db.Numeric(10, 2), nullable=True)
    current_value = db.Column(db.Numeric(10, 2), default=0)
    unit = db.Column(db.String(50))  # %, adet, TL, vb.
    priority = db.Column(db.String(50), default='medium')  # low, medium, high, critical
    status = db.Column(db.String(50), default='not_started')  # not_started, in_progress, completed, on_hold
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    due_date = db.Column(db.Date, nullable=True)
    progress_percentage = db.Column(db.Numeric(5, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    plan = db.relationship('StrategicPlan', backref=db.backref('items', lazy=True, cascade='all, delete-orphan'))
    parent = db.relationship('PlanItem', remote_side=[id], backref=db.backref('children', lazy=True))
    assignee = db.relationship('User', backref=db.backref('assigned_plan_items', lazy=True))
    
    def __repr__(self):
        return f'<PlanItem {self.title} ({self.item_type})>'


class GembaWalk(db.Model):
    """Gemba Walk Modeli - Dijital Gemba için"""
    __tablename__ = 'gemba_walk'
    
    id = db.Column(db.Integer, primary_key=True)
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'), nullable=False, index=True)
    surec_id = db.Column(db.Integer, db.ForeignKey('surec.id'), nullable=True, index=True)
    conducted_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    walk_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    location = db.Column(db.String(200))  # Fiziksel veya dijital lokasyon
    observations = db.Column(db.Text, nullable=False)  # Gözlemler
    findings = db.Column(db.Text)  # Bulgular
    improvements = db.Column(db.Text)  # İyileştirme önerileri
    status = db.Column(db.String(50), default='completed')  # planned, in_progress, completed, follow_up
    follow_up_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    kurum = db.relationship('Kurum', backref=db.backref('gemba_walks', lazy=True))
    surec = db.relationship('Surec', backref=db.backref('gemba_walks', lazy=True))
    conductor = db.relationship('User', backref=db.backref('conducted_gemba_walks', lazy=True))
    
    def __repr__(self):
        return f'<GembaWalk {self.walk_date} Process:{self.surec_id}>'


# V60.0 - Talent & Risk Paketi
class Competency(db.Model):
    """Yetkinlik Modeli - Yetkinlik Matrisi için"""
    __tablename__ = 'competency'
    
    id = db.Column(db.Integer, primary_key=True)
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'), nullable=False, index=True)
    competency_name = db.Column(db.String(200), nullable=False)
    competency_category = db.Column(db.String(100))  # technical, leadership, soft_skills, domain
    description = db.Column(db.Text)
    competency_levels = db.Column(db.Text)  # JSON: {"1": "Başlangıç", "2": "Temel", ...}
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # İlişkiler
    kurum = db.relationship('Kurum', backref=db.backref('competencies', lazy=True))
    
    def __repr__(self):
        return f'<Competency {self.competency_name}>'


class UserCompetency(db.Model):
    """Kullanıcı Yetkinlik Modeli - Kullanıcının yetkinlik seviyelerini tutar"""
    __tablename__ = 'user_competency'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    competency_id = db.Column(db.Integer, db.ForeignKey('competency.id'), nullable=False, index=True)
    level = db.Column(db.Integer, nullable=False, default=1)  # 1-5 arası seviye
    self_assessed = db.Column(db.Boolean, default=True)  # Kendi değerlendirmesi mi?
    assessed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Değerlendiren kişi
    assessment_date = db.Column(db.Date, default=datetime.utcnow)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('competencies', lazy=True))
    competency = db.relationship('Competency', backref=db.backref('user_competencies', lazy=True))
    assessor = db.relationship('User', foreign_keys=[assessed_by], backref=db.backref('assessed_competencies', lazy=True))
    
    # Unique constraint: Bir kullanıcının aynı yetkinliği sadece bir kez olabilir
    __table_args__ = (db.UniqueConstraint('user_id', 'competency_id', name='uq_user_competency'),)
    
    def __repr__(self):
        return f'<UserCompetency User:{self.user_id} Competency:{self.competency_id} Level:{self.level}>'


class StrategicRisk(db.Model):
    """Stratejik Risk Modeli - Risk Yönetimi için"""
    __tablename__ = 'strategic_risk'
    
    id = db.Column(db.Integer, primary_key=True)
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'), nullable=False, index=True)
    risk_name = db.Column(db.String(300), nullable=False)
    risk_category = db.Column(db.String(100))  # strategic, operational, financial, compliance, reputation
    description = db.Column(db.Text, nullable=False)
    probability = db.Column(db.Integer, nullable=False, default=3)  # 1-5 arası (5x5 matris)
    impact = db.Column(db.Integer, nullable=False, default=3)  # 1-5 arası
    mitigation_strategy = db.Column(db.Text)  # Azaltma stratejisi
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    status = db.Column(db.String(50), default='open')  # open, mitigated, accepted, transferred
    risk_score = db.Column(db.Integer, nullable=False)  # probability * impact (1-25)
    identified_date = db.Column(db.Date, default=datetime.utcnow)
    mitigation_due_date = db.Column(db.Date, nullable=True)
    review_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    kurum = db.relationship('Kurum', backref=db.backref('strategic_risks', lazy=True))
    owner = db.relationship('User', backref=db.backref('owned_risks', lazy=True))
    
    @property
    def risk_level(self):
        """Risk seviyesi: Düşük, Orta, Yüksek, Kritik (5x5 matrisine göre)"""
        if self.risk_score <= 6:
            return 'Düşük'
        elif self.risk_score <= 12:
            return 'Orta'
        elif self.risk_score <= 20:
            return 'Yüksek'
        else:  # score >= 21
            return 'Kritik'
    
    def __repr__(self):
        return f'<StrategicRisk {self.risk_name} Score:{self.risk_score}>'


# V65.0 - Muda Hunter (Waste Eliminator)
class MudaFinding(db.Model):
    """Muda (İsraf) Bulgusu Modeli - Süreç verimsizliği analizi için"""
    __tablename__ = 'muda_finding'
    
    id = db.Column(db.Integer, primary_key=True)
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'), nullable=False, index=True)
    surec_id = db.Column(db.Integer, db.ForeignKey('surec.id'), nullable=False, index=True)
    muda_type = db.Column(db.String(100), nullable=False)  # overproduction, waiting, transport, overprocessing, inventory, motion, defects
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(50), default='medium')  # low, medium, high, critical
    estimated_waste_hours = db.Column(db.Numeric(10, 2), nullable=True)  # Tahmini israf saati
    estimated_waste_cost = db.Column(db.Numeric(12, 2), nullable=True)  # Tahmini maliyet kaybı
    identified_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    identified_date = db.Column(db.Date, default=datetime.utcnow)
    status = db.Column(db.String(50), default='identified')  # identified, analyzing, improving, resolved, accepted
    improvement_plan = db.Column(db.Text)  # İyileştirme planı
    resolved_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    kurum = db.relationship('Kurum', backref=db.backref('muda_findings', lazy=True))
    surec = db.relationship('Surec', backref=db.backref('muda_findings', lazy=True))
    identifier = db.relationship('User', backref=db.backref('identified_mudas', lazy=True))
    
    def __repr__(self):
        return f'<MudaFinding {self.title} Type:{self.muda_type} Severity:{self.severity}>'


# ============================================
# FAZ 3: İLERİ SEVİYE MODÜLLER
# ============================================

# V61.0 - Titan & Zenith Paketi
class CrisisMode(db.Model):
    """Kriz Modu Modeli - Kriz Komuta Merkezi için"""
    __tablename__ = 'crisis_mode'
    
    id = db.Column(db.Integer, primary_key=True)
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'), nullable=False, index=True)
    crisis_name = db.Column(db.String(300), nullable=False)
    crisis_type = db.Column(db.String(100))  # financial, operational, reputation, legal, other
    severity = db.Column(db.String(50), default='medium')  # low, medium, high, critical
    description = db.Column(db.Text, nullable=False)
    activated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activated_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='active')  # active, resolved, closed
    resolution_notes = db.Column(db.Text)
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    # İlişkiler
    kurum = db.relationship('Kurum', backref=db.backref('crisis_modes', lazy=True))
    activator = db.relationship('User', backref=db.backref('activated_crises', lazy=True))
    
    def __repr__(self):
        return f'<CrisisMode {self.crisis_name} ({self.crisis_type})>'


class SafetyCheck(db.Model):
    """Güvenlik Kontrolü Modeli - Kriz öncesi güvenlik kontrolleri"""
    __tablename__ = 'safety_check'
    
    id = db.Column(db.Integer, primary_key=True)
    crisis_id = db.Column(db.Integer, db.ForeignKey('crisis_mode.id'), nullable=False, index=True)
    check_name = db.Column(db.String(200), nullable=False)
    check_category = db.Column(db.String(100))  # data, system, communication, legal, financial
    status = db.Column(db.String(50), default='pending')  # pending, checked, failed, passed
    checked_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    checked_at = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text)
    
    # İlişkiler
    crisis = db.relationship('CrisisMode', backref=db.backref('safety_checks', lazy=True))
    checker = db.relationship('User', backref=db.backref('safety_checks', lazy=True))
    
    def __repr__(self):
        return f'<SafetyCheck {self.check_name} Status:{self.status}>'


class SuccessionPlan(db.Model):
    """Halefiyet Planı Modeli"""
    __tablename__ = 'succession_plan'
    
    id = db.Column(db.Integer, primary_key=True)
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'), nullable=False, index=True)
    position_name = db.Column(db.String(200), nullable=False)
    current_holder_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    successor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    readiness_level = db.Column(db.Integer, default=1)  # 1-5 arası hazırlık seviyesi
    development_plan = db.Column(db.Text)
    timeline = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), default='active')  # active, executed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    kurum = db.relationship('Kurum', backref=db.backref('succession_plans', lazy=True))
    current_holder = db.relationship('User', foreign_keys=[current_holder_id], backref=db.backref('held_positions', lazy=True))
    successor = db.relationship('User', foreign_keys=[successor_id], backref=db.backref('succession_candidates', lazy=True))
    
    def __repr__(self):
        return f'<SuccessionPlan {self.position_name}>'


class OrgScenario(db.Model):
    """Organizasyon Senaryosu Modeli - Dinamik Organizasyon Tasarımcısı için"""
    __tablename__ = 'org_scenario'
    
    id = db.Column(db.Integer, primary_key=True)
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'), nullable=False, index=True)
    scenario_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    scenario_type = db.Column(db.String(100))  # expansion, restructuring, merger, downsizing
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(50), default='draft')  # draft, active, implemented, archived
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    kurum = db.relationship('Kurum', backref=db.backref('org_scenarios', lazy=True))
    creator = db.relationship('User', backref=db.backref('created_org_scenarios', lazy=True))
    
    def __repr__(self):
        return f'<OrgScenario {self.scenario_name}>'


class OrgChange(db.Model):
    """Organizasyon Değişikliği Modeli - Senaryo değişikliklerini tutar"""
    __tablename__ = 'org_change'
    
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey('org_scenario.id'), nullable=False, index=True)
    change_type = db.Column(db.String(100), nullable=False)  # create_department, merge_departments, add_role, remove_role
    change_description = db.Column(db.Text, nullable=False)
    affected_departments = db.Column(db.Text)  # JSON: list of department names
    affected_roles = db.Column(db.Text)  # JSON: list of role names
    impact_assessment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # İlişkiler
    scenario = db.relationship('OrgScenario', backref=db.backref('changes', lazy=True, cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<OrgChange {self.change_type} Scenario:{self.scenario_id}>'


class InfluenceScore(db.Model):
    """Etki Skoru Modeli - ONA (Organizasyonel Ağ Analizi) için"""
    __tablename__ = 'influence_score'
    
    id = db.Column(db.Integer, primary_key=True)
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    score = db.Column(db.Numeric(5, 2), nullable=False, default=0)  # 0-100 arası etki skoru
    calculation_date = db.Column(db.Date, default=datetime.utcnow)
    network_metrics = db.Column(db.Text)  # JSON: centrality, betweenness, closeness scores
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # İlişkiler
    kurum = db.relationship('Kurum', backref=db.backref('influence_scores', lazy=True))
    user = db.relationship('User', backref=db.backref('influence_scores', lazy=True))
    
    # Unique constraint: Bir kullanıcının aynı tarihte sadece bir skoru olabilir
    __table_args__ = (db.UniqueConstraint('user_id', 'calculation_date', name='uq_user_influence_date'),)
    
    def __repr__(self):
        return f'<InfluenceScore User:{self.user_id} Score:{self.score}>'


class MarketIntel(db.Model):
    """Pazar İstihbaratı Modeli - Market Watcher için"""
    __tablename__ = 'market_intel'
    
    id = db.Column(db.Integer, primary_key=True)
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'), nullable=False, index=True)
    intel_type = db.Column(db.String(100), nullable=False)  # competitor, trend, opportunity, threat
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text, nullable=False)
    source = db.Column(db.String(200))
    relevance_score = db.Column(db.Integer, default=3)  # 1-5 arası
    collected_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    collected_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='new')  # new, reviewed, archived
    
    # İlişkiler
    kurum = db.relationship('Kurum', backref=db.backref('market_intels', lazy=True))
    collector = db.relationship('User', backref=db.backref('collected_intels', lazy=True))
    
    def __repr__(self):
        return f'<MarketIntel {self.title} Type:{self.intel_type}>'


# V62.0 - Corporate Consciousness
class WellbeingScore(db.Model):
    """Refah Skoru Modeli - Tükenmişlik Kalkanı için"""
    __tablename__ = 'wellbeing_score'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'), nullable=False, index=True)
    score_date = db.Column(db.Date, default=datetime.utcnow)
    overall_score = db.Column(db.Numeric(5, 2), nullable=False)  # 0-100 arası
    workload_score = db.Column(db.Numeric(5, 2))
    stress_score = db.Column(db.Numeric(5, 2))
    satisfaction_score = db.Column(db.Numeric(5, 2))
    work_life_balance_score = db.Column(db.Numeric(5, 2))
    assessment_data = db.Column(db.Text)  # JSON: detaylı değerlendirme verileri
    risk_level = db.Column(db.String(50), default='low')  # low, medium, high, critical
    recommendations = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # İlişkiler
    user = db.relationship('User', backref=db.backref('wellbeing_scores', lazy=True))
    kurum = db.relationship('Kurum', backref=db.backref('wellbeing_scores', lazy=True))
    
    def __repr__(self):
        return f'<WellbeingScore User:{self.user_id} Score:{self.overall_score} Date:{self.score_date}>'


class SimulationScenario(db.Model):
    """Simülasyon Senaryosu Modeli - Monte Carlo Simülatörü için"""
    __tablename__ = 'simulation_scenario'
    
    id = db.Column(db.Integer, primary_key=True)
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'), nullable=False, index=True)
    scenario_name = db.Column(db.String(200), nullable=False)
    scenario_type = db.Column(db.String(100))  # financial, operational, strategic, risk
    description = db.Column(db.Text)
    parameters = db.Column(db.Text)  # JSON: simülasyon parametreleri
    results = db.Column(db.Text)  # JSON: simülasyon sonuçları
    iterations = db.Column(db.Integer, default=1000)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(50), default='draft')  # draft, running, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # İlişkiler
    kurum = db.relationship('Kurum', backref=db.backref('simulation_scenarios', lazy=True))
    creator = db.relationship('User', backref=db.backref('created_simulations', lazy=True))
    
    def __repr__(self):
        return f'<SimulationScenario {self.scenario_name} Type:{self.scenario_type}>'


class DeepWorkSession(db.Model):
    """Derin Çalışma Oturumu Modeli - Deep Work Protokolü için"""
    __tablename__ = 'deep_work_session'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    session_date = db.Column(db.Date, default=datetime.utcnow)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    duration_minutes = db.Column(db.Integer, nullable=True)
    session_type = db.Column(db.String(50), default='focused')  # focused, distraction_free, flow_state
    status = db.Column(db.String(50), default='active')  # active, completed, interrupted
    productivity_score = db.Column(db.Numeric(5, 2))  # 0-100 arası
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # İlişkiler
    user = db.relationship('User', backref=db.backref('deep_work_sessions', lazy=True))
    
    def __repr__(self):
        return f'<DeepWorkSession User:{self.user_id} Date:{self.session_date} Status:{self.status}>'


# V63.0 - Transcendence Pack
class Persona(db.Model):
    """Persona Modeli - Sentetik Müşteri Laboratuvarı için"""
    __tablename__ = 'persona'
    
    id = db.Column(db.Integer, primary_key=True)
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'), nullable=False, index=True)
    persona_name = db.Column(db.String(200), nullable=False)
    persona_type = db.Column(db.String(100))  # customer, employee, stakeholder, partner
    demographics = db.Column(db.Text)  # JSON: yaş, cinsiyet, lokasyon, vb.
    behaviors = db.Column(db.Text)  # JSON: davranış özellikleri
    preferences = db.Column(db.Text)  # JSON: tercihler
    pain_points = db.Column(db.Text)  # JSON: sorun noktaları
    goals = db.Column(db.Text)  # JSON: hedefler
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # İlişkiler
    kurum = db.relationship('Kurum', backref=db.backref('personas', lazy=True))
    creator = db.relationship('User', backref=db.backref('created_personas', lazy=True))
    
    def __repr__(self):
        return f'<Persona {self.persona_name} Type:{self.persona_type}>'


class ProductSimulation(db.Model):
    """Ürün Simülasyonu Modeli - Sentetik müşteri ile ürün testleri"""
    __tablename__ = 'product_simulation'
    
    id = db.Column(db.Integer, primary_key=True)
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'), nullable=False, index=True)
    persona_id = db.Column(db.Integer, db.ForeignKey('persona.id'), nullable=True, index=True)
    simulation_name = db.Column(db.String(200), nullable=False)
    product_description = db.Column(db.Text)
    simulation_results = db.Column(db.Text)  # JSON: simülasyon sonuçları
    feedback = db.Column(db.Text)  # Sentetik müşteri geri bildirimi
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # İlişkiler
    kurum = db.relationship('Kurum', backref=db.backref('product_simulations', lazy=True))
    persona = db.relationship('Persona', backref=db.backref('simulations', lazy=True))
    creator = db.relationship('User', backref=db.backref('created_product_simulations', lazy=True))
    
    def __repr__(self):
        return f'<ProductSimulation {self.simulation_name}>'


class SmartContract(db.Model):
    """Akıllı Sözleşme Modeli - DAO için"""
    __tablename__ = 'smart_contract'
    
    id = db.Column(db.Integer, primary_key=True)
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'), nullable=False, index=True)
    contract_name = db.Column(db.String(200), nullable=False)
    contract_type = db.Column(db.String(100))  # governance, payment, token, voting
    contract_address = db.Column(db.String(200))  # Blockchain adresi
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='draft')  # draft, deployed, active, archived
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # İlişkiler
    kurum = db.relationship('Kurum', backref=db.backref('smart_contracts', lazy=True))
    creator = db.relationship('User', backref=db.backref('created_smart_contracts', lazy=True))
    
    def __repr__(self):
        return f'<SmartContract {self.contract_name} Type:{self.contract_type}>'


class DaoProposal(db.Model):
    """DAO Önerisi Modeli"""
    __tablename__ = 'dao_proposal'
    
    id = db.Column(db.Integer, primary_key=True)
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'), nullable=False, index=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('smart_contract.id'), nullable=True, index=True)
    proposal_title = db.Column(db.String(300), nullable=False)
    proposal_description = db.Column(db.Text, nullable=False)
    proposal_type = db.Column(db.String(100))  # governance, funding, strategic, operational
    proposed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    voting_start = db.Column(db.DateTime, nullable=True)
    voting_end = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(50), default='draft')  # draft, active, passed, rejected, executed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # İlişkiler
    kurum = db.relationship('Kurum', backref=db.backref('dao_proposals', lazy=True))
    contract = db.relationship('SmartContract', backref=db.backref('proposals', lazy=True))
    proposer = db.relationship('User', backref=db.backref('dao_proposals', lazy=True))
    
    def __repr__(self):
        return f'<DaoProposal {self.proposal_title} Status:{self.status}>'


class DaoVote(db.Model):
    """DAO Oyu Modeli"""
    __tablename__ = 'dao_vote'
    
    id = db.Column(db.Integer, primary_key=True)
    proposal_id = db.Column(db.Integer, db.ForeignKey('dao_proposal.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    vote_choice = db.Column(db.String(50), nullable=False)  # yes, no, abstain
    vote_weight = db.Column(db.Numeric(10, 2), default=1.0)  # Oylama ağırlığı
    voted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # İlişkiler
    proposal = db.relationship('DaoProposal', backref=db.backref('votes', lazy=True))
    user = db.relationship('User', backref=db.backref('dao_votes', lazy=True))
    
    # Unique constraint: Bir kullanıcı aynı öneriye sadece bir kez oy verebilir
    __table_args__ = (db.UniqueConstraint('proposal_id', 'user_id', name='uq_proposal_user_vote'),)
    
    def __repr__(self):
        return f'<DaoVote Proposal:{self.proposal_id} User:{self.user_id} Choice:{self.vote_choice}>'


class MetaverseDepartment(db.Model):
    """Metaverse Departman İkizi Modeli"""
    __tablename__ = 'metaverse_department'
    
    id = db.Column(db.Integer, primary_key=True)
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'), nullable=False, index=True)
    department_name = db.Column(db.String(200), nullable=False)
    virtual_location = db.Column(db.String(200))  # Metaverse lokasyonu
    avatar_count = db.Column(db.Integer, default=0)
    active_users = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='active')  # active, inactive, archived
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # İlişkiler
    kurum = db.relationship('Kurum', backref=db.backref('metaverse_departments', lazy=True))
    creator = db.relationship('User', backref=db.backref('created_metaverse_departments', lazy=True))
    
    def __repr__(self):
        return f'<MetaverseDepartment {self.department_name}>'


class LegacyKnowledge(db.Model):
    """Miras Bilgi Modeli - Kurucu Miras AI için"""
    __tablename__ = 'legacy_knowledge'
    
    id = db.Column(db.Integer, primary_key=True)
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'), nullable=False, index=True)
    knowledge_type = db.Column(db.String(100))  # decision, strategy, culture, process, wisdom
    title = db.Column(db.String(300), nullable=False)
    content = db.Column(db.Text, nullable=False)
    source = db.Column(db.String(200))  # Kurucu, yönetici, vb.
    tags = db.Column(db.Text)  # JSON: etiketler
    relevance_score = db.Column(db.Integer, default=3)  # 1-5 arası
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # İlişkiler
    kurum = db.relationship('Kurum', backref=db.backref('legacy_knowledge', lazy=True))
    creator = db.relationship('User', backref=db.backref('created_legacy_knowledge', lazy=True))
    
    def __repr__(self):
        return f'<LegacyKnowledge {self.title} Type:{self.knowledge_type}>'


# ============================================
# FAZ 4: NIRVANA LEGACY
# ============================================

# V66.0 - Nirvana Legacy Paketi
class Competitor(db.Model):
    """Rakip Modeli - Oyun Teorisi (Game Theory Grid) için"""
    __tablename__ = 'competitor'
    
    id = db.Column(db.Integer, primary_key=True)
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'), nullable=False, index=True)
    competitor_name = db.Column(db.String(200), nullable=False)
    competitor_type = db.Column(db.String(100))  # direct, indirect, potential, substitute
    market_position = db.Column(db.String(100))  # leader, challenger, follower, nicher
    strengths = db.Column(db.Text)  # JSON: güçlü yönler
    weaknesses = db.Column(db.Text)  # JSON: zayıf yönler
    market_share = db.Column(db.Numeric(5, 2))  # Pazar payı (%)
    competitive_score = db.Column(db.Integer, default=50)  # 0-100 arası rekabet skoru
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    kurum = db.relationship('Kurum', backref=db.backref('competitors', lazy=True))
    
    def __repr__(self):
        return f'<Competitor {self.competitor_name}>'


class GameScenario(db.Model):
    """Oyun Senaryosu Modeli - Nash Dengesi analizi için"""
    __tablename__ = 'game_scenario'
    
    id = db.Column(db.Integer, primary_key=True)
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'), nullable=False, index=True)
    scenario_name = db.Column(db.String(200), nullable=False)
    scenario_description = db.Column(db.Text)
    competitor_id = db.Column(db.Integer, db.ForeignKey('competitor.id'), nullable=True, index=True)
    game_type = db.Column(db.String(100))  # prisoner_dilemma, chicken_game, stag_hunt, battle_of_sexes
    payoffs = db.Column(db.Text)  # JSON: kazanç matrisi
    nash_equilibrium = db.Column(db.Text)  # JSON: Nash dengesi sonucu
    strategy_recommendation = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # İlişkiler
    kurum = db.relationship('Kurum', backref=db.backref('game_scenarios', lazy=True))
    competitor = db.relationship('Competitor', backref=db.backref('game_scenarios', lazy=True))
    creator = db.relationship('User', backref=db.backref('created_game_scenarios', lazy=True))
    
    def __repr__(self):
        return f'<GameScenario {self.scenario_name} Type:{self.game_type}>'


class DoomsdayScenario(db.Model):
    """Kıyamet Senaryosu Modeli - Siyah Kuğu Simülatörü için"""
    __tablename__ = 'doomsday_scenario'
    
    id = db.Column(db.Integer, primary_key=True)
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'), nullable=False, index=True)
    scenario_name = db.Column(db.String(200), nullable=False)
    scenario_type = db.Column(db.String(100))  # economic, natural_disaster, cyber_attack, pandemic, regulatory, market_crash
    severity_level = db.Column(db.Integer, default=5)  # 1-10 arası şiddet seviyesi
    probability_percentage = db.Column(db.Numeric(5, 2))  # Olasılık yüzdesi
    description = db.Column(db.Text, nullable=False)
    impact_assessment = db.Column(db.Text)  # Etki değerlendirmesi
    mitigation_strategy = db.Column(db.Text)  # Azaltma stratejisi
    survival_probability = db.Column(db.Numeric(5, 2))  # Hayatta kalma olasılığı (%)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # İlişkiler
    kurum = db.relationship('Kurum', backref=db.backref('doomsday_scenarios', lazy=True))
    creator = db.relationship('User', backref=db.backref('created_doomsday_scenarios', lazy=True))
    
    def __repr__(self):
        return f'<DoomsdayScenario {self.scenario_name} Severity:{self.severity_level}>'


class YearlyChronicle(db.Model):
    """Yıllık Vakayiname Modeli - Omega'nın Kitabı (Auto-Biography) için"""
    __tablename__ = 'yearly_chronicle'
    
    id = db.Column(db.Integer, primary_key=True)
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'), nullable=False, index=True)
    year = db.Column(db.Integer, nullable=False, index=True)
    chronicle_title = db.Column(db.String(300), nullable=False)
    major_events = db.Column(db.Text)  # JSON: önemli olaylar
    achievements = db.Column(db.Text)  # JSON: başarılar
    challenges = db.Column(db.Text)  # JSON: zorluklar
    lessons_learned = db.Column(db.Text)  # JSON: öğrenilen dersler
    strategic_decisions = db.Column(db.Text)  # JSON: stratejik kararlar
    performance_summary = db.Column(db.Text)
    full_chronicle = db.Column(db.Text)  # Tam vakayiname metni
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    kurum = db.relationship('Kurum', backref=db.backref('yearly_chronicles', lazy=True))
    creator = db.relationship('User', backref=db.backref('created_chronicles', lazy=True))
    
    # Unique constraint: Bir kurum için aynı yıl sadece bir kez olabilir
    __table_args__ = (db.UniqueConstraint('kurum_id', 'year', name='uq_kurum_year_chronicle'),)
    
    def __repr__(self):
        return f'<YearlyChronicle {self.year} {self.chronicle_title}>'


