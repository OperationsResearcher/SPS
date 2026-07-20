"""
API Routes
Sprint 13-15: API ve Entegrasyonlar
RESTful API endpoints
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import db
from app.services.date_sovereign import resolve_request_year
from app.models.process import Process, ProcessKpi, KpiData
from app.services.analytics_service import AnalyticsService
from app.services.report_service import ReportService
from app.utils.validation import validate_request
from app.schemas.kpi_schemas import KpiDataSchema, ProcessKpiSchema
from app.utils.audit_logger import AuditLogger
from app.utils.db_sequence import is_pk_duplicate, sync_kpi_data_related_sequences
from datetime import datetime
from flask_babel import gettext as _

# Create API blueprint
api_bp = Blueprint('api_routes', __name__, url_prefix='/api/v1')

# ============================================
# PROCESS ENDPOINTS
# ============================================

@api_bp.route('/processes', methods=['GET'])
@login_required
def list_processes():
    """
    Süreç listesi
    
    Query Parameters:
        - page: Sayfa numarası (default: 1)
        - per_page: Sayfa başına kayıt (default: 20)
        - search: Arama terimi
        - status: Durum filtresi
    """
    page = max(1, request.args.get('page', 1, type=int))
    per_page = min(100, max(1, request.args.get('per_page', 20, type=int)))
    search = request.args.get('search', '')
    
    query = Process.query.filter_by(
        tenant_id=current_user.tenant_id,
        is_active=True
    )
    
    if search:
        query = query.filter(
            Process.name.ilike(f'%{search}%') | 
            Process.code.ilike(f'%{search}%')
        )
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'items': [p.to_dict() for p in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'per_page': per_page
    })


@api_bp.route('/processes/<int:process_id>', methods=['GET'])
@login_required
def get_process(process_id):
    """Süreç detayı"""
    process = Process.query.filter_by(
        id=process_id,
        tenant_id=current_user.tenant_id,
        is_active=True
    ).first_or_404()
    
    return jsonify(process.to_dict())


@api_bp.route('/processes/<int:process_id>/kpis', methods=['GET'])
@login_required
def list_process_kpis(process_id):
    """Süreç KPI'ları"""
    process = Process.query.filter_by(
        id=process_id,
        tenant_id=current_user.tenant_id,
        is_active=True
    ).first_or_404()
    
    kpis = ProcessKpi.query.filter_by(
        process_id=process_id,
        is_active=True
    ).all()
    
    return jsonify({
        'process': process.to_dict(),
        'kpis': [kpi.to_dict() for kpi in kpis]
    })


# ============================================
# KPI DATA ENDPOINTS
# ============================================

@api_bp.route('/kpi-data', methods=['POST'])
@login_required
@validate_request(KpiDataSchema)
def create_kpi_data(validated_data):
    """
    KPI veri girişi
    
    Body:
        {
            "process_kpi_id": 1,
            "data_date": "2024-03-13",
            "actual_value": 85.5,
            "target_value": 90.0,
            "notes": "Optional notes"
        }
    """
    # Güvenlik: process_kpi_id caller'ın tenant'ına ait olmalı (cross-tenant veri yazma önlemi).
    _owns = (
        ProcessKpi.query.join(Process, ProcessKpi.process_id == Process.id)
        .filter(ProcessKpi.id == validated_data["process_kpi_id"],
                Process.tenant_id == current_user.tenant_id)
        .first()
    )
    if not _owns:
        return jsonify({"success": False, "message": _("Erişim reddedildi.")}), 403

    # Map schema fields to model (notes->description, add year)
    create_data = {
        "process_kpi_id": validated_data["process_kpi_id"],
        "data_date": validated_data["data_date"],
        "year": validated_data["data_date"].year,
        "actual_value": str(validated_data["actual_value"]),
        "target_value": str(validated_data["target_value"]),
        "description": validated_data.get("notes"),
    }
    kpi_data = None
    for attempt in (1, 2):
        try:
            kpi_data = KpiData(**create_data)
            kpi_data.user_id = current_user.id
            db.session.add(kpi_data)
            db.session.commit()
            break
        except Exception as e:
            db.session.rollback()
            if attempt == 1 and is_pk_duplicate(e, "kpi_data"):
                sync_kpi_data_related_sequences()
                db.session.commit()
                continue
            raise

    AuditLogger.log_create("KpiData", kpi_data.id, validated_data)

    return jsonify({
        "success": True,
        "id": kpi_data.id,
        "data": kpi_data.to_dict(),
    }), 201


