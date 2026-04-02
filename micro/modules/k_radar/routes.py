"""K-Radar route'lari (hub + alt radarlar)."""

from flask import current_app, flash, jsonify, redirect, render_template, request, url_for
import csv
import io
from datetime import datetime, timezone
from flask_login import current_user, login_required
from sqlalchemy import text

from platform_core import app_bp
from app.models import db
from app.models.process import Process
from app.models.k_radar_domain import ProcessMaturity, StakeholderMap
from models.project import Project, Task, TaskDependency
from services.k_radar_service import (
    get_cross_heatmap_data,
    get_hub_summary,
    get_kp_data,
    get_kpr_data,
    get_recommendation_states,
    get_recommendations_from_summary,
    get_ks_data,
    recommendation_key,
    set_recommendation_state,
    list_recommendation_action_history,
    get_ks_extended_data,
    get_kp_extended_data,
    get_kpr_extended_data,
    get_cross_extended_data,
    get_recommendation_triggers,
)
from services import k_radar_scheduler_service as _scheduler


_WRITE_ROLES = {"Admin", "tenant_admin", "executive_manager"}


def _can_manage_k_radar() -> bool:
    role_name = current_user.role.name if current_user.role else ""
    return role_name in _WRITE_ROLES


def _forbidden_json():
    return jsonify({"success": False, "message": "Yetkisiz"}), 403


def _required_tenant_id() -> int:
    tid = getattr(current_user, "tenant_id", None)
    if not tid:
        raise ValueError("Kullanici tenant baglaminda degil.")
    return int(tid)


def _safe_json(callable_fn):
    try:
        return callable_fn()
    except Exception as e:
        current_app.logger.exception("[k_radar] %s", e)
        return jsonify({"success": False, "message": "Islem sirasinda hata olustu."}), 500


def _ks_swot_summary(tenant_id: int) -> dict:
    process_count = Process.query.filter_by(tenant_id=tenant_id, is_active=True).count()
    low_perf = db.session.execute(
        text(
            """
            SELECT COUNT(*) FROM kpi_data kd
            JOIN process_kpis pk ON pk.id = kd.process_kpi_id
            JOIN processes p ON p.id = pk.process_id
            WHERE p.tenant_id=:tid AND p.is_active=true AND kd.is_active=true
              AND NULLIF(kd.target_value, '') IS NOT NULL
              AND NULLIF(kd.actual_value, '') IS NOT NULL
              AND (CAST(kd.actual_value AS FLOAT) / NULLIF(CAST(kd.target_value AS FLOAT),0)) < 0.8
            """
        ),
        {"tid": tenant_id},
    ).scalar()
    return {"process_count": int(process_count or 0), "low_perf_kpi_rows": int(low_perf or 0)}


@app_bp.route("/k-radar")
@login_required
def k_radar_hub():
    schedule = _scheduler.load_schedule(current_app)
    return render_template(
        "platform/k_radar/index.html",
        can_manage_k_radar=_can_manage_k_radar(),
        schedule=schedule,
    )


@app_bp.route("/k-radar/ks")
@login_required
def k_radar_ks():
    return render_template("platform/k_radar/ks.html", can_manage_k_radar=_can_manage_k_radar())


@app_bp.route("/k-radar/ks/swot")
@login_required
def k_radar_ks_swot():
    tenant_id = _required_tenant_id()
    return render_template(
        "platform/k_radar/ks_swot.html",
        can_manage_k_radar=_can_manage_k_radar(),
        summary=_ks_swot_summary(tenant_id),
    )


@app_bp.route("/k-radar/ks/pestle")
@login_required
def k_radar_ks_pestle():
    return render_template("platform/k_radar/ks_pestle.html", can_manage_k_radar=_can_manage_k_radar())


@app_bp.route("/k-radar/ks/tows")
@login_required
def k_radar_ks_tows():
    return render_template("platform/k_radar/ks_tows.html", can_manage_k_radar=_can_manage_k_radar())


@app_bp.route("/k-radar/ks/gap")
@login_required
def k_radar_ks_gap():
    return render_template("platform/k_radar/ks_gap.html", can_manage_k_radar=_can_manage_k_radar())


