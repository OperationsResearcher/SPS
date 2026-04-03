"""REST API v1 katmanı — `/api/v1/` (Micro kök)."""

from flask import jsonify, request, render_template, current_app, make_response
from flask_login import login_required, current_user

from platform_core import app_bp
from app.models import db
from app.models.process import Process, ProcessKpi, KpiData, KpiDataAudit
from app.utils.audit_logger import AuditLogger
from app.utils.db_sequence import is_pk_duplicate, sync_kpi_data_related_sequences


def _tenant_guard(process_id):
    """Süreci tenant kapsamında döndür, yoksa None."""
    return Process.query.filter_by(
        id=process_id, tenant_id=current_user.tenant_id, is_active=True
    ).first()


def _unauth():
    return jsonify({"success": False, "message": "Kimlik doğrulama gerekli."}), 401


# ── Süreç Endpoint'leri ───────────────────────────────────────────────────────

@app_bp.route("/api/v1/processes")
@login_required
def api_processes_list():
    processes = Process.query.filter_by(
        tenant_id=current_user.tenant_id, is_active=True
    ).order_by(Process.code).all()
    return jsonify({
        "success": True,
        "data": [{"id": p.id, "code": p.code, "name": p.name, "status": p.status} for p in processes],
    })


@app_bp.route("/api/v1/processes/<int:process_id>")
@login_required
def api_processes_detail(process_id):
    p = _tenant_guard(process_id)
    if not p:
        return jsonify({"success": False, "message": "Süreç bulunamadı."}), 404
    return jsonify({
        "success": True,
        "data": {
            "id": p.id, "code": p.code, "name": p.name,
            "english_name": p.english_name, "description": p.description,
            "status": p.status, "progress": p.progress,
            "document_no": p.document_no, "revision_no": p.revision_no,
            "parent_id": p.parent_id,
        },
    })


# ── KPI Veri Endpoint'leri ────────────────────────────────────────────────────

@app_bp.route("/api/v1/kpi-data", methods=["POST"])
@login_required
def api_kpi_data_create():
    data = request.get_json() or {}
    kpi_id = data.get("kpi_id")
    kpi = ProcessKpi.query.join(Process).filter(
        ProcessKpi.id == kpi_id,
        Process.tenant_id == current_user.tenant_id,
        ProcessKpi.is_active == True,
    ).first()
    if not kpi:
        return jsonify({"success": False, "message": "PG bulunamadı."}), 404
    try:
        from datetime import date
        entry = None
        for attempt in (1, 2):
            try:
                entry = KpiData(
                    process_kpi_id=kpi.id,
                    year=int(data.get("year", date.today().year)),
                    data_date=date.today(),
                    period_type=data.get("period_type", "aylik"),
                    period_no=int(data.get("period_no", 1)),
                    actual_value=str(data.get("actual_value", "")),
                    target_value=data.get("target_value"),
                    description=data.get("description"),
                    user_id=current_user.id,
                )
                db.session.add(entry)
                db.session.flush()
                db.session.add(KpiDataAudit(
                    kpi_data_id=entry.id, action_type="CREATE",
                    new_value=entry.actual_value, user_id=current_user.id,
                ))
                db.session.commit()
                break
            except Exception as e:
                db.session.rollback()
                if attempt == 1 and (
                    is_pk_duplicate(e, "kpi_data")
                    or is_pk_duplicate(e, "kpi_data_audits")
                ):
                    sync_kpi_data_related_sequences()
                    db.session.commit()
                    continue
                raise
        return jsonify({"success": True, "id": entry.id}), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[api_kpi_data_create] {e}")
        return jsonify({"success": False, "message": "Kayıt sırasında hata oluştu."}), 500


@app_bp.route("/api/v1/kpi-data/<int:entry_id>")
@login_required
def api_kpi_data_get(entry_id):
    entry = KpiData.query.join(ProcessKpi).join(Process).filter(
        KpiData.id == entry_id,
        Process.tenant_id == current_user.tenant_id,
        KpiData.is_active == True,
    ).first_or_404()
    return jsonify({
        "success": True,
        "data": {
            "id": entry.id, "kpi_id": entry.process_kpi_id,
            "year": entry.year, "data_date": str(entry.data_date),
            "actual_value": entry.actual_value, "target_value": entry.target_value,
            "period_type": entry.period_type, "period_no": entry.period_no,
        },
    })