@api_bp.route('/kpi-data/<int:kpi_data_id>', methods=['GET'])
@login_required
def get_kpi_data(kpi_data_id):
    """KPI veri detayı"""
    kpi_data = (KpiData.query
        .join(ProcessKpi, KpiData.process_kpi_id == ProcessKpi.id)
        .join(Process, ProcessKpi.process_id == Process.id)
        .filter(KpiData.id == kpi_data_id, KpiData.is_active.is_(True), Process.tenant_id == current_user.tenant_id)
        .first_or_404())

    return jsonify(kpi_data.to_dict())


@api_bp.route('/kpi-data/<int:kpi_data_id>', methods=['PATCH'])
@login_required
def update_kpi_data(kpi_data_id):
    """KPI veri güncelleme"""
    kpi_data = (KpiData.query
        .join(ProcessKpi, KpiData.process_kpi_id == ProcessKpi.id)
        .join(Process, ProcessKpi.process_id == Process.id)
        .filter(KpiData.id == kpi_data_id, KpiData.is_active.is_(True), Process.tenant_id == current_user.tenant_id)
        .first_or_404())

    old_values = {
        'actual_value': kpi_data.actual_value,
        'target_value': kpi_data.target_value
    }
    
    data = request.get_json(silent=True) or {}
    # Update fields
    if 'actual_value' in data:
        kpi_data.actual_value = data['actual_value']
    if 'target_value' in data:
        kpi_data.target_value = data['target_value']
    if 'notes' in data:
        kpi_data.description = data['notes']

    db.session.commit()

    # Audit log
    AuditLogger.log_update('KpiData', kpi_data_id, old_values, data)
    
    return jsonify({
        'success': True,
        'data': kpi_data.to_dict()
    })


@api_bp.route('/kpi-data/<int:kpi_data_id>', methods=['DELETE'])
@login_required
def delete_kpi_data(kpi_data_id):
    """KPI veri silme (soft delete)"""
    kpi_data = (KpiData.query
        .join(ProcessKpi, KpiData.process_kpi_id == ProcessKpi.id)
        .join(Process, ProcessKpi.process_id == Process.id)
        .filter(KpiData.id == kpi_data_id, KpiData.is_active.is_(True), Process.tenant_id == current_user.tenant_id)
        .first_or_404())

    old_values = kpi_data.to_dict()
    
    kpi_data.is_active = False
    db.session.commit()
    
    # Audit log
    AuditLogger.log_delete('KpiData', kpi_data_id, old_values)
    
    return jsonify({'success': True}), 204



# ============================================
# ANALYTICS ENDPOINTS
# ============================================

@api_bp.route('/analytics/trend/<int:kpi_id>', methods=['GET'])
@login_required
def get_trend(kpi_id):
    """
    KPI trend analizi
    
    Query Parameters:
        - start_date: Başlangıç tarihi (YYYY-MM-DD)
        - end_date: Bitiş tarihi (YYYY-MM-DD)
        - frequency: daily, weekly, monthly, quarterly
    """
    start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d')
    end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d')
    frequency = request.args.get('frequency', 'monthly')
    
    kpi = (ProcessKpi.query
           .join(Process, ProcessKpi.process_id == Process.id)
           .filter(ProcessKpi.id == kpi_id, Process.tenant_id == current_user.tenant_id)
           .first_or_404())

    trend = AnalyticsService.get_performance_trend(
        process_id=kpi.process_id,
        kpi_id=kpi_id,
        start_date=start_date,
        end_date=end_date,
        frequency=frequency
    )

    return jsonify(trend)


