"""Bireysel Performans modülü."""

from collections import defaultdict
from datetime import datetime, timezone, date

from flask import render_template, jsonify, request, current_app, redirect, url_for
from flask_login import login_required, current_user

from platform_core import app_bp
from app_platform.modules.surec.permissions import user_can_enter_pgv
from app.models import db
from sqlalchemy.orm import contains_eager
from app.utils.db_sequence import is_pk_duplicate, sync_pg_sequence_if_needed
from app.models.process import (
    Process,
    ProcessKpi,
    IndividualPerformanceIndicator,
    IndividualActivity,
    IndividualKpiData,
    IndividualActivityTrack,
    FavoriteKpi,
)
from app.utils.process_utils import last_day_of_period, data_date_to_period_keys
from app.services.plan_year_service import get_active_plan_year_for_user
from app.services.date_sovereign import (
    resolve_plan_year_for_date,
    entity_exists_in_year,
    build_existence_error,
    build_cross_year_notice,
    get_view_year,
)
from app.models.core import Tenant as _Tenant
from flask_babel import gettext as _


def _is_individual_pg_pk_duplicate(err: Exception) -> bool:
    return is_pk_duplicate(err, "individual_performance_indicators")


def _normalize_katman(data) -> tuple:
    """payload'tan (katman, strategy_id) üret — L1 Dal 4.

    Katman yalnızca 'Standart'/'Stratejik' olabilir (geçersizse 'Standart').
    strategy_id yalnızca 'Stratejik' iken ve kullanıcının kurumuna ait bir
    aktif stratejiye işaret ediyorsa korunur; aksi halde None (tenant izolasyonu).
    """
    katman = (data.get("katman") or "Standart").strip()
    if katman not in ("Standart", "Stratejik"):
        katman = "Standart"

    strategy_id = None
    if katman == "Stratejik":
        raw = data.get("strategy_id")
        if raw not in (None, "", "null"):
            try:
                sid = int(raw)
            except (TypeError, ValueError):
                sid = None
            if sid is not None:
                from app.models.core import Strategy
                ok = Strategy.query.filter_by(
                    id=sid, tenant_id=current_user.tenant_id, is_active=True
                ).first()
                strategy_id = sid if ok else None
    return katman, strategy_id


# ── Sayfa ─────────────────────────────────────────────────────────────────────

@app_bp.route("/individual/scorecard")
@login_required
def bireysel_karne():
    """Bireysel karne sayfası."""
    current_year = datetime.now().year
    # L1 Dal 4: stratejik hedefin opsiyonel kurum stratejisi bağı için liste
    from app.models.core import Strategy
    strategies = (
        Strategy.query
        .filter_by(tenant_id=current_user.tenant_id, is_active=True)
        .order_by(Strategy.code)
        .all()
    )
    strateji_secenekleri = [
        {"id": s.id, "baslik": (f"{s.code} — {s.title}" if s.code else s.title)}
        for s in strategies
    ]
    return render_template(
        "platform/bireysel/karne.html",
        current_year=current_year,
        strateji_secenekleri=strateji_secenekleri,
    )


@app_bp.route("/individual")
@login_required
def bireysel():
    """Bireysel modül giriş yönlendirmesi."""
    return redirect(url_for("app_bp.bireysel_karne"))


# ── API: Bireysel PG CRUD ─────────────────────────────────────────────────────

