"""Zamanlanmış Raporlar — kullanıcı e-posta abonelikleri (H2)."""
import json

from flask import render_template, jsonify, request, current_app
from flask_login import login_required, current_user

from platform_core import app_bp
from extensions import db, csrf
from flask_babel import gettext as _


_DEFAULT_PREFS = {
    "weekly_digest":   {"enabled": False, "day": "mon",  "hour": 9},
    "morning_summary": {"enabled": False, "hour": 7},
    "risk_alert":      {"enabled": False, "frequency": "daily"},
    "monthly_kpi":     {"enabled": False, "day_of_month": 1, "hour": 9},
}


def _load_subs():
    raw = getattr(current_user, "notification_preferences", None) or "{}"
    try:
        prefs = json.loads(raw) if isinstance(raw, str) else (raw or {})
    except Exception:
        prefs = {}
    sched = prefs.get("scheduled_reports") or {}
    out = {}
    for k, default in _DEFAULT_PREFS.items():
        merged = dict(default)
        if isinstance(sched.get(k), dict):
            merged.update({kk: vv for kk, vv in sched[k].items() if vv is not None})
        out[k] = merged
    return out, prefs


def _save_subs(subs, prefs_obj):
    prefs_obj["scheduled_reports"] = subs
    current_user.notification_preferences = json.dumps(prefs_obj)
    db.session.commit()


@app_bp.route("/settings/scheduled-reports")
@login_required
def scheduled_reports_page():
    subs, _ = _load_subs()
    return render_template("platform/ayarlar/zamanlanmis_raporlar.html",
                           subs=subs, user_email=current_user.email or "")


@app_bp.route("/api/scheduled-reports", methods=["GET"])
@login_required
def api_scheduled_reports_get():
    subs, _ = _load_subs()
    return jsonify({"success": True, "subscriptions": subs, "email": current_user.email or ""})


@app_bp.route("/api/scheduled-reports", methods=["POST"])
@csrf.exempt
@login_required
def api_scheduled_reports_save():
    data = request.get_json(silent=True) or {}
    incoming = data.get("subscriptions")
    if not isinstance(incoming, dict):
        return jsonify({"success": False, "message": _("subscriptions alanı zorunlu.")}), 400
    try:
        subs, prefs = _load_subs()
        for k in _DEFAULT_PREFS.keys():
            if k in incoming and isinstance(incoming[k], dict):
                merged = dict(subs.get(k, _DEFAULT_PREFS[k]))
                for kk, vv in incoming[k].items():
                    if kk == "enabled":
                        merged["enabled"] = bool(vv)
                    elif kk == "day" and isinstance(vv, str):
                        merged["day"] = vv.lower()[:3]
                    elif kk == "hour":
                        try: merged["hour"] = max(0, min(23, int(vv)))
                        except Exception: pass
                    elif kk == "day_of_month":
                        try: merged["day_of_month"] = max(1, min(28, int(vv)))
                        except Exception: pass
                    elif kk == "frequency" and vv in ("daily", "weekly"):
                        merged["frequency"] = vv
                subs[k] = merged
        _save_subs(subs, prefs)
        return jsonify({"success": True, "subscriptions": subs})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[scheduled_reports_save] {e}", exc_info=True)
        return jsonify({"success": False, "message": "Kaydedilemedi."}), 500
