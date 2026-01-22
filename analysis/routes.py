# -*- coding: utf-8 -*-
"""
Strategic Analysis Module routes.
"""
from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from extensions import db
from models import AnalysisItem, TowsMatrix


analysis_bp = Blueprint('analysis', __name__)

ALLOWED_TYPES = {'SWOT', 'PESTLE'}
SWOT_CATEGORIES = {'Strengths', 'Weaknesses', 'Opportunities', 'Threats'}
PESTLE_CATEGORIES = {'Political', 'Economic', 'Social', 'Technological', 'Legal', 'Environmental'}


def _get_kurum_id():
    return getattr(current_user, 'kurum_id', None)


def _validate_analysis_input(analysis_type, category, score):
    if analysis_type not in ALLOWED_TYPES:
        return 'Geçersiz analiz türü.'
    if analysis_type == 'SWOT' and category not in SWOT_CATEGORIES:
        return 'Geçersiz SWOT kategorisi.'
    if analysis_type == 'PESTLE' and category not in PESTLE_CATEGORIES:
        return 'Geçersiz PESTLE kategorisi.'
    try:
        score_int = int(score)
    except (TypeError, ValueError):
        return 'Puan 1-5 aralığında olmalı.'
    if score_int < 1 or score_int > 5:
        return 'Puan 1-5 aralığında olmalı.'
    return None


@analysis_bp.route('/analiz-merkezi/<int:kurum_id>')
@login_required
def analysis_hub(kurum_id):
    current_kurum_id = _get_kurum_id()
    if current_kurum_id is None:
        return 'Kurum bilgisi bulunamadı.', 403

    swot_count = AnalysisItem.query.filter_by(kurum_id=current_kurum_id, analysis_type='SWOT').count()
    pestle_count = AnalysisItem.query.filter_by(kurum_id=current_kurum_id, analysis_type='PESTLE').count()
    tows_count = TowsMatrix.query.filter_by(kurum_id=current_kurum_id).count()

    return render_template(
        'analysis/hub.html',
        kurum_id=current_kurum_id,
        swot_count=swot_count,
        pestle_count=pestle_count,
        tows_count=tows_count,
    )


@analysis_bp.route('/analiz/swot/<int:kurum_id>')
@login_required
def swot_board(kurum_id):
    current_kurum_id = _get_kurum_id()
    if current_kurum_id is None:
        return 'Kurum bilgisi bulunamadı.', 403

    items = AnalysisItem.query.filter_by(kurum_id=current_kurum_id, analysis_type='SWOT').all()
    strengths = [item for item in items if item.category == 'Strengths']
    weaknesses = [item for item in items if item.category == 'Weaknesses']
    opportunities = [item for item in items if item.category == 'Opportunities']
    threats = [item for item in items if item.category == 'Threats']

    return render_template(
        'analysis/swot.html',
        kurum_id=current_kurum_id,
        strengths=strengths,
        weaknesses=weaknesses,
        opportunities=opportunities,
        threats=threats,
    )


@analysis_bp.route('/analiz/pestle/<int:kurum_id>')
@login_required
def pestle_board(kurum_id):
    current_kurum_id = _get_kurum_id()
    if current_kurum_id is None:
        return 'Kurum bilgisi bulunamadı.', 403

    items = AnalysisItem.query.filter_by(kurum_id=current_kurum_id, analysis_type='PESTLE').all()
    grouped = {key: [] for key in PESTLE_CATEGORIES}
    for item in items:
        if item.category in grouped:
            grouped[item.category].append(item)

    return render_template(
        'analysis/pestle.html',
        kurum_id=current_kurum_id,
        pestle_items=grouped,
    )


@analysis_bp.route('/tows-matrisi/<int:kurum_id>')
@login_required
def tows_matrix(kurum_id):
    current_kurum_id = _get_kurum_id()
    if current_kurum_id is None:
        return 'Kurum bilgisi bulunamadı.', 403

    swot_items = AnalysisItem.query.filter_by(kurum_id=current_kurum_id, analysis_type='SWOT').all()
    strengths = [item for item in swot_items if item.category == 'Strengths']
    weaknesses = [item for item in swot_items if item.category == 'Weaknesses']
    opportunities = [item for item in swot_items if item.category == 'Opportunities']
    threats = [item for item in swot_items if item.category == 'Threats']

    return render_template(
        'analysis/tows.html',
        kurum_id=current_kurum_id,
        strengths=strengths,
        weaknesses=weaknesses,
        opportunities=opportunities,
        threats=threats,
    )