@app_bp.route("/k-radar/ks/okr")
@login_required
def k_radar_ks_okr():
    return render_template("platform/k_radar/ks_okr.html", can_manage_k_radar=_can_manage_k_radar())


@app_bp.route("/k-radar/ks/bsc")
@login_required
def k_radar_ks_bsc():
    return render_template("platform/k_radar/ks_bsc.html", can_manage_k_radar=_can_manage_k_radar())


@app_bp.route("/k-radar/ks/efqm")
@login_required
def k_radar_ks_efqm():
    return render_template("platform/k_radar/ks_efqm.html", can_manage_k_radar=_can_manage_k_radar())


@app_bp.route("/k-radar/ks/hoshin")
@login_required
def k_radar_ks_hoshin():
    return render_template("platform/k_radar/ks_hoshin.html", can_manage_k_radar=_can_manage_k_radar())


@app_bp.route("/k-radar/ks/ansoff")
@login_required
def k_radar_ks_ansoff():
    return render_template("platform/k_radar/ks_ansoff.html", can_manage_k_radar=_can_manage_k_radar())


@app_bp.route("/k-radar/ks/bcg")
@login_required
def k_radar_ks_bcg():
    return render_template("platform/k_radar/ks_bcg.html", can_manage_k_radar=_can_manage_k_radar())


@app_bp.route("/k-radar/kp")
@login_required
def k_radar_kp():
    return render_template("platform/k_radar/kp.html", can_manage_k_radar=_can_manage_k_radar())


@app_bp.route("/k-radar/kp/darbogaz")
@login_required
def k_radar_kp_darbogaz():
    return render_template("platform/k_radar/kp_darbogaz.html", can_manage_k_radar=_can_manage_k_radar())


@app_bp.route("/k-radar/kp/deger-zinciri")
@login_required
def k_radar_kp_deger_zinciri():
    return render_template("platform/k_radar/kp_deger_zinciri.html", can_manage_k_radar=_can_manage_k_radar())


@app_bp.route("/k-radar/kp/pareto")
@login_required
def k_radar_kp_pareto():
    return render_template("platform/k_radar/kp_pareto.html", can_manage_k_radar=_can_manage_k_radar())


@app_bp.route("/k-radar/kp/sla")
@login_required
def k_radar_kp_sla():
    return render_template("platform/k_radar/kp_sla.html", can_manage_k_radar=_can_manage_k_radar())


@app_bp.route("/k-radar/kp/benchmark")
@login_required
def k_radar_kp_benchmark():
    return render_template("platform/k_radar/kp_benchmark.html", can_manage_k_radar=_can_manage_k_radar())


@app_bp.route("/k-radar/kp/oee")
@login_required
def k_radar_kp_oee():
    return render_template("platform/k_radar/kp_oee.html", can_manage_k_radar=_can_manage_k_radar())


@app_bp.route("/k-radar/kp/vsm")
@login_required
def k_radar_kp_vsm():
    return render_template("platform/k_radar/kp_vsm.html", can_manage_k_radar=_can_manage_k_radar())


@app_bp.route("/k-radar/kp/kapasite")
@login_required
def k_radar_kp_kapasite():
    return render_template("platform/k_radar/kp_kapasite.html", can_manage_k_radar=_can_manage_k_radar())


@app_bp.route("/k-radar/kp/olgunluk")
@login_required
def k_radar_kp_olgunluk():
    tenant_id = _required_tenant_id()
    rows = (
        ProcessMaturity.query.filter_by(tenant_id=tenant_id, is_active=True)
        .order_by(ProcessMaturity.updated_at.desc())
        .limit(100)
        .all()
    )
    processes = (
        Process.query.filter_by(tenant_id=tenant_id, is_active=True)
        .order_by(Process.code, Process.name)
        .all()
    )
    return render_template(
        "platform/k_radar/kp_olgunluk.html",
        can_manage_k_radar=_can_manage_k_radar(),
        rows=rows,
        processes=processes,
    )


