"""Faz 5 — Büyük altyapı MVP (mobile, BI connector, ML anomaly, workflow)."""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, date as _date, timezone

from flask import render_template, jsonify, request, current_app, send_file
from flask_login import login_required, current_user
from app.utils.decorators import require_module
from sqlalchemy import func, and_, or_, text, select
from sqlalchemy.orm import joinedload, selectinload

from platform_core import app_bp
from app.models import db
from app.models.core import User, Strategy, SubStrategy, Tenant
from app.models.process import (
    Process, ProcessKpi, KpiData, IndividualPerformanceIndicator,
    ProcessActivity, ProcessSubStrategyLink, process_leaders,
)
from app.models.k_vektor import KVektorStrategyWeight
from app.models.plan_year import PlanYear, KpiYearConfig
from app.models.initiative import Initiative
from app.services.plan_year_service import get_active_plan_year_for_user, list_plan_years
from app.services.score_engine_service import compute_process_scores_internal

from .helpers import _tid_or_none, MUDA_MAX_PROCESSES
from flask_babel import gettext as _

# ═══════════════════════════════════════════════════════════════════════════
# FAZ 5 — BÜYÜK ALTYAPI (MVP'ler)
# ═══════════════════════════════════════════════════════════════════════════

# ─── IF-01: Mobile Hub (PWA-style responsive sayfa) ────────────────────────

@app_bp.route("/k-report/mobile")
@login_required
@require_module("raporlar")
def raporlar_mobile():
    return render_template("platform/raporlar/mobile.html")


@app_bp.route("/k-report/api/mobile/snapshot")
@login_required
@require_module("raporlar")
def raporlar_api_mobile_snapshot():
    """Mobile için kompakt veri snapshot — anasayfa metrikleri."""
    tid = _tid_or_none()
    if not tid:
        return jsonify({"success": False, "message": "Tenant yok"}), 400
    tenant = db.session.get(Tenant, tid)
    active_py = get_active_plan_year_for_user(current_user)

    # Vizyon skor
    try:
        from app.services.score_engine_service import compute_vision_score
        today = _date.today()
        v = compute_vision_score(tid, active_py.year if active_py else today.year,
                                       today, plan_year=active_py)
        vision = v.get('vision_score') if isinstance(v, dict) else v
    except Exception as e:
        current_app.logger.warning(f"[mobile-snapshot] vision_score hesaplanamadı: {e}")
        vision = None

    # Bugün metrikleri
    today = _date.today()
    week_ahead = today + timedelta(days=7)
    proc_ids = db.session.query(Process.id).filter(
        Process.tenant_id == tid, Process.is_active.is_(True)).subquery()
    today_due = ProcessActivity.query.filter(
        ProcessActivity.process_id.in_(proc_ids),
        ProcessActivity.is_active.is_(True),
        func.date(ProcessActivity.end_at) == today,
    ).count()
    upcoming = ProcessActivity.query.filter(
        ProcessActivity.process_id.in_(proc_ids),
        ProcessActivity.is_active.is_(True),
        ProcessActivity.end_at.between(today, week_ahead),
    ).count()
    overdue = ProcessActivity.query.filter(
        ProcessActivity.process_id.in_(proc_ids),
        ProcessActivity.is_active.is_(True),
        ProcessActivity.end_at < datetime.now(timezone.utc),
        ProcessActivity.status != "Tamamlandı",
    ).count()

    # Kullanıcının bireysel PG'si
    my_pgs = IndividualPerformanceIndicator.query.filter_by(
        user_id=current_user.id, is_active=True).count()

    return jsonify({"success": True, "data": {
        "tenant": tenant.name if tenant else "—",
        "user": f"{current_user.first_name or ''} {current_user.last_name or ''}".strip() or current_user.email,
        "vision_score": round(vision, 1) if vision else None,
        "plan_year": active_py.year if active_py else None,
        "metrics": {
            "today_due": today_due,
            "upcoming_7d": upcoming,
            "overdue": overdue,
            "my_pgs": my_pgs,
        },
    }})


# ─── IF-03: BI Connector ───────────────────────────────────────────────────

@app_bp.route("/k-report/bi-connector")
@login_required
@require_module("raporlar")
def raporlar_bi_connector():
    return render_template("platform/raporlar/bi_connector.html")


