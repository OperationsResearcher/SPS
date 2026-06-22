"""Faz 1 — 15 hızlı kazanç raporu (sunburst, VRIO, OKR, roadmap, MUDA, CMMI, op istatistik, ROI, bireysel, risk, 2FA, karbon, AI danışman/coach, early warning)."""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, date as _date

from flask import render_template, jsonify, request, current_app, send_file
from flask_login import login_required, current_user
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

# ═══════════════════════════════════════════════════════════════════════════
# FAZ 1 — 15 HIZLI KAZANC RAPORU (PLAN-TUM-RAPORLAR.md Faz 1)
# ═══════════════════════════════════════════════════════════════════════════

def _tid_or_none():
    return current_user.tenant_id if current_user.tenant_id else None


# ─── ST-01: Stratejik Hiyerarşi Sunburst ─────────────────────────────────────

@app_bp.route("/reports/sunburst")
@login_required
def raporlar_sunburst():
    return render_template("platform/reports/sunburst.html")


@app_bp.route("/reports/api/sunburst")
@login_required
def raporlar_api_sunburst():
    tid = _tid_or_none()
    if not tid:
        return jsonify({"success": False, "message": "Tenant yok"}), 400
    active_py = get_active_plan_year_for_user(current_user)
    py_id = active_py.id if active_py else None

    # Nested chain: strategy → sub_strategies → process_sub_strategy_links → process
    strat_q = Strategy.query.options(
        selectinload(Strategy.sub_strategies)
            .selectinload(SubStrategy.process_sub_strategy_links)
            .joinedload(ProcessSubStrategyLink.process)
    ).filter_by(tenant_id=tid, is_active=True)
    if py_id:
        strat_q = strat_q.filter(or_(Strategy.plan_year_id == py_id, Strategy.plan_year_id.is_(None)))
    strategies = strat_q.order_by(Strategy.code).all()

    weights = {w.strategy_id: w.weight_raw or 0 for w in
               KVektorStrategyWeight.query.filter_by(tenant_id=tid).all()}
    total_w = sum(weights.values()) or 1

    # Tree yapısı: vizyon → strateji → alt → süreç
    tree = {"name": "Vizyon", "value": 100, "children": []}
    for s in strategies:
        s_node = {
            "name": (s.code or "?") + " " + (s.title or "")[:30],
            "value": round((weights.get(s.id, 0) / total_w) * 100, 1),
            "children": [],
        }
        sub_count = max(len([ss for ss in s.sub_strategies if getattr(ss, "is_active", True)]), 1)
        for ss in s.sub_strategies:
            if not getattr(ss, "is_active", True):
                continue
            ss_node = {
                "name": (ss.code or "?") + " " + (ss.title or "")[:25],
                "value": round(s_node["value"] / sub_count, 1),
                "children": [],
            }
            for pssl in ss.process_sub_strategy_links:
                p = pssl.process
                if not p or not p.is_active:
                    continue
                if py_id and p.plan_year_id and p.plan_year_id != py_id:
                    continue
                ss_node["children"].append({
                    "name": (p.code or "?") + " " + (p.name or "")[:25],
                    "value": round((pssl.contribution_pct or 10) / 5, 1),
                })
            s_node["children"].append(ss_node)
        tree["children"].append(s_node)

    return jsonify({"success": True, "tree": tree, "summary": {
        "strategies": len(strategies),
        "plan_year": active_py.year if active_py else None,
    }})


# ─── ST-06: VRIO Portföy 4-Köşe ─────────────────────────────────────────────

@app_bp.route("/reports/vrio-portfoy")
@login_required
def raporlar_vrio_portfoy():
    return render_template("platform/reports/vrio_portfoy.html")


@app_bp.route("/reports/api/vrio-portfoy")
@login_required
def raporlar_api_vrio_portfoy():
    from app.models.strategy_frameworks import VRIOResource
    tid = _tid_or_none()
    if not tid:
        return jsonify({"success": False, "message": "Tenant yok"}), 400
    resources = VRIOResource.query.filter_by(tenant_id=tid, is_active=True).order_by(VRIOResource.name).all()

    buckets = {
        "Rekabetçi Dezavantaj": [],
        "Rekabet Paritesi": [],
        "Geçici Rekabet Avantajı": [],
        "Kullanılmayan Avantaj": [],
        "Sürdürülebilir Rekabet Avantajı": [],
    }
    for r in resources:
        buckets[r.competitive_label].append({
            "id": r.id, "name": r.name, "category": r.category, "note": r.note,
            "v": r.is_valuable, "r": r.is_rare, "i": r.is_inimitable, "o": r.is_organized,
        })

    return jsonify({"success": True, "summary": {
        "total": len(resources),
        "sustainable": len(buckets["Sürdürülebilir Rekabet Avantajı"]),
        "temporary": len(buckets["Geçici Rekabet Avantajı"]),
        "parity": len(buckets["Rekabet Paritesi"]),
        "unused": len(buckets["Kullanılmayan Avantaj"]),
        "disadvantage": len(buckets["Rekabetçi Dezavantaj"]),
    }, "buckets": buckets})