@app_bp.route("/k-radar/kp/olgunluk/ekle", methods=["POST"])
@login_required
def k_radar_kp_olgunluk_ekle():
    if not _can_manage_k_radar():
        return render_template("platform/errors/403.html"), 403
    tenant_id = _required_tenant_id()
    process_id = request.form.get("process_id", type=int)
    maturity_level = request.form.get("maturity_level", type=int)
    dimension = (request.form.get("dimension") or "").strip() or None
    if not process_id or not maturity_level:
        flash("Süreç ve seviye zorunludur.", "danger")
        return redirect(url_for("app_bp.k_radar_kp_olgunluk"))
    row = ProcessMaturity(
        tenant_id=tenant_id,
        process_id=process_id,
        maturity_level=max(1, min(5, maturity_level)),
        dimension=dimension,
        assessed_by=current_user.id,
        assessed_at=datetime.now(timezone.utc),
        is_active=True,
    )
    db.session.add(row)
    db.session.commit()
    flash("Olgunluk kaydı eklendi.", "success")
    return redirect(url_for("app_bp.k_radar_kp_olgunluk"))


@app_bp.route("/k-radar/kpr")
@login_required
def k_radar_kpr():
    return render_template("platform/k_radar/kpr.html", can_manage_k_radar=_can_manage_k_radar())


@app_bp.route("/k-radar/kpr/cpm")
@login_required
def k_radar_kpr_cpm():
    tenant_id = _required_tenant_id()
    project_id = request.args.get("project_id", type=int)
    projects = Project.query.filter_by(tenant_id=tenant_id, is_archived=False).order_by(Project.name).all()
    analysis = None
    if project_id:
        tasks = Task.query.filter_by(project_id=project_id, is_archived=False).all()
        dep_rows = TaskDependency.query.filter_by(project_id=project_id).all()
        predecessor_map = {t.id: set() for t in tasks}
        for d in dep_rows:
            predecessor_map.setdefault(d.successor_id, set()).add(d.predecessor_id)
        critical = [t for t in tasks if len(predecessor_map.get(t.id, set())) == 0]
        analysis = {
            "task_count": len(tasks),
            "dependency_count": len(dep_rows),
            "critical_starts": [{"id": t.id, "title": t.title} for t in critical[:15]],
        }
    return render_template(
        "platform/k_radar/kpr_cpm.html",
        can_manage_k_radar=_can_manage_k_radar(),
        projects=projects,
        selected_project_id=project_id,
        analysis=analysis,
    )


@app_bp.route("/k-radar/kpr/evm")
@login_required
def k_radar_kpr_evm():
    return render_template("platform/k_radar/kpr_evm.html", can_manage_k_radar=_can_manage_k_radar())


@app_bp.route("/k-radar/kpr/risk")
@login_required
def k_radar_kpr_risk():
    return render_template("platform/k_radar/kpr_risk.html", can_manage_k_radar=_can_manage_k_radar())


@app_bp.route("/k-radar/kpr/kaynak-kapasite")
@login_required
def k_radar_kpr_kaynak_kapasite():
    return render_template("platform/k_radar/kpr_kaynak_kapasite.html", can_manage_k_radar=_can_manage_k_radar())


@app_bp.route("/k-radar/kpr/gantt")
@login_required
def k_radar_kpr_gantt():
    return render_template("platform/k_radar/kpr_gantt.html", can_manage_k_radar=_can_manage_k_radar())


@app_bp.route("/k-radar/cross")
@login_required
def k_radar_cross():
    return render_template("platform/k_radar/cross.html", can_manage_k_radar=_can_manage_k_radar())


@app_bp.route("/k-radar/cross/paydas")
@login_required
def k_radar_cross_paydas():
    tenant_id = _required_tenant_id()
    rows = (
        StakeholderMap.query.filter_by(tenant_id=tenant_id, is_active=True)
        .order_by(StakeholderMap.updated_at.desc())
        .limit(200)
        .all()
    )


@app_bp.route("/k-radar/cross/rekabet")
@login_required
def k_radar_cross_rekabet():
    return render_template("platform/k_radar/cross_rekabet.html", can_manage_k_radar=_can_manage_k_radar())


@app_bp.route("/k-radar/cross/a3")
@login_required
def k_radar_cross_a3():
    return render_template("platform/k_radar/cross_a3.html", can_manage_k_radar=_can_manage_k_radar())


@app_bp.route("/k-radar/cross/anket")
@login_required
def k_radar_cross_anket():
    return render_template("platform/k_radar/cross_anket.html", can_manage_k_radar=_can_manage_k_radar())
    return render_template(
        "platform/k_radar/cross_paydas.html",
        can_manage_k_radar=_can_manage_k_radar(),
        rows=rows,
    )


