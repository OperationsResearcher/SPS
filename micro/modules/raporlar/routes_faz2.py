"""Faz 2 — Persona dashboard'ları (CFO, COO, CHRO, quarterly review, strateji hikayesi)."""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone, date as _date

from flask import render_template, jsonify, request, current_app, send_file
from flask_login import login_required, current_user
from sqlalchemy import func, and_, or_, text, select

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

# ═══════════════════════════════════════════════════════════════════════════
# FAZ 2 — PERSONA DASHBOARDS + AI ÜRÜNLERİ
# ═══════════════════════════════════════════════════════════════════════════

# ─── PD-01: CFO Dashboard ──────────────────────────────────────────────────

@app_bp.route("/reports/cfo-dashboard")
@login_required
def raporlar_cfo_dashboard():
    return render_template("platform/reports/cfo_dashboard.html")


@app_bp.route("/reports/api/cfo-dashboard")
@login_required
def raporlar_api_cfo_dashboard():
    from app.models.llm_usage import LLMUsageLog
    tid = _tid_or_none()
    if not tid:
        return jsonify({"success": False, "message": "Tenant yok"}), 400

    # Initiative bütçe özeti
    inits = Initiative.query.filter_by(tenant_id=tid, is_active=True).all()
    total_budget = sum(float(i.budget_total or 0) for i in inits)
    total_spent = sum(float(i.budget_spent or 0) for i in inits)
    over_budget = sum(1 for i in inits if (i.budget_spent or 0) > (i.budget_total or 0))

    # En büyük 5 initiative
    top5_inits = sorted(inits, key=lambda x: float(x.budget_total or 0), reverse=True)[:5]
    top5 = [{
        "code": i.code, "name": i.name, "status": i.status,
        "budget": float(i.budget_total or 0),
        "spent": float(i.budget_spent or 0),
        "progress": i.progress_pct or 0,
        "usage_pct": round(float(i.budget_spent or 0) / float(i.budget_total or 1) * 100, 1) if i.budget_total else 0,
    } for i in top5_inits]

    # LLM kullanım maliyeti (son 30 gün)
    last_30 = datetime.now(timezone.utc) - timedelta(days=30)
    llm_cost = db.session.query(func.coalesce(func.sum(LLMUsageLog.cost_usd), 0)).filter(
        LLMUsageLog.tenant_id == tid,
        LLMUsageLog.created_at >= last_30,
    ).scalar() or 0
    llm_calls = LLMUsageLog.query.filter(
        LLMUsageLog.tenant_id == tid,
        LLMUsageLog.created_at >= last_30,
    ).count()

    # Recurring task tahmini (yıllık)
    try:
        from app.models.portfolio_project import RecurringTask, Project
        recurring = db.session.query(func.count(RecurringTask.id)).join(
            Project, Project.id == RecurringTask.project_id,
        ).filter(Project.tenant_id == tid, RecurringTask.is_active.is_(True)).scalar() or 0
    except Exception:
        recurring = 0

    # Status dağılımı
    by_status = defaultdict(int)
    for i in inits:
        by_status[i.status] += 1

    # Strateji bazlı bütçe atıf
    by_strategy = defaultdict(lambda: {"budget": 0, "spent": 0, "count": 0})
    for i in inits:
        key = i.strategy_id or 0
        by_strategy[key]["budget"] += float(i.budget_total or 0)
        by_strategy[key]["spent"] += float(i.budget_spent or 0)
        by_strategy[key]["count"] += 1

    strat_budgets = []
    for sid, d in by_strategy.items():
        if sid:
            s = db.session.get(Strategy, sid)
            label = f"{s.code} {s.title}" if s else f"#{sid}"
        else:
            label = "(stratejisiz)"
        strat_budgets.append({
            "label": label, "budget": d["budget"], "spent": d["spent"],
            "count": d["count"],
            "usage_pct": round(d["spent"] / d["budget"] * 100, 1) if d["budget"] else 0,
        })
    strat_budgets.sort(key=lambda x: -x["budget"])

    return jsonify({"success": True, "metrics": {
        "total_budget": total_budget,
        "total_spent": total_spent,
        "remaining": total_budget - total_spent,
        "usage_pct": round(total_spent / total_budget * 100, 1) if total_budget else 0,
        "initiative_count": len(inits),
        "over_budget_count": over_budget,
        "llm_cost_30d_usd": float(llm_cost),
        "llm_calls_30d": llm_calls,
        "recurring_count": recurring,
    }, "by_status": dict(by_status),
       "top_initiatives": top5,
       "by_strategy": strat_budgets[:10]})