# ─── ST-09: OKR Cascade Görseli ─────────────────────────────────────────────

@app_bp.route("/reports/okr-cascade")
@login_required
def raporlar_okr_cascade():
    return render_template("platform/reports/okr_cascade.html")


@app_bp.route("/reports/api/okr-cascade")
@login_required
def raporlar_api_okr_cascade():
    from app.models.okr import OkrObjective, OkrKeyResult
    tid = _tid_or_none()
    if not tid:
        return jsonify({"success": False, "message": "Tenant yok"}), 400
    active_py = get_active_plan_year_for_user(current_user)
    py_id = active_py.id if active_py else None

    q = OkrObjective.query.filter_by(tenant_id=tid, is_active=True)
    if py_id:
        q = q.filter_by(plan_year_id=py_id)
    objectives = q.order_by(OkrObjective.quarter.nullsfirst(), OkrObjective.order_no).all()

    items = []
    for obj in objectives:
        krs = []
        for kr in obj.key_results:
            if not kr.is_active:
                continue
            krs.append({
                "id": kr.id, "title": kr.title, "metric": kr.metric,
                "start": kr.start_value, "target": kr.target_value, "current": kr.current_value,
                "progress_pct": kr.progress_pct,
                "linked_kpi_id": kr.linked_process_kpi_id,
            })
        strat_name = obj.linked_strategy.title if obj.linked_strategy else None
        sub_name = obj.linked_sub_strategy.title if obj.linked_sub_strategy else None
        items.append({
            "id": obj.id, "title": obj.title, "quarter": obj.quarter,
            "owner": obj.owner, "strategy": strat_name, "sub_strategy": sub_name,
            "kr_count": len(krs), "key_results": krs,
            "avg_progress": round(sum((k["progress_pct"] or 0) for k in krs) / max(len(krs), 1), 1),
        })

    return jsonify({"success": True, "summary": {
        "total_objectives": len(items),
        "total_krs": sum(o["kr_count"] for o in items),
        "avg_completion": round(sum(o["avg_progress"] for o in items) / max(len(items), 1), 1),
        "plan_year": active_py.year if active_py else None,
    }, "objectives": items})


# ─── ST-11: Initiative Roadmap Gantt ────────────────────────────────────────

@app_bp.route("/reports/initiative-roadmap")
@login_required
def raporlar_initiative_roadmap():
    return render_template("platform/reports/initiative_roadmap.html")


@app_bp.route("/reports/api/initiative-roadmap")
@login_required
def raporlar_api_initiative_roadmap():
    from app.models.initiative import InitiativeMilestone
    tid = _tid_or_none()
    if not tid:
        return jsonify({"success": False, "message": "Tenant yok"}), 400
    inits = Initiative.query.filter_by(tenant_id=tid, is_active=True).order_by(Initiative.start_year).all()

    items = []
    for i in inits:
        milestones = []
        for m in i.milestones:
            milestones.append({
                "id": m.id, "name": m.name,
                "target_date": m.target_date.isoformat() if m.target_date else None,
                "completed_date": m.completed_date.isoformat() if m.completed_date else None,
                "status": m.status,
            })
        items.append({
            "id": i.id, "code": i.code, "name": i.name,
            "start_year": i.start_year, "end_year": i.end_year,
            "status": i.status, "priority": i.priority,
            "progress_pct": i.progress_pct,
            "milestones": milestones,
        })
    return jsonify({"success": True, "summary": {
        "total": len(items),
        "year_range": f"{min((i['start_year'] for i in items), default=0)}–{max((i['end_year'] for i in items), default=0)}" if items else "—",
        "total_milestones": sum(len(i["milestones"]) for i in items),
    }, "initiatives": items})


# ─── OP-04: 7 Muda Waste Analizi ───────────────────────────────────────────

@app_bp.route("/reports/muda-analysis")
@login_required
def raporlar_muda_analizi():
    from app.services.plan_year_service import list_plan_years
    years, active_year = [], None
    if current_user.tenant_id:
        years = [py.year for py in list_plan_years(current_user.tenant_id)]
        apy = get_active_plan_year_for_user(current_user)
        active_year = apy.year if apy else None
    return render_template("platform/reports/muda_analizi.html",
                           plan_years=years, active_year=active_year)