@app_bp.route("/k-radar/cross/paydas/ekle", methods=["POST"])
@login_required
def k_radar_cross_paydas_ekle():
    if not _can_manage_k_radar():
        return render_template("platform/errors/403.html"), 403
    tenant_id = _required_tenant_id()
    name = (request.form.get("name") or "").strip()
    role = (request.form.get("role") or "").strip() or None
    strategy = (request.form.get("strategy") or "").strip() or None
    influence = request.form.get("influence", type=int)
    interest = request.form.get("interest", type=int)
    if not name:
        flash("Paydaş adı zorunludur.", "danger")
        return redirect(url_for("app_bp.k_radar_cross_paydas"))
    row = StakeholderMap(
        tenant_id=tenant_id,
        name=name,
        role=role,
        strategy=strategy,
        influence=max(1, min(5, influence or 3)),
        interest=max(1, min(5, interest or 3)),
        is_active=True,
    )
    db.session.add(row)
    db.session.commit()
    flash("Paydaş kaydı eklendi.", "success")
    return redirect(url_for("app_bp.k_radar_cross_paydas"))


@app_bp.route("/k-radar/api/ks/swot-summary")
@login_required
def k_radar_api_ks_swot_summary():
    return _safe_json(lambda: jsonify({"success": True, "data": _ks_swot_summary(_required_tenant_id())}))


@app_bp.route("/k-radar/api/ks/pestle")
@login_required
def k_radar_api_ks_pestle():
    return _safe_json(lambda: jsonify({"success": True, "data": get_ks_extended_data(_required_tenant_id()).get("pestle", {})}))


@app_bp.route("/k-radar/api/ks/tows")
@login_required
def k_radar_api_ks_tows():
    return _safe_json(lambda: jsonify({"success": True, "data": get_ks_extended_data(_required_tenant_id()).get("tows", {})}))


@app_bp.route("/k-radar/api/ks/gap")
@login_required
def k_radar_api_ks_gap():
    return _safe_json(lambda: jsonify({"success": True, "data": get_ks_extended_data(_required_tenant_id()).get("gap", {})}))


@app_bp.route("/k-radar/api/ks/okr")
@login_required
def k_radar_api_ks_okr():
    return _safe_json(lambda: jsonify({"success": True, "data": get_ks_extended_data(_required_tenant_id()).get("okr", {})}))


@app_bp.route("/k-radar/api/ks/bsc")
@login_required
def k_radar_api_ks_bsc():
    return _safe_json(lambda: jsonify({"success": True, "data": get_ks_extended_data(_required_tenant_id()).get("bsc", {})}))


@app_bp.route("/k-radar/api/ks/efqm")
@login_required
def k_radar_api_ks_efqm():
    return _safe_json(lambda: jsonify({"success": True, "data": get_ks_extended_data(_required_tenant_id()).get("efqm", {})}))


@app_bp.route("/k-radar/api/ks/hoshin")
@login_required
def k_radar_api_ks_hoshin():
    return _safe_json(lambda: jsonify({"success": True, "data": get_ks_extended_data(_required_tenant_id()).get("hoshin", {})}))


@app_bp.route("/k-radar/api/ks/ansoff")
@login_required
def k_radar_api_ks_ansoff():
    return _safe_json(lambda: jsonify({"success": True, "data": get_ks_extended_data(_required_tenant_id()).get("ansoff", {})}))


@app_bp.route("/k-radar/api/ks/bcg")
@login_required
def k_radar_api_ks_bcg():
    return _safe_json(lambda: jsonify({"success": True, "data": get_ks_extended_data(_required_tenant_id()).get("bcg", {})}))


@app_bp.route("/k-radar/api/kp/olgunluk")
@login_required
def k_radar_api_kp_olgunluk():
    def _build():
        tenant_id = _required_tenant_id()
        rows = (
            ProcessMaturity.query.filter_by(tenant_id=tenant_id, is_active=True)
            .order_by(ProcessMaturity.updated_at.desc())
            .limit(200)
            .all()
        )
        return jsonify(
            {
                "success": True,
                "data": {
                    "rows": [
                        {
                            "id": r.id,
                            "process_id": r.process_id,
                            "maturity_level": r.maturity_level,
                            "dimension": r.dimension,
                            "updated_at": r.updated_at.isoformat() if r.updated_at else None,
                        }
                        for r in rows
                    ]
                },
            }
        )
    return _safe_json(_build)


