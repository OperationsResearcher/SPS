"""Exec Dashboard + AI Pivot Advisor + Template Marketplace routes.

Önerilen Hamleler #2, #4, #5.
"""
from __future__ import annotations

from flask import render_template, jsonify, request, current_app, redirect, url_for
from flask_login import login_required, current_user

from platform_core import app_bp
from app.services.exec_dashboard_service import build_exec_snapshot
from app.services.ai_pivot_advisor_service import generate_pivot_recommendations
from app.services.plan_year_template_service import (
    list_templates, get_template, apply_template_to_tenant,
)
from micro.modules.sp.helpers import _check_sp_role, sp_plan_year_open
from app.utils.decorators import require_module
from flask_babel import gettext as _
import logging

logger = logging.getLogger(__name__)


def _can():
    return _check_sp_role(current_user)


# ─── Exec Dashboard ──────────────────────────────────────────────────────────

@app_bp.route("/k-plan/strategy/exec-dashboard")
@login_required
@require_module("surec")  # süreç PG verisi gösterir → süreç paketi gerekir
def sp_exec_dashboard():
    if not _can():
        return render_template("errors/403.html"), 403
    from app.services.plan_year_service import list_plan_years, get_active_plan_year_for_user
    plan_years = list_plan_years(current_user.tenant_id) if current_user.tenant_id else []
    active_py = get_active_plan_year_for_user(current_user)
    # T7/C: Yönetici Paneli mühür durumunu GÖRÜR ama YÖNETMEZ.
    # İzleme/eylem ayrımı: yönetim Plan Dönemleri sayfasındadır.
    muhursuz_yillar = [
        py.year for py in plan_years
        if py.status not in ("closed", "archived") and py.year < (active_py.year if active_py else 0)
    ]
    return render_template(
        "platform/sp/exec_dashboard.html",
        plan_years=plan_years,
        active_year=(active_py.year if active_py else None),
        muhursuz_yillar=sorted(muhursuz_yillar, reverse=True),
    )


@app_bp.route("/k-plan/strategy/api/exec-snapshot")
@login_required
def sp_api_exec_snapshot():
    if not _can():
        return jsonify({"error": "yetki yok"}), 403
    try:
        year = request.args.get("year", type=int)
        snap = build_exec_snapshot(current_user.tenant_id, year=year)
        return jsonify({"success": True, "snapshot": snap})
    except Exception as e:
        current_app.logger.error(f"exec_snapshot error: {e}", exc_info=True)
        return jsonify({"success": False, "message": _("İşlem tamamlanamadı.")}), 500


# ─── Strateji bazlı performans sıralaması ────────────────────────────────────

@app_bp.route("/k-plan/strategy/api/exec-strategy-scores")
@login_required
def sp_api_exec_strategy_scores():
    """Aktif (veya verilen) yıl için strateji bazlı PG hedef üstü %; top 5 + bottom 5."""
    if not _can():
        return jsonify({"error": "yetki yok"}), 403
    from sqlalchemy import text as _t
    from app.extensions import db
    try:
        year = request.args.get("year", type=int)
        if year is None:
            import datetime as _d
            year = _d.date.today().year
        from app.services import pg_year_scores as _pys
        tid = current_user.tenant_id
        link_rows = db.session.execute(_t("""
            SELECT DISTINCT s.id, k.id AS pg_id
            FROM strategies s
            JOIN sub_strategies ss ON ss.strategy_id = s.id AND ss.is_active=true
            JOIN process_sub_strategy_links psl ON psl.sub_strategy_id = ss.id
            JOIN processes p ON p.id = psl.process_id AND p.is_active=true
            JOIN process_kpis k ON k.process_id = p.id AND k.is_active=true
            WHERE s.tenant_id=:t AND s.is_active=true
        """), {"t": tid}).fetchall()
        strat_rows = db.session.execute(_t(
            "SELECT id, code, title FROM strategies WHERE tenant_id=:t AND is_active=true "
            "ORDER BY code NULLS LAST"), {"t": tid}).fetchall()
        groups = {}
        for r in link_rows:
            groups.setdefault(r.id, set()).add(r.pg_id)
        score_map, _pgs = _pys.score_rows(tid, year)
        items = []
        for r in strat_rows:
            total, on_t, comp = _pys.on_target_stats(score_map, groups.get(r.id, ()))
            items.append({
                "id": r.id, "code": r.code or "", "title": r.title or "",
                "pg_total": total,
                "on_target_pct": _pys.pct(on_t, comp),
                "comparable": comp,
            })
        with_data = [x for x in items if x["on_target_pct"] is not None]
        top    = sorted(with_data, key=lambda x: x["on_target_pct"], reverse=True)[:5]
        bottom = sorted(with_data, key=lambda x: x["on_target_pct"])[:5]
        return jsonify({"success": True, "data": {
            "year": year, "all": items, "top": top, "bottom": bottom,
        }})
    except Exception as e:
        current_app.logger.error(f"exec_strategy_scores error: {e}", exc_info=True)
        return jsonify({"success": False, "message": _("İşlem tamamlanamadı.")}), 500


