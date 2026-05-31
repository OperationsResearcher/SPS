"""Süreç ve performans analitikleri (trend, sağlık skoru, raporlar)."""

from datetime import datetime, timedelta

from flask import render_template, jsonify, request, current_app, make_response
from flask_login import login_required, current_user

from platform_core import app_bp
from app.models.process import Process, ProcessKpi


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
    """Süreçteki tüm aktif PG'ler için trend serileri döner (frontend çoklu seri çizer)."""
    Process.query.filter_by(
        id=process_id, tenant_id=current_user.tenant_id, is_active=True
    ).first_or_404()
    try:
        from app.services.analytics_service import AnalyticsService
        start_str = request.args.get("start_date")
        end_str   = request.args.get("end_date")
        frequency = request.args.get("frequency", "monthly")
        end_date   = datetime.fromisoformat(end_str) if end_str else datetime.now()
        start_date = datetime.fromisoformat(start_str) if start_str else (end_date - timedelta(days=365))

        kpis = ProcessKpi.query.filter_by(process_id=process_id, is_active=True).all()
        series = []
        first_dir = None
        for k in kpis:
            try:
                d = AnalyticsService.get_performance_trend(
                    process_id, kpi_id=k.id, start_date=start_date,
                    end_date=end_date, frequency=frequency
                )
            except Exception as _e:
                current_app.logger.warning(f"[analiz_api_trend] kpi {k.id} atlandı: {_e}")
                continue
            vals = d.get("actual_values") or []
            if not vals:
                continue
            # Trend yönü (basit ilk-son karşılaştırması)
            direction = "flat"
            if len(vals) >= 2 and vals[0] is not None and vals[-1] is not None:
                if vals[-1] > vals[0] * 1.02: direction = "up"
                elif vals[-1] < vals[0] * 0.98: direction = "down"
            if first_dir is None:
                first_dir = direction
            series.append({
                "kpi_id": k.id,
                "kpi_name": k.name,
                "labels": d.get("dates") or [],
                "values": vals,
                "targets": d.get("target_values") or [],
                "direction": direction,
            })
        return jsonify({"success": True, "data": {
            "series": series,
            "direction": first_dir or "flat",
            "kpi_count": len(series),
        }})
    except Exception as e:
        current_app.logger.error(f"[analiz_api_trend] {e}", exc_info=True)
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
        # Frontend `data.score` bekliyor — service `overall_score` döndürür
        result["score"] = result.get("overall_score", 0)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        current_app.logger.error(f"[analiz_api_health] {e}", exc_info=True)
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
        end_str = request.args.get("end_date")
        start_str = request.args.get("start_date")
        end_date   = datetime.fromisoformat(end_str) if end_str else datetime.now()
        start_date = datetime.fromisoformat(start_str) if start_str else (end_date - timedelta(days=365))
        result = ReportService.generate_performance_report(
            process_id, start_date=start_date, end_date=end_date, format=fmt
        )
        if fmt == "excel" and isinstance(result, (bytes, bytearray)):
            response = make_response(bytes(result))
            response.headers["Content-Type"] = (
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            response.headers["Content-Disposition"] = (
                f"attachment; filename=rapor_{process_id}.xlsx"
            )
            return response
        return jsonify({"success": True, "data": result})
    except Exception as e:
        current_app.logger.error(f"[analiz_api_report] {e}", exc_info=True)
        return jsonify({"success": False, "message": "Rapor oluşturulamadı."}), 500


# ── Anomali Tespiti ───────────────────────────────────────────────────────────

@app_bp.route("/analiz/api/anomalies")
@login_required
def analiz_api_anomalies():
    """Tenant geneli (veya tek süreç) için tüm aktif PG'lerde anomali tarar."""
    try:
        from app.services.anomaly_service import AnomalyService
        svc = AnomalyService()

        process_id = request.args.get("process_id", type=int)
        method     = request.args.get("method", "zscore")

        # Hedef PG kümesi: ya tek süreç ya tenant geneli
        kpi_q = ProcessKpi.query.join(Process, ProcessKpi.process_id == Process.id).filter(
            Process.tenant_id == current_user.tenant_id,
            Process.is_active.is_(True),
            ProcessKpi.is_active.is_(True),
        )
        if process_id:
            Process.query.filter_by(
                id=process_id, tenant_id=current_user.tenant_id, is_active=True
            ).first_or_404()
            kpi_q = kpi_q.filter(ProcessKpi.process_id == process_id)
        kpis = kpi_q.all()

        items = []
        scanned = 0
        for k in kpis:
            try:
                r = svc.detect_anomalies(k.id, method=method)
            except Exception as _e:
                current_app.logger.warning(f"[analiz_api_anomalies] kpi {k.id} atlandı: {_e}")
                continue
            scanned += 1
            if not r or not r.get("success"):
                continue
            for an in (r.get("anomalies") or []):
                items.append({
                    "kpi_id": k.id,
                    "kpi_name": k.name,
                    "process_id": k.process_id,
                    "value": an.get("value"),
                    "date": an.get("date"),
                    "score": an.get("score"),
                    "type": an.get("type"),
                    "description": an.get("description") or an.get("message"),
                })

        return jsonify({"success": True, "data": {
            "anomalies": items,
            "kpis_scanned": scanned,
            "kpis_total": len(kpis),
            "method": method,
        }})
    except Exception as e:
        current_app.logger.error(f"[analiz_api_anomalies] {e}", exc_info=True)
        return jsonify({"success": False, "message": "Anomali verisi alınamadı."}), 500