@app_bp.route("/reports/api/muda-analysis")
@login_required
def raporlar_api_muda_analizi():
    from app.services.plan_year_service import get_plan_year
    tid = _tid_or_none()
    if not tid:
        return jsonify({"success": False, "message": "Tenant yok"}), 400
    try:
        from app.services.muda_analyzer import MudaAnalyzerService
    except Exception as e:
        return jsonify({"success": False, "message": f"Muda servisi yüklenemedi: {e}"}), 500

    # ?year= → o yıl; yoksa aktif yıl
    year_q = request.args.get("year", type=int)
    active_py = get_plan_year(tid, year_q) if year_q else get_active_plan_year_for_user(current_user)
    py_id = active_py.id if active_py else None

    proc_q = Process.query.filter_by(tenant_id=tid, is_active=True)
    if py_id:
        proc_q = proc_q.filter(or_(Process.plan_year_id == py_id, Process.plan_year_id.is_(None)))
    procs = proc_q.all()
    process_findings = []
    muda_counter = defaultdict(int)
    for p in procs[:MUDA_MAX_PROCESSES]:
        try:
            findings = MudaAnalyzerService.analyze_process_inefficiency(p.id, tid)
            if findings:
                for f in findings:
                    muda_counter[f.get("muda_type", "other")] += 1
                process_findings.append({
                    "process_id": p.id, "code": p.code, "name": p.name,
                    "findings_count": len(findings),
                    "findings": findings[:5],
                })
        except Exception as e:
            current_app.logger.warning(f"[muda] proses {p.id} analiz hatası: {e}")
            continue

    # 7 muda tipinin Türkçe etiketleri + açıklamaları + örnekleri
    muda_meta = {
        "overproduction":  {"label": "Aşırı Üretim",      "color": "#dc2626", "desc": "İhtiyaçtan fazla üretim, ham veri/rapor hazırlama. Stoğa eklenir, çürür.",      "ex": "Talep edilmemiş raporlar; satılamayan ürün stoku"},
        "waiting":         {"label": "Bekleme",            "color": "#f59e0b", "desc": "Onay, malzeme, makine veya bilgi beklemesi. Üretim akışını keser.",          "ex": "Onay zincirinde bekleyen evrak; teslimat geciken malzeme"},
        "transport":       {"label": "Taşıma / Nakliye",   "color": "#0ea5e9", "desc": "Gereksiz malzeme/dosya/insan hareketi. Değer üretmez.",                    "ex": "Atölyeden depoya gereksiz gidip-gelme; çoklu dosya kopyaları"},
        "overprocessing":  {"label": "Aşırı İşlem",        "color": "#8b5cf6", "desc": "Müşterinin değer vermediği fazladan adımlar/kontroller/standart fazlası.",   "ex": "Aynı veriye 3 farklı yerden imza; gereksiz detaylı paketleme"},
        "inventory":       {"label": "Stok",               "color": "#0d9488", "desc": "Bilgi/malzeme/iş emrinin kuyrukta birikmesi. Para bağlar, kaliteyi gizler.",  "ex": "Yarı mamul yığını; iş listesi 100+ açık iş emri"},
        "motion":          {"label": "Hareket",            "color": "#16a34a", "desc": "Çalışanın gereksiz fiziksel/dijital hareketi (arama, eğilme, yürüme).",       "ex": "Doğru klasörü bulmak için 10 ekran tıklama"},
        "defects":         {"label": "Kusurlar / Hatalar", "color": "#ef4444", "desc": "Yeniden yapım, düzeltme, iade gerektiren hatalı çıktı.",                     "ex": "Hatalı veri girişi nedeniyle yeniden raporlama"},
    }
    muda_summary = [{
        "key": k, **muda_meta.get(k, {"label": k, "color": "#64748b", "desc": "", "ex": ""}),
        "count": v
    } for k, v in sorted(muda_counter.items(), key=lambda x: -x[1])]
    # Hiç bulgu olmayan tipler için de meta gönder (UI tüm 7'yi göstersin)
    for k, m in muda_meta.items():
        if not any(it["key"] == k for it in muda_summary):
            muda_summary.append({"key": k, **m, "count": 0})

    return jsonify({"success": True, "summary": {
        "total_processes_analyzed": len(procs),
        "processes_with_findings": len(process_findings),
        "total_findings": sum(muda_counter.values()),
        "plan_year": active_py.year if active_py else None,
    }, "by_muda": muda_summary, "by_process": process_findings})