@app_bp.route("/individual/api/pi/ensure-from-process-kpi", methods=["POST"])
@login_required
def bireysel_api_pg_ensure_from_process_kpi():
    """
    Süreç PG'si için geçerli kullanıcıda bireysel PG yoksa oluşturur (aynı kullanıcı adına).
    Süreç karnesi VGS — KpiData ile bireysel karneyi eşlemek için.
    """
    data = request.get_json() or {}
    raw_id = data.get("process_kpi_id")
    if raw_id is None:
        return jsonify({"success": False, "message": "process_kpi_id gerekli."}), 400
    try:
        kpi_id = int(raw_id)
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": _("Geçersiz process_kpi_id.")}), 400

    kpi = (
        ProcessKpi.query.join(Process)
        .filter(
            ProcessKpi.id == kpi_id,
            Process.tenant_id == current_user.tenant_id,
            Process.is_active.is_(True),
            ProcessKpi.is_active.is_(True),
        )
        .first()
    )
    if not kpi:
        return jsonify({"success": False, "message": _("PG bulunamadı.")}), 404

    proc = Process.query.filter_by(
        id=kpi.process_id, tenant_id=current_user.tenant_id, is_active=True
    ).first()
    if not proc or not user_can_enter_pgv(current_user, proc):
        return jsonify({"success": False, "message": _("Bu PG için veri girişi yapamazsınız.")}), 403

    existing = IndividualPerformanceIndicator.query.filter_by(
        user_id=current_user.id,
        source_process_kpi_id=kpi.id,
        is_active=True,
    ).first()
    if existing:
        return jsonify({"success": True, "id": existing.id, "created": False})

    active_py = get_active_plan_year_for_user(current_user)
    for attempt in (1, 2):
        try:
            pg = IndividualPerformanceIndicator(
                user_id=current_user.id,
                name=kpi.name or f"PG #{kpi.id}",
                description=kpi.description,
                code=kpi.code,
                target_value=kpi.target_value,
                unit=kpi.unit,
                period=kpi.period or "Çeyreklik",
                weight=float(kpi.weight or 0),
                direction=kpi.direction or "Increasing",
                basari_puani_araliklari=kpi.basari_puani_araliklari,
                source="Süreç",
                source_process_id=kpi.process_id,
                source_process_kpi_id=kpi.id,
                plan_year_id=active_py.id if active_py else None,
                is_active=True,
            )
            db.session.add(pg)
            db.session.commit()
            return jsonify({"success": True, "id": pg.id, "created": True})
        except Exception as e:
            db.session.rollback()
            if attempt == 1 and _is_individual_pg_pk_duplicate(e):
                sync_pg_sequence_if_needed("individual_performance_indicators", "id")
                db.session.commit()
                continue
            current_app.logger.error(f"[bireysel_api_pg_ensure_from_process_kpi] {e}")
            return jsonify({"success": False, "message": _("İşlem tamamlanamadı.")}), 400


@app_bp.route("/individual/api/pi/add", methods=["POST"])
@login_required
def bireysel_api_pg_add():
    data = request.get_json() or {}
    active_py = get_active_plan_year_for_user(current_user)
    for attempt in (1, 2):
        try:
            pg = IndividualPerformanceIndicator(
                user_id=current_user.id,
                name=data.get("name"),
                description=data.get("description"),
                code=data.get("code"),
                target_value=data.get("target_value"),
                unit=data.get("unit"),
                period=data.get("period", "Aylık"),
                weight=float(data.get("weight") or 0),
                direction=data.get("direction", "Increasing"),
                basari_puani_araliklari=data.get("basari_puani_araliklari"),
                plan_year_id=active_py.id if active_py else None,
            )
            katman, strategy_id = _normalize_katman(data)
            pg.katman = katman
            pg.strategy_id = strategy_id
            if data.get("start_date"):
                pg.start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
            if data.get("end_date"):
                pg.end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
            db.session.add(pg)
            db.session.commit()
            return jsonify({"success": True, "message": "Bireysel PG eklendi.", "id": pg.id})
        except Exception as e:
            db.session.rollback()
            if attempt == 1 and _is_individual_pg_pk_duplicate(e):
                sync_pg_sequence_if_needed("individual_performance_indicators", "id")
                db.session.commit()
                continue
            current_app.logger.error(f"[bireysel_api_pg_add] {e}")
            return jsonify({"success": False, "message": _("İşlem tamamlanamadı.")}), 400


@app_bp.route("/individual/api/pi/update/<int:pg_id>", methods=["POST"])
@login_required
def bireysel_api_pg_update(pg_id):
    pg = IndividualPerformanceIndicator.query.filter_by(
        id=pg_id, user_id=current_user.id, is_active=True
    ).first_or_404()
    data = request.get_json() or {}
    try:
        pg.name        = data.get("name", pg.name)
        pg.description = data.get("description", pg.description)
        pg.code        = data.get("code", pg.code)
        pg.target_value = data.get("target_value", pg.target_value)
        pg.unit        = data.get("unit", pg.unit)
        pg.period      = data.get("period", pg.period)
        pg.weight      = float(data.get("weight") or pg.weight or 0)
        pg.direction   = data.get("direction", pg.direction)
        if "katman" in data:
            pg.katman, pg.strategy_id = _normalize_katman(data)
        db.session.commit()
        return jsonify({"success": True, "message": _("Bireysel PG güncellendi.")})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[bireysel_api_pg_update] {e}")
        return jsonify({"success": False, "message": _("İşlem tamamlanamadı.")}), 400