# ─── K-Vektör puan gelişimi (günlük/aylık/çeyreklik/yıllık) ─────────────────

def _kv_score_at(tenant_id: int, as_of_date, plan_year_obj):
    """Verilen as_of tarihinde K-Vektör vizyon puanı (0-100). Geçmiş tarihler cache'lenir."""
    from app.extensions import cache
    from app.services.score_engine_service import compute_vision_score
    import datetime as _d
    key = f"kv:{tenant_id}:{plan_year_obj.id if plan_year_obj else 0}:{as_of_date.isoformat()}"
    val = cache.get(key)
    if val is not None:
        return val
    try:
        bundle = compute_vision_score(
            tenant_id,
            year=plan_year_obj.year if plan_year_obj else None,
            as_of_date=as_of_date,
            persist_pg_scores=False,
            plan_year=plan_year_obj,
        )
        v1000 = bundle.get("vision_score_1000")
        if v1000 is None:
            return None
        v100 = round(max(0.0, min(100.0, float(v1000) / 10.0)), 1)
        # Geçmiş tarihler 7 gün, bugün 5 dk
        ttl = 300 if as_of_date == _d.date.today() else 7 * 24 * 3600
        cache.set(key, v100, timeout=ttl)
        return v100
    except Exception:
        return None


@app_bp.route("/k-plan/strategy/api/exec-kvektor-trend")
@login_required
def sp_api_exec_kvektor_trend():
    """K-Vektör puanı gelişimi — günlük / aylık / çeyreklik / yıllık seriler."""
    if not _can():
        return jsonify({"error": "yetki yok"}), 403
    import datetime as _d
    try:
        from app.services.plan_year_service import get_plan_year, get_active_plan_year_for_user
        year_q = request.args.get("year", type=int)
        py = get_plan_year(current_user.tenant_id, year_q) if year_q else get_active_plan_year_for_user(current_user)
        today = _d.date.today()

        # Günlük: son 30 gün, her 5 günde 1 (7 nokta)
        daily_labels, daily_values = [], []
        for i in range(6, -1, -1):
            d = today - _d.timedelta(days=i * 5)
            daily_labels.append(d.strftime("%d.%m"))
            daily_values.append(_kv_score_at(current_user.tenant_id, d, py))

        # Aylık: son 12 ay sonu
        monthly_labels, monthly_values = [], []
        cur = today.replace(day=1)
        months = []
        for _ in range(12):
            # ayın son günü
            if cur.month == 12:
                last_day = cur.replace(day=31)
            else:
                last_day = (cur.replace(month=cur.month + 1, day=1) - _d.timedelta(days=1))
            if last_day > today:
                last_day = today
            months.append((cur, last_day))
            # bir önceki ayın 1'i
            if cur.month == 1:
                cur = cur.replace(year=cur.year - 1, month=12)
            else:
                cur = cur.replace(month=cur.month - 1)
        for cur_first, d in reversed(months):
            monthly_labels.append(cur_first.strftime("%Y-%m"))
            monthly_values.append(_kv_score_at(current_user.tenant_id, d, py))

        # Çeyreklik: son 8 çeyrek sonu
        def _q_end(yr, q):
            mm = q * 3
            if mm == 12:
                return _d.date(yr, 12, 31)
            return _d.date(yr, mm + 1, 1) - _d.timedelta(days=1)
        cur_q = (today.month - 1) // 3 + 1
        cur_y = today.year
        qpts = []
        for _ in range(8):
            qpts.append((cur_y, cur_q))
            cur_q -= 1
            if cur_q == 0:
                cur_q = 4
                cur_y -= 1
        quarterly_labels, quarterly_values = [], []
        for yr, q in reversed(qpts):
            d = _q_end(yr, q)
            if d > today: d = today
            quarterly_labels.append(f"{yr} Ç{q}")
            quarterly_values.append(_kv_score_at(current_user.tenant_id, d, py))

        # Yıllık: son 5 yıl sonu
        yearly_labels, yearly_values = [], []
        for i in range(4, -1, -1):
            yr = today.year - i
            d = _d.date(yr, 12, 31)
            if d > today: d = today
            yearly_labels.append(str(yr))
            yearly_values.append(_kv_score_at(current_user.tenant_id, d, py))

        # Bugünkü puan (özet)
        current = _kv_score_at(current_user.tenant_id, today, py)

        return jsonify({"success": True, "data": {
            "current": current,
            "plan_year": py.year if py else None,
            "daily":     {"labels": daily_labels,     "values": daily_values},
            "monthly":   {"labels": monthly_labels,   "values": monthly_values},
            "quarterly": {"labels": quarterly_labels, "values": quarterly_values},
            "yearly":    {"labels": yearly_labels,    "values": yearly_values},
        }})
    except Exception as e:
        current_app.logger.error(f"exec_kvektor_trend error: {e}", exc_info=True)
        return jsonify({"success": False, "message": _("İşlem tamamlanamadı.")}), 500