@app_bp.route("/k-report/api/bi/kpi-data.csv")
@login_required
@require_module("raporlar")
def raporlar_api_bi_kpi_data_csv():
    """KPI ölçümlerini CSV olarak döner (Power BI/Tableau direkt çekebilir)."""
    from flask import Response
    import csv, io
    tid = _tid_or_none()
    if not tid:
        return jsonify({"success": False, "message": "Tenant yok"}), 400

    rows = db.session.query(
        KpiData.id, KpiData.year, KpiData.data_date, KpiData.period_type,
        KpiData.period_no, KpiData.target_value, KpiData.actual_value,
        KpiData.status, KpiData.status_percentage,
        ProcessKpi.code.label("kpi_code"), ProcessKpi.name.label("kpi_name"),
        Process.code.label("process_code"), Process.name.label("process_name"),
    ).join(ProcessKpi, ProcessKpi.id == KpiData.process_kpi_id
    ).join(Process, Process.id == ProcessKpi.process_id
    ).filter(
        Process.tenant_id == tid, Process.is_active.is_(True),
        KpiData.is_active.is_(True),
    ).limit(10000).all()

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["id", "year", "data_date", "period_type", "period_no",
                "target_value", "actual_value", "status", "status_pct",
                "kpi_code", "kpi_name", "process_code", "process_name"])
    for r in rows:
        w.writerow([r[0], r[1], r[2].isoformat() if r[2] else "", r[3], r[4],
                    r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12]])

    return Response(buf.getvalue(), mimetype="text/csv; charset=utf-8",
                    headers={"Content-Disposition": "attachment; filename=kpi_data.csv"})


@app_bp.route("/k-report/api/bi/strategies.json")
@login_required
@require_module("raporlar")
def raporlar_api_bi_strategies_json():
    """Strateji ağacı + skor JSON (BI tool'lar için)."""
    tid = _tid_or_none()
    if not tid:
        return jsonify({"success": False, "message": "Tenant yok"}), 400
    active_py = get_active_plan_year_for_user(current_user)
    py_id = active_py.id if active_py else None

    strat_q = Strategy.query.options(selectinload(Strategy.sub_strategies)).filter_by(tenant_id=tid, is_active=True)
    if py_id: strat_q = strat_q.filter_by(plan_year_id=py_id)

    out = []
    for s in strat_q.order_by(Strategy.code).all():
        out.append({
            "id": s.id, "code": s.code, "title": s.title,
            "sub_count": sum(1 for ss in s.sub_strategies if getattr(ss, "is_active", True)),
            "plan_year_id": s.plan_year_id,
        })
    return jsonify({"plan_year": active_py.year if active_py else None,
                    "strategies": out, "count": len(out)})


# ─── IF-05: ML Anomali (IsolationForest) ───────────────────────────────────

@app_bp.route("/k-report/ml-anomaly")
@login_required
@require_module("raporlar")
def raporlar_ml_anomaly():
    return render_template("platform/raporlar/ml_anomaly.html")


@app_bp.route("/k-report/api/ml-anomaly")
@login_required
@require_module("raporlar")
def raporlar_api_ml_anomaly():
    """IsolationForest tabanlı KPI anomali tespiti."""
    tid = _tid_or_none()
    if not tid:
        return jsonify({"success": False, "message": "Tenant yok"}), 400
    try:
        from sklearn.ensemble import IsolationForest
        import numpy as np
    except ImportError as e:
        return jsonify({"success": False, "message": f"ML kütüphane eksik: {e}"}), 500

    active_py = get_active_plan_year_for_user(current_user)
    py_id = active_py.id if active_py else None

    # PG'leri çek, her PG için son 24 ölçüm sayısal değer
    kpis_q = ProcessKpi.query.options(joinedload(ProcessKpi.process)).join(Process).filter(
        Process.tenant_id == tid, Process.is_active.is_(True),
        ProcessKpi.is_active.is_(True),
    )
    if py_id: kpis_q = kpis_q.filter(Process.plan_year_id == py_id)
    kpis = kpis_q.all()

    # İlk 200 PG için son 24 ölçümü tek sorguda topla (N+1 önlemi: 200 → 1)
    _kpi_subset = kpis[:200]
    _kpi_ids = [k.id for k in _kpi_subset]
    _data_by_kid = defaultdict(list)
    if _kpi_ids:
        for d in KpiData.query.filter(
            KpiData.process_kpi_id.in_(_kpi_ids),
            KpiData.is_active.is_(True),
        ).order_by(KpiData.process_kpi_id, KpiData.data_date.desc()).all():
            if len(_data_by_kid[d.process_kpi_id]) < 24:
                _data_by_kid[d.process_kpi_id].append(d)

    anomalies = []
    analyzed = 0
    for k in _kpi_subset:
        recent = _data_by_kid.get(k.id, [])
        # Sayısal değerleri çek
        values = []
        for r in recent:
            try:
                v = float(r.actual_value)
                values.append((r.data_date, v))
            except (ValueError, TypeError):
                continue
        if len(values) < 8:  # en az 8 nokta gerekli
            continue
        analyzed += 1
        arr = np.array([v[1] for v in values]).reshape(-1, 1)
        try:
            iso = IsolationForest(contamination=0.1, random_state=42, n_estimators=50)
            preds = iso.fit_predict(arr)
            scores = iso.score_samples(arr)
            # Anomali = -1 + score < median
            for i, (dt, v) in enumerate(values):
                if preds[i] == -1:
                    anomalies.append({
                        "kpi_id": k.id, "kpi_code": k.code or f"PG-{k.id}",
                        "kpi_name": k.name,
                        "process_name": k.process.name if k.process else "?",
                        "date": dt.isoformat() if dt else None,
                        "value": v,
                        "anomaly_score": round(float(scores[i]), 3),
                    })
        except Exception as e:
            current_app.logger.warning(f"[ml-anomaly] PG analiz hatası: {e}")
            continue

    # En düşük score (en anormal) ilk
    anomalies.sort(key=lambda x: x["anomaly_score"])

    return jsonify({"success": True, "summary": {
        "kpis_analyzed": analyzed,
        "kpis_skipped": len(kpis) - analyzed,
        "anomalies_found": len(anomalies),
        "method": "IsolationForest (contamination=0.1)",
    }, "anomalies": anomalies[:30]})