# ─── PD-02: COO Dashboard ──────────────────────────────────────────────────

@app_bp.route("/reports/coo-dashboard")
@login_required
def raporlar_coo_dashboard():
    return render_template("platform/reports/coo_dashboard.html")


@app_bp.route("/reports/api/coo-dashboard")
@login_required
def raporlar_api_coo_dashboard():
    from app.models.k_radar_domain import BottleneckLog, ProcessMaturity
    tid = _tid_or_none()
    if not tid:
        return jsonify({"success": False, "message": "Tenant yok"}), 400

    active_py = get_active_plan_year_for_user(current_user)
    py_id = active_py.id if active_py else None

    # Süreç skorları
    try:
        today = _date.today()
        proc_scores, _ = compute_process_scores_internal(
            tid, active_py.year if active_py else today.year, today,
            persist_pg_scores=False, plan_year=active_py,
        )
    except Exception:
        proc_scores = {}

    procs = Process.query.filter_by(
        tenant_id=tid, is_active=True,
        plan_year_id=py_id,
    ).order_by(Process.code).all() if py_id else Process.query.filter_by(tenant_id=tid, is_active=True).all()

    proc_health = []
    for p in procs:
        score = proc_scores.get(p.id)
        proc_health.append({
            "id": p.id, "code": p.code, "name": p.name,
            "score": round(score, 1) if score is not None else None,
            "weight": p.weight,
        })

    # Skor dağılımı
    scored = [p["score"] for p in proc_health if p["score"] is not None]
    distribution = {
        "good": sum(1 for s in scored if s >= 70),
        "medium": sum(1 for s in scored if 50 <= s < 70),
        "low": sum(1 for s in scored if s < 50),
        "no_data": len(proc_health) - len(scored),
    }

    # Darboğaz
    bottlenecks = BottleneckLog.query.filter_by(tenant_id=tid, is_active=True).order_by(
        BottleneckLog.triggered_at.desc().nullslast()
    ).limit(10).all()
    bn_list = [{
        "id": b.id, "process_id": b.process_id, "severity": b.severity, "note": b.note,
        "triggered_at": b.triggered_at.isoformat() if b.triggered_at else None,
        "resolved": b.resolved_at is not None,
    } for b in bottlenecks]

    # Geciken faaliyet sayımı
    overdue_count = ProcessActivity.query.join(Process).filter(
        Process.tenant_id == tid,
        ProcessActivity.is_active.is_(True),
        ProcessActivity.end_at < datetime.now(timezone.utc),
        ProcessActivity.status != "Tamamlandı",
    ).count()

    # CMMI ortalama
    maturity_rows = db.session.query(func.avg(ProcessMaturity.maturity_level)).filter(
        ProcessMaturity.tenant_id == tid, ProcessMaturity.is_active.is_(True),
    ).scalar()
    avg_cmmi = round(float(maturity_rows), 2) if maturity_rows else None

    return jsonify({"success": True, "metrics": {
        "total_processes": len(proc_health),
        "avg_score": round(sum(scored) / len(scored), 1) if scored else None,
        "overdue_activities": overdue_count,
        "active_bottlenecks": sum(1 for b in bottlenecks if not b.resolved_at),
        "avg_cmmi_level": avg_cmmi,
    }, "distribution": distribution,
       "processes": proc_health,
       "bottlenecks": bn_list})


# ─── PD-03: CHRO Dashboard ──────────────────────────────────────────────────

@app_bp.route("/reports/chro-dashboard")
@login_required
def raporlar_chro_dashboard():
    return render_template("platform/reports/chro_dashboard.html")


