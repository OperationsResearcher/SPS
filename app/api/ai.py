"""
AI & ML API Routes
Sprint 16-18: AI ve Otomasyon
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.services.ml_service import MLService
from app.services.anomaly_service import AnomalyService
from app.services.recommendation_service import RecommendationService
from app.services.automated_reporting_service import AutomatedReportingService

ai_bp = Blueprint('ai_api', __name__, url_prefix='/api/ai')

# Service instances
ml_service = MLService()
anomaly_service = AnomalyService()
recommendation_service = RecommendationService()
reporting_service = AutomatedReportingService()


@ai_bp.route('/forecast/<int:kpi_id>', methods=['GET'])
@login_required
def forecast_kpi(kpi_id):
    """KPI tahmini"""
    periods = request.args.get('periods', 3, type=int)
    result = ml_service.forecast_kpi(kpi_id, periods)
    return jsonify(result)


@ai_bp.route('/achievement-probability/<int:kpi_id>', methods=['GET'])
@login_required
def achievement_probability(kpi_id):
    """Hedef başarı olasılığı"""
    target = request.args.get('target', type=float)
    result = ml_service.calculate_achievement_probability(kpi_id, target)
    return jsonify(result)


@ai_bp.route('/seasonality/<int:kpi_id>', methods=['GET'])
@login_required
def detect_seasonality(kpi_id):
    """Mevsimsellik analizi"""
    result = ml_service.detect_seasonality(kpi_id)
    return jsonify(result)


@ai_bp.route('/anomalies/<int:kpi_id>', methods=['GET'])
@login_required
def detect_anomalies(kpi_id):
    """Anomali tespiti"""
    method = request.args.get('method', 'zscore')
    threshold = request.args.get('threshold', 2.5, type=float)
    result = anomaly_service.detect_anomalies(kpi_id, method, threshold)
    return jsonify(result)


@ai_bp.route('/recommendations/process/<int:process_id>', methods=['GET'])
@login_required
def process_recommendations(process_id):
    """Süreç önerileri"""
    result = recommendation_service.get_process_recommendations(process_id)
    return jsonify(result)


@ai_bp.route('/insights', methods=['GET'])
@login_required
def smart_insights():
    """Akıllı insights"""
    result = recommendation_service.get_smart_insights(current_user.tenant_id)
    return jsonify(result)


@ai_bp.route('/reports/daily', methods=['GET'])
@login_required
def daily_digest():
    """Günlük özet raporu"""
    result = reporting_service.generate_daily_digest(current_user.tenant_id)
    return jsonify(result)


@ai_bp.route('/reports/weekly', methods=['GET'])
@login_required
def weekly_summary():
    """Haftalık özet"""
    result = reporting_service.generate_weekly_summary(current_user.tenant_id)
    return jsonify(result)


@ai_bp.route('/reports/monthly', methods=['GET'])
@login_required
def monthly_report():
    """Aylık rapor"""
    result = reporting_service.generate_monthly_report(current_user.tenant_id)
    return jsonify(result)
