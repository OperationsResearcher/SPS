"""Raporlar modülü — yeni rapor önerileri için staging.

Sol menüden "Raporlar" → /raporlar landing → kartlar → tek tek raporlar.
docs/rapor/27mayisraporu.md'deki önerilerden seçilenler burada inşa edilir.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, date as _date

from flask import render_template, jsonify, request, current_app
from flask_login import login_required, current_user
from sqlalchemy import func, and_, or_, text

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


# ─── /raporlar — Landing kart-grid ────────────────────────────────────────────

@app_bp.route("/raporlar")
@login_required
def raporlar_index():
    """Yeni rapor önerileri için landing — kart grid."""
    return render_template("platform/raporlar/index.html")


# ─── Rapor 1: Veri Kalitesi ──────────────────────────────────────────────────

@app_bp.route("/raporlar/veri-kalitesi")
@login_required
def raporlar_veri_kalitesi():
    """Veri Kalitesi Raporu — PG doluluk, eksik alanlar, son giriş tarihleri."""
    return render_template("platform/raporlar/veri_kalitesi.html")


@app_bp.route("/raporlar/api/veri-kalitesi")
@login_required
def raporlar_api_veri_kalitesi():
    """Veri kalitesi metriklerini JSON döner."""
    tid = current_user.tenant_id
    if not tid:
        return jsonify({"success": False, "message": "Tenant yok"}), 400

    active_py = get_active_plan_year_for_user(current_user)
    py_filter = (Process.plan_year_id == active_py.id) if active_py else True

    # Tüm aktif PG'ler (aktif plan yılındaki süreçlere bağlı)
    kpis_q = ProcessKpi.query.join(Process).filter(
        Process.tenant_id == tid,
        Process.is_active.is_(True),
        ProcessKpi.is_active.is_(True),
        py_filter if active_py else True,
    )
    all_kpis = kpis_q.all()
    total_kpi = len(all_kpis)

    if total_kpi == 0:
        return jsonify({
            "success": True,
            "summary": {"total_kpi": 0, "score": 0},
            "categories": {"kritik": [], "orta": [], "iyi": []},
            "department_breakdown": [],
            "by_process": [],
        })

    # Her PG için son ölçüm tarihi + ölçüm sayısı
    kpi_id_to_last = {}
    kpi_id_to_count = {}
    rows = db.session.query(
        KpiData.process_kpi_id,
        func.max(KpiData.data_date),
        func.count(KpiData.id),
    ).filter(
        KpiData.process_kpi_id.in_([k.id for k in all_kpis]),
        KpiData.is_active.is_(True),
    ).group_by(KpiData.process_kpi_id).all()
    for kid, last_date, cnt in rows:
        kpi_id_to_last[kid] = last_date
        kpi_id_to_count[kid] = cnt

    # Kategorize: kritik / orta / iyi
    today = datetime.utcnow().date()
    kritik, orta, iyi = [], [], []

    for k in all_kpis:
        last = kpi_id_to_last.get(k.id)
        cnt = kpi_id_to_count.get(k.id, 0)
        issues = []
        if not last:
            issues.append("hiç ölçüm yok")
        elif (today - last).days > 180:
            issues.append(f"son ölçüm {(today - last).days} gün önce")
        if not k.target_value:
            issues.append("hedef tanımsız")
        if not k.unit:
            issues.append("birim tanımsız")
        if not k.basari_puani_araliklari:
            issues.append("başarı puan aralığı tanımsız")

        item = {
            "id": k.id,
            "code": k.code or f"PG-{k.id}",
            "name": k.name,
            "process_name": k.process.name if k.process else "?",
            "last_data_date": last.isoformat() if last else None,
            "data_count": cnt,
            "issues": issues,
        }
        if len(issues) >= 3 or (not last):
            kritik.append(item)
        elif issues:
            orta.append(item)
        else:
            iyi.append(item)

    # Süreç bazlı doluluk
    by_process = defaultdict(lambda: {"total": 0, "filled": 0, "name": ""})
    for k in all_kpis:
        pname = k.process.name if k.process else "?"
        by_process[k.process_id]["name"] = pname
        by_process[k.process_id]["total"] += 1
        if kpi_id_to_last.get(k.id):
            by_process[k.process_id]["filled"] += 1
    by_process_list = sorted(
        [{"process_id": pid, **v, "fill_rate": round(v["filled"] / v["total"] * 100, 1) if v["total"] else 0}
         for pid, v in by_process.items()],
        key=lambda x: x["fill_rate"]
    )

    # Genel skor
    score = round(
        (len(iyi) * 100 + len(orta) * 60 + len(kritik) * 20) / (total_kpi * 100) * 100, 1
    ) if total_kpi else 0

    return jsonify({
        "success": True,
        "summary": {
            "total_kpi": total_kpi,
            "score": score,
            "kritik_count": len(kritik),
            "orta_count": len(orta),
            "iyi_count": len(iyi),
            "plan_year": active_py.year if active_py else None,
        },
        "categories": {
            "kritik": sorted(kritik, key=lambda x: -len(x["issues"]))[:20],
            "orta": orta[:20],
            "iyi_count_only": len(iyi),
        },
        "by_process": by_process_list,
    })


# ─── Rapor 2: K-Vektör Çarpıklık ──────────────────────────────────────────────

@app_bp.route("/raporlar/k-vektor-carpiklik")
@login_required
def raporlar_kv_carpiklik():
    """K-Vektör Çarpıklık — strateji ağırlığı × skor uyumsuzluğu."""
    return render_template("platform/raporlar/kv_carpiklik.html")


@app_bp.route("/raporlar/api/k-vektor-carpiklik")
@login_required
def raporlar_api_kv_carpiklik():
    """Her ana stratejinin K-Vektör ağırlığı vs gerçek skor uyumsuzluğu."""
    tid = current_user.tenant_id
    if not tid:
        return jsonify({"success": False, "message": "Tenant yok"}), 400

    active_py = get_active_plan_year_for_user(current_user)
    py_id = active_py.id if active_py else None

    # Stratejiler + ağırlık
    strat_q = Strategy.query.filter_by(tenant_id=tid, is_active=True)
    if py_id:
        strat_q = strat_q.filter(or_(Strategy.plan_year_id == py_id, Strategy.plan_year_id.is_(None)))
    strategies = strat_q.order_by(Strategy.code).all()

    weights = {w.strategy_id: w.weight_raw for w in
               KVektorStrategyWeight.query.filter_by(tenant_id=tid).all()}

    # Skor motorundan strateji skorları
    try:
        today = datetime.utcnow().date()
        score_year = active_py.year if active_py else today.year
        proc_scores, _ = compute_process_scores_internal(
            tid, score_year, today, persist_pg_scores=False, plan_year=active_py
        )
    except Exception as e:
        current_app.logger.warning(f"[raporlar/kv-carpiklik] skor hesaplanamadı: {e}")
        proc_scores = {}

    # Her strateji için: alt-strateji aracılığıyla bağlı süreçlerin ortalama skoru
    rows = []
    total_weight = sum(weights.values()) if weights else 0
    for s in strategies:
        sub_ids = [ss.id for ss in s.sub_strategies if getattr(ss, "is_active", True)]
        # bu alt-stratejilere bağlı PG'ler -> hangi süreçlerden
        related_proc_ids = set()
        if sub_ids:
            related_proc_ids = set(r[0] for r in db.session.query(ProcessKpi.process_id).filter(
                ProcessKpi.sub_strategy_id.in_(sub_ids),
                ProcessKpi.is_active.is_(True),
            ).all())
        # bu süreçlerin skor ortalaması
        proc_score_vals = [proc_scores.get(pid) for pid in related_proc_ids
                           if proc_scores.get(pid) is not None]
        avg_score = round(sum(proc_score_vals) / len(proc_score_vals), 1) if proc_score_vals else None

        weight_raw = weights.get(s.id, 0) or 0
        weight_pct = round((weight_raw / total_weight * 100), 1) if total_weight else 0

        # Çarpıklık: yüksek ağırlık + düşük skor = sorunlu
        skew = None
        skew_label = ""
        if avg_score is not None and weight_pct > 0:
            # 0-100 skalada: weight_pct ağırlık, avg_score performans
            skew = round(weight_pct - avg_score, 1)
            if skew > 10:
                skew_label = "Ağır ama düşük performans"
            elif skew < -10:
                skew_label = "Hafif ama yüksek performans"
            else:
                skew_label = "Dengeli"

        rows.append({
            "code": s.code,
            "title": s.title,
            "weight_pct": weight_pct,
            "avg_score": avg_score,
            "skew": skew,
            "skew_label": skew_label,
            "related_process_count": len(related_proc_ids),
        })

    # Genel sağlık: kaç strateji "dengeli"
    balanced = sum(1 for r in rows if r["skew_label"] == "Dengeli")
    unbalanced = sum(1 for r in rows if r["skew_label"] in ("Ağır ama düşük performans", "Hafif ama yüksek performans"))

    return jsonify({
        "success": True,
        "summary": {
            "total_strategies": len(rows),
            "balanced": balanced,
            "unbalanced": unbalanced,
            "plan_year": active_py.year if active_py else None,
        },
        "strategies": rows,
    })


# ─── Rapor 3: Stratejik Hizalama Sankey ──────────────────────────────────────

@app_bp.route("/raporlar/hizalama-sankey")
@login_required
def raporlar_hizalama_sankey():
    return render_template("platform/raporlar/hizalama_sankey.html")


@app_bp.route("/raporlar/api/hizalama-sankey")
@login_required
def raporlar_api_hizalama_sankey():
    """Vizyon → Strateji → Alt Strateji → Süreç akış verisi."""
    tid = current_user.tenant_id
    if not tid:
        return jsonify({"success": False, "message": "Tenant yok"}), 400
    active_py = get_active_plan_year_for_user(current_user)
    py_id = active_py.id if active_py else None

    # Stratejiler + ağırlık
    weights = {w.strategy_id: w.weight_raw or 0 for w in
               KVektorStrategyWeight.query.filter_by(tenant_id=tid).all()}
    total_w = sum(weights.values()) or 1

    strat_q = Strategy.query.filter_by(tenant_id=tid, is_active=True)
    if py_id:
        strat_q = strat_q.filter(or_(Strategy.plan_year_id == py_id, Strategy.plan_year_id.is_(None)))
    strategies = strat_q.order_by(Strategy.code).all()

    nodes = [{"id": "vision", "label": "Vizyon", "level": 0, "color": "#0f172a"}]
    links = []
    node_index = {"vision": 0}

    for s in strategies:
        sid = f"s-{s.id}"
        node_index[sid] = len(nodes)
        nodes.append({
            "id": sid,
            "label": f"{s.code or ''} {s.title}".strip()[:40],
            "level": 1,
            "color": "#4f46e5",
        })
        w = weights.get(s.id, 0)
        links.append({"source": 0, "target": node_index[sid], "value": round(w / total_w * 100, 1)})

        # Alt stratejiler
        for ss in s.sub_strategies:
            if not getattr(ss, "is_active", True):
                continue
            ssid = f"ss-{ss.id}"
            node_index[ssid] = len(nodes)
            nodes.append({
                "id": ssid,
                "label": f"{ss.code or ''} {ss.title}".strip()[:40],
                "level": 2,
                "color": "#8b5cf6",
            })
            links.append({"source": node_index[sid], "target": node_index[ssid], "value": 1})

            # Bağlı süreçler (process_sub_strategy_links)
            for pssl in ss.process_sub_strategy_links:
                p = pssl.process
                if not p or not p.is_active:
                    continue
                if p.tenant_id != tid:
                    continue
                if py_id and p.plan_year_id and p.plan_year_id != py_id:
                    continue
                pid = f"p-{p.id}"
                if pid not in node_index:
                    node_index[pid] = len(nodes)
                    nodes.append({
                        "id": pid,
                        "label": f"{p.code or ''} {p.name}".strip()[:40],
                        "level": 3,
                        "color": "#10b981",
                    })
                contrib = pssl.contribution_pct or 1
                links.append({"source": node_index[ssid], "target": node_index[pid], "value": round(contrib, 1)})

    return jsonify({
        "success": True,
        "summary": {
            "vision_nodes": 1,
            "strategy_nodes": len(strategies),
            "sub_strategy_nodes": sum(1 for n in nodes if n["level"] == 2),
            "process_nodes": sum(1 for n in nodes if n["level"] == 3),
            "total_links": len(links),
            "plan_year": active_py.year if active_py else None,
        },
        "nodes": nodes,
        "links": links,
    })


# ─── Rapor 4: PG Hedef Revizyon Sıklığı ──────────────────────────────────────

@app_bp.route("/raporlar/hedef-revizyon")
@login_required
def raporlar_hedef_revizyon():
    return render_template("platform/raporlar/hedef_revizyon.html")


@app_bp.route("/raporlar/api/hedef-revizyon")
@login_required
def raporlar_api_hedef_revizyon():
    """Yıl bazlı hedef override sayımı (kpi_year_configs vs ProcessKpi.target_value)."""
    tid = current_user.tenant_id
    if not tid:
        return jsonify({"success": False, "message": "Tenant yok"}), 400

    # Tüm plan yıllarını + kpi_year_configs sayımı (override yapılmış PG'ler)
    py_list = list_plan_years(tid)
    py_data = []
    revised_kpis = []  # tek tek revize edilen PG detayı

    for py in py_list:
        configs = KpiYearConfig.query.filter_by(plan_year_id=py.id).all()
        revised_count = 0
        for cfg in configs:
            kpi = cfg.process_kpi
            if not kpi:
                continue
            # Override aktif sayılır: target_value/weight/period vs farklıysa
            differences = []
            if cfg.target_value and cfg.target_value != (kpi.target_value or ""):
                differences.append("hedef")
            if cfg.weight is not None and cfg.weight != (kpi.weight or 0):
                differences.append("ağırlık")
            if cfg.period and cfg.period != (kpi.period or ""):
                differences.append("periyot")
            if differences:
                revised_count += 1
                revised_kpis.append({
                    "year": py.year,
                    "kpi_code": kpi.code or f"PG-{kpi.id}",
                    "kpi_name": kpi.name,
                    "diff_fields": differences,
                    "base_target": kpi.target_value,
                    "year_target": cfg.target_value,
                })

        py_data.append({
            "year": py.year,
            "status": py.status,
            "config_count": len(configs),
            "revised_count": revised_count,
        })

    return jsonify({
        "success": True,
        "summary": {
            "total_years": len(py_list),
            "total_revisions": len(revised_kpis),
            "years_with_revisions": sum(1 for x in py_data if x["revised_count"] > 0),
        },
        "by_year": py_data,
        "revised_kpis": revised_kpis[:50],
    })


# ─── Rapor 5: Departman Performans Skoru ─────────────────────────────────────

@app_bp.route("/raporlar/departman-performans")
@login_required
def raporlar_departman_performans():
    return render_template("platform/raporlar/departman_performans.html")


@app_bp.route("/raporlar/api/departman-performans")
@login_required
def raporlar_api_departman_performans():
    """Departman bazlı kullanıcı + bireysel PG + atanan görev sayısı."""
    tid = current_user.tenant_id
    if not tid:
        return jsonify({"success": False, "message": "Tenant yok"}), 400

    rows = db.session.query(
        User.department,
        func.count(func.distinct(User.id)).label("user_count"),
    ).filter(
        User.tenant_id == tid,
        User.is_active.is_(True),
    ).group_by(User.department).all()

    # Departman başına bireysel PG sayısı + başarı medyanı
    dept_data = []
    for dept, user_count in rows:
        users_in_dept = db.session.query(User.id).filter(
            User.tenant_id == tid, User.is_active.is_(True),
            User.department == dept,
        ).subquery()

        pg_count = db.session.query(func.count(IndividualPerformanceIndicator.id)).filter(
            IndividualPerformanceIndicator.user_id.in_(users_in_dept),
            IndividualPerformanceIndicator.is_active.is_(True),
        ).scalar() or 0

        # Önemli PG sayısı (is_important)
        important_pg = db.session.query(func.count(IndividualPerformanceIndicator.id)).filter(
            IndividualPerformanceIndicator.user_id.in_(users_in_dept),
            IndividualPerformanceIndicator.is_active.is_(True),
            IndividualPerformanceIndicator.is_important.is_(True),
        ).scalar() or 0

        # Departman içindeki kullanıcıların 2FA oranı (security proxy)
        totp_enabled = db.session.query(func.count(User.id)).filter(
            User.tenant_id == tid, User.is_active.is_(True),
            User.department == dept, User.totp_enabled.is_(True),
        ).scalar() or 0

        dept_data.append({
            "department": dept or "(belirsiz)",
            "user_count": user_count,
            "pg_count": pg_count,
            "pg_per_user": round(pg_count / user_count, 2) if user_count else 0,
            "important_pg": important_pg,
            "totp_rate": round(totp_enabled / user_count * 100, 1) if user_count else 0,
        })

    dept_data.sort(key=lambda x: -x["user_count"])

    return jsonify({
        "success": True,
        "summary": {
            "total_departments": len(dept_data),
            "total_users": sum(d["user_count"] for d in dept_data),
            "total_pgs": sum(d["pg_count"] for d in dept_data),
        },
        "departments": dept_data,
    })


# ─── Rapor 6: Yönetici Liderlik Skoru ────────────────────────────────────────

@app_bp.route("/raporlar/yonetici-liderlik")
@login_required
def raporlar_yonetici_liderlik():
    return render_template("platform/raporlar/yonetici_liderlik.html")


@app_bp.route("/raporlar/api/yonetici-liderlik")
@login_required
def raporlar_api_yonetici_liderlik():
    """Süreç liderlerinin liderliğindeki süreçlerin ortalama performans skoru."""
    tid = current_user.tenant_id
    if not tid:
        return jsonify({"success": False, "message": "Tenant yok"}), 400

    active_py = get_active_plan_year_for_user(current_user)
    py_id = active_py.id if active_py else None

    # Süreç liderleri (M:N tablosu)
    rows = db.session.query(
        process_leaders.c.user_id,
        process_leaders.c.process_id,
    ).join(Process, Process.id == process_leaders.c.process_id).filter(
        Process.tenant_id == tid,
        Process.is_active.is_(True),
    ).all()

    if not rows:
        # Fallback: hiç process_leaders yoksa user.role==yonetici olanları göster
        managers = User.query.filter_by(
            tenant_id=tid, is_active=True,
        ).join(User.role).filter(
            (User.role.has(name="yonetici")) | (User.role.has(name="tenant_admin"))
        ).all()
        return jsonify({
            "success": True,
            "summary": {
                "total_leaders": len(managers),
                "has_leader_data": False,
                "note": "Süreç-lider eşleştirmesi bulunamadı. Rol bazlı yönetici listesi gösterildi.",
            },
            "leaders": [{
                "user_id": u.id,
                "name": f"{u.first_name or ''} {u.last_name or ''}".strip() or u.email,
                "email": u.email,
                "department": u.department,
                "led_process_count": 0,
                "avg_process_score": None,
            } for u in managers[:25]],
        })

    # Skor motorundan süreç skorları
    try:
        today = _date.today()
        score_year = active_py.year if active_py else today.year
        proc_scores, _ = compute_process_scores_internal(
            tid, score_year, today, persist_pg_scores=False, plan_year=active_py
        )
    except Exception:
        proc_scores = {}

    # Lider → bağlı süreçler agregasyonu
    leader_map = defaultdict(list)
    for uid, pid in rows:
        leader_map[uid].append(pid)

    leaders = []
    for uid, pids in leader_map.items():
        u = User.query.get(uid)
        if not u or not u.is_active:
            continue
        scores = [proc_scores.get(pid) for pid in pids if proc_scores.get(pid) is not None]
        avg = round(sum(scores) / len(scores), 1) if scores else None
        leaders.append({
            "user_id": uid,
            "name": f"{u.first_name or ''} {u.last_name or ''}".strip() or u.email,
            "email": u.email,
            "department": u.department,
            "led_process_count": len(pids),
            "avg_process_score": avg,
        })
    leaders.sort(key=lambda x: -(x["avg_process_score"] or 0))

    return jsonify({
        "success": True,
        "summary": {
            "total_leaders": len(leaders),
            "has_leader_data": True,
            "with_score": sum(1 for l in leaders if l["avg_process_score"] is not None),
            "avg_score_overall": round(
                sum(l["avg_process_score"] for l in leaders if l["avg_process_score"]) /
                max(sum(1 for l in leaders if l["avg_process_score"]), 1), 1
            ),
        },
        "leaders": leaders,
    })


# ─── Rapor 7: Initiative Portföy Bubble ──────────────────────────────────────

@app_bp.route("/raporlar/initiative-bubble")
@login_required
def raporlar_initiative_bubble():
    return render_template("platform/raporlar/initiative_bubble.html")


@app_bp.route("/raporlar/api/initiative-bubble")
@login_required
def raporlar_api_initiative_bubble():
    """Initiative portföyü: bütçe × ilerleme × öncelik."""
    tid = current_user.tenant_id
    if not tid:
        return jsonify({"success": False, "message": "Tenant yok"}), 400

    inits = Initiative.query.filter_by(tenant_id=tid, is_active=True).all()
    PRIO_COLOR = {
        "critical": "#dc2626", "high": "#f59e0b",
        "medium": "#0ea5e9", "low": "#94a3b8",
    }
    STATUS_OPACITY = {
        "completed": 0.55, "cancelled": 0.25, "on_hold": 0.4,
        "in_progress": 1.0, "planned": 0.7,
    }
    bubbles = []
    for i in inits:
        budget = float(i.budget_total or 0)
        spent = float(i.budget_spent or 0)
        bubbles.append({
            "id": i.id,
            "code": i.code or f"INI-{i.id}",
            "name": i.name,
            "status": i.status,
            "priority": i.priority,
            "color": PRIO_COLOR.get(i.priority, "#64748b"),
            "opacity": STATUS_OPACITY.get(i.status, 0.7),
            "budget_total": budget,
            "budget_spent": spent,
            "budget_usage_pct": round(spent / budget * 100, 1) if budget else 0,
            "progress_pct": i.progress_pct or 0,
            "start_year": i.start_year,
            "end_year": i.end_year,
            "duration": (i.end_year or 0) - (i.start_year or 0) + 1,
        })

    # Özet
    by_status = defaultdict(int)
    by_priority = defaultdict(int)
    for b in bubbles:
        by_status[b["status"]] += 1
        by_priority[b["priority"]] += 1

    return jsonify({
        "success": True,
        "summary": {
            "total": len(bubbles),
            "total_budget": sum(b["budget_total"] for b in bubbles),
            "total_spent": sum(b["budget_spent"] for b in bubbles),
            "by_status": dict(by_status),
            "by_priority": dict(by_priority),
            "avg_progress": round(sum(b["progress_pct"] for b in bubbles) / max(len(bubbles), 1), 1),
        },
        "bubbles": bubbles,
    })


# ─── Rapor 8: Operasyonel Sabah Özeti+ ──────────────────────────────────────

@app_bp.route("/raporlar/sabah-ozeti")
@login_required
def raporlar_sabah_ozeti():
    return render_template("platform/raporlar/sabah_ozeti.html")


@app_bp.route("/raporlar/api/sabah-ozeti")
@login_required
def raporlar_api_sabah_ozeti():
    """Bugünün ve son 7 günün operasyonel özeti."""
    tid = current_user.tenant_id
    if not tid:
        return jsonify({"success": False, "message": "Tenant yok"}), 400

    today = _date.today()
    week_ago = today - timedelta(days=7)
    week_ahead = today + timedelta(days=7)

    # Tenant süreçleri
    proc_ids_subq = db.session.query(Process.id).filter(
        Process.tenant_id == tid, Process.is_active.is_(True),
    ).subquery()

    # Faaliyet sayımları
    overdue = ProcessActivity.query.filter(
        ProcessActivity.process_id.in_(proc_ids_subq),
        ProcessActivity.is_active.is_(True),
        ProcessActivity.end_at < datetime.utcnow(),
        ProcessActivity.status != "Tamamlandı",
    ).count()

    today_due = ProcessActivity.query.filter(
        ProcessActivity.process_id.in_(proc_ids_subq),
        ProcessActivity.is_active.is_(True),
        func.date(ProcessActivity.end_at) == today,
    ).count()

    upcoming = ProcessActivity.query.filter(
        ProcessActivity.process_id.in_(proc_ids_subq),
        ProcessActivity.is_active.is_(True),
        ProcessActivity.end_at.between(today, week_ahead),
    ).count()

    completed_week = ProcessActivity.query.filter(
        ProcessActivity.process_id.in_(proc_ids_subq),
        ProcessActivity.status == "Tamamlandı",
        ProcessActivity.completed_at.between(week_ago, today + timedelta(days=1)),
    ).count()

    # KPI ölçüm akışı
    kpi_ids_subq = db.session.query(ProcessKpi.id).filter(
        ProcessKpi.process_id.in_(proc_ids_subq),
        ProcessKpi.is_active.is_(True),
    ).subquery()

    measurements_today = KpiData.query.filter(
        KpiData.process_kpi_id.in_(kpi_ids_subq),
        KpiData.is_active.is_(True),
        func.date(KpiData.created_at) == today,
    ).count()

    measurements_week = KpiData.query.filter(
        KpiData.process_kpi_id.in_(kpi_ids_subq),
        KpiData.is_active.is_(True),
        KpiData.created_at >= week_ago,
    ).count()

    # En son 5 ölçüm girişi (recent activity)
    recent_data = db.session.query(
        KpiData.id, KpiData.created_at, KpiData.actual_value,
        ProcessKpi.name.label("kpi_name"),
        ProcessKpi.code.label("kpi_code"),
        User.first_name, User.last_name, User.email,
    ).join(ProcessKpi, ProcessKpi.id == KpiData.process_kpi_id).join(
        Process, Process.id == ProcessKpi.process_id
    ).join(User, User.id == KpiData.user_id, isouter=True).filter(
        Process.tenant_id == tid,
        KpiData.is_active.is_(True),
    ).order_by(KpiData.created_at.desc()).limit(8).all()

    recent_entries = [{
        "kpi_code": r.kpi_code,
        "kpi_name": r.kpi_name,
        "value": r.actual_value,
        "when": r.created_at.isoformat() if r.created_at else None,
        "who": (f"{r.first_name or ''} {r.last_name or ''}").strip() or r.email or "—",
    } for r in recent_data]

    return jsonify({
        "success": True,
        "today": today.isoformat(),
        "metrics": {
            "overdue_activities": overdue,
            "today_due_activities": today_due,
            "upcoming_7d_activities": upcoming,
            "completed_7d_activities": completed_week,
            "measurements_today": measurements_today,
            "measurements_7d": measurements_week,
        },
        "recent_entries": recent_entries,
    })
