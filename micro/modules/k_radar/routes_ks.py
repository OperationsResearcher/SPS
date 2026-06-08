"""K-Radar — K-Süreç (KS) route'ları."""

from flask import jsonify, render_template, request
from flask_login import current_user, login_required

from platform_core import app_bp
from micro.modules.k_radar.routes_common import _can_manage_k_radar, _required_tenant_id, _safe_json


def _ks_swot_summary(tenant_id: int) -> dict:
    from app.models.process import Process, ProcessKpi, KpiData
    process_count = Process.query.filter_by(tenant_id=tenant_id, is_active=True).count()
    try:
        kpis = (
            ProcessKpi.query.join(Process)
            .filter(Process.tenant_id == tenant_id, Process.is_active.is_(True), ProcessKpi.is_active.is_(True))
            .all()
        )
        kpi_ids = [k.id for k in kpis]
        low_perf = 0
        if kpi_ids:
            rows = (
                KpiData.query
                .filter(KpiData.process_kpi_id.in_(kpi_ids), KpiData.is_active.is_(True))
                .all()
            )
            for r in rows:
                try:
                    actual = float(r.actual_value)
                    target = float(r.target_value)
                    if target > 0 and (actual / target) < 0.8:
                        low_perf += 1
                except (ValueError, TypeError):
                    pass
    except Exception:
        low_perf = 0
    return {"process_count": int(process_count or 0), "low_perf_kpi_rows": int(low_perf or 0)}


@app_bp.route("/k-radar/ks")
@login_required
def k_radar_ks():
    return render_template("platform/k_radar/ks.html", can_manage_k_radar=_can_manage_k_radar())


@app_bp.route("/k-radar/api/ks/swot-summary")
@login_required
def k_radar_api_ks_swot_summary():
    return _safe_json(lambda: jsonify({"success": True, "data": _ks_swot_summary(_required_tenant_id())}))


@app_bp.route("/k-radar/api/ks/pestle")
@login_required
def k_radar_api_ks_pestle():
    from services.k_radar_service import get_ks_extended_data
    return _safe_json(lambda: jsonify({"success": True, "data": get_ks_extended_data(_required_tenant_id()).get("pestle", {})}))


@app_bp.route("/k-radar/api/ks/tows")
@login_required
def k_radar_api_ks_tows():
    from services.k_radar_service import get_ks_extended_data
    return _safe_json(lambda: jsonify({"success": True, "data": get_ks_extended_data(_required_tenant_id()).get("tows", {})}))


@app_bp.route("/k-radar/api/ks/gap")
@login_required
def k_radar_api_ks_gap():
    from services.k_radar_service import get_ks_extended_data
    return _safe_json(lambda: jsonify({"success": True, "data": get_ks_extended_data(_required_tenant_id()).get("gap", {})}))


@app_bp.route("/k-radar/api/ks/okr")
@login_required
def k_radar_api_ks_okr():
    from services.k_radar_service import get_ks_extended_data
    return _safe_json(lambda: jsonify({"success": True, "data": get_ks_extended_data(_required_tenant_id()).get("okr", {})}))


@app_bp.route("/k-radar/api/ks/bsc")
@login_required
def k_radar_api_ks_bsc():
    from services.k_radar_service import get_ks_extended_data
    return _safe_json(lambda: jsonify({"success": True, "data": get_ks_extended_data(_required_tenant_id()).get("bsc", {})}))


@app_bp.route("/k-radar/api/ks/efqm")
@login_required
def k_radar_api_ks_efqm():
    from services.k_radar_service import get_ks_extended_data
    return _safe_json(lambda: jsonify({"success": True, "data": get_ks_extended_data(_required_tenant_id()).get("efqm", {})}))


@app_bp.route("/k-radar/api/ks/efqm-detail")
@login_required
def k_radar_api_ks_efqm_detail():
    """EFQM Modeli 2025 — 7 kriter × 3 boyut türev değerlendirmesi (1000 ölçek)."""
    from app.services.efqm_assessment import compute_efqm_assessment
    from app.services.plan_year_service import get_active_plan_year_for_user
    from flask_login import current_user
    tid = _required_tenant_id()
    py = get_active_plan_year_for_user(current_user)
    py_id = py.id if py else None
    return _safe_json(lambda: jsonify({
        "success": True,
        "data": compute_efqm_assessment(tid, py_id),
    }))