# ─── OP-15: CMMI Olgunluk Heatmap ──────────────────────────────────────────

@app_bp.route("/reports/cmmi-heatmap")
@login_required
def raporlar_cmmi_heatmap():
    from app.services.plan_year_service import list_plan_years
    years, active_year = [], None
    if current_user.tenant_id:
        years = [py.year for py in list_plan_years(current_user.tenant_id)]
        apy = get_active_plan_year_for_user(current_user)
        active_year = apy.year if apy else None
    return render_template("platform/reports/cmmi_heatmap.html",
                           plan_years=years, active_year=active_year)


@app_bp.route("/reports/api/cmmi-heatmap")
@login_required
def raporlar_api_cmmi_heatmap():
    from app.models.k_radar_domain import ProcessMaturity
    from app.services.plan_year_service import get_plan_year
    tid = _tid_or_none()
    if not tid:
        return jsonify({"success": False, "message": "Tenant yok"}), 400

    # ?year= → o yıl; yoksa aktif yıl
    year_q = request.args.get("year", type=int)
    active_py = get_plan_year(tid, year_q) if year_q else get_active_plan_year_for_user(current_user)
    py_id = active_py.id if active_py else None

    # Süreçleri plan yılına göre filtrele
    proc_q = Process.query.filter(Process.tenant_id == tid, Process.is_active.is_(True))
    if py_id:
        proc_q = proc_q.filter(or_(Process.plan_year_id == py_id, Process.plan_year_id.is_(None)))
    process_ids = [p.id for p in proc_q.all()]

    # Her süreç için en son maturity kaydı
    rows = db.session.query(
        Process.id, Process.code, Process.name,
        func.max(ProcessMaturity.maturity_level).label("level"),
    ).join(ProcessMaturity, ProcessMaturity.process_id == Process.id).filter(
        Process.id.in_(process_ids) if process_ids else False,
        ProcessMaturity.is_active.is_(True),
    ).group_by(Process.id, Process.code, Process.name).all() if process_ids else []

    processes = [{"id": r[0], "code": r[1], "name": r[2], "level": int(r[3])} for r in rows]

    # Seviye dağılımı
    distribution = defaultdict(int)
    for p in processes:
        distribution[p["level"]] += 1

    avg_level = round(sum(p["level"] for p in processes) / max(len(processes), 1), 2)

    # CMMI seviyeleri — Türkçe açıklamalar
    level_meta = {
        1: {"label": "1 — Başlangıç",        "en": "Initial",                  "color": "#dc2626", "desc": "Süreç ad-hoc/kaotik; kişiye bağımlı, tekrarlanabilirlik yok."},
        2: {"label": "2 — Yönetilen",        "en": "Managed",                  "color": "#f59e0b", "desc": "Temel süreç disiplini var; planlama, izleme, kontrol uygulanıyor."},
        3: {"label": "3 — Tanımlı",          "en": "Defined",                  "color": "#0ea5e9", "desc": "Süreç dokümante edilmiş, kurum standardı; iyileştirmeler proaktif."},
        4: {"label": "4 — Sayısal Yönetilen","en": "Quantitatively Managed",   "color": "#6366f1", "desc": "Süreç istatistiksel teknikleriyle ölçülüyor; sapmalar sayısal kontrol altında."},
        5: {"label": "5 — Optimize Eden",    "en": "Optimizing",               "color": "#10b981", "desc": "Sürekli iyileştirme döngüsü; inovasyon ve teknolojik yenilik kurumsallaşmış."},
    }
    distribution_list = [{
        "level": k, "label": level_meta[k]["label"], "en": level_meta[k]["en"],
        "color": level_meta[k]["color"], "desc": level_meta[k]["desc"],
        "count": distribution.get(k, 0),
        "pct": round((distribution.get(k, 0) / max(len(processes), 1)) * 100, 1) if processes else 0,
    } for k in [1, 2, 3, 4, 5]]

    # Genel olgunluk yorumu
    if avg_level >= 4.5:
        overall_label = "Mükemmel — Optimize Eden"
        overall_color = "#10b981"
        overall_advice = "Süreçleriniz sınıfın en iyisi seviyesinde. İnovasyonu kurumsallaştırma odaklı kalın."
    elif avg_level >= 3.5:
        overall_label = "Çok İyi — Sayısal Yönetim"
        overall_color = "#6366f1"
        overall_advice = "Sayısal teknik uygulanıyor; süreçleri optimize etmeye geçiş zamanı."
    elif avg_level >= 2.5:
        overall_label = "İyi — Tanımlı"
        overall_color = "#0ea5e9"
        overall_advice = "Standart süreçler var; ölçüm ve istatistik kontrol için yatırım yapın."
    elif avg_level >= 1.5:
        overall_label = "Orta — Yönetilen"
        overall_color = "#f59e0b"
        overall_advice = "Temel disiplin var; dokümantasyon ve kurum standardı için çalışın."
    else:
        overall_label = "Düşük — Başlangıç"
        overall_color = "#dc2626"
        overall_advice = "Süreçler ad-hoc; öncelik temel planlama ve izleme disiplinini kurmaktır."

    # Olgunluk hesaplanmamış süreçler
    measured_ids = {p["id"] for p in processes}
    unmeasured = [{"id": p.id, "code": p.code or "", "name": p.name or ""} for p in proc_q.all() if p.id not in measured_ids]

    return jsonify({"success": True, "summary": {
        "total_processes": len(processes),
        "unmeasured_count": len(unmeasured),
        "tenant_process_count": len(process_ids),
        "avg_level": avg_level,
        "overall_label": overall_label,
        "overall_color": overall_color,
        "overall_advice": overall_advice,
        "level_5_count": distribution.get(5, 0),
        "low_level_count": distribution.get(1, 0) + distribution.get(2, 0),
        "plan_year": active_py.year if active_py else None,
    }, "distribution": distribution_list, "processes": processes, "unmeasured": unmeasured[:20]})


