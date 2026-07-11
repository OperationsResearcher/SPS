"""K-Radar — K-Proje (KPR) route'ları."""

from flask import jsonify, render_template, request
from flask_login import current_user, login_required

from platform_core import app_bp
from app.models.portfolio_project import Project, Task, TaskDependency
from micro.modules.k_radar.routes_common import (
    _can_manage_k_radar, _required_tenant_id, _safe_json, _scope_tuples,
)


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
        project = Project.query.filter_by(id=project_id, tenant_id=tenant_id, is_archived=False).first()
        if not project:
            project_id = None
        else:
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


@app_bp.route("/k-radar/kpr/resource-capacity")
@login_required
def k_radar_kpr_kaynak_kapasite():
    return render_template("platform/k_radar/kpr_kaynak_kapasite.html", can_manage_k_radar=_can_manage_k_radar())


@app_bp.route("/k-radar/kpr/gantt")
@login_required
def k_radar_kpr_gantt():
    return render_template("platform/k_radar/kpr_gantt.html", can_manage_k_radar=_can_manage_k_radar())


@app_bp.route("/k-radar/api/kpr")
@login_required
def k_radar_api_kpr():
    from services.k_radar_service import get_kpr_data
    _, _spr = _scope_tuples()
    return _safe_json(lambda: jsonify({"success": True, "data": get_kpr_data(_required_tenant_id(), _spr)}))


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
        return jsonify({
            "success": True,
            "data": {
                "task_count": len(tasks),
                "dependency_count": len(dep_rows),
                "critical_starts": [{"id": t.id, "title": t.title} for t in critical_sorted[:20]],
            },
        })
    return _safe_json(_build)


@app_bp.route("/k-radar/api/kpr/evm")
@login_required
def k_radar_api_kpr_evm():
    from services.k_radar_service import get_kpr_extended_data
    return _safe_json(lambda: jsonify({"success": True, "data": get_kpr_extended_data(_required_tenant_id()).get("evm", {})}))


@app_bp.route("/k-radar/api/kpr/risk")
@login_required
def k_radar_api_kpr_risk():
    from services.k_radar_service import get_kpr_extended_data
    return _safe_json(lambda: jsonify({"success": True, "data": get_kpr_extended_data(_required_tenant_id()).get("risk", {})}))


@app_bp.route("/k-radar/api/kpr/resource-capacity")
@login_required
def k_radar_api_kpr_kaynak_kapasite():
    from services.k_radar_service import get_kpr_extended_data
    return _safe_json(lambda: jsonify({"success": True, "data": get_kpr_extended_data(_required_tenant_id()).get("kaynak_kapasite", {})}))


@app_bp.route("/k-radar/api/kpr/gantt")
@login_required
def k_radar_api_kpr_gantt():
    from services.k_radar_service import get_kpr_extended_data
    return _safe_json(lambda: jsonify({"success": True, "data": get_kpr_extended_data(_required_tenant_id()).get("gantt", {})}))