# ─── Son 12 ay sağlık trendi (PG hedef üstü oranı) ───────────────────────────

@app_bp.route("/k-plan/strategy/api/exec-trend")
@login_required
def sp_api_exec_trend():
    """Son 12 ay için aylık PG hedef üstü yüzdesi — sparkline için."""
    if not _can():
        return jsonify({"error": "yetki yok"}), 403
    from sqlalchemy import text as _t
    from app.extensions import db
    try:
        import datetime as _d
        import calendar as _cal
        from app.services import pg_year_scores as _pys
        from app.utils.tr_time import today_tr
        tid = current_user.tenant_id
        today = today_tr()
        labels, values = [], []
        pgs_cache = {}
        y, m = today.year, today.month
        months = []
        for _i in range(12):
            months.append((y, m))
            m -= 1
            if m == 0:
                y, m = y - 1, 12
        for (y, m) in reversed(months):
            last = _d.date(y, m, _cal.monthrange(y, m)[1])
            as_of = min(last, today)
            rows, pgs_cache[y] = _pys.score_rows(tid, y, as_of, pgs_cache.get(y))
            _t0, on_t, comp = _pys.on_target_stats(rows, rows.keys())
            labels.append(f"{y:04d}-{m:02d}")
            values.append(_pys.pct(on_t, comp))
        return jsonify({"success": True, "data": {"labels": labels, "values": values}})
    except Exception as e:
        current_app.logger.error(f"exec_trend error: {e}", exc_info=True)
        return jsonify({"success": False, "message": _("İşlem tamamlanamadı.")}), 500


# ─── AI Pivot Advisor ────────────────────────────────────────────────────────

@app_bp.route("/k-plan/strategy/api/ai-pivot", methods=["POST"])
@login_required
def sp_api_ai_pivot():
    if not _can():
        return jsonify({"error": "yetki yok"}), 403
    use_llm = (request.args.get("use_llm", "1") in ("1", "true"))
    try:
        result = generate_pivot_recommendations(
            current_user.tenant_id, use_llm=use_llm, user_id=current_user.id,
        )
        # Kota aşıldı ise 429 (rate limit) status
        status = 429 if result.get("source") == "heuristic_quota" else 200
        return jsonify({"success": True, **result}), status
    except Exception as e:
        current_app.logger.error(f"ai_pivot error: {e}", exc_info=True)
        return jsonify({"success": False, "message": _("İşlem tamamlanamadı.")}), 500


# ─── Template Marketplace ────────────────────────────────────────────────────

@app_bp.route("/k-plan/strategy/templates")
@login_required
def sp_templates_page():
    if not _can():
        return render_template("errors/403.html"), 403
    return render_template("platform/sp/templates.html")


@app_bp.route("/k-plan/strategy/api/templates")
@login_required
def sp_api_templates_list():
    if not _can():
        return jsonify({"error": "yetki yok"}), 403
    return jsonify({"success": True, "items": list_templates()})


@app_bp.route("/k-plan/strategy/api/templates/<code>")
@login_required
def sp_api_template_get(code):
    if not _can():
        return jsonify({"error": "yetki yok"}), 403
    t = get_template(code)
    if not t:
        return jsonify({"error": "not found"}), 404
    return jsonify({"success": True, "template": t})


# ── TV / War-room modu ────────────────────────────────────────────────────────

@app_bp.route("/k-radar/savas-odasi")
@login_required
def sp_tv_mode():
    """Tam ekran TV / war-room KPI duvarı (exec-snapshot verisini döngüyle gösterir).

    Teşhis katmanı (`/k-radar/`) — saf gösterim, sıfır girdi. Endpoint adı
    tarihsel (`sp_tv_mode`); endpoint sözleşmesi gereği DEĞİŞMEZ, sadece path
    taşındı. Bkz. docs/kontrol/ENDPOINT-SOZLESMESI.md
    """
    if not _can():
        return render_template("errors/403.html"), 403
    return render_template(
        "platform/sp/tv.html",
        savas_uid=current_user.id,
        savas_tid=current_user.tenant_id or 0,
    )