# ─── OP-17: Operasyonel İstatistik Sayfası (süreç bazlı) ───────────────────

@app_bp.route("/reports/operation-statistics")
@login_required
def raporlar_op_istatistik():
    from app.services.plan_year_service import list_plan_years
    years, active_year = [], None
    if current_user.tenant_id:
        years = [py.year for py in list_plan_years(current_user.tenant_id)]
        apy = get_active_plan_year_for_user(current_user)
        active_year = apy.year if apy else None
    return render_template("platform/reports/op_istatistik.html",
                           plan_years=years, active_year=active_year)


@app_bp.route("/reports/api/operation-statistics")
@login_required
def raporlar_api_op_istatistik():
    from app.services.plan_year_service import get_plan_year
    tid = _tid_or_none()
    if not tid:
        return jsonify({"success": False, "message": "Tenant yok"}), 400

    # ?year= varsa o yıl; yoksa aktif yıl
    year_q = request.args.get("year", type=int)
    active_py = get_plan_year(tid, year_q) if year_q else get_active_plan_year_for_user(current_user)
    py_id = active_py.id if active_py else None

    # Süreç başına: PG sayısı, faaliyet sayısı — plan_year filtreli (legacy NULL dahil)
    proc_filter = [Process.tenant_id == tid, Process.is_active.is_(True)]
    if py_id:
        proc_filter.append(or_(Process.plan_year_id == py_id, Process.plan_year_id.is_(None)))
    pg_filter = [ProcessKpi.is_active.is_(True)]
    if py_id:
        pg_filter.append(or_(ProcessKpi.plan_year_id == py_id, ProcessKpi.plan_year_id.is_(None)))
    act_filter = [ProcessActivity.is_active.is_(True)]
    if py_id:
        act_filter.append(or_(ProcessActivity.plan_year_id == py_id, ProcessActivity.plan_year_id.is_(None)))

    rows = db.session.query(
        Process.id, Process.code, Process.name, Process.status,
        func.count(func.distinct(ProcessKpi.id)).label("kpi_count"),
        func.count(func.distinct(ProcessActivity.id)).label("activity_count"),
    ).outerjoin(ProcessKpi, and_(ProcessKpi.process_id == Process.id, *pg_filter)
    ).outerjoin(ProcessActivity, and_(ProcessActivity.process_id == Process.id, *act_filter)
    ).filter(*proc_filter
    ).group_by(Process.id, Process.code, Process.name, Process.status).order_by(Process.code).all()

    items = [{
        "id": r[0], "code": r[1], "name": r[2], "status": r[3],
        "kpi_count": r[4], "activity_count": r[5],
    } for r in rows]

    return jsonify({"success": True, "summary": {
        "total_processes": len(items),
        "total_kpis": sum(i["kpi_count"] for i in items),
        "total_activities": sum(i["activity_count"] for i in items),
        "plan_year": active_py.year if active_py else None,
    }, "processes": items})


# ─── FN-05: ROI per Strategy — KALDIRILDI (kapsam dışı) ─────────────────────


# ─── HR-07: Bireysel Hedef Hizalama ────────────────────────────────────────

@app_bp.route("/reports/individual-alignment")
@login_required
def raporlar_bireysel_hizalama():
    return render_template("platform/reports/bireysel_hizalama.html")