@app_bp.route("/k-radar/api/ks/hoshin")
@login_required
def k_radar_api_ks_hoshin():
    from services.k_radar_service import get_ks_extended_data
    return _safe_json(lambda: jsonify({"success": True, "data": get_ks_extended_data(_required_tenant_id()).get("hoshin", {})}))


@app_bp.route("/k-radar/api/ks/ansoff")
@login_required
def k_radar_api_ks_ansoff():
    from services.k_radar_service import get_ks_extended_data
    return _safe_json(lambda: jsonify({"success": True, "data": get_ks_extended_data(_required_tenant_id()).get("ansoff", {})}))


@app_bp.route("/k-radar/api/ks/bcg")
@login_required
def k_radar_api_ks_bcg():
    from services.k_radar_service import get_ks_extended_data
    return _safe_json(lambda: jsonify({"success": True, "data": get_ks_extended_data(_required_tenant_id()).get("bcg", {})}))


@app_bp.route("/k-radar/api/ks")
@login_required
def k_radar_api_ks():
    from services.k_radar_service import get_ks_data
    return _safe_json(lambda: jsonify({"success": True, "data": get_ks_data(_required_tenant_id())}))


# ── Gerçek Veri API'leri ──────────────────────────────────────────────────────

@app_bp.route("/k-radar/api/ks/swot-real")
@login_required
def k_radar_api_ks_swot_real():
    from services.k_radar_service import get_ks_swot_real
    from app.services.plan_year_service import get_active_plan_year_for_user
    active_py = get_active_plan_year_for_user(current_user)
    year = request.args.get("year", type=int) or (active_py.year if active_py else None)
    return _safe_json(lambda: jsonify({"success": True, "data": get_ks_swot_real(_required_tenant_id(), year)}))


@app_bp.route("/k-radar/api/ks/tows-real")
@login_required
def k_radar_api_ks_tows_real():
    from services.k_radar_service import get_ks_tows_real
    from app.services.plan_year_service import get_active_plan_year_for_user
    active_py = get_active_plan_year_for_user(current_user)
    year = request.args.get("year", type=int) or (active_py.year if active_py else None)
    return _safe_json(lambda: jsonify({"success": True, "data": get_ks_tows_real(_required_tenant_id(), year)}))


@app_bp.route("/k-radar/api/ks/pestel-real")
@login_required
def k_radar_api_ks_pestel_real():
    from services.k_radar_service import get_ks_pestel_real
    from app.services.plan_year_service import get_active_plan_year_for_user
    active_py = get_active_plan_year_for_user(current_user)
    year = request.args.get("year", type=int) or (active_py.year if active_py else None)
    return _safe_json(lambda: jsonify({"success": True, "data": get_ks_pestel_real(_required_tenant_id(), year)}))


@app_bp.route("/k-radar/api/ks/porter-real")
@login_required
def k_radar_api_ks_porter_real():
    from services.k_radar_service import get_ks_porter_real
    from app.services.plan_year_service import get_active_plan_year_for_user
    active_py = get_active_plan_year_for_user(current_user)
    year = request.args.get("year", type=int) or (active_py.year if active_py else None)
    return _safe_json(lambda: jsonify({"success": True, "data": get_ks_porter_real(_required_tenant_id(), year)}))


@app_bp.route("/k-radar/api/ks/gap-real")
@login_required
def k_radar_api_ks_gap_real():
    from services.k_radar_service import get_ks_gap_real
    from app.services.plan_year_service import get_active_plan_year_for_user
    active_py = get_active_plan_year_for_user(current_user)
    year = request.args.get("year", type=int) or (active_py.year if active_py else None)
    return _safe_json(lambda: jsonify({"success": True, "data": get_ks_gap_real(_required_tenant_id(), year)}))


@app_bp.route("/k-radar/api/ks/strateji-real")
@login_required
def k_radar_api_ks_strateji_real():
    from services.k_radar_service import get_ks_strateji_real
    return _safe_json(lambda: jsonify({"success": True, "data": get_ks_strateji_real(_required_tenant_id())}))