# ─── IF-06: Workflow MVP — Initiative Onay Zinciri ────────────────────────

@app_bp.route("/k-report/approval-chain")
@login_required
@require_module("raporlar")
def raporlar_onay_zinciri():
    return render_template("platform/raporlar/onay_zinciri.html")


@app_bp.route("/k-report/api/approval-chain")
@login_required
@require_module("raporlar")
def raporlar_api_onay_zinciri():
    """Initiative onay zinciri MVP — durum + sorumlu + işlem."""
    tid = _tid_or_none()
    if not tid:
        return jsonify({"success": False, "message": "Tenant yok"}), 400

    inits = Initiative.query.filter_by(tenant_id=tid, is_active=True).all()
    items = []
    for i in inits:
        # MVP onay durumu: status'tan türetilmiş
        approval = {
            "planned": "Onay bekliyor",
            "in_progress": "Onaylanmış · yürütmede",
            "completed": "Tamamlandı (geçti)",
            "on_hold": "Beklemeye alındı",
            "cancelled": "Reddedildi",
        }.get(i.status, "—")
        approval_color = {
            "planned": "#f59e0b",
            "in_progress": "#0ea5e9",
            "completed": "#10b981",
            "on_hold": "#94a3b8",
            "cancelled": "#dc2626",
        }.get(i.status, "#64748b")

        owner = None
        if i.owner_user_id:
            u = db.session.get(User, i.owner_user_id)
            owner = f"{u.first_name or ''} {u.last_name or ''}".strip() or u.email if u else None

        priority_tr = {
            "high": "Yüksek", "medium": "Orta", "low": "Düşük",
            "critical": "Kritik",
        }.get((i.priority or "").lower(), i.priority or "—")

        items.append({
            "id": i.id, "code": i.code, "name": i.name,
            "priority": priority_tr,
            "priority_raw": i.priority,
            "status": i.status,
            "approval": approval, "approval_color": approval_color,
            "owner": owner,
            "budget": float(i.budget_total or 0),
            "progress": i.progress_pct or 0,
        })

    # Durum bazlı sayım
    by_approval = defaultdict(int)
    for it in items:
        by_approval[it["approval"]] += 1

    return jsonify({"success": True, "summary": {
        "total": len(items),
        "by_approval": dict(by_approval),
        "pending": by_approval.get("Onay bekliyor", 0),
        "approved": by_approval.get("Onaylanmış · yürütmede", 0),
        "rejected": by_approval.get("Reddedildi", 0),
    }, "items": items})


# ─── PG × Proje Çapraz Etki Analizi (D2) ─────────────────────────────────────

@app_bp.route("/k-report/pi-project-impact")
@login_required
@require_module("raporlar")
def raporlar_pg_proje_etki():
    """PG × Proje çapraz etki analizi sayfası."""
    return render_template("platform/raporlar/pg_proje_etki.html")