@app_bp.route("/sp/tv")
@login_required
def sp_tv_mode_legacy():
    """Eski Savaş Odası adresi → teşhis katmanı. Bookmark'lar kırılmasın."""
    return redirect(url_for("app_bp.sp_tv_mode"), code=301)


# ── Tenant-geneli AI Yönetici Özeti (exec + kurum üstü) ───────────────────────

def _exec_heuristik_ozet(snap):
    """exec-snapshot dict'inden LLM olmadan da çalışan Türkçe yönetici özeti."""
    snap = snap or {}
    kpi = snap.get("kpi") or {}
    act = snap.get("activity") or {}
    risk = snap.get("risk") or {}
    ano = snap.get("anomaly") or {}
    parts = []
    hs = snap.get("health_score")
    if hs is not None:
        try:
            parts.append(_("Genel sağlık skoru %%%(v).0f.", v=float(hs)))
        except (TypeError, ValueError) as e:
            logger.warning(f"_exec_heuristik_ozet failed: {e}")
    ot = kpi.get("on_target_pct")
    if ot is not None:
        try:
            parts.append(_("PG'lerin %%%(v).0f'ı hedef üstünde.", v=float(ot)))
        except (TypeError, ValueError) as e:
            logger.warning(f"_exec_heuristik_ozet failed: {e}")
    total = kpi.get("total") or 0
    wd = kpi.get("with_data")
    if total and wd is not None and wd < total:
        parts.append(_("%(total)s PG'den %(n)s'ine veri girilmemiş.", total=total, n=total - wd))
    flags = []
    if act.get("overdue"):
        flags.append(_("%(n)s geciken faaliyet", n=act["overdue"]))
    if risk.get("critical"):
        flags.append(_("%(n)s kritik risk", n=risk["critical"]))
    if ano.get("high"):
        flags.append(_("%(n)s yüksek anomali", n=ano["high"]))
    if flags:
        parts.append(_("Kırmızı bayraklar: %(liste)s.", liste=", ".join(flags)))
    if not parts:
        parts.append(_("Özet üretecek yeterli veri yok; PG ve faaliyet verisi girin."))
    return " ".join(parts)


@app_bp.route("/k-plan/strategy/api/exec-ai-summary")
@login_required
def sp_api_exec_ai_ozet():
    """Tenant-geneli 2-3 cümlelik Türkçe yönetici özeti (exec + kurum üstü).

    Her zaman deterministik heuristik döner; LLM varsa cilalanır (yerelde anahtarsız çalışır).
    """
    if not _can():
        return jsonify({"error": "yetki yok"}), 403
    year = request.args.get("year", type=int)
    try:
        snap = build_exec_snapshot(current_user.tenant_id, year=year)
    except Exception as e:
        current_app.logger.info(f"[exec-ai-ozet] snapshot fallback ({e})")
        snap = {}

    ozet = _exec_heuristik_ozet(snap)
    kaynak = "heuristik"
    try:
        from app.services.llm_gateway import call_llm
        prompt = (
            "Aşağıdaki kurum performans özetinden, bir üst yöneticinin tek bakışta okuyacağı "
            "2-3 cümlelik Türkçe özet yaz. Sırasıyla: kazanım(lar), kırmızı bayrak(lar), "
            "bu hafta odak. Sade ve net.\n\n" + str(snap)
        )
        res = call_llm(
            tenant_id=current_user.tenant_id, endpoint="exec_ozet",
            prompt=prompt,
            system_prompt="Sen kısa ve net konuşan bir Türkçe strateji danışmanısın.",
            user_id=current_user.id, max_output_tokens=260,
        )
        if isinstance(res, dict) and res.get("text"):
            ozet = res["text"].strip()
            kaynak = "ai"
    except Exception as e:
        current_app.logger.info(f"[exec-ai-ozet] LLM fallback ({e})")

    return jsonify({"success": True, "ozet": ozet, "kaynak": kaynak})


