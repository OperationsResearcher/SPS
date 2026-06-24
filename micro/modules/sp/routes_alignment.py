"""Strateji ↔ Proje Hizalama Matrisi sayfası ve API'si (D1)."""
from flask import render_template, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import text

from platform_core import app_bp
from extensions import db
from app.services.plan_year_service import get_active_plan_year_for_user
from micro.modules.sp.helpers import _check_sp_role
from flask_babel import gettext as _


def _can_view():
    return _check_sp_role(current_user)


@app_bp.route("/sp/strategy-project-matrix")
@login_required
def sp_strategy_project_matrix():
    if not _can_view():
        return render_template("errors/403.html"), 403
    return render_template("platform/sp/strategy_project_matrix.html")


@app_bp.route("/sp/api/strategy-project-matrix")
@login_required
def sp_api_strategy_project_matrix():
    """Aktif plan yılı için ana strateji × proje hizalama matrisi.

    Hücre değeri: ortak süreçler üzerinden o stratejinin alt stratejilerine
    bağlı süreç-link sayısı (alignment skoru).
    """
    if not _can_view():
        return jsonify({"error": "yetki yok"}), 403

    tid = current_user.tenant_id
    active_py = get_active_plan_year_for_user(current_user)
    py_id = active_py.id if active_py else None

    try:
        # Stratejiler
        strat_rows = db.session.execute(text("""
            SELECT id, code, title FROM strategies
            WHERE tenant_id=:t AND is_active=true
              AND (CAST(:py_id AS INTEGER) IS NULL OR plan_year_id = CAST(:py_id AS INTEGER))
            ORDER BY code NULLS LAST, id
        """), {"t": tid, "py_id": py_id}).fetchall()
        strategies = [{"id": r.id, "code": r.code or "", "title": r.title or ""} for r in strat_rows]

        # Projeler (tenant'ın aktif projeleri)
        proj_rows = db.session.execute(text("""
            SELECT id, name, COALESCE(health_score, 0) AS health_score
            FROM project
            WHERE tenant_id=:t AND COALESCE(is_archived, false) = false
            ORDER BY name LIMIT 60
        """), {"t": tid}).fetchall()
        projects = [{"id": r.id, "name": r.name or "", "health_score": float(r.health_score or 0)} for r in proj_rows]

        # Hizalama: proje → süreç → alt strateji → ana strateji
        align_rows = db.session.execute(text("""
            SELECT
              prp.project_id AS pid,
              s.id            AS sid,
              count(*)        AS alignment
            FROM project_related_processes prp
            JOIN processes p ON p.id = prp.surec_id
            JOIN process_sub_strategy_links psl ON psl.process_id = p.id
            JOIN sub_strategies ss ON ss.id = psl.sub_strategy_id AND ss.is_active = true
            JOIN strategies s ON s.id = ss.strategy_id AND s.is_active = true
            WHERE p.tenant_id = :t
              AND (CAST(:py_id AS INTEGER) IS NULL OR s.plan_year_id = CAST(:py_id AS INTEGER))
            GROUP BY prp.project_id, s.id
        """), {"t": tid, "py_id": py_id}).fetchall()

        align_map = {}
        max_v = 0
        for r in align_rows:
            align_map[(r.pid, r.sid)] = int(r.alignment)
            if r.alignment > max_v:
                max_v = int(r.alignment)

        # Matrisi inşa et
        matrix = []
        for s in strategies:
            row = []
            for p in projects:
                row.append(align_map.get((p["id"], s["id"]), 0))
            matrix.append(row)

        # Skor: kapsayıcılık
        total_cells = len(strategies) * len(projects)
        non_zero = sum(1 for r in matrix for v in r if v > 0)
        coverage_pct = round((non_zero / total_cells) * 100, 1) if total_cells else 0
        zero_proj = [p for i, p in enumerate(projects) if all(matrix[s][i] == 0 for s in range(len(strategies)))]
        zero_strat = [s for j, s in enumerate(strategies) if all(matrix[j][i] == 0 for i in range(len(projects)))]

        return jsonify({"success": True, "data": {
            "strategies": strategies,
            "projects": projects,
            "matrix": matrix,
            "max_value": max_v,
            "coverage_pct": coverage_pct,
            "unaligned_projects": [p["name"] for p in zero_proj][:20],
            "unaligned_strategies": [s["title"] for s in zero_strat][:20],
            "year": active_py.year if active_py else None,
        }})
    except Exception as e:
        current_app.logger.error(f"[strategy_project_matrix] {e}", exc_info=True)
        return jsonify({"success": False, "message": _("İşlem tamamlanamadı.")}), 500
