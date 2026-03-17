# -*- coding: utf-8 -*-
"""
Stratejik Analiz Modülü Modelleri
--------------------------------
SWOT, PESTLE ve TOWS için temel veri yapıları.
"""
from datetime import datetime
from extensions import db


class AnalysisItem(db.Model):
    __tablename__ = 'analysis_item'

    id = db.Column(db.Integer, primary_key=True)
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'), nullable=False, index=True)
    analysis_type = db.Column(db.String(20), nullable=False, index=True)  # SWOT | PESTLE
    category = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    score = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    kurum = db.relationship('Kurum', foreign_keys=[kurum_id], backref=db.backref('analysis_items', lazy=True))

    def __repr__(self):
        return f'<AnalysisItem {self.analysis_type}:{self.category}>'


class TowsMatrix(db.Model):
    __tablename__ = 'tows_matrix'

    id = db.Column(db.Integer, primary_key=True)
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'), nullable=False, index=True)
    strength_id = db.Column(db.Integer, db.ForeignKey('analysis_item.id'), nullable=False, index=True)
    opportunity_threat_id = db.Column(db.Integer, db.ForeignKey('analysis_item.id'), nullable=False, index=True)
    strategy_text = db.Column(db.Text, nullable=False)
    action_plan = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    kurum = db.relationship('Kurum', foreign_keys=[kurum_id], backref=db.backref('tows_strategies', lazy=True))
    strength = db.relationship('AnalysisItem', foreign_keys=[strength_id], backref=db.backref('tows_strength_links', lazy=True))
    opportunity_threat = db.relationship(
        'AnalysisItem',
        foreign_keys=[opportunity_threat_id],
        backref=db.backref('tows_opportunity_threat_links', lazy=True),
    )

    def __repr__(self):
        return f'<TowsMatrix {self.id}>'