@app_bp.route("/k-plan/strategy/api/templates/<code>/apply", methods=["POST"])
@login_required
@sp_plan_year_open
def sp_api_template_apply(code):
    if not _can():
        return jsonify({"error": "yetki yok"}), 403
    data = request.get_json(silent=True) or {}
    try:
        target_year = int(data.get("target_year"))
    except (TypeError, ValueError):
        return jsonify({"error": "target_year zorunlu"}), 400
    if not (2000 <= target_year <= 2100):
        return jsonify({"error": "Geçersiz yıl değeri."}), 400
    overwrite = bool(data.get("overwrite_identity", False))
    try:
        py = apply_template_to_tenant(
            current_user.tenant_id, code, target_year, overwrite_identity=overwrite
        )
        return jsonify({
            "success": True,
            "plan_year": {"id": py.id, "year": py.year, "name": py.name, "status": py.status},
        }), 201
    except Exception as e:
        current_app.logger.error(f"template_apply error: {e}", exc_info=True)
        return jsonify({"success": False, "message": _("İşlem tamamlanamadı.")}), 500


# ── Savaş Odası cepheleri: alt strateji + süreç + proje sıralaması ────────────

_SUBSTRAT_SQL = """
    SELECT DISTINCT ss.id AS gid, ss.code, ss.title, k.id AS pg_id
    FROM sub_strategies ss
    JOIN strategies s ON ss.strategy_id = s.id AND s.is_active=true
    JOIN process_sub_strategy_links psl ON psl.sub_strategy_id = ss.id
    JOIN processes p ON p.id = psl.process_id AND p.is_active=true
    JOIN process_kpis k ON k.process_id = p.id AND k.is_active=true
    WHERE s.tenant_id=:t AND ss.is_active=true
"""

_PROCESS_SQL = """
    SELECT DISTINCT p.id AS gid, p.code, p.name AS title, k.id AS pg_id
    FROM processes p
    JOIN process_kpis k ON k.process_id = p.id AND k.is_active=true
    WHERE p.tenant_id=:t AND p.is_active=true
"""


def _savas_rank(sql, tid, year):
    """Grup -> PG kümesi (DISTINCT); skor motordan, PG başına tek değer (B-005)."""
    from app.extensions import db
    from sqlalchemy import text as _t
    from app.services import pg_year_scores as _pys
    rows = db.session.execute(_t(sql), {"t": tid}).fetchall()
    groups, meta = {}, {}
    for r in rows:
        groups.setdefault(r.gid, set()).add(r.pg_id)
        meta[r.gid] = (r.code, r.title)
    score_map, _pgs = _pys.score_rows(tid, year)
    items = []
    for gid, ids in groups.items():
        total, on_t, comp = _pys.on_target_stats(score_map, ids)
        code, title = meta[gid]
        items.append({"code": code or "", "title": title or "",
                      "on_target_pct": _pys.pct(on_t, comp), "pg_total": total})
    items.sort(key=lambda x: x["code"])
    wd = [x for x in items if x["on_target_pct"] is not None]
    return {
        "top": sorted(wd, key=lambda x: x["on_target_pct"], reverse=True)[:5],
        "bottom": sorted(wd, key=lambda x: x["on_target_pct"])[:5],
    }


@app_bp.route("/k-plan/strategy/api/war-room/fronts")
@login_required
def sp_api_savas_odasi_fronts():
    """Savaş Odası ek cepheleri: alt strateji + süreç (hedef üstü %) + proje (sağlık)."""
    if not _can():
        return jsonify({"error": "yetki yok"}), 403
    import datetime as _d
    year = request.args.get("year", type=int) or _d.date.today().year
    tid = current_user.tenant_id

    out = {}
    try:
        out["sub_strategies"] = _savas_rank(_SUBSTRAT_SQL, tid, year)
    except Exception as e:
        current_app.logger.info(f"[savas-fronts] sub {e}")
        out["sub_strategies"] = {"top": [], "bottom": []}
    try:
        out["processes"] = _savas_rank(_PROCESS_SQL, tid, year)
    except Exception as e:
        current_app.logger.info(f"[savas-fronts] proc {e}")
        out["processes"] = {"top": [], "bottom": []}

    projects = {"top": [], "bottom": []}
    try:
        from app.models.portfolio_project import Project
        pj = []
        for p in Project.query.filter_by(tenant_id=tid, is_active=True).all():
            if getattr(p, "is_archived", False):
                continue
            hs = getattr(p, "health_score", None)
            pj.append({"code": "", "title": p.name or "",
                       "on_target_pct": (round(float(hs), 1) if hs is not None else None)})
        wd = [x for x in pj if x["on_target_pct"] is not None]
        projects["top"] = sorted(wd, key=lambda x: x["on_target_pct"], reverse=True)[:5]
        projects["bottom"] = sorted(wd, key=lambda x: x["on_target_pct"])[:5]
    except Exception as e:
        current_app.logger.info(f"[savas-fronts] proj {e}")
    out["projects"] = projects

    return jsonify({"success": True, "data": out})
