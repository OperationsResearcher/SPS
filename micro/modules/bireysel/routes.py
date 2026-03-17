"""Bireysel Performans modülü."""

from datetime import datetime, timezone, date

from flask import render_template, jsonify, request, current_app
from flask_login import login_required, current_user

from micro import micro_bp
from app.models import db
from app.models.process import (
    IndividualPerformanceIndicator,
    IndividualActivity,
    IndividualKpiData,
    IndividualActivityTrack,
    FavoriteKpi,
)
from app.utils.process_utils import last_day_of_period, data_date_to_period_keys


# ── Sayfa ─────────────────────────────────────────────────────────────────────

@micro_bp.route("/bireysel/karne")
@login_required
def bireysel_karne():
    """Bireysel karne sayfası."""
    current_year = datetime.now().year
    return render_template(
        "micro/bireysel/karne.html",
        current_year=current_year,
    )


# ── API: Bireysel PG CRUD ─────────────────────────────────────────────────────

@micro_bp.route("/bireysel/api/pg/add", methods=["POST"])
@login_required
def bireysel_api_pg_add():
    data = request.get_json() or {}
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
        )
        if data.get("start_date"):
            pg.start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
        if data.get("end_date"):
            pg.end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
        db.session.add(pg)
        db.session.commit()
        return jsonify({"success": True, "message": "Bireysel PG eklendi.", "id": pg.id})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[bireysel_api_pg_add] {e}")
        return jsonify({"success": False, "message": str(e)}), 400


@micro_bp.route("/bireysel/api/pg/update/<int:pg_id>", methods=["POST"])
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
        db.session.commit()
        return jsonify({"success": True, "message": "Bireysel PG güncellendi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[bireysel_api_pg_update] {e}")
        return jsonify({"success": False, "message": str(e)}), 400


@micro_bp.route("/bireysel/api/pg/delete/<int:pg_id>", methods=["POST"])
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
        return jsonify({"success": False, "message": str(e)}), 400


# ── API: Bireysel Veri Girişi ─────────────────────────────────────────────────

@micro_bp.route("/bireysel/api/veri/add", methods=["POST"])
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

        last_day = last_day_of_period(year_val, pt, pn, period_month)
        data_date_val = last_day or date.today()

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
        return jsonify({"success": True, "message": "Veri kaydedildi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[bireysel_api_veri_add] {e}")
        return jsonify({"success": False, "message": str(e)}), 400


# ── API: Bireysel Faaliyet CRUD ───────────────────────────────────────────────

@micro_bp.route("/bireysel/api/faaliyet/add", methods=["POST"])
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
        return jsonify({"success": False, "message": str(e)}), 400


@micro_bp.route("/bireysel/api/faaliyet/update/<int:act_id>", methods=["POST"])
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
        return jsonify({"success": True, "message": "Faaliyet güncellendi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[bireysel_api_faaliyet_update] {e}")
        return jsonify({"success": False, "message": str(e)}), 400


@micro_bp.route("/bireysel/api/faaliyet/delete/<int:act_id>", methods=["POST"])
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
        return jsonify({"success": False, "message": str(e)}), 400


@micro_bp.route("/bireysel/api/faaliyet/track/<int:act_id>", methods=["POST"])
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
        return jsonify({"success": False, "message": str(e)}), 400


# ── API: Favori PG toggle ─────────────────────────────────────────────────────

@micro_bp.route("/bireysel/api/favori/toggle/<int:kpi_id>", methods=["POST"])
@login_required
def bireysel_api_favori_toggle(kpi_id):
    """Favori KPI oluştur veya soft delete."""
    try:
        fav = FavoriteKpi.query.filter_by(
            user_id=current_user.id, process_kpi_id=kpi_id
        ).first()
        if fav:
            fav.is_active = not fav.is_active
        else:
            fav = FavoriteKpi(user_id=current_user.id, process_kpi_id=kpi_id, is_active=True)
            db.session.add(fav)
        db.session.commit()
        return jsonify({"success": True, "is_favorite": fav.is_active})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[bireysel_api_favori_toggle] {e}")
        return jsonify({"success": False, "message": str(e)}), 400


# ── API: Bireysel Karne AJAX ──────────────────────────────────────────────────

@micro_bp.route("/bireysel/api/karne")
@login_required
def bireysel_api_karne():
    """Yıl bazlı bireysel PG + faaliyet takip verisi."""
    year = request.args.get("year", datetime.now().year, type=int)
    uid  = current_user.id

    pgs = IndividualPerformanceIndicator.query.filter_by(
        user_id=uid, is_active=True
    ).all()
    activities = IndividualActivity.query.filter_by(
        user_id=uid, is_active=True
    ).all()

    def _parse_float(v):
        try:
            return float(v) if v not in (None, "") else None
        except (ValueError, TypeError):
            return None

    pg_list = []
    for pg in pgs:
        entries = IndividualKpiData.query.filter_by(
            individual_pg_id=pg.id, year=year
        ).order_by(IndividualKpiData.data_date).all()

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
            "entries": entries_by_period,
        })

    act_list = []
    for a in activities:
        tracks = IndividualActivityTrack.query.filter_by(
            individual_activity_id=a.id, user_id=uid, year=year
        ).all()
        act_list.append({
            "id": a.id,
            "name": a.name,
            "status": a.status,
            "progress": a.progress,
            "monthly_tracks": {t.month: t.completed for t in tracks},
        })

    return jsonify({
        "success": True,
        "year": year,
        "pgs": pg_list,
        "activities": act_list,
    })
