"""K-Radar — paylaşılan yardımcılar ve hub route'ları."""

from datetime import datetime, timezone
from flask import current_app, jsonify, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from sqlalchemy import text

from platform_core import app_bp
from app.models import db
from services import k_radar_scheduler_service as _scheduler

from app.constants.roles import WRITE_ROLES as _WRITE_ROLES


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


@app_bp.route("/k-radar")
@login_required
def k_radar_hub():
    """K-Radar birleşik hub — Eski K-Rapor sekmeleri + raporlar bir arada."""
    return render_template("platform/k_radar/hub.html")


@app_bp.route("/k-analiz")
@login_required
def k_analiz_hub():
    """K-Analiz alt sayfası — KS-Radar'a yönlendirir (K-Radar hub'undan da erişilebilir)."""
    return redirect(url_for("app_bp.k_radar_ks"))


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


@app_bp.route("/k-radar/api/hub-summary")
@login_required
def k_radar_api_hub_summary():
    from services.k_radar_service import get_hub_summary
    return _safe_json(lambda: jsonify({"success": True, "data": get_hub_summary(_required_tenant_id())}))


@app_bp.route("/k-radar/api/recommendations")
@login_required
def k_radar_api_recommendations():
    from services.k_radar_service import (
        get_hub_summary, get_recommendations_from_summary,
        get_recommendation_states, recommendation_key, get_recommendation_triggers,
    )
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
    from services.k_radar_service import get_hub_summary, get_recommendation_triggers
    return _safe_json(
        lambda: jsonify({"success": True, "data": {"items": get_recommendation_triggers(get_hub_summary(_required_tenant_id()))}})
    )


@app_bp.route("/k-radar/api/recommendations/action", methods=["POST"])
@login_required
def k_radar_api_recommendation_action():
    if not _can_manage_k_radar():
        return _forbidden_json()
    from services.k_radar_service import set_recommendation_state
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
        return jsonify({"success": False, "message": "İşlem tamamlanamadı."}), 400
    except Exception as e:
        current_app.logger.exception("[k_radar_action] %s", e)
        return jsonify({"success": False, "message": "Aksiyon kaydi olusturulamadi."}), 500


@app_bp.route("/k-radar/api/recommendations/history")
@login_required
def k_radar_api_recommendation_history():
    from services.k_radar_service import list_recommendation_action_history
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
        lambda: jsonify({
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
        })
    )


@app_bp.route("/k-radar/api/recommendations/history.csv")
@login_required
def k_radar_api_recommendation_history_csv():
    import csv
    import io
    from services.k_radar_service import list_recommendation_action_history
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
            headers={"Content-Disposition": "attachment; filename=k_radar_history.csv"},
        )
    return _safe_json(_build_csv)