@app_bp.route("/k-report/api/pi-project-impact")
@login_required
@require_module("raporlar")
def raporlar_api_pg_proje_etki():
    """Proje × Süreç × PG matrisini ve özet metrikleri döner."""
    from sqlalchemy import text as _t
    from app.extensions import db as _db
    tid = current_user.tenant_id
    if not tid:
        return jsonify({"success": False, "message": _("Kurum bulunamadı.")}), 400
    try:
        # Projeler
        proj_rows = _db.session.execute(_t("""
            SELECT id, name, COALESCE(health_score, 0) AS health_score
            FROM project
            WHERE tenant_id=:t AND COALESCE(is_archived, false) = false
            ORDER BY name LIMIT 80
        """), {"t": tid}).fetchall()
        projects = [{"id": r.id, "name": r.name or "", "health_score": float(r.health_score or 0)} for r in proj_rows]

        # Proje × süreç bağlantıları
        link_rows = _db.session.execute(_t("""
            SELECT prp.project_id AS pid, p.id AS proc_id, p.code, p.name
            FROM project_related_processes prp
            JOIN processes p ON p.id = prp.surec_id
            WHERE p.tenant_id=:t AND p.is_active=true
        """), {"t": tid}).fetchall()
        proj_processes = {}
        all_proc_ids = set()
        for r in link_rows:
            proj_processes.setdefault(r.pid, []).append({
                "id": r.proc_id, "code": r.code or "", "name": r.name or "",
            })
            all_proc_ids.add(r.proc_id)

        # Süreç başına PG sayısı + hedef üstü/altı dağılım
        if all_proc_ids:
            # H-33 fix: ANY(:ids) ve FILTER(WHERE EXISTS...) PostgreSQL-only
            # → SQLite'ta bu endpoint anlamlı veri üretemiyor, dialect guard ekle
            from sqlalchemy import inspect as _sqlinspect
            if _sqlinspect(_db.engine).dialect.name == 'postgresql':
                from sqlalchemy.dialects.postgresql import array as _pgarray
                pg_rows = _db.session.execute(_t(r"""
                    SELECT
                      p.id AS proc_id,
                      count(DISTINCT k.id) AS pg_total,
                      count(DISTINCT k.id) FILTER (
                        WHERE EXISTS (
                          SELECT 1 FROM kpi_data kd
                          WHERE kd.process_kpi_id=k.id AND kd.is_active=true
                            AND kd.actual_value ~ '^-?[0-9]+\.?[0-9]*$'
                            AND kd.target_value ~ '^-?[0-9]+\.?[0-9]*$'
                            AND kd.actual_value::float >= kd.target_value::float
                        )
                      ) AS pg_on_target
                    FROM processes p
                    JOIN process_kpis k ON k.process_id = p.id AND k.is_active=true
                    WHERE p.id = ANY(:ids)
                    GROUP BY p.id
                """), {"ids": list(all_proc_ids)}).fetchall()
            else:
                # SQLite (Yerel geliştirme): basit ORM sorgusu, regex kontrol yok
                pg_rows = _db.session.execute(_t("""
                    SELECT
                      p.id AS proc_id,
                      count(DISTINCT k.id) AS pg_total,
                      0 AS pg_on_target
                    FROM processes p
                    JOIN process_kpis k ON k.process_id = p.id AND k.is_active=1
                    WHERE p.id IN :ids
                    GROUP BY p.id
                """), {"ids": tuple(all_proc_ids)}).fetchall()
            pg_by_proc = {r.proc_id: {"total": int(r.pg_total or 0), "on_target": int(r.pg_on_target or 0)} for r in pg_rows}
        else:
            pg_by_proc = {}

        # Proje başına agregat
        items = []
        for proj in projects:
            procs = proj_processes.get(proj["id"], [])
            total_pg = 0; on_target = 0
            for pr in procs:
                stat = pg_by_proc.get(pr["id"], {})
                total_pg += stat.get("total", 0)
                on_target += stat.get("on_target", 0)
                pr["pg_total"] = stat.get("total", 0)
                pr["pg_on_target"] = stat.get("on_target", 0)
            ratio = round((on_target / total_pg) * 100, 1) if total_pg else None
            items.append({
                "project_id": proj["id"],
                "project_name": proj["name"],
                "health_score": proj["health_score"],
                "process_count": len(procs),
                "pg_total": total_pg,
                "pg_on_target": on_target,
                "pg_on_target_pct": ratio,
                "processes": procs,
            })

        # Özet
        total_projects = len(projects)
        projects_with_pg = sum(1 for it in items if it["pg_total"] > 0)
        avg_ratio = round(sum(it["pg_on_target_pct"] or 0 for it in items if it["pg_on_target_pct"] is not None) / max(projects_with_pg, 1), 1)
        return jsonify({"success": True, "data": {
            "items": items,
            "summary": {
                "projects": total_projects,
                "projects_with_pg": projects_with_pg,
                "projects_without_pg": total_projects - projects_with_pg,
                "avg_pg_on_target_pct": avg_ratio,
                "total_pg_touched": sum(it["pg_total"] for it in items),
            }
        }})
    except Exception as e:
        current_app.logger.error(f"[raporlar_api_pg_proje_etki] {e}", exc_info=True)
        return jsonify({"success": False, "message": _("Veri alınamadı.")}), 500