@app_bp.route("/k-radar/api/kp/darbogaz")
@login_required
def k_radar_api_kp_darbogaz():
    return _safe_json(lambda: jsonify({"success": True, "data": get_kp_extended_data(_required_tenant_id()).get("darbogaz", {})}))


@app_bp.route("/k-radar/api/kp/deger-zinciri")
@login_required
def k_radar_api_kp_deger_zinciri():
    return _safe_json(lambda: jsonify({"success": True, "data": get_kp_extended_data(_required_tenant_id()).get("deger_zinciri", {})}))


@app_bp.route("/k-radar/api/kp/pareto")
@login_required
def k_radar_api_kp_pareto():
    return _safe_json(lambda: jsonify({"success": True, "data": get_kp_extended_data(_required_tenant_id()).get("pareto", {})}))


@app_bp.route("/k-radar/api/kp/sla")
@login_required
def k_radar_api_kp_sla():
    return _safe_json(lambda: jsonify({"success": True, "data": get_kp_extended_data(_required_tenant_id()).get("sla", {})}))


@app_bp.route("/k-radar/api/kp/benchmark")
@login_required
def k_radar_api_kp_benchmark():
    return _safe_json(lambda: jsonify({"success": True, "data": get_kp_extended_data(_required_tenant_id()).get("benchmark", {})}))


@app_bp.route("/k-radar/api/kp/oee")
@login_required
def k_radar_api_kp_oee():
    return _safe_json(lambda: jsonify({"success": True, "data": get_kp_extended_data(_required_tenant_id()).get("oee", {})}))


@app_bp.route("/k-radar/api/kp/vsm")
@login_required
def k_radar_api_kp_vsm():
    return _safe_json(lambda: jsonify({"success": True, "data": get_kp_extended_data(_required_tenant_id()).get("vsm", {})}))


@app_bp.route("/k-radar/api/kp/kapasite")
@login_required
def k_radar_api_kp_kapasite():
    return _safe_json(lambda: jsonify({"success": True, "data": get_kp_extended_data(_required_tenant_id()).get("kapasite", {})}))


@app_bp.route("/k-radar/api/kp/olgunluk", methods=["POST"])
@login_required
def k_radar_api_kp_olgunluk_create():
    if not _can_manage_k_radar():
        return _forbidden_json()
    payload = request.get_json(silent=True) or {}
    process_id = payload.get("process_id")
    maturity_level = payload.get("maturity_level")
    dimension = (payload.get("dimension") or "").strip() or None
    if not process_id or not maturity_level:
        return jsonify({"success": False, "message": "process_id ve maturity_level zorunlu"}), 400
    def _create():
        row = ProcessMaturity(
            tenant_id=_required_tenant_id(),
            process_id=int(process_id),
            maturity_level=max(1, min(5, int(maturity_level))),
            dimension=dimension,
            assessed_by=current_user.id,
            assessed_at=datetime.now(timezone.utc),
            is_active=True,
        )
        db.session.add(row)
        db.session.commit()
        return jsonify({"success": True, "data": {"id": row.id}})
    return _safe_json(_create)


@app_bp.route("/k-radar/api/kp/olgunluk/<int:row_id>", methods=["PUT"])
@login_required
def k_radar_api_kp_olgunluk_update(row_id: int):
    if not _can_manage_k_radar():
        return _forbidden_json()
    payload = request.get_json(silent=True) or {}
    maturity_level = payload.get("maturity_level")
    dimension = (payload.get("dimension") or "").strip() or None
    if maturity_level is None:
        return jsonify({"success": False, "message": "maturity_level zorunlu"}), 400

    def _update():
        row = ProcessMaturity.query.filter_by(id=row_id, tenant_id=_required_tenant_id(), is_active=True).first()
        if not row:
            return jsonify({"success": False, "message": "Kayıt bulunamadı"}), 404
        row.maturity_level = max(1, min(5, int(maturity_level)))
        row.dimension = dimension
        row.assessed_by = current_user.id
        row.assessed_at = datetime.now(timezone.utc)
        db.session.commit()
        return jsonify({"success": True, "data": {"id": row.id}})

    return _safe_json(_update)