@analysis_bp.route('/api/analiz/ekle', methods=['POST'])
@login_required
def add_analysis_item():
    current_kurum_id = _get_kurum_id()
    if current_kurum_id is None:
        return jsonify({'success': False, 'message': 'Kurum bilgisi bulunamadı.'}), 403

    data = request.get_json(silent=True) or {}
    analysis_type = str(data.get('analysis_type', '')).strip()
    category = str(data.get('category', '')).strip()
    content = str(data.get('content', '')).strip()
    score = data.get('score', 1)

    if not content:
        return jsonify({'success': False, 'message': 'İçerik boş olamaz.'}), 400

    validation_error = _validate_analysis_input(analysis_type, category, score)
    if validation_error:
        return jsonify({'success': False, 'message': validation_error}), 400

    try:
        item = AnalysisItem(
            kurum_id=current_kurum_id,
            analysis_type=analysis_type,
            category=category,
            content=content,
            score=int(score),
        )
        db.session.add(item)
        db.session.commit()
        return jsonify({
            'success': True,
            'item': {
                'id': item.id,
                'analysis_type': item.analysis_type,
                'category': item.category,
                'content': item.content,
                'score': item.score,
                'created_at': item.created_at.isoformat(),
            }
        })
    except Exception as exc:
        db.session.rollback()
        current_app.logger.error(f'Analiz kaydı eklenemedi: {exc}', exc_info=True)
        return jsonify({'success': False, 'message': 'Kayıt oluşturulamadı.'}), 500


@analysis_bp.route('/api/analiz/sil/<int:item_id>', methods=['DELETE'])
@login_required
def delete_analysis_item(item_id):
    current_kurum_id = _get_kurum_id()
    if current_kurum_id is None:
        return jsonify({'success': False, 'message': 'Kurum bilgisi bulunamadı.'}), 403

    item = AnalysisItem.query.filter_by(id=item_id, kurum_id=current_kurum_id).first()
    if not item:
        return jsonify({'success': False, 'message': 'Kayıt bulunamadı.'}), 404

    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as exc:
        db.session.rollback()
        current_app.logger.error(f'Analiz kaydı silinemedi: {exc}', exc_info=True)
        return jsonify({'success': False, 'message': 'Silme işlemi başarısız.'}), 500


@analysis_bp.route('/api/tows/olustur', methods=['POST'])
@login_required
def create_tows_strategy():
    current_kurum_id = _get_kurum_id()
    if current_kurum_id is None:
        return jsonify({'success': False, 'message': 'Kurum bilgisi bulunamadı.'}), 403

    data = request.get_json(silent=True) or {}
    strength_id = data.get('strength_id')
    opp_threat_id = data.get('opportunity_threat_id')
    strategy_text = str(data.get('strategy_text', '')).strip()
    action_plan = str(data.get('action_plan', '')).strip() or None

    if not strength_id or not opp_threat_id or not strategy_text:
        return jsonify({'success': False, 'message': 'Zorunlu alanlar eksik.'}), 400

    strength = AnalysisItem.query.filter_by(id=strength_id, kurum_id=current_kurum_id).first()
    opp_threat = AnalysisItem.query.filter_by(id=opp_threat_id, kurum_id=current_kurum_id).first()

    if not strength or not opp_threat:
        return jsonify({'success': False, 'message': 'Analiz öğeleri bulunamadı.'}), 404

    if strength.analysis_type != 'SWOT' or strength.category != 'Strengths':
        return jsonify({'success': False, 'message': 'Geçersiz güçlü yön seçimi.'}), 400

    if opp_threat.analysis_type != 'SWOT' or opp_threat.category not in {'Opportunities', 'Threats'}:
        return jsonify({'success': False, 'message': 'Geçersiz fırsat/tehdit seçimi.'}), 400

    try:
        strategy = TowsMatrix(
            kurum_id=current_kurum_id,
            strength_id=strength.id,
            opportunity_threat_id=opp_threat.id,
            strategy_text=strategy_text,
            action_plan=action_plan,
        )
        db.session.add(strategy)
        db.session.commit()
        return jsonify({'success': True, 'strategy_id': strategy.id})
    except Exception as exc:
        db.session.rollback()
        current_app.logger.error(f'TOWS stratejisi kaydedilemedi: {exc}', exc_info=True)
        return jsonify({'success': False, 'message': 'Strateji kaydedilemedi.'}), 500
