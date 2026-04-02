"""Bireysel Performans modülü."""

from datetime import datetime, timezone, date

from flask import render_template, jsonify, request, current_app, redirect, url_for
from flask_login import login_required, current_user

from platform_core import app_bp
from app_platform.modules.surec.permissions import user_can_enter_pgv
from app.models import db
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


def _is_individual_pg_pk_duplicate(err: Exception) -> bool:
    return is_pk_duplicate(err, "individual_performance_indicators")


# ── Sayfa ─────────────────────────────────────────────────────────────────────

@app_bp.route("/bireysel/karne")
@login_required
def bireysel_karne():
    """Bireysel karne sayfası."""
    current_year = datetime.now().year
    return render_template(
        "platform/bireysel/karne.html",
        current_year=current_year,
    )


@app_bp.route("/bireysel")
@login_required
def bireysel():
    """Bireysel modül giriş yönlendirmesi."""
    return redirect(url_for("app_bp.bireysel_karne"))


# ── API: Bireysel PG CRUD ─────────────────────────────────────────────────────

@app_bp.route("/bireysel/api/pg/ensure-from-process-kpi", methods=["POST"])
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
        return jsonify({"success": False, "message": "Geçersiz process_kpi_id."}), 400

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
        return jsonify({"success": False, "message": "PG bulunamadı."}), 404

    proc = Process.query.filter_by(
        id=kpi.process_id, tenant_id=current_user.tenant_id, is_active=True
    ).first()
    if not proc or not user_can_enter_pgv(current_user, proc):
        return jsonify({"success": False, "message": "Bu PG için veri girişi yapamazsınız."}), 403

    existing = IndividualPerformanceIndicator.query.filter_by(
        user_id=current_user.id,
        source_process_kpi_id=kpi.id,
        is_active=True,
    ).first()
    if existing:
        return jsonify({"success": True, "id": existing.id, "created": False})

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
            return jsonify({"success": False, "message": str(e)}), 400


@app_bp.route("/bireysel/api/pg/add", methods=["POST"])
@login_required
def bireysel_api_pg_add():
    data = request.get_json() or {}
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
            if attempt == 1 and _is_individual_pg_pk_duplicate(e):
                sync_pg_sequence_if_needed("individual_performance_indicators", "id")
                db.session.commit()
                continue
            current_app.logger.error(f"[bireysel_api_pg_add] {e}")
            return jsonify({"success": False, "message": str(e)}), 400


@app_bp.route("/bireysel/api/pg/update/<int:pg_id>", methods=["POST"])
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


@app_bp.route("/bireysel/api/pg/delete/<int:pg_id>", methods=["POST"])
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

@app_bp.route("/bireysel/api/veri/add", methods=["POST"])
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

@app_bp.route("/bireysel/api/faaliyet/add", methods=["POST"])
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


@app_bp.route("/bireysel/api/faaliyet/update/<int:act_id>", methods=["POST"])
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


@app_bp.route("/bireysel/api/faaliyet/delete/<int:act_id>", methods=["POST"])
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


@app_bp.route("/bireysel/api/faaliyet/track/<int:act_id>", methods=["POST"])
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

@app_bp.route("/bireysel/api/favori/toggle/<int:kpi_id>", methods=["POST"])
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

@app_bp.route("/bireysel/api/karne")
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


@app_bp.route("/bireysel/api/pg/<int:pg_id>/series")
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