@app_bp.route("/reports/api/individual-alignment")
@login_required
def raporlar_api_bireysel_hizalama():
    tid = _tid_or_none()
    if not tid:
        return jsonify({"success": False, "message": "Tenant yok"}), 400

    # Her aktif kullanıcı için: kaç bireysel PG'si var, kaçı bir sürece bağlı
    users = User.query.filter_by(tenant_id=tid, is_active=True).all()

    # Tüm PG'leri tek sorguda topla, user_id'ye göre grupla (N+1 önlemi)
    _uids = [u.id for u in users]
    _pgs_by_uid = defaultdict(list)
    if _uids:
        for p in IndividualPerformanceIndicator.query.filter(
            IndividualPerformanceIndicator.user_id.in_(_uids),
            IndividualPerformanceIndicator.is_active.is_(True),
        ).all():
            _pgs_by_uid[p.user_id].append(p)

    rows = []
    for u in users:
        pgs = _pgs_by_uid.get(u.id, [])
        if not pgs:
            continue
        total = len(pgs)
        aligned = sum(1 for p in pgs if p.source_process_id or p.source_process_kpi_id)
        rows.append({
            "user_id": u.id, "name": f"{u.first_name or ''} {u.last_name or ''}".strip() or u.email,
            "email": u.email, "department": u.department,
            "total_pgs": total, "aligned_pgs": aligned,
            "alignment_pct": round(aligned / total * 100, 1),
        })
    rows.sort(key=lambda x: -x["alignment_pct"])

    overall = round(sum(r["alignment_pct"] for r in rows) / max(len(rows), 1), 1)

    return jsonify({"success": True, "summary": {
        "users_with_pg": len(rows),
        "total_users": len(users),
        "overall_alignment_pct": overall,
    }, "users": rows[:50]})


# ─── RK-01: Risk Heatmap Detay ─────────────────────────────────────────────

@app_bp.route("/reports/risk-heatmap")
@login_required
def raporlar_risk_heatmap():
    return render_template("platform/reports/risk_heatmap.html")


@app_bp.route("/reports/api/risk-heatmap")
@login_required
def raporlar_api_risk_heatmap():
    from app.models.k_radar_domain import RiskHeatmapItem
    from sqlalchemy import or_
    tid = _tid_or_none()
    if not tid:
        return jsonify({"success": False, "message": "Tenant yok"}), 400

    year_q = request.args.get("year", type=int)
    if year_q:
        from app.models.plan_year import PlanYear
        _py = PlanYear.query.filter_by(tenant_id=tid, year=year_q).first()
        py_id = _py.id if _py else None
    else:
        py_id = None
        _py = get_active_plan_year_for_user(current_user)
        if _py:
            py_id = _py.id

    risk_q = RiskHeatmapItem.query.filter_by(tenant_id=tid, is_active=True)
    if py_id:
        risk_q = risk_q.filter(or_(
            RiskHeatmapItem.plan_year_id == py_id,
            RiskHeatmapItem.plan_year_id.is_(None),
        ))
    risks = risk_q.order_by(RiskHeatmapItem.rpn.desc().nullslast()).all()

    # 5×5 grid
    grid = [[[] for _ in range(5)] for _ in range(5)]
    for r in risks:
        p = max(1, min(r.probability or 1, 5))
        i = max(1, min(r.impact or 1, 5))
        grid[p - 1][i - 1].append({
            "id": r.id, "title": r.title, "status": r.status or "open",
            "rpn": r.rpn, "source": r.source_type,
        })

    summary = {
        "total": len(risks),
        "open": sum(1 for r in risks if (r.status or "open").lower() == "open"),
        "mitigated": sum(1 for r in risks if (r.status or "").lower() == "mitigated"),
        "high_rpn": sum(1 for r in risks if (r.rpn or 0) >= 15),
    }
    return jsonify({"success": True, "summary": summary, "grid": grid,
                    "top_risks": [{"id": r.id, "title": r.title, "rpn": r.rpn,
                                   "probability": r.probability, "impact": r.impact,
                                   "status": r.status} for r in risks[:10]]})


# ─── RK-08: 2FA Kullanım Raporu ────────────────────────────────────────────

@app_bp.route("/reports/two-fa")
@login_required
def raporlar_iki_fa():
    return render_template("platform/reports/iki_fa.html")