@app_bp.route("/individual/api/pi/delete/<int:pg_id>", methods=["POST"])
@login_required
def bireysel_api_pg_delete(pg_id):
    pg = IndividualPerformanceIndicator.query.filter_by(
        id=pg_id, user_id=current_user.id
    ).first_or_404()
    try:
        pg.is_active = False
        db.session.commit()
        return jsonify({"success": True, "message": "Bireysel PG silindi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[bireysel_api_pg_delete] {e}")
        return jsonify({"success": False, "message": _("İşlem tamamlanamadı.")}), 400


# ── API: Bireysel Veri Girişi ─────────────────────────────────────────────────

@app_bp.route("/individual/api/data/add", methods=["POST"])
@login_required
def bireysel_api_veri_add():
    data = request.get_json() or {}
    pg_id = data.get("pg_id")
    pg = IndividualPerformanceIndicator.query.filter_by(
        id=pg_id, user_id=current_user.id, is_active=True
    ).first_or_404()
    try:
        year_val = int(data.get("year", datetime.now().year))
        pt = (data.get("period_type") or "aylik").lower().strip()
        pn = int(data.get("period_no") or 1)
        pm = data.get("period_month")
        period_month = int(pm) if pm is not None and str(pm).strip() else None

        data_date_val = None
        if data.get("data_date"):
            data_date_val = datetime.strptime(data["data_date"], "%Y-%m-%d").date()
        else:
            last_day = last_day_of_period(year_val, pt, pn, period_month)
            data_date_val = last_day or date.today()
        # Tarih egemen: year_val data_date'ten türesin
        year_val = data_date_val.year

        # Tarih egemen plan year kontrolü (Faz 2)
        cross_year_notice = None
        tenant_obj = db.session.get(_Tenant, current_user.tenant_id)
        if tenant_obj and getattr(tenant_obj, "plan_year_enabled", False):
            target_py = resolve_plan_year_for_date(current_user.tenant_id, data_date_val)
            if not entity_exists_in_year(pg, target_py):
                return jsonify(build_existence_error(
                    entity=pg,
                    entity_label=f"{pg.code or ''} {pg.name}".strip(),
                    data_date=data_date_val,
                    target_plan_year=target_py,
                    entity_kind="bireysel PG",
                )), 409
            cross_year_notice = build_cross_year_notice(
                view_year=get_view_year(current_user),
                target_year=data_date_val.year,
            )

        entry = IndividualKpiData(
            individual_pg_id=pg.id,
            year=year_val,
            data_date=data_date_val,
            period_type=pt,
            period_no=pn,
            period_month=period_month,
            target_value=data.get("target_value"),
            actual_value=data.get("actual_value", ""),
            description=data.get("description"),
            user_id=current_user.id,
        )
        db.session.add(entry)
        db.session.commit()
        resp = {"success": True, "message": "Veri kaydedildi."}
        if cross_year_notice:
            resp["notice"] = cross_year_notice
        return jsonify(resp)
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[bireysel_api_veri_add] {e}")
        return jsonify({"success": False, "message": _("İşlem tamamlanamadı.")}), 400


# ── API: Bireysel Faaliyet CRUD ───────────────────────────────────────────────

@app_bp.route("/individual/api/activity/add", methods=["POST"])
@login_required
def bireysel_api_faaliyet_add():
    data = request.get_json() or {}
    try:
        act = IndividualActivity(
            user_id=current_user.id,
            name=data.get("name"),
            description=data.get("description"),
            status=data.get("status", "Planlandı"),
            progress=int(data.get("progress") or 0),
        )
        if data.get("start_date"):
            act.start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
        if data.get("end_date"):
            act.end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
        db.session.add(act)
        db.session.commit()
        return jsonify({"success": True, "message": "Faaliyet eklendi.", "id": act.id})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[bireysel_api_faaliyet_add] {e}")
        return jsonify({"success": False, "message": _("İşlem tamamlanamadı.")}), 400


@app_bp.route("/individual/api/activity/update/<int:act_id>", methods=["POST"])
@login_required
def bireysel_api_faaliyet_update(act_id):
    act = IndividualActivity.query.filter_by(
        id=act_id, user_id=current_user.id, is_active=True
    ).first_or_404()
    data = request.get_json() or {}
    try:
        act.name        = data.get("name", act.name)
        act.description = data.get("description", act.description)
        act.status      = data.get("status", act.status)
        act.progress    = int(data.get("progress", act.progress) or 0)
        if data.get("start_date"):
            act.start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
        if data.get("end_date"):
            act.end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
        db.session.commit()
        return jsonify({"success": True, "message": _("Faaliyet güncellendi.")})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[bireysel_api_faaliyet_update] {e}")
        return jsonify({"success": False, "message": _("İşlem tamamlanamadı.")}), 400


@app_bp.route("/individual/api/activity/delete/<int:act_id>", methods=["POST"])
@login_required
def bireysel_api_faaliyet_delete(act_id):
    act = IndividualActivity.query.filter_by(
        id=act_id, user_id=current_user.id
    ).first_or_404()
    try:
        act.is_active = False
        db.session.commit()
        return jsonify({"success": True, "message": "Faaliyet silindi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[bireysel_api_faaliyet_delete] {e}")
        return jsonify({"success": False, "message": _("İşlem tamamlanamadı.")}), 400


@app_bp.route("/individual/api/activity/track/<int:act_id>", methods=["POST"])
@login_required
def bireysel_api_faaliyet_track(act_id):
    """Bireysel faaliyet aylık tamamlanma toggle."""
    act = IndividualActivity.query.filter_by(
        id=act_id, user_id=current_user.id, is_active=True
    ).first_or_404()
    data = request.get_json() or {}
    year      = int(data.get("year", datetime.now().year))
    month     = int(data.get("month", 1))
    completed = bool(data.get("completed", False))
    try:
        track = IndividualActivityTrack.query.filter_by(
            individual_activity_id=act.id, user_id=current_user.id, year=year, month=month
        ).first()
        if track:
            track.completed = completed
        else:
            track = IndividualActivityTrack(
                individual_activity_id=act.id,
                user_id=current_user.id,
                year=year, month=month, completed=completed,
            )
            db.session.add(track)
        db.session.commit()
        return jsonify({"success": True, "completed": track.completed})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[bireysel_api_faaliyet_track] {e}")
        return jsonify({"success": False, "message": _("İşlem tamamlanamadı.")}), 400


# ── API: Favori PG toggle ─────────────────────────────────────────────────────

@app_bp.route("/individual/api/favorite/toggle/<int:kpi_id>", methods=["POST"])
@login_required
def bireysel_api_favori_toggle(kpi_id):
    """Favori KPI oluştur veya soft delete."""
    try:
        # Tenant isolation: yalnızca bu tenant'a ait KPI favorilere eklenebilir
        kpi = (ProcessKpi.query.join(Process)
               .filter(ProcessKpi.id == kpi_id,
                       Process.tenant_id == current_user.tenant_id,
                       ProcessKpi.is_active.is_(True))
               .first_or_404())
        fav = FavoriteKpi.query.filter_by(
            user_id=current_user.id, process_kpi_id=kpi.id
        ).first()
        if fav:
            fav.is_active = not fav.is_active
        else:
            fav = FavoriteKpi(user_id=current_user.id, process_kpi_id=kpi.id, is_active=True)
            db.session.add(fav)
        db.session.commit()
        return jsonify({"success": True, "is_favorite": fav.is_active})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[bireysel_api_favori_toggle] {e}")
        return jsonify({"success": False, "message": _("İşlem tamamlanamadı.")}), 400


# ── API: Bireysel Karne AJAX ──────────────────────────────────────────────────

@app_bp.route("/individual/api/scorecard")
@login_required
def bireysel_api_karne():
    """Yıl bazlı bireysel PG + faaliyet takip verisi."""
    year = request.args.get("year", datetime.now().year, type=int)
    uid  = current_user.id
    active_py = get_active_plan_year_for_user(current_user)

    pg_q = IndividualPerformanceIndicator.query.filter_by(user_id=uid, is_active=True)
    if active_py:
        pg_q_year = pg_q.filter(IndividualPerformanceIndicator.plan_year_id == active_py.id)
        pgs = pg_q_year.all()
        if not pgs:
            pgs = pg_q.all()  # fallback: yıl filtresi olmadan göster
    else:
        pgs = pg_q.all()
    activities = IndividualActivity.query.filter_by(user_id=uid, is_active=True).all()

    def _parse_float(v):
        try:
            return float(v) if v not in (None, "") else None
        except (ValueError, TypeError):
            return None

    # PG entries tek IN-sorguda topla (N+1 önlemi)
    _pg_ids = [pg.id for pg in pgs]
    _entries_by_pg = defaultdict(list)
    if _pg_ids:
        for e in IndividualKpiData.query.filter(
            IndividualKpiData.individual_pg_id.in_(_pg_ids),
            IndividualKpiData.year == year,
        ).order_by(IndividualKpiData.data_date).all():
            _entries_by_pg[e.individual_pg_id].append(e)

    pg_list = []
    for pg in pgs:
        entries = _entries_by_pg.get(pg.id, [])

        entries_by_period = {}
        for e in entries:
            for key in data_date_to_period_keys(e.data_date, year):
                entries_by_period[key] = e.actual_value

        pg_list.append({
            "id": pg.id,
            "name": pg.name,
            "code": pg.code,
            "target_value": pg.target_value,
            "unit": pg.unit,
            "period": pg.period,
            "direction": pg.direction,
            "weight": pg.weight,
            "katman": pg.katman,
            "strategy_id": pg.strategy_id,
            "strategy_baslik": pg.strategy.title if pg.strategy else None,
            "entries": entries_by_period,
        })

    # Faaliyet track'leri tek IN-sorguda topla (N+1 önlemi)
    _act_ids = [a.id for a in activities]
    _tracks_by_act = defaultdict(list)
    if _act_ids:
        for t in IndividualActivityTrack.query.filter(
            IndividualActivityTrack.individual_activity_id.in_(_act_ids),
            IndividualActivityTrack.user_id == uid,
            IndividualActivityTrack.year == year,
        ).all():
            _tracks_by_act[t.individual_activity_id].append(t)

    act_list = []
    for a in activities:
        tracks = _tracks_by_act.get(a.id, [])
        act_list.append({
            "id": a.id,
            "name": a.name,
            "status": a.status,
            "progress": a.progress,
            "monthly_tracks": {t.month: t.completed for t in tracks},
        })

    # Zaman çizgisi: PG veri girişleri + tamamlanan faaliyet ayları
    pg_by_id = {p.id: p for p in pgs}
    timeline_events = []

    for d in (
        IndividualKpiData.query.filter_by(user_id=uid, year=year)
        .order_by(IndividualKpiData.created_at.desc())
        .limit(45)
        .all()
    ):
        pg = pg_by_id.get(d.individual_pg_id)
        pname = pg.name if pg else "Performans göstergesi"
        ts = d.created_at or d.updated_at
        timeline_events.append({
            "ts": ts.isoformat() if ts else None,
            "kind": "pg_veri",
            "title": pname,
            "detail": str(d.actual_value) if d.actual_value is not None else "",
            "sub": d.data_date.strftime("%d.%m.%Y") if d.data_date else "",
        })

    for t in (
        IndividualActivityTrack.query.join(
            IndividualActivity,
            IndividualActivity.id == IndividualActivityTrack.individual_activity_id,
        )
        .options(contains_eager(IndividualActivityTrack.individual_activity))
        .filter(
            IndividualActivityTrack.user_id == uid,
            IndividualActivityTrack.year == year,
            IndividualActivityTrack.completed.is_(True),
            IndividualActivity.is_active.is_(True),
        )
        .order_by(IndividualActivityTrack.updated_at.desc())
        .limit(30)
        .all()
    ):
        act = t.individual_activity
        if not act:
            continue
        ts = t.updated_at or t.created_at
        aylar = ["", "Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]
        ay_ad = aylar[t.month] if 1 <= t.month <= 12 else str(t.month)
        timeline_events.append({
            "ts": ts.isoformat() if ts else None,
            "kind": "faaliyet",
            "title": act.name,
            "detail": f"{ay_ad} ayı tamamlandı",
            "sub": "",
        })

    timeline_events = [e for e in timeline_events if e.get("ts")]
    timeline_events.sort(key=lambda x: x["ts"], reverse=True)
    timeline_events = timeline_events[:40]

    return jsonify({
        "success": True,
        "year": year,
        "pgs": pg_list,
        "activities": act_list,
        "timeline": timeline_events,
    })


@app_bp.route("/individual/api/pi/<int:pg_id>/series")
@login_required
def bireysel_api_pg_series(pg_id):
    """Seçilen PG için yıllık veri serisi (modal / sparkline)."""
    year = request.args.get("year", datetime.now().year, type=int)
    pg = IndividualPerformanceIndicator.query.filter_by(
        id=pg_id, user_id=current_user.id, is_active=True
    ).first_or_404()

    entries = (
        IndividualKpiData.query.filter_by(individual_pg_id=pg.id, year=year)
        .order_by(IndividualKpiData.data_date, IndividualKpiData.id)
        .all()
    )

    series = []
    monthly_last = {m: None for m in range(1, 13)}
    for e in entries:
        series.append({
            "data_date": e.data_date.isoformat() if e.data_date else None,
            "actual_value": e.actual_value,
            "description": e.description,
            "period_type": e.period_type,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        })
        if e.data_date:
            for key in data_date_to_period_keys(e.data_date, year):
                if key.startswith("aylik_"):
                    try:
                        m = int(key.split("_", 1)[1])
                        if 1 <= m <= 12:
                            monthly_last[m] = e.actual_value
                    except (ValueError, IndexError):
                        pass

    return jsonify({
        "success": True,
        "pg": {
            "id": pg.id,
            "name": pg.name,
            "target_value": pg.target_value,
            "unit": pg.unit,
            "direction": pg.direction,
        },
        "year": year,
        "series": series,
        "monthly": {str(k): v for k, v in monthly_last.items()},
    })



# ── Hizalama Skoru ────────────────────────────────────────────────────────────

@app_bp.route("/individual/api/alignment-score")
@login_required
def bireysel_api_hizalama_skoru():
    """Oturum kullanıcısının bireysel→stratejik hizalama skorunu döner."""
    from services.alignment_score_service import get_user_alignment_score
    data = get_user_alignment_score(current_user.id, current_user.tenant_id)
    return jsonify({"success": True, "data": data})


@app_bp.route("/individual/api/team-alignment")
@login_required
def bireysel_api_ekip_hizalama():
    """Yöneticiler için tüm ekip hizalama özeti."""
    _MANAGE_ROLES = ("tenant_admin", "executive_manager", "Admin")
    if not current_user.role or current_user.role.name not in _MANAGE_ROLES:
        return jsonify({"success": False, "message": "Yetkisiz."}), 403
    from services.alignment_score_service import get_team_alignment_summary
    data = get_team_alignment_summary(current_user.tenant_id)
    return jsonify({"success": True, "data": data})


# ── Bireysel Karne PDF Export (Sprint 11.3) ──────────────────────────────────

@app_bp.route("/individual/api/scorecard/export-pdf")
@login_required
def bireysel_api_karne_export_pdf():
    """Kullanıcının bireysel karnesini PDF olarak indir."""
    from app.utils.pdf_export import make_pdf, kvp_table
    from app.models.process import IndividualPerformanceIndicator
    from app.models.core import Tenant
    from flask import send_file
    import io
    import datetime as _dt

    try:
        year = request.args.get("year", _dt.date.today().year, type=int)
        tenant = Tenant.query.get(current_user.tenant_id) if current_user.tenant_id else None

        pgs = (
            IndividualPerformanceIndicator.query
            .filter_by(user_id=current_user.id, is_active=True)
            .all()
        )

        if pgs:
            pg_table = [["Kod", "PG Adı", "Birim", "Hedef", "Ağırlık"]]
            for pg in pgs:
                pg_table.append([
                    str(pg.code or "—"),
                    str(pg.name or "—"),
                    str(pg.unit or "—"),
                    str(pg.target_value or "—"),
                    f"%{pg.weight}" if pg.weight else "—",
                ])
        else:
            pg_table = [["Bilgi"], ["Henüz atanmış bireysel PG yok."]]

        full_name = f"{current_user.first_name or ''} {current_user.last_name or ''}".strip()
        sections = [
            {
                "heading": "Kullanıcı Bilgileri",
                "table": kvp_table([
                    ("Ad Soyad", full_name or current_user.email),
                    ("E-posta", current_user.email),
                    ("Unvan", current_user.job_title or "—"),
                    ("Departman", current_user.department or "—"),
                    ("Plan yılı", year),
                ]),
            },
            {
                "heading": "Bireysel Performans Göstergeleri",
                "table": pg_table,
            },
        ]

        pdf_bytes = make_pdf(
            title="Bireysel Performans Karnesi",
            sections=sections,
            tenant_name=tenant.name if tenant else None,
            footer=f"Kokpitim · {_dt.date.today().isoformat()}",
        )

        safe_name = (full_name or current_user.email or "karne").replace(" ", "_")
        return send_file(
            io.BytesIO(pdf_bytes),
            as_attachment=True,
            download_name=f"bireysel-karne-{safe_name}-{year}.pdf",
            mimetype="application/pdf",
        )
    except Exception as e:
        current_app.logger.error(f"[bireysel_karne_pdf] {e}", exc_info=True)
        return jsonify({"success": False, "message": _("PDF oluşturulamadı.")}), 500


# ── Inline AI Özet (bireysel karne üstü) ──────────────────────────────────────

def _bireysel_heuristik_ozet(year, total_pg, pg_with_data, aktif_fa, geciken_fa):
    """LLM olmadan da çalışan deterministik Türkçe bireysel performans özeti."""
    parts = []
    if total_pg:
        cov = round((pg_with_data / total_pg) * 100) if total_pg else 0
        parts.append(f"{year} yılında {total_pg} performans göstergen var, %{cov}'ine veri girilmiş.")
        if pg_with_data < total_pg:
            parts.append(f"{total_pg - pg_with_data} PG'ye henüz veri girmedin.")
    else:
        parts.append(f"{year} için tanımlı performans göstergen yok.")
    if geciken_fa:
        parts.append(f"Kırmızı bayrak: {geciken_fa} geciken faaliyet.")
    elif aktif_fa:
        parts.append(f"{aktif_fa} aktif faaliyetin sürüyor.")
    if not parts:
        parts.append("Özet üretecek yeterli veri yok.")
    return " ".join(parts)


@app_bp.route("/individual/api/ai-summary")
@login_required
def bireysel_api_ai_ozet():
    """Bireysel karne üstü 2 cümlelik Türkçe AI özet (heuristik + opsiyonel LLM)."""
    from datetime import date as _date
    uid = current_user.id
    year = request.args.get("year", datetime.now().year, type=int)
    today = _date.today()

    pg_ids = [r[0] for r in db.session.query(IndividualPerformanceIndicator.id)
              .filter_by(user_id=uid, is_active=True).all()]
    total_pg = len(pg_ids)
    pg_with_data = 0
    if pg_ids:
        pg_with_data = (
            db.session.query(IndividualKpiData.individual_pg_id)
            .filter(IndividualKpiData.individual_pg_id.in_(pg_ids),
                    IndividualKpiData.year == year)
            .distinct().count()
        )

    acts = IndividualActivity.query.filter_by(user_id=uid, is_active=True).all()
    aktif_fa = sum(1 for a in acts if a.status != "Tamamlandı")
    geciken_fa = sum(1 for a in acts if a.status != "Tamamlandı" and a.end_date and a.end_date < today)

    ozet = _bireysel_heuristik_ozet(year, total_pg, pg_with_data, aktif_fa, geciken_fa)
    kaynak = "heuristik"
    try:
        from app.services.llm_gateway import call_llm
        ad = (current_user.first_name or "").strip() or "Kullanıcı"
        veri = (f"Kullanıcı: {ad}. Yıl: {year}. PG sayısı: {total_pg}, veri girilen: {pg_with_data}. "
                f"Aktif faaliyet: {aktif_fa}, geciken: {geciken_fa}.")
        prompt = ("Aşağıdaki bireysel performans verisinden 2 cümlelik Türkçe özet yaz: "
                  "ilerleme durumu ve bu hafta odak. Teşvik edici ama abartısız.\n\n" + veri)
        res = call_llm(
            tenant_id=current_user.tenant_id, endpoint="bireysel_ozet",
            prompt=prompt,
            system_prompt="Sen kısa konuşan bir Türkçe performans koçusun.",
            user_id=uid, max_output_tokens=200,
        )
        if isinstance(res, dict) and res.get("text"):
            ozet = res["text"].strip()
            kaynak = "ai"
    except Exception as e:
        current_app.logger.info(f"[bireysel-ai-ozet] LLM fallback ({e})")

    return jsonify({"success": True, "ozet": ozet, "kaynak": kaynak})
