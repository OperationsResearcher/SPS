"""Süreç ve performans analitikleri (trend, sağlık skoru, raporlar)."""

from flask import render_template, jsonify, request, current_app, make_response
from flask_login import login_required, current_user

from platform_core import app_bp
from app.models.process import Process


@app_bp.route("/analiz")
@login_required
def analiz():
    """Analitik özet — tenant süreçleri üzerinden."""
    processes = (
        Process.query
        .filter_by(tenant_id=current_user.tenant_id, is_active=True)
        .order_by(Process.code)
        .all()
    )
    return render_template("platform/analiz/index.html", processes=processes)


# ── Trend Analizi ─────────────────────────────────────────────────────────────

@app_bp.route("/analiz/api/trend/<int:process_id>")
@login_required
def analiz_api_trend(process_id):
    Process.query.filter_by(
        id=process_id, tenant_id=current_user.tenant_id, is_active=True
    ).first_or_404()
    try:
        from app.services.analytics_service import AnalyticsService
        start_date = request.args.get("start_date")
        end_date   = request.args.get("end_date")
        frequency  = request.args.get("frequency", "monthly")
        result = AnalyticsService.get_performance_trend(
            process_id, start_date=start_date, end_date=end_date, frequency=frequency
        )
        return jsonify({"success": True, "data": result})
    except Exception as e:
        current_app.logger.error(f"[analiz_api_trend] {e}")
        return jsonify({"success": False, "message": "Trend verisi alınamadı."}), 500


# ── Sağlık Skoru ──────────────────────────────────────────────────────────────

@app_bp.route("/analiz/api/health/<int:process_id>")
@login_required
def analiz_api_health(process_id):
    Process.query.filter_by(
        id=process_id, tenant_id=current_user.tenant_id, is_active=True
    ).first_or_404()
    try:
        from app.services.analytics_service import AnalyticsService
        result = AnalyticsService.get_process_health_score(process_id)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        current_app.logger.error(f"[analiz_api_health] {e}")
        return jsonify({"success": False, "message": "Sağlık skoru alınamadı."}), 500


# ── Tahmin Analizi ────────────────────────────────────────────────────────────

@app_bp.route("/analiz/api/forecast/<int:process_id>")
@login_required
def analiz_api_forecast(process_id):
    Process.query.filter_by(
        id=process_id, tenant_id=current_user.tenant_id, is_active=True
    ).first_or_404()
    try:
        from app.services.analytics_service import AnalyticsService
        periods = request.args.get("periods", 3, type=int)
        method  = request.args.get("method", "linear")
        result  = AnalyticsService.get_forecast(process_id, periods=periods, method=method)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        current_app.logger.error(f"[analiz_api_forecast] {e}")
        return jsonify({"success": False, "message": "Tahmin verisi alınamadı."}), 500


# ── Karşılaştırma Analizi ─────────────────────────────────────────────────────

@app_bp.route("/analiz/api/comparison", methods=["POST"])
@login_required
def analiz_api_comparison():
    data = request.get_json() or {}
    process_ids = data.get("process_ids", [])
    # Tenant izolasyonu: yalnızca kendi tenant süreçleri
    valid_ids = [
        p.id for p in Process.query.filter(
            Process.id.in_(process_ids),
            Process.tenant_id == current_user.tenant_id,
            Process.is_active == True,
        ).all()
    ]
    try:
        from app.services.analytics_service import AnalyticsService
        result = AnalyticsService.get_comparative_analysis(valid_ids)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        current_app.logger.error(f"[analiz_api_comparison] {e}")
        return jsonify({"success": False, "message": "Karşılaştırma verisi alınamadı."}), 500


# ── Performans Raporu ─────────────────────────────────────────────────────────

@app_bp.route("/analiz/api/report/<int:process_id>")
@login_required
def analiz_api_report(process_id):
    Process.query.filter_by(
        id=process_id, tenant_id=current_user.tenant_id, is_active=True
    ).first_or_404()
    fmt = request.args.get("format", "json")
    try:
        from app.services.report_service import ReportService
        result = ReportService.generate_performance_report(process_id)
        if fmt == "excel":
            response = make_response(result)
            response.headers["Content-Type"] = (
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            response.headers["Content-Disposition"] = (
                f"attachment; filename=rapor_{process_id}.xlsx"
            )
            return response
        return jsonify({"success": True, "data": result})
    except Exception as e:
        current_app.logger.error(f"[analiz_api_report] {e}")
        return jsonify({"success": False, "message": "Rapor oluşturulamadı."}), 500


# ── Anomali Tespiti ───────────────────────────────────────────────────────────

@app_bp.route("/analiz/api/anomalies")
@login_required
def analiz_api_anomalies():
    try:
        from app.services.anomaly_service import AnomalyService
        result = AnomalyService.detect_anomalies(tenant_id=current_user.tenant_id)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        current_app.logger.error(f"[analiz_api_anomalies] {e}")
        return jsonify({"success": False, "message": "Anomali verisi alınamadı."}), 500