@app_bp.route("/reports/api/two-fa")
@login_required
def raporlar_api_iki_fa():
    tid = _tid_or_none()
    if not tid:
        return jsonify({"success": False, "message": "Tenant yok"}), 400

    total = User.query.filter_by(tenant_id=tid, is_active=True).count()
    enabled = User.query.filter_by(tenant_id=tid, is_active=True, totp_enabled=True).count()
    disabled_admins = db.session.query(User.id, User.email, User.first_name, User.last_name).join(
        User.role
    ).filter(
        User.tenant_id == tid, User.is_active.is_(True),
        User.totp_enabled.is_(False),
        User.role.has(name="tenant_admin"),
    ).all()

    return jsonify({"success": True, "summary": {
        "total_users": total,
        "totp_enabled": enabled,
        "totp_disabled": total - enabled,
        "enable_pct": round(enabled / max(total, 1) * 100, 1),
        "admins_without_2fa": len(disabled_admins),
    }, "admins_without_2fa": [{
        "id": a.id, "email": a.email,
        "name": f"{a.first_name or ''} {a.last_name or ''}".strip(),
    } for a in disabled_admins]})


# ─── ES-01: Carbon Footprint Toplam Trend ──────────────────────────────────

@app_bp.route("/reports/carbon-trend")
@login_required
def raporlar_carbon_trend():
    return render_template("platform/reports/carbon_trend.html")


@app_bp.route("/reports/api/carbon-trend")
@login_required
def raporlar_api_carbon_trend():
    from app.models.esg import EsgMetric, EsgMetricValue
    tid = _tid_or_none()
    if not tid:
        return jsonify({"success": False, "message": "Tenant yok"}), 400

    # Tüm scope 1+2+3 metrikleri
    metrics = EsgMetric.query.filter_by(tenant_id=tid, is_active=True).filter(
        EsgMetric.scope.in_(["scope1", "scope2", "scope3"])
    ).all()

    by_year_scope = defaultdict(lambda: {"scope1": 0, "scope2": 0, "scope3": 0})
    for m in metrics:
        for v in m.values:
            if v.value is not None:
                by_year_scope[v.year][m.scope] += v.value or 0

    years_sorted = sorted(by_year_scope.keys())
    trend = []
    for y in years_sorted:
        d = by_year_scope[y]
        trend.append({
            "year": y, "scope1": round(d["scope1"], 2), "scope2": round(d["scope2"], 2),
            "scope3": round(d["scope3"], 2),
            "total": round(d["scope1"] + d["scope2"] + d["scope3"], 2),
        })

    return jsonify({"success": True, "summary": {
        "metrics_count": len(metrics),
        "years_with_data": len(trend),
        "latest_total": trend[-1]["total"] if trend else 0,
        "first_total": trend[0]["total"] if trend else 0,
    }, "trend": trend})


# ─── AI-02: AI Strateji Danışmanı ──────────────────────────────────────────

@app_bp.route("/reports/ai-advisor")
@login_required
def raporlar_ai_danisman():
    return render_template("platform/reports/ai_danisman.html")


@app_bp.route("/reports/api/ai-advisor")
@login_required
def raporlar_api_ai_danisman():
    tid = _tid_or_none()
    if not tid:
        return jsonify({"success": False, "message": "Tenant yok"}), 400
    try:
        from app.services.ai_pivot_advisor_service import generate_pivot_recommendations
        result = generate_pivot_recommendations(tenant_id=tid, use_llm=True, user_id=current_user.id)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        current_app.logger.warning(f"[ai-danisman] hata: {e}")
        return jsonify({"success": False, "message": f"AI danışman hatası: {e}"}), 500


# ─── AI-04: AI Coach ───────────────────────────────────────────────────────

@app_bp.route("/reports/ai-coach")
@login_required
def raporlar_ai_coach():
    return render_template("platform/reports/ai_coach.html")