@app_bp.route("/k-radar/api/kp/olgunluk/<int:row_id>", methods=["DELETE"])
@login_required
def k_radar_api_kp_olgunluk_delete(row_id: int):
    if not _can_manage_k_radar():
        return _forbidden_json()

    def _delete():
        row = ProcessMaturity.query.filter_by(id=row_id, tenant_id=_required_tenant_id(), is_active=True).first()
        if not row:
            return jsonify({"success": False, "message": "Kayıt bulunamadı"}), 404
        row.is_active = False
        db.session.commit()
        return jsonify({"success": True, "data": {"id": row.id}})

    return _safe_json(_delete)


@app_bp.route("/k-radar/api/kpr/cpm")
@login_required
def k_radar_api_kpr_cpm():
    def _build():
        tenant_id = _required_tenant_id()
        project_id = request.args.get("project_id", type=int)
        if not project_id:
            return jsonify({"success": True, "data": {"task_count": 0, "dependency_count": 0, "critical_starts": []}})
        project = Project.query.filter_by(id=project_id, tenant_id=tenant_id, is_archived=False).first()
        if not project:
            return jsonify({"success": False, "message": "Proje bulunamadi"}), 404
        tasks = Task.query.filter_by(project_id=project_id, is_archived=False).all()
        dep_rows = TaskDependency.query.filter_by(project_id=project_id).all()
        predecessor_map = {t.id: set() for t in tasks}
        successor_count = {t.id: 0 for t in tasks}
        for d in dep_rows:
            predecessor_map.setdefault(d.successor_id, set()).add(d.predecessor_id)
            successor_count[d.predecessor_id] = successor_count.get(d.predecessor_id, 0) + 1
        critical = [t for t in tasks if len(predecessor_map.get(t.id, set())) == 0]
        critical_sorted = sorted(critical, key=lambda x: successor_count.get(x.id, 0), reverse=True)
        return jsonify(
            {
                "success": True,
                "data": {
                    "task_count": len(tasks),
                    "dependency_count": len(dep_rows),
                    "critical_starts": [{"id": t.id, "title": t.title} for t in critical_sorted[:20]],
                },
            }
        )
    return _safe_json(_build)


@app_bp.route("/k-radar/api/kpr/evm")
@login_required
def k_radar_api_kpr_evm():
    return _safe_json(lambda: jsonify({"success": True, "data": get_kpr_extended_data(_required_tenant_id()).get("evm", {})}))


@app_bp.route("/k-radar/api/kpr/risk")
@login_required
def k_radar_api_kpr_risk():
    return _safe_json(lambda: jsonify({"success": True, "data": get_kpr_extended_data(_required_tenant_id()).get("risk", {})}))


@app_bp.route("/k-radar/api/kpr/kaynak-kapasite")
@login_required
def k_radar_api_kpr_kaynak_kapasite():
    return _safe_json(lambda: jsonify({"success": True, "data": get_kpr_extended_data(_required_tenant_id()).get("kaynak_kapasite", {})}))


@app_bp.route("/k-radar/api/kpr/gantt")
@login_required
def k_radar_api_kpr_gantt():
    return _safe_json(lambda: jsonify({"success": True, "data": get_kpr_extended_data(_required_tenant_id()).get("gantt", {})}))


@app_bp.route("/k-radar/api/cross/paydas")
@login_required
def k_radar_api_cross_paydas():
    def _build():
        rows = (
            StakeholderMap.query.filter_by(tenant_id=_required_tenant_id(), is_active=True)
            .order_by(StakeholderMap.updated_at.desc())
            .limit(300)
            .all()
        )
        return jsonify(
            {
                "success": True,
                "data": {
                    "rows": [
                        {
                            "id": r.id,
                            "name": r.name,
                            "role": r.role,
                            "influence": r.influence,
                            "interest": r.interest,
                            "strategy": r.strategy,
                        }
                        for r in rows
                    ]
                },
            }
        )
    return _safe_json(_build)