@app_bp.route("/api/v1/kpi-data/<int:entry_id>", methods=["PATCH"])
@login_required
def api_kpi_data_update(entry_id):
    entry = KpiData.query.join(ProcessKpi).join(Process).filter(
        KpiData.id == entry_id,
        Process.tenant_id == current_user.tenant_id,
        KpiData.is_active == True,
    ).first_or_404()
    data = request.get_json() or {}
    try:
        old_val = entry.actual_value
        entry.actual_value = str(data.get("actual_value", entry.actual_value))
        entry.target_value = data.get("target_value", entry.target_value)
        entry.description  = data.get("description", entry.description)
        db.session.add(KpiDataAudit(
            kpi_data_id=entry.id, action_type="UPDATE",
            old_value=old_val, new_value=entry.actual_value, user_id=current_user.id,
        ))
        db.session.commit()
        return jsonify({"success": True, "message": "Güncellendi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[api_kpi_data_update] {e}")
        return jsonify({"success": False, "message": "Güncelleme sırasında hata oluştu."}), 500


@app_bp.route("/api/v1/kpi-data/<int:entry_id>", methods=["DELETE"])
@login_required
def api_kpi_data_delete(entry_id):
    entry = KpiData.query.join(ProcessKpi).join(Process).filter(
        KpiData.id == entry_id,
        Process.tenant_id == current_user.tenant_id,
        KpiData.is_active == True,
    ).first_or_404()
    try:
        entry.is_active = False
        db.session.add(KpiDataAudit(
            kpi_data_id=entry.id, action_type="DELETE",
            old_value=entry.actual_value, user_id=current_user.id,
        ))
        try:
            AuditLogger.log(
                action="DELETE", resource_type="KpiData",
                resource_id=entry.id,
            )
        except Exception:
            pass
        db.session.commit()
        return jsonify({"success": True, "message": "Silindi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[api_kpi_data_delete] {e}")
        return jsonify({"success": False, "message": "Silme sırasında hata oluştu."}), 500


# ── Analitik Endpoint'leri ────────────────────────────────────────────────────

@app_bp.route("/api/v1/analytics/trend/<int:process_id>")
@login_required
def api_analytics_trend(process_id):
    if not _tenant_guard(process_id):
        return jsonify({"success": False, "message": "Süreç bulunamadı."}), 404
    try:
        from app.services.analytics_service import AnalyticsService
        return jsonify({"success": True, "data": AnalyticsService.get_performance_trend(process_id)})
    except Exception as e:
        current_app.logger.error(f"[api_analytics_trend] {e}")
        return jsonify({"success": False, "message": "Veri alınamadı."}), 500


@app_bp.route("/api/v1/analytics/health/<int:process_id>")
@login_required
def api_analytics_health(process_id):
    if not _tenant_guard(process_id):
        return jsonify({"success": False, "message": "Süreç bulunamadı."}), 404
    try:
        from app.services.analytics_service import AnalyticsService
        return jsonify({"success": True, "data": AnalyticsService.get_process_health_score(process_id)})
    except Exception as e:
        current_app.logger.error(f"[api_analytics_health] {e}")
        return jsonify({"success": False, "message": "Veri alınamadı."}), 500


@app_bp.route("/api/v1/analytics/comparison", methods=["POST"])
@login_required
def api_analytics_comparison():
    data = request.get_json() or {}
    ids  = [
        p.id for p in Process.query.filter(
            Process.id.in_(data.get("process_ids", [])),
            Process.tenant_id == current_user.tenant_id,
            Process.is_active == True,
        ).all()
    ]
    try:
        from app.services.analytics_service import AnalyticsService
        return jsonify({"success": True, "data": AnalyticsService.get_comparative_analysis(ids)})
    except Exception as e:
        current_app.logger.error(f"[api_analytics_comparison] {e}")
        return jsonify({"success": False, "message": "Veri alınamadı."}), 500


@app_bp.route("/api/v1/analytics/forecast/<int:process_id>")
@login_required
def api_analytics_forecast(process_id):
    if not _tenant_guard(process_id):
        return jsonify({"success": False, "message": "Süreç bulunamadı."}), 404
    try:
        from app.services.analytics_service import AnalyticsService
        periods = request.args.get("periods", 3, type=int)
        return jsonify({"success": True, "data": AnalyticsService.get_forecast(process_id, periods=periods)})
    except Exception as e:
        current_app.logger.error(f"[api_analytics_forecast] {e}")
        return jsonify({"success": False, "message": "Veri alınamadı."}), 500


# ── Rapor Endpoint'leri ───────────────────────────────────────────────────────

@app_bp.route("/api/v1/reports/performance/<int:process_id>")
@login_required
def api_reports_performance(process_id):
    if not _tenant_guard(process_id):
        return jsonify({"success": False, "message": "Süreç bulunamadı."}), 404
    try:
        from app.services.report_service import ReportService
        return jsonify({"success": True, "data": ReportService.generate_performance_report(process_id)})
    except Exception as e:
        current_app.logger.error(f"[api_reports_performance] {e}")
        return jsonify({"success": False, "message": "Rapor oluşturulamadı."}), 500


@app_bp.route("/api/v1/reports/dashboard")
@login_required
def api_reports_dashboard():
    try:
        from app.services.report_service import ReportService
        return jsonify({"success": True, "data": ReportService.generate_dashboard_report(
            tenant_id=current_user.tenant_id
        )})
    except Exception as e:
        current_app.logger.error(f"[api_reports_dashboard] {e}")
        return jsonify({"success": False, "message": "Rapor oluşturulamadı."}), 500


# ── AI & Push Delegasyonu ─────────────────────────────────────────────────────

@app_bp.route("/api/v1/ai/recommend")
@login_required
def api_ai_recommend():
    try:
        from app.api.ai import get_recommendations
        return get_recommendations()
    except Exception as e:
        current_app.logger.error(f"[api_ai_recommend] {e}")
        return jsonify({"success": False, "message": "AI servisi kullanılamıyor."}), 503


@app_bp.route("/api/v1/push/subscribe", methods=["POST"])
@login_required
def api_push_subscribe():
    try:
        from app.api.push import subscribe
        return subscribe()
    except Exception as e:
        current_app.logger.error(f"[api_push_subscribe] {e}")
        return jsonify({"success": False, "message": "Push servisi kullanılamıyor."}), 503


# ── API Dokümantasyonu ────────────────────────────────────────────────────────

@app_bp.route("/api/docs")
@login_required
def api_docs():
    """Swagger/OpenAPI dokümantasyon sayfası."""
    endpoints = [
        {"method": "GET",    "url": "/api/v1/processes",           "desc": "Süreç listesi"},
        {"method": "GET",    "url": "/api/v1/processes/<id>",       "desc": "Süreç detayı"},
        {"method": "POST",   "url": "/api/v1/kpi-data",             "desc": "KPI veri oluştur"},
        {"method": "GET",    "url": "/api/v1/kpi-data/<id>",        "desc": "KPI veri detayı"},
        {"method": "PATCH",  "url": "/api/v1/kpi-data/<id>",        "desc": "KPI veri güncelle"},
        {"method": "DELETE", "url": "/api/v1/kpi-data/<id>",        "desc": "KPI veri soft delete"},
        {"method": "GET",    "url": "/api/v1/analytics/trend/<id>", "desc": "Trend analizi"},
        {"method": "GET",    "url": "/api/v1/analytics/health/<id>","desc": "Sağlık skoru"},
        {"method": "POST",   "url": "/api/v1/analytics/comparison", "desc": "Karşılaştırma"},
        {"method": "GET",    "url": "/api/v1/analytics/forecast/<id>","desc": "Tahmin"},
        {"method": "GET",    "url": "/api/v1/reports/performance/<id>","desc": "Performans raporu"},
        {"method": "GET",    "url": "/api/v1/reports/dashboard",    "desc": "Dashboard raporu"},
    ]
    return render_template("platform/api/docs.html", endpoints=endpoints)
