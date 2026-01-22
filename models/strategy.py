# -*- coding: utf-8 -*-
"""
Strateji Modelleri
------------------
Ana Strateji, Alt Strateji ve Strateji-Süreç ilişkilerini yöneten modelleri içerir.
"""
from extensions import db
from datetime import datetime

class AnaStrateji(db.Model):
    """
    Ana Strateji Modeli
    
    Kurumun en üst seviye stratejik hedeflerini tanımlar.
    V3.0 ile birlikte 'code' alanı eklenmiştir.
    """
    __tablename__ = 'ana_strateji'
    
    id = db.Column(db.Integer, primary_key=True)
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'), nullable=False, index=True)
    
    # Kod ve Tanım
    code = db.Column(db.String(20), nullable=True, index=True)  # Örn: ST1
    ad = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(200), nullable=True)  # İngilizce tanım (opsiyonel)
    aciklama = db.Column(db.Text)

    # BSC Perspektifi ve kısa kod
    perspective = db.Column(db.String(20), nullable=True, index=True)  # FINANSAL, MUSTERI, SUREC, OGRENME
    bsc_code = db.Column(db.String(10), nullable=True, index=True)  # Örn: F1, M2
    
    # Meta Veriler
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    # Alt stratejiler, AltStrateji modelinde backref ile tanımlanacak

    __table_args__ = (
        db.UniqueConstraint('kurum_id', 'code', name='uq_ana_strateji_kurum_code'),
    )
    
    def __repr__(self):
        return f'<AnaStrateji {self.code or ""} - {self.ad}>'


class AltStrateji(db.Model):
    """
    Alt Strateji Modeli
    
    Ana stratejilerin alt kırılımlarını oluşturur.
    V3.0 ile birlikte 'target_method' ve süreç ilişkisi eklenmiştir.
    """
    __tablename__ = 'alt_strateji'
    
    id = db.Column(db.Integer, primary_key=True)
    ana_strateji_id = db.Column(db.Integer, db.ForeignKey('ana_strateji.id'), nullable=False, index=True)
    
    # Kod ve Tanım
    code = db.Column(db.String(20), nullable=True, index=True)  # Örn: ST1.1
    ad = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(200), nullable=True)  # İngilizce tanım
    
    # Yöntem
    target_method = db.Column(db.String(10), nullable=True)  # HKY, RG, SH, DH, HK, SGH
    aciklama = db.Column(db.Text)
    
    # Meta Veriler
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    ana_strateji = db.relationship('AnaStrateji', backref=db.backref('alt_stratejiler', lazy=True, cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<AltStrateji {self.code or ""} - {self.ad}>'


class StrategyProcessMatrix(db.Model):
    """
    Strateji-Süreç Matrisi Modeli
    
    Alt stratejiler ile süreçler arasındaki ilişkinin gücünü (skorunu) tutar.
    V3.0: Excel'deki A/B ilişkileri için kullanılır (A=9 puan, B=3 puan).
    """
    __tablename__ = 'strategy_process_matrix'
    
    id = db.Column(db.Integer, primary_key=True)
    sub_strategy_id = db.Column(db.Integer, db.ForeignKey('alt_strateji.id'), nullable=False, index=True)
    process_id = db.Column(db.Integer, db.ForeignKey('surec.id'), nullable=False, index=True)
    
    relationship_strength = db.Column(db.Integer, default=0)  # 0-9 arası ilişki gücü
    relationship_score = db.Column(db.Integer, default=0)     # A=9, B=3
    
    # İlişkiler
    sub_strategy = db.relationship('AltStrateji', backref=db.backref('matrix_relations', lazy=True))
    process = db.relationship('Surec', backref=db.backref('strategy_matrix_relations', lazy=True))
    
    # Unique Constraint: Aynı çift sadece bir kez olabilir
    __table_args__ = (db.UniqueConstraint('sub_strategy_id', 'process_id', name='uq_strategy_process_matrix'),)
    
    def __repr__(self):
        return f'<StrategyProcessMatrix Sub:{self.sub_strategy_id} Proc:{self.process_id} Score:{self.relationship_score}>'


class StrategyMapLink(db.Model):
    """
    BSC Strateji Haritası Bağlantı Modeli
    Ana stratejiler arasındaki neden-sonuç ilişkilerini tutar.
    """
    __tablename__ = 'strategy_map_link'

    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, db.ForeignKey('ana_strateji.id'), nullable=False, index=True)
    target_id = db.Column(db.Integer, db.ForeignKey('ana_strateji.id'), nullable=False, index=True)
    connection_type = db.Column(db.String(30), nullable=False, default='CAUSE_EFFECT')

    source = db.relationship('AnaStrateji', foreign_keys=[source_id], backref=db.backref('bsc_out_links', lazy=True))
    target = db.relationship('AnaStrateji', foreign_keys=[target_id], backref=db.backref('bsc_in_links', lazy=True))

    __table_args__ = (
        db.UniqueConstraint('source_id', 'target_id', name='uq_strategy_map_link_pair'),
    )

    def __repr__(self):
        return f'<StrategyMapLink {self.source_id} -> {self.target_id}>'
