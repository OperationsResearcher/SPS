"""Küresel arama API'si — Komut Paleti (Ctrl+K) için."""
from flask import jsonify, request, current_app
from flask_login import login_required, current_user
from sqlalchemy import or_

from platform_core import app_bp
from app.models.process import Process, ProcessKpi
from app.models.core import User
from app.models.core import Strategy, SubStrategy
from flask_babel import gettext as _

_MIN_Q = 2
_LIMIT = 8


def _icon(kind):
    return {
        "process": "fa-sitemap",
        "kpi": "fa-chart-line",
        "strategy": "fa-bullseye",
        "sub_strategy": "fa-bullseye",
        "project": "fa-folder-open",
        "user": "fa-user",
    }.get(kind, "fa-circle")


def _kind_label(kind):
    return {
        "process": "Süreç",
        "kpi": "PG",
        "strategy": "Strateji",
        "sub_strategy": "Alt Strateji",
        "project": "Proje",
        "user": "Kullanıcı",
    }.get(kind, kind)


@app_bp.route("/api/search")
@login_required
def api_global_search():
    """Stratejik plan + süreç + PG + proje + kullanıcı genelinde hızlı arama."""
    q = (request.args.get("q") or "").strip()
    if len(q) < _MIN_Q:
        return jsonify({"success": True, "items": []})
    tid = current_user.tenant_id
    if not tid:
        return jsonify({"success": True, "items": []})

    like = f"%{q.lower()}%"
    items = []

    try:
        # Süreçler
        procs = (
            Process.query.filter(
                Process.tenant_id == tid,
                Process.is_active.is_(True),
                or_(Process.name.ilike(like), Process.code.ilike(like)),
            ).order_by(Process.code).limit(_LIMIT).all()
        )
        for p in procs:
            items.append({
                "kind": "process",
                "kind_label": _kind_label("process"),
                "icon": _icon("process"),
                "title": ((p.code + " — ") if p.code else "") + (p.name or "(adsız)"),
                "subtitle": "Süreç karnesi",
                "url": f"/process/{p.id}/karne",
            })

        # PG'ler
        kpis = (
            ProcessKpi.query.join(Process, ProcessKpi.process_id == Process.id).filter(
                Process.tenant_id == tid,
                Process.is_active.is_(True),
                ProcessKpi.is_active.is_(True),
                ProcessKpi.name.ilike(like),
            ).order_by(ProcessKpi.name).limit(_LIMIT).all()
        )
        for k in kpis:
            items.append({
                "kind": "kpi",
                "kind_label": _kind_label("kpi"),
                "icon": _icon("kpi"),
                "title": k.name or "(adsız PG)",
                "subtitle": "Süreç: " + (k.process.name if k.process else ""),
                "url": f"/process/{k.process_id}/karne",
            })

        # Stratejiler
        strats = (
            Strategy.query.filter(
                Strategy.tenant_id == tid,
                Strategy.is_active.is_(True),
                or_(Strategy.title.ilike(like), Strategy.code.ilike(like)),
            ).limit(_LIMIT).all()
        )
        for s in strats:
            items.append({
                "kind": "strategy",
                "kind_label": _kind_label("strategy"),
                "icon": _icon("strategy"),
                "title": ((s.code + " — ") if s.code else "") + (s.title or ""),
                "subtitle": "Stratejik Plan",
                "url": "/sp",
            })

        # Alt stratejiler
        subs = (
            SubStrategy.query.join(Strategy).filter(
                Strategy.tenant_id == tid,
                SubStrategy.is_active.is_(True),
                or_(SubStrategy.title.ilike(like), SubStrategy.code.ilike(like)),
            ).limit(_LIMIT).all()
        )
        for s in subs:
            items.append({
                "kind": "sub_strategy",
                "kind_label": _kind_label("sub_strategy"),
                "icon": _icon("sub_strategy"),
                "title": ((s.code + " — ") if s.code else "") + (s.title or ""),
                "subtitle": "Alt strateji",
                "url": "/sp",
            })

        # Projeler
        try:
            from app.models.project import Project
            projs = (
                Project.query.filter(
                    Project.tenant_id == tid,
                    Project.is_active.is_(True),
                    Project.name.ilike(like),
                ).limit(_LIMIT).all()
            )
            for p in projs:
                items.append({
                    "kind": "project",
                    "kind_label": _kind_label("project"),
                    "icon": _icon("project"),
                    "title": p.name or "(adsız)",
                    "subtitle": "Proje",
                    "url": f"/project/{p.id}",
                })
        except Exception as e:
            current_app.logger.warning(f"[api_global_search] suppressed: {e}")

        # Kullanıcılar (yalnız kendi kurum)
        users = (
            User.query.filter(
                User.tenant_id == tid,
                User.is_active.is_(True),
                or_(
                    User.first_name.ilike(like),
                    User.last_name.ilike(like),
                    User.email.ilike(like),
                ),
            ).limit(_LIMIT).all()
        )
        for u in users:
            full = ((u.first_name or "") + " " + (u.last_name or "")).strip() or u.email
            items.append({
                "kind": "user",
                "kind_label": _kind_label("user"),
                "icon": _icon("user"),
                "title": full,
                "subtitle": u.email or "",
                "url": "/profile",
            })

    except Exception as e:
        current_app.logger.error(f"[api_global_search] {e}", exc_info=True)
        return jsonify({"success": False, "message": _("Arama hatası.")}), 500

    return jsonify({"success": True, "items": items[: _LIMIT * 6]})