@api_bp.route('/analytics/health/<int:process_id>', methods=['GET'])
@login_required
def get_health(process_id):
    """
    Süreç sağlık skoru
    
    Query Parameters:
        - year: Yıl (default: current year)
    """
    year = resolve_request_year()
    Process.query.filter_by(id=process_id, tenant_id=current_user.tenant_id).first_or_404()

    health = AnalyticsService.get_process_health_score(process_id, year)

    return jsonify(health)


@api_bp.route('/analytics/comparison', methods=['POST'])
@login_required
def get_comparison():
    """
    Karşılaştırmalı analiz
    
    Body:
        {
            "process_ids": [1, 2, 3],
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        }
    """
    data = request.get_json(silent=True) or {}
    start_date = datetime.strptime(data.get('start_date', ''), '%Y-%m-%d')
    end_date = datetime.strptime(data.get('end_date', ''), '%Y-%m-%d')

    # Yalnızca bu tenant'a ait process_id'leri kabul et
    raw_ids = [int(i) for i in (data.get('process_ids') or []) if str(i).isdigit()]
    valid_ids = [p.id for p in Process.query.filter(
        Process.id.in_(raw_ids), Process.tenant_id == current_user.tenant_id
    ).all()] if raw_ids else []

    comparison = AnalyticsService.get_comparative_analysis(
        process_ids=valid_ids,
        start_date=start_date,
        end_date=end_date
    )

    return jsonify(comparison)


@api_bp.route('/analytics/forecast/<int:kpi_id>', methods=['GET'])
@login_required
def get_forecast(kpi_id):
    """
    Tahminleme
    
    Query Parameters:
        - periods: Tahmin periyodu (default: 3)
        - method: moving_average, linear_trend
    """
    periods = request.args.get('periods', 3, type=int)
    method = request.args.get('method', 'moving_average')

    # Güvenlik: kpi_id caller'ın tenant'ına ait olmalı (cross-tenant veri okuma önlemi).
    ProcessKpi.query.join(Process, ProcessKpi.process_id == Process.id).filter(
        ProcessKpi.id == kpi_id, Process.tenant_id == current_user.tenant_id
    ).first_or_404()

    forecast = AnalyticsService.get_forecast(kpi_id, periods, method)
    
    return jsonify(forecast)


# ============================================
# REPORT ENDPOINTS
# ============================================

@api_bp.route('/reports/performance/<int:process_id>', methods=['GET'])
@login_required
def get_performance_report(process_id):
    """
    Performans raporu
    
    Query Parameters:
        - start_date: Başlangıç tarihi
        - end_date: Bitiş tarihi
        - format: json, excel
    """
    Process.query.filter_by(id=process_id, tenant_id=current_user.tenant_id).first_or_404()
    start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d')
    end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d')
    format = request.args.get('format', 'json')

    report = ReportService.generate_performance_report(
        process_id=process_id,
        start_date=start_date,
        end_date=end_date,
        format=format
    )
    
    if format == 'excel':
        from flask import send_file
        import io
        return send_file(
            io.BytesIO(report),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'performance_report_{process_id}.xlsx'
        )
    
    return jsonify(report)


@api_bp.route('/reports/dashboard', methods=['GET'])
@login_required
def get_dashboard_report():
    """Dashboard özet raporu"""
    year = resolve_request_year()
    
    dashboard = ReportService.generate_dashboard_report(
        tenant_id=current_user.tenant_id,
        year=year
    )
    
    return jsonify(dashboard)


# ============================================
# WEBHOOK ENDPOINTS
# ============================================

@api_bp.route('/webhooks', methods=['POST'])
@login_required
def create_webhook():
    """
    Webhook oluştur
    
    Body:
        {
            "url": "https://example.com/webhook",
            "events": ["kpi.created", "kpi.updated"],
            "secret": "optional_secret"
        }
    """
    # TODO: Webhook implementation
    return jsonify({
        'success': True,
        'message': 'Webhook created (placeholder)'
    }), 201


# ============================================
# ERROR HANDLERS
# ============================================

@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'message': 'Kaynak bulunamadı'}), 404


@api_bp.errorhandler(400)
def bad_request(error):
    return jsonify({'success': False, 'message': 'Geçersiz istek'}), 400


@api_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'message': 'Sunucu hatası'}), 500