@app_bp.route("/k-radar/api/cross/paydas", methods=["POST"])
@login_required
def k_radar_api_cross_paydas_create():
    if not _can_manage_k_radar():
        return _forbidden_json()
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    if not name:
        return jsonify({"success": False, "message": "name zorunlu"}), 400
    role = (payload.get("role") or "").strip() or None
    strategy = (payload.get("strategy") or "").strip() or None
    influence = int(payload.get("influence") or 3)
    interest = int(payload.get("interest") or 3)
    def _create():
        row = StakeholderMap(
            tenant_id=_required_tenant_id(),
            name=name,
            role=role,
            strategy=strategy,
            influence=max(1, min(5, influence)),
            interest=max(1, min(5, interest)),
            is_active=True,
        )
        db.session.add(row)
        db.session.commit()
        return jsonify({"success": True, "data": {"id": row.id}})
    return _safe_json(_create)


@app_bp.route("/k-radar/api/cross/paydas/<int:row_id>", methods=["PUT"])
@login_required
def k_radar_api_cross_paydas_update(row_id: int):
    if not _can_manage_k_radar():
        return _forbidden_json()
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    if not name:
        return jsonify({"success": False, "message": "name zorunlu"}), 400
    role = (payload.get("role") or "").strip() or None
    strategy = (payload.get("strategy") or "").strip() or None
    influence = int(payload.get("influence") or 3)
    interest = int(payload.get("interest") or 3)

    def _update():
        row = StakeholderMap.query.filter_by(id=row_id, tenant_id=_required_tenant_id(), is_active=True).first()
        if not row:
            return jsonify({"success": False, "message": "Kayıt bulunamadı"}), 404
        row.name = name
        row.role = role
        row.strategy = strategy
        row.influence = max(1, min(5, influence))
        row.interest = max(1, min(5, interest))
        db.session.commit()
        return jsonify({"success": True, "data": {"id": row.id}})

    return _safe_json(_update)


@app_bp.route("/k-radar/api/cross/paydas/<int:row_id>", methods=["DELETE"])
@login_required
def k_radar_api_cross_paydas_delete(row_id: int):
    if not _can_manage_k_radar():
        return _forbidden_json()

    def _delete():
        row = StakeholderMap.query.filter_by(id=row_id, tenant_id=_required_tenant_id(), is_active=True).first()
        if not row:
            return jsonify({"success": False, "message": "Kayıt bulunamadı"}), 404
        row.is_active = False
        db.session.commit()
        return jsonify({"success": True, "data": {"id": row.id}})

    return _safe_json(_delete)


@app_bp.route("/k-radar/api/cross/rekabet")
@login_required
def k_radar_api_cross_rekabet():
    return _safe_json(lambda: jsonify({"success": True, "data": get_cross_extended_data(_required_tenant_id()).get("rekabet", {})}))


@app_bp.route("/k-radar/api/cross/a3")
@login_required
def k_radar_api_cross_a3():
    return _safe_json(lambda: jsonify({"success": True, "data": get_cross_extended_data(_required_tenant_id()).get("a3_5neden", {})}))


@app_bp.route("/k-radar/api/cross/anket")
@login_required
def k_radar_api_cross_anket():
    return _safe_json(lambda: jsonify({"success": True, "data": get_cross_extended_data(_required_tenant_id()).get("anket", {})}))


@app_bp.route("/k-radar/api/hub-summary")
@login_required
def k_radar_api_hub_summary():
    return _safe_json(lambda: jsonify({"success": True, "data": get_hub_summary(_required_tenant_id())}))


@app_bp.route("/k-radar/api/ks")
@login_required
def k_radar_api_ks():
    return _safe_json(lambda: jsonify({"success": True, "data": get_ks_data(_required_tenant_id())}))


@app_bp.route("/k-radar/api/kp")
@login_required
def k_radar_api_kp():
    return _safe_json(lambda: jsonify({"success": True, "data": get_kp_data(_required_tenant_id())}))


@app_bp.route("/k-radar/api/kpr")
@login_required
def k_radar_api_kpr():
    return _safe_json(lambda: jsonify({"success": True, "data": get_kpr_data(_required_tenant_id())}))


@app_bp.route("/k-radar/api/cross/risk-heatmap")
@login_required
def k_radar_api_cross_risk_heatmap():
    return _safe_json(
        lambda: jsonify({"success": True, "data": get_cross_heatmap_data(_required_tenant_id())})
    )