@app_bp.route("/reports/api/ai-coach")
@login_required
def raporlar_api_ai_coach():
    tid = _tid_or_none()
    if not tid:
        return jsonify({"success": False, "message": "Tenant yok"}), 400

    # En düşük skorlu 3 stratejiyi tespit et + AI ile öneri al
    active_py = get_active_plan_year_for_user(current_user)
    try:
        today = _date.today()
        score_year = active_py.year if active_py else today.year
        proc_scores, _ = compute_process_scores_internal(tid, score_year, today, persist_pg_scores=False, plan_year=active_py)
    except Exception:
        proc_scores = {}

    strat_q = Strategy.query.options(selectinload(Strategy.sub_strategies)).filter_by(tenant_id=tid, is_active=True)
    if active_py:
        strat_q = strat_q.filter(or_(Strategy.plan_year_id == active_py.id, Strategy.plan_year_id.is_(None)))
    strategies = strat_q.all()

    # Tüm sub_strategy → process_id eşlemesini tek sorguda topla (N+1 önlemi)
    _all_sub_ids = [ss.id for s in strategies for ss in s.sub_strategies if getattr(ss, "is_active", True)]
    _proc_by_sub = defaultdict(set)
    if _all_sub_ids:
        for sub_id, proc_id in db.session.query(ProcessKpi.sub_strategy_id, ProcessKpi.process_id).filter(
            ProcessKpi.sub_strategy_id.in_(_all_sub_ids)
        ).all():
            _proc_by_sub[sub_id].add(proc_id)

    strat_scores = []
    for s in strategies:
        sub_ids = [ss.id for ss in s.sub_strategies if getattr(ss, "is_active", True)]
        if not sub_ids:
            continue
        related = set().union(*(_proc_by_sub[sid] for sid in sub_ids))
        sc = [proc_scores.get(pid) for pid in related if proc_scores.get(pid) is not None]
        if sc:
            strat_scores.append({
                "code": s.code, "title": s.title,
                "score": round(sum(sc) / len(sc), 1),
            })

    strat_scores.sort(key=lambda x: x["score"])
    bottom3 = strat_scores[:3]

    # AI coach servisini çağır
    try:
        from services.ai_coach_service import analyze_strategic_performance
        coach_text = analyze_strategic_performance(
            data={
                "tenant_id": tid,
                "bottom_strategies": bottom3,
                "all_strategies": strat_scores,
            },
            tenant_id=tid, user_id=current_user.id,
        )
    except Exception as e:
        current_app.logger.info(f"[ai-coach] fallback ({e})")
        coach_text = (
            f"Sistemde {len(strat_scores)} ana strateji izlenmektedir. "
            f"En düşük performanslı 3 strateji: " +
            ", ".join(f"{s['code']} ({s['score']})" for s in bottom3) + ". "
            "Bu stratejilere bağlı PG'lerin gözden geçirilmesi, hedef revizyonu ve "
            "ek initiative tahsisi önerilmektedir."
        )

    return jsonify({"success": True, "data": {
        "strategies_analyzed": len(strat_scores),
        "bottom3": bottom3,
        "coach_advice": coach_text,
    }})


# ─── AI-05: AI Early Warning Dashboard ─────────────────────────────────────

@app_bp.route("/reports/early-warning")
@login_required
def raporlar_early_warning():
    return render_template("platform/reports/early_warning.html")


@app_bp.route("/reports/api/early-warning")
@login_required
def raporlar_api_early_warning():
    tid = _tid_or_none()
    if not tid:
        return jsonify({"success": False, "message": "Tenant yok"}), 400

    # Trend analizi: son 3 dönem hedef altında olan PG'leri tespit
    active_py = get_active_plan_year_for_user(current_user)
    py_id = active_py.id if active_py else None

    kpi_q = ProcessKpi.query.options(joinedload(ProcessKpi.process)).join(Process).filter(
        Process.tenant_id == tid, Process.is_active.is_(True),
        ProcessKpi.is_active.is_(True),
    )
    if py_id:
        kpi_q = kpi_q.filter(Process.plan_year_id == py_id)
    all_kpis = kpi_q.all()

    # İlk 100 PG için son 6 ölçümleri tek sorguda topla (N+1 önlemi)
    _kpi_subset = all_kpis[:100]
    _kpi_ids = [k.id for k in _kpi_subset]
    _data_by_kid = defaultdict(list)
    if _kpi_ids:
        for d in KpiData.query.filter(
            KpiData.process_kpi_id.in_(_kpi_ids),
            KpiData.is_active.is_(True),
        ).order_by(KpiData.process_kpi_id, KpiData.data_date.desc()).all():
            if len(_data_by_kid[d.process_kpi_id]) < 6:
                _data_by_kid[d.process_kpi_id].append(d)

    warnings = []
    for k in _kpi_subset:
        recent = _data_by_kid.get(k.id, [])
        if len(recent) < 3:
            continue
        # Status_percentage düşüş trendi
        scores = [r.status_percentage for r in recent if r.status_percentage is not None]
        if len(scores) >= 3:
            last3 = scores[:3]
            if all(s < 70 for s in last3):
                warnings.append({
                    "kpi_id": k.id, "kpi_code": k.code or f"PG-{k.id}",
                    "kpi_name": k.name,
                    "process_name": k.process.name if k.process else "?",
                    "last_scores": last3,
                    "severity": "high" if all(s < 50 for s in last3) else "medium",
                })

    return jsonify({"success": True, "summary": {
        "total_kpis_checked": len(all_kpis),
        "warnings_count": len(warnings),
        "high_severity": sum(1 for w in warnings if w["severity"] == "high"),
    }, "warnings": warnings[:25]})