@app_bp.route("/reports/api/chro-dashboard")
@login_required
def raporlar_api_chro_dashboard():
    tid = _tid_or_none()
    if not tid:
        return jsonify({"success": False, "message": "Tenant yok"}), 400

    # Çalışan + departman özeti
    total_users = User.query.filter_by(tenant_id=tid, is_active=True).count()
    totp_enabled = User.query.filter_by(tenant_id=tid, is_active=True, totp_enabled=True).count()

    dept_rows = db.session.query(
        User.department, func.count(User.id),
    ).filter(User.tenant_id == tid, User.is_active.is_(True)).group_by(User.department).all()
    departments = [{"dept": d or "(belirsiz)", "count": c} for d, c in dept_rows]
    departments.sort(key=lambda x: -x["count"])

    # Bireysel PG özeti
    pg_users = db.session.query(func.count(func.distinct(IndividualPerformanceIndicator.user_id))).join(
        User, User.id == IndividualPerformanceIndicator.user_id
    ).filter(
        User.tenant_id == tid, User.is_active.is_(True),
        IndividualPerformanceIndicator.is_active.is_(True),
    ).scalar() or 0
    total_pgs = db.session.query(func.count(IndividualPerformanceIndicator.id)).join(
        User, User.id == IndividualPerformanceIndicator.user_id
    ).filter(
        User.tenant_id == tid, User.is_active.is_(True),
        IndividualPerformanceIndicator.is_active.is_(True),
    ).scalar() or 0

    # Rol dağılımı — kanonik etiketler (tek kaynak: app.constants.roles)
    from app.models.core import Role
    from app.constants.roles import role_label_tr
    role_rows = db.session.query(Role.name, func.count(User.id)).join(
        User, User.role_id == Role.id
    ).filter(User.tenant_id == tid, User.is_active.is_(True)).group_by(Role.name).all()
    roles = [{"role": role_label_tr(r), "count": c} for r, c in role_rows]

    # En çok bireysel PG sahibi top 10 user
    top_user_rows = db.session.query(
        User.id, User.first_name, User.last_name, User.email, User.department,
        func.count(IndividualPerformanceIndicator.id).label("pg_count"),
    ).join(IndividualPerformanceIndicator, IndividualPerformanceIndicator.user_id == User.id).filter(
        User.tenant_id == tid, User.is_active.is_(True),
        IndividualPerformanceIndicator.is_active.is_(True),
    ).group_by(User.id, User.first_name, User.last_name, User.email, User.department).order_by(
        func.count(IndividualPerformanceIndicator.id).desc()
    ).limit(10).all()
    top_users = [{
        "id": r[0], "name": f"{r[1] or ''} {r[2] or ''}".strip() or r[3],
        "email": r[3], "department": r[4], "pg_count": r[5],
    } for r in top_user_rows]

    # Süreç-üye M:N (her kullanıcı kaç süreçte üye)
    from app.models.process import process_members
    member_rows = db.session.query(
        process_members.c.user_id, func.count(process_members.c.process_id),
    ).join(Process, Process.id == process_members.c.process_id).filter(
        Process.tenant_id == tid, Process.is_active.is_(True),
    ).group_by(process_members.c.user_id).all()
    process_membership = {uid: cnt for uid, cnt in member_rows}
    most_loaded = sorted(process_membership.items(), key=lambda x: -x[1])[:5]
    most_loaded_users = []
    for uid, cnt in most_loaded:
        u = db.session.get(User, uid)
        if u:
            most_loaded_users.append({
                "id": uid, "name": f"{u.first_name or ''} {u.last_name or ''}".strip() or u.email,
                "process_count": cnt,
            })

    return jsonify({"success": True, "metrics": {
        "total_users": total_users,
        "total_departments": len(departments),
        "totp_pct": round(totp_enabled / max(total_users, 1) * 100, 1),
        "users_with_pg": pg_users,
        "total_pgs": total_pgs,
        "avg_pg_per_user": round(total_pgs / max(pg_users, 1), 1),
    }, "departments": departments[:15],
       "roles": roles,
       "top_users_by_pg": top_users,
       "most_loaded_in_processes": most_loaded_users})


# ─── AI-11: AI Quarterly Review Hazırlayıcısı ──────────────────────────────

@app_bp.route("/reports/quarterly-review")
@login_required
def raporlar_quarterly_review():
    return render_template("platform/reports/quarterly_review.html")