@app_bp.route("/k-radar/api/recommendations")
@login_required
def k_radar_api_recommendations():
    def _build():
        summary = get_hub_summary(_required_tenant_id())
        recs = get_recommendations_from_summary(summary)
        states = get_recommendation_states(_required_tenant_id(), current_user.id, recs)
        items = [{"key": recommendation_key(r), "text": r, "state": states.get(recommendation_key(r), "pending")} for r in recs]
        return jsonify({"success": True, "data": {"items": items, "triggers": get_recommendation_triggers(summary)}})
    return _safe_json(_build)


@app_bp.route("/k-radar/api/recommendations/triggers")
@login_required
def k_radar_api_recommendation_triggers():
    return _safe_json(
        lambda: jsonify({"success": True, "data": {"items": get_recommendation_triggers(get_hub_summary(_required_tenant_id()))}})
    )


@app_bp.route("/k-radar/takvim/kaydet", methods=["POST"])
@login_required
def k_radar_schedule_save():
    if not _can_manage_k_radar():
        return render_template("platform/errors/403.html"), 403
    enabled = bool(request.form.get("enabled"))
    time_val = (request.form.get("time") or "08:30").strip()
    cfg = _scheduler.save_schedule(current_app, {"enabled": enabled, "time": time_val})
    _scheduler.apply_schedule(current_app)
    flash(f"K-Radar takvimi guncellendi: {'Acik' if cfg['enabled'] else 'Kapali'} {cfg['time']}", "success")
    return redirect(url_for("app_bp.k_radar_hub"))


@app_bp.route("/k-radar/api/recommendations/action", methods=["POST"])
@login_required
def k_radar_api_recommendation_action():
    if not _can_manage_k_radar():
        return _forbidden_json()
    payload = request.get_json(silent=True) or {}
    item = (payload.get("item") or "").strip()
    action = (payload.get("action") or "").strip().lower()
    if not item:
        return jsonify({"success": False, "message": "item zorunlu"}), 400
    def _do():
        saved = set_recommendation_state(_required_tenant_id(), current_user.id, item, action)
        return jsonify({"success": True, "data": saved})
    try:
        return _do()
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception as e:
        current_app.logger.exception("[k_radar_action] %s", e)
        return jsonify({"success": False, "message": "Aksiyon kaydi olusturulamadi."}), 500


@app_bp.route("/k-radar/api/recommendations/history")
@login_required
def k_radar_api_recommendation_history():
    try:
        limit = request.args.get("per_page", 10, type=int)
    except Exception:
        limit = 10
    try:
        page = request.args.get("page", 1, type=int)
    except Exception:
        page = 1
    state = (request.args.get("state") or "").strip().lower()
    actor_user_id = request.args.get("user_id", type=int)
    return _safe_json(
        lambda: jsonify(
            {
                "success": True,
                "data": list_recommendation_action_history(
                    tenant_id=_required_tenant_id(),
                    user_id=current_user.id,
                    can_manage=_can_manage_k_radar(),
                    limit=limit,
                    page=page,
                    state=state,
                    actor_user_id=actor_user_id,
                ),
            }
        )
    )


@app_bp.route("/k-radar/api/recommendations/history.csv")
@login_required
def k_radar_api_recommendation_history_csv():
    state = (request.args.get("state") or "").strip().lower()
    actor_user_id = request.args.get("user_id", type=int)
    def _build_csv():
        payload = list_recommendation_action_history(
            tenant_id=_required_tenant_id(),
            user_id=current_user.id,
            can_manage=_can_manage_k_radar(),
            limit=200,
            page=1,
            state=state,
            actor_user_id=actor_user_id,
        )
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["state", "user_id", "updated_at", "recommendation_text"])
        for row in payload.get("items", []):
            writer.writerow([
                row.get("state", ""),
                row.get("user_id", ""),
                row.get("updated_at", ""),
                row.get("recommendation_text", ""),
            ])
        csv_data = output.getvalue()
        return current_app.response_class(
            csv_data,
            mimetype="text/csv; charset=utf-8",
            headers={
                "Content-Disposition": "attachment; filename=k_radar_history.csv",
            },
        )
    return _safe_json(_build_csv)