@app_bp.route("/reports/api/quarterly-review")
@login_required
def raporlar_api_quarterly_review():
    tid = _tid_or_none()
    if not tid:
        return jsonify({"success": False, "message": "Tenant yok"}), 400

    today = _date.today()
    quarter = (today.month - 1) // 3 + 1
    active_py = get_active_plan_year_for_user(current_user)

    # Son çeyreğin metrikleri
    q_start_month = (quarter - 1) * 3 + 1
    q_start = _date(today.year, q_start_month, 1)
    if quarter < 4:
        q_end = _date(today.year, q_start_month + 3, 1) - timedelta(days=1)
    else:
        q_end = _date(today.year, 12, 31)

    # Çeyrek içinde girilen KPI ölçüm sayısı
    proc_ids = db.session.query(Process.id).filter(
        Process.tenant_id == tid, Process.is_active.is_(True),
    ).subquery()
    kpi_ids = db.session.query(ProcessKpi.id).filter(
        ProcessKpi.process_id.in_(proc_ids), ProcessKpi.is_active.is_(True),
    ).subquery()

    measurements_q = KpiData.query.filter(
        KpiData.process_kpi_id.in_(kpi_ids),
        KpiData.data_date.between(q_start, q_end),
        KpiData.is_active.is_(True),
    ).count()

    # Yeni initiative + biten initiative bu çeyrek
    new_inits = Initiative.query.filter(
        Initiative.tenant_id == tid,
        Initiative.created_at >= q_start,
    ).count()
    completed_inits = Initiative.query.filter(
        Initiative.tenant_id == tid,
        Initiative.status == "completed",
        Initiative.updated_at >= q_start,
    ).count()

    # AI ile çeyrek özeti üret
    summary_text = (
        f"{today.year} Q{quarter} ({q_start.strftime('%d %b')} - {q_end.strftime('%d %b')}) "
        f"döneminde sistem {measurements_q:,} KPI ölçümü topladı. "
        f"{new_inits} yeni stratejik girişim başlatıldı, {completed_inits} girişim tamamlandı. "
        "Çeyrek değerlendirme toplantısı için aşağıdaki gündem önerilmektedir."
    )
    try:
        from app.services.llm_gateway import call_llm
        prompt = (
            f"Türkçe, 3-4 cümlelik bir çeyrek değerlendirme özeti yaz. "
            f"Çeyrek: {today.year} Q{quarter}. "
            f"Veri: {measurements_q} ölçüm, {new_inits} yeni girişim, {completed_inits} tamamlanmış girişim. "
            "Resmî, yöneticiye uygun ton."
        )
        r = call_llm(prompt=prompt, tenant_id=tid, user_id=current_user.id,
                     endpoint="ai_quarterly_review", max_output_tokens=300)
        if r and r.get("text"):
            summary_text = r["text"].strip()
    except Exception as e:
        current_app.logger.info(f"[quarterly-review] LLM fallback: {e}")

    # Önerilen ajanda
    agenda = [
        f"1. Yönetici özeti — {today.year} Q{quarter} performans snapshot (10 dk)",
        "2. Stratejik hedef başarı durumu (Vizyon skor + 6 ana strateji) (15 dk)",
        "3. Initiative portföyü gözden geçirme + bütçe durumu (20 dk)",
        "4. OKR check-in — KR ilerlemeleri (15 dk)",
        "5. Risk register güncelleme — yeni risk + mitigation (10 dk)",
        "6. Önümüzdeki çeyrek için odak alanları ve replan kararları (15 dk)",
        "7. Açık tartışma ve aksiyon maddeleri (15 dk)",
    ]

    # Ön çalışma soruları
    prep_questions = [
        "Bu çeyrekte hedeflerinin altında kalan PG'ler için sebep analizi hazırlandı mı?",
        "Bütçe sapması olan initiative'ler için açıklama metni var mı?",
        "Yeni risk olarak değerlendirilmesi gereken durumlar belirlendi mi?",
        "Önümüzdeki çeyrek için yeni initiative önerisi var mı?",
        "Geçen çeyreğin aksiyon maddelerinin durumu güncellendi mi?",
    ]

    return jsonify({"success": True, "data": {
        "year": today.year, "quarter": quarter,
        "period_start": q_start.isoformat(), "period_end": q_end.isoformat(),
        "plan_year": active_py.year if active_py else None,
        "metrics": {
            "measurements_q": measurements_q,
            "new_initiatives": new_inits,
            "completed_initiatives": completed_inits,
        },
        "ai_summary": summary_text,
        "agenda": agenda,
        "prep_questions": prep_questions,
    }})


# ─── AI-12: AI Strateji Hikayeleştirici ────────────────────────────────────

@app_bp.route("/reports/strategy-story")
@login_required
def raporlar_strateji_hikayesi():
    return render_template("platform/reports/strateji_hikayesi.html")


@app_bp.route("/reports/api/strategy-story")
@login_required
def raporlar_api_strateji_hikayesi():
    tid = _tid_or_none()
    if not tid:
        return jsonify({"success": False, "message": "Tenant yok"}), 400

    tenant = db.session.get(Tenant, tid)
    py_list = list_plan_years(tid)
    if not py_list:
        return jsonify({"success": True, "data": {"narrative": "Henüz plan yılı yok.", "highlights": []}})

    py_sorted = sorted(py_list, key=lambda x: x.year)
    # Tüm yıllar için sayımları 4 sorguda topla (N+1 önlemi: yıl başına 4 query patlatıyordu)
    _py_ids = [py.id for py in py_sorted]
    _years = [py.year for py in py_sorted]
    _s_counts = dict(db.session.query(Strategy.plan_year_id, func.count(Strategy.id)).filter(
        Strategy.tenant_id == tid, Strategy.is_active.is_(True), Strategy.plan_year_id.in_(_py_ids)
    ).group_by(Strategy.plan_year_id).all())
    _p_counts = dict(db.session.query(Process.plan_year_id, func.count(Process.id)).filter(
        Process.tenant_id == tid, Process.is_active.is_(True), Process.plan_year_id.in_(_py_ids)
    ).group_by(Process.plan_year_id).all())
    _k_counts = dict(db.session.query(Process.plan_year_id, func.count(ProcessKpi.id))
        .join(ProcessKpi, ProcessKpi.process_id == Process.id)
        .filter(Process.tenant_id == tid, Process.plan_year_id.in_(_py_ids),
                ProcessKpi.is_active.is_(True))
        .group_by(Process.plan_year_id).all())
    _m_counts = dict(db.session.query(KpiData.year, func.count(KpiData.id)).filter(
        KpiData.year.in_(_years)
    ).group_by(KpiData.year).all())

    snapshots = []
    for py in py_sorted:
        snapshots.append({
            "year": py.year, "status": py.status,
            "strategy_count": _s_counts.get(py.id, 0),
            "process_count": _p_counts.get(py.id, 0),
            "kpi_count": _k_counts.get(py.id, 0),
            "measurement_count": _m_counts.get(py.year, 0),
        })

    # Kırılım noktaları (yıl yıl yapısal değişim)
    highlights = []
    for i in range(1, len(snapshots)):
        prev, curr = snapshots[i - 1], snapshots[i]
        delta_s = curr["strategy_count"] - prev["strategy_count"]
        delta_p = curr["process_count"] - prev["process_count"]
        if abs(delta_s) >= 1 or abs(delta_p) >= 2:
            highlights.append({
                "year": curr["year"],
                "change": f"Strateji {prev['strategy_count']}→{curr['strategy_count']}, Süreç {prev['process_count']}→{curr['process_count']}",
            })

    # AI ile hikaye yaz
    fallback_narrative = (
        f"{tenant.name if tenant else 'Kurum'} {snapshots[0]['year']} yılında "
        f"{snapshots[0]['strategy_count']} stratejik direkle başlayıp "
        f"{snapshots[-1]['year']} yılına {snapshots[-1]['strategy_count']} strateji + "
        f"{snapshots[-1]['process_count']} süreçle ulaştı. "
        f"Toplam {sum(s['measurement_count'] for s in snapshots):,} ölçüm verisi "
        "stratejik kararların temelini oluşturdu."
    )
    narrative = fallback_narrative
    try:
        from app.services.llm_gateway import call_llm
        data_str = "\n".join([
            f"  {s['year']}: {s['strategy_count']} strateji, {s['process_count']} süreç, {s['kpi_count']} PG, {s['measurement_count']:,} ölçüm"
            for s in snapshots
        ])
        prompt = (
            f"Sen kurumsal stratejik danışmansın. {tenant.name if tenant else 'Bir kurum'} için "
            f"{len(snapshots)} yıllık stratejik plan evrimini anlatan 4-6 cümlelik bir hikaye yaz. "
            f"Veri:\n{data_str}\n\n"
            f"Önemli değişim noktaları: {[h['year'] for h in highlights]}.\n"
            "Resmî ama akıcı bir dil kullan. Sayılarla başla, evrime ve dönüşüme vurgu yap."
        )
        r = call_llm(prompt=prompt, tenant_id=tid, user_id=current_user.id,
                     endpoint="ai_strateji_hikaye", max_output_tokens=600)
        if r and r.get("text"):
            narrative = r["text"].strip()
    except Exception as e:
        current_app.logger.info(f"[strateji-hikaye] LLM fallback: {e}")

    return jsonify({"success": True, "data": {
        "tenant_name": tenant.name if tenant else "—",
        "year_range": f"{snapshots[0]['year']}–{snapshots[-1]['year']}",
        "narrative": narrative,
        "snapshots": snapshots,
        "highlights": highlights,
    }})


