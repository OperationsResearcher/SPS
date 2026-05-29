"""Faz 4 — Sektörel paketler + AI NLP + sektör benchmark."""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, date as _date

from flask import render_template, jsonify, request, current_app, send_file
from flask_login import login_required, current_user
from sqlalchemy import func, and_, or_, text, select
from sqlalchemy.orm import joinedload

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

from .helpers import _tid_or_none, MUDA_MAX_PROCESSES, _ai_text
import os as _os
import json as _json

# ═══════════════════════════════════════════════════════════════════════════
# FAZ 4 — SEKTÖREL PAKETLER + AI DERİNLEŞME
# ═══════════════════════════════════════════════════════════════════════════

_SEKTOREL_DIR = _os.path.realpath(
    _os.path.join(_os.path.dirname(__file__), "..", "..", "..", "data", "sektorel")
)


def _load_sektor(code):
    # Whitelist: kod yalnızca alfanumerik + alt çizgi olabilir (path traversal koruması)
    if not code or not isinstance(code, str) or not code.replace("_", "").isalnum():
        return None
    path = _os.path.realpath(_os.path.join(_SEKTOREL_DIR, f"{code}.json"))
    # Realpath sektor klasörünün dışına çıkarsa reddet
    if not path.startswith(_SEKTOREL_DIR + _os.sep):
        return None
    if not _os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return _json.load(f)
    except Exception as e:
        current_app.logger.warning(f"[sektor] yüklenemedi {code}: {e}")
        return None


# ─── SP-Marketplace: Sektörel Paketler ─────────────────────────────────────

SEKTOR_CATALOG = [
    {"code": "otomotiv", "name": "Otomotiv / Yan Sanayi", "icon": "fa-car",
     "color": "#4f46e5", "bg": "#eef2ff", "status": "hazır"},
    {"code": "saglik", "name": "Sağlık / Hastane", "icon": "fa-hospital",
     "color": "#dc2626", "bg": "#fef2f2", "status": "hazır"},
    {"code": "finans", "name": "Finans / Banka", "icon": "fa-university",
     "color": "#0ea5e9", "bg": "#e0f2fe", "status": "hazır"},
    {"code": "egitim", "name": "Eğitim / Üniversite", "icon": "fa-graduation-cap",
     "color": "#16a34a", "bg": "#f0fdf4", "status": "yakında"},
    {"code": "kamu", "name": "Belediye / Kamu", "icon": "fa-landmark",
     "color": "#f59e0b", "bg": "#fffbeb", "status": "yakında"},
    {"code": "perakende", "name": "Perakende / Zincir", "icon": "fa-shopping-cart",
     "color": "#db2777", "bg": "#fdf2f8", "status": "yakında"},
    {"code": "insaat", "name": "İnşaat / Müteahhitlik", "icon": "fa-hard-hat",
     "color": "#7c3aed", "bg": "#faf5ff", "status": "yakında"},
    {"code": "hizmet", "name": "Hizmet / Danışmanlık", "icon": "fa-briefcase",
     "color": "#0d9488", "bg": "#f0fdfa", "status": "yakında"},
]


@app_bp.route("/raporlar/sektorel")
@login_required
def raporlar_sektorel():
    return render_template("platform/raporlar/sektorel.html", sektorler=SEKTOR_CATALOG)


@app_bp.route("/raporlar/sektorel/<code>")
@login_required
def raporlar_sektorel_detay(code):
    pkg = _load_sektor(code)
    if not pkg:
        return render_template("platform/raporlar/sektorel.html",
                               sektorler=SEKTOR_CATALOG,
                               error=f"\"{code}\" sektörü için hazır paket henüz yok."), 404
    return render_template("platform/raporlar/sektorel_detay.html",
                           code=code, package=pkg)


@app_bp.route("/raporlar/api/sektorel/<code>")
@login_required
def raporlar_api_sektorel(code):
    pkg = _load_sektor(code)
    if not pkg:
        return jsonify({"success": False, "message": f"{code} bulunamadı"}), 404
    return jsonify({"success": True, "package": pkg})


# ─── AI-01: AI Doğal Dil Sorgu (pattern-based + free) ───────────────────────

@app_bp.route("/raporlar/nlp-query")
@login_required
def raporlar_nlp_query():
    return render_template("platform/raporlar/nlp_query.html")


_NLP_PATTERNS = [
    {
        "id": "top5_kpi_score",
        "label": "Bu yıl en yüksek skorlu 5 PG'mi göster",
        "icon": "fa-trophy",
    },
    {
        "id": "bottom5_kpi_score",
        "label": "Bu yıl en düşük skorlu 5 PG'mi göster",
        "icon": "fa-exclamation-triangle",
    },
    {
        "id": "process_health",
        "label": "Süreçlerin sağlık durumunu sırala",
        "icon": "fa-heart-pulse",
    },
    {
        "id": "active_initiatives",
        "label": "Aktif initiative'leri ve bütçelerini göster",
        "icon": "fa-rocket",
    },
    {
        "id": "overdue_activities",
        "label": "Geciken faaliyetleri listele",
        "icon": "fa-clock",
    },
    {
        "id": "kpi_data_volume",
        "label": "Hangi PG'lerde en çok ölçüm var",
        "icon": "fa-database",
    },
    {
        "id": "department_user_count",
        "label": "Departmanlardaki kullanıcı sayısı",
        "icon": "fa-users",
    },
    {
        "id": "high_risks",
        "label": "RPN'i 10'dan büyük riskleri göster",
        "icon": "fa-shield-alt",
    },
]


@app_bp.route("/raporlar/api/nlp-query/patterns")
@login_required
def raporlar_api_nlp_patterns():
    return jsonify({"success": True, "patterns": _NLP_PATTERNS})


@app_bp.route("/raporlar/api/nlp-query", methods=["GET", "POST"])
@login_required
def raporlar_api_nlp_query():
    """Pattern bazlı + free-form NLP sorgu — tenant filtreli güvenli."""
    tid = _tid_or_none()
    if not tid:
        return jsonify({"success": False, "message": "Tenant yok"}), 400
    if request.method == "GET":
        pattern_id = request.args.get("pattern_id")
        free_text = (request.args.get("query") or "").strip()
    else:
        data = request.get_json() or {}
        pattern_id = data.get("pattern_id")
        free_text = (data.get("query") or "").strip()

    # Pattern handlers
    if pattern_id == "top5_kpi_score":
        rows = db.session.query(
            ProcessKpi.code, ProcessKpi.name,
            func.avg(KpiData.status_percentage).label("avg"),
            func.count(KpiData.id).label("cnt"),
        ).join(KpiData, KpiData.process_kpi_id == ProcessKpi.id
        ).join(Process, Process.id == ProcessKpi.process_id
        ).filter(
            Process.tenant_id == tid, Process.is_active.is_(True),
            ProcessKpi.is_active.is_(True), KpiData.is_active.is_(True),
            KpiData.year == _date.today().year,
        ).group_by(ProcessKpi.code, ProcessKpi.name
        ).having(func.count(KpiData.id) >= 3
        ).order_by(func.avg(KpiData.status_percentage).desc().nullslast()
        ).limit(5).all()
        result = [{"code": r[0] or "—", "name": r[1], "avg_score": round(r[2] or 0, 1), "count": r[3]} for r in rows]
        return jsonify({"success": True, "type": "table",
                        "columns": ["Kod", "PG Adı", "Ort. Başarı %", "Ölçüm"],
                        "rows": [[r["code"], r["name"], r["avg_score"], r["count"]] for r in result],
                        "summary": f"{_date.today().year} yılı en yüksek 5 PG"})

    if pattern_id == "bottom5_kpi_score":
        rows = db.session.query(
            ProcessKpi.code, ProcessKpi.name,
            func.avg(KpiData.status_percentage).label("avg"),
            func.count(KpiData.id).label("cnt"),
        ).join(KpiData, KpiData.process_kpi_id == ProcessKpi.id
        ).join(Process, Process.id == ProcessKpi.process_id
        ).filter(
            Process.tenant_id == tid, Process.is_active.is_(True),
            ProcessKpi.is_active.is_(True), KpiData.is_active.is_(True),
            KpiData.year == _date.today().year,
        ).group_by(ProcessKpi.code, ProcessKpi.name
        ).having(func.count(KpiData.id) >= 3
        ).order_by(func.avg(KpiData.status_percentage).asc().nullslast()
        ).limit(5).all()
        return jsonify({"success": True, "type": "table",
                        "columns": ["Kod", "PG Adı", "Ort. Başarı %", "Ölçüm"],
                        "rows": [[r[0] or "—", r[1], round(r[2] or 0, 1), r[3]] for r in rows],
                        "summary": f"{_date.today().year} yılı en düşük 5 PG"})

    if pattern_id == "process_health":
        active_py = get_active_plan_year_for_user(current_user)
        try:
            today = _date.today()
            proc_scores, _ = compute_process_scores_internal(
                tid, active_py.year if active_py else today.year, today,
                persist_pg_scores=False, plan_year=active_py)
        except Exception:
            proc_scores = {}
        procs = Process.query.filter_by(tenant_id=tid, is_active=True,
            plan_year_id=active_py.id if active_py else None).order_by(Process.code).all()
        result = []
        for p in procs:
            score = proc_scores.get(p.id)
            result.append({"code": p.code or "—", "name": p.name,
                "score": round(score, 1) if score is not None else None})
        result.sort(key=lambda x: -(x["score"] or 0))
        return jsonify({"success": True, "type": "table",
                        "columns": ["Kod", "Süreç", "Sağlık Skoru"],
                        "rows": [[r["code"], r["name"], r["score"] if r["score"] is not None else "—"] for r in result[:30]],
                        "summary": f"{len(result)} süreç sağlık skoru sıralı"})

    if pattern_id == "active_initiatives":
        inits = Initiative.query.filter_by(tenant_id=tid, is_active=True).filter(
            Initiative.status.in_(["in_progress", "planned"])).order_by(Initiative.priority).all()
        return jsonify({"success": True, "type": "table",
                        "columns": ["Kod", "Ad", "Durum", "Öncelik", "Bütçe", "İlerleme %"],
                        "rows": [[i.code or "—", i.name, i.status, i.priority,
                                  f"{float(i.budget_total or 0):,.0f} ₺", i.progress_pct or 0] for i in inits],
                        "summary": f"{len(inits)} aktif/planlanan initiative"})

    if pattern_id == "overdue_activities":
        overdue = ProcessActivity.query.options(joinedload(ProcessActivity.process)).join(Process).filter(
            Process.tenant_id == tid, ProcessActivity.is_active.is_(True),
            ProcessActivity.end_at < datetime.utcnow(),
            ProcessActivity.status != "Tamamlandı",
        ).order_by(ProcessActivity.end_at).limit(20).all()
        return jsonify({"success": True, "type": "table",
                        "columns": ["Faaliyet", "Süreç", "Son Tarih", "Durum"],
                        "rows": [[a.name or "—",
                                  a.process.code if a.process else "—",
                                  a.end_at.strftime("%d.%m.%Y") if a.end_at else "—",
                                  a.status or "—"] for a in overdue],
                        "summary": f"{len(overdue)} geciken faaliyet (top 20)"})

    if pattern_id == "kpi_data_volume":
        rows = db.session.query(
            ProcessKpi.code, ProcessKpi.name, func.count(KpiData.id).label("cnt"),
        ).join(KpiData, KpiData.process_kpi_id == ProcessKpi.id
        ).join(Process, Process.id == ProcessKpi.process_id
        ).filter(Process.tenant_id == tid, KpiData.is_active.is_(True)
        ).group_by(ProcessKpi.code, ProcessKpi.name
        ).order_by(func.count(KpiData.id).desc()).limit(10).all()
        return jsonify({"success": True, "type": "table",
                        "columns": ["Kod", "PG", "Ölçüm Sayısı"],
                        "rows": [[r[0] or "—", r[1], r[2]] for r in rows],
                        "summary": "En çok ölçüm yapılan 10 PG"})

    if pattern_id == "department_user_count":
        rows = db.session.query(User.department, func.count(User.id)).filter(
            User.tenant_id == tid, User.is_active.is_(True),
        ).group_by(User.department).order_by(func.count(User.id).desc()).all()
        return jsonify({"success": True, "type": "table",
                        "columns": ["Departman", "Kullanıcı Sayısı"],
                        "rows": [[r[0] or "(belirsiz)", r[1]] for r in rows],
                        "summary": f"{len(rows)} farklı departman"})

    if pattern_id == "high_risks":
        from app.models.k_radar_domain import RiskHeatmapItem
        risks = RiskHeatmapItem.query.filter_by(tenant_id=tid, is_active=True).filter(
            RiskHeatmapItem.rpn >= 10).order_by(RiskHeatmapItem.rpn.desc()).all()
        return jsonify({"success": True, "type": "table",
                        "columns": ["Risk", "Olasılık", "Etki", "RPN", "Durum"],
                        "rows": [[r.title, r.probability, r.impact, r.rpn, r.status or "Open"] for r in risks],
                        "summary": f"RPN ≥ 10 olan {len(risks)} risk"})

    # Free-form: AI ile SQL üret + güvenlik kontrolleri
    if free_text:
        ai_response = _ai_text(
            prompt=(f"Türkçe doğal dil sorusunu analiz et: '{free_text}'\n\n"
                    "Kokpitim platformunda hangi tablodan/raporundan veri çekilebilir? "
                    "Yalnızca 2-3 cümlelik açıklama yaz, SQL yazma. "
                    "Eğer mevcut pattern'lerden biriyse onu öner. "
                    f"Mevcut pattern'ler: {[p['label'] for p in _NLP_PATTERNS]}"),
            fallback=("Sorunuzu anlamaya çalıştım. Şu anda yalnızca öntanımlı pattern'leri destekliyorum. "
                      "Lütfen sol taraftan bir hazır soru seçin."),
            tid=tid, endpoint="ai_nlp_query", max_tokens=200,
        )
        return jsonify({"success": True, "type": "text", "summary": "AI Analizi",
                        "text": ai_response})

    return jsonify({"success": False, "message": "Pattern veya sorgu metni gerekli"}), 400


# ─── AI-10: AI Sektör Benchmark ────────────────────────────────────────────

@app_bp.route("/raporlar/sektor-benchmark")
@login_required
def raporlar_sektor_benchmark():
    return render_template("platform/raporlar/sektor_benchmark.html")


# Mock sektör ortalamaları (gerçek müşteride dış API/manuel veri girişi olur)
_SEKTOR_BENCHMARKS = {
    "otomotiv": {
        "OEE": 65, "PPM Defect": 80, "OTIF": 88, "NPS": 45, "EBITDA": 12,
        "Stok Devir": 8, "Patent (yıllık)": 4, "Çalışan Devir %": 14,
        "CO₂ (tCO₂e)": 18000, "eNPS": 25,
    },
    "saglik": {
        "Bekleme Süresi (dk)": 25, "Memnuniyet %": 78, "Doluluk %": 68,
        "Enfeksiyon ‰": 4, "Mortalite %": 2.3, "Hekim Devir %": 18,
    },
    "finans": {
        "NIM %": 3.8, "Cost-Income %": 55, "ROE %": 14, "NPL %": 4.5,
        "CAR %": 12.5, "NPS": 42, "Mobil Adopsyon %": 65,
    },
}


@app_bp.route("/raporlar/api/sektor-benchmark")
@login_required
def raporlar_api_sektor_benchmark():
    tid = _tid_or_none()
    if not tid:
        return jsonify({"success": False, "message": "Tenant yok"}), 400
    tenant = db.session.get(Tenant, tid)

    # Sektörü tenant.sector'dan tahmin et
    sector_field = (tenant.sector or "").lower() if tenant else ""
    sektor_key = "otomotiv"  # default
    if "sağlık" in sector_field or "hastane" in sector_field:
        sektor_key = "saglik"
    elif "finans" in sector_field or "banka" in sector_field:
        sektor_key = "finans"

    benchmark = _SEKTOR_BENCHMARKS.get(sektor_key, _SEKTOR_BENCHMARKS["otomotiv"])

    # Tomofil/tenant verisinden basit metrikler (özet)
    active_py = get_active_plan_year_for_user(current_user)
    py_id = active_py.id if active_py else None
    proc_count = Process.query.filter_by(tenant_id=tid, is_active=True,
        plan_year_id=py_id).count()
    kpi_count = ProcessKpi.query.join(Process).filter(
        Process.tenant_id == tid, Process.plan_year_id == py_id,
        ProcessKpi.is_active.is_(True)).count()
    user_count = User.query.filter_by(tenant_id=tid, is_active=True).count()

    # AI yorumu
    ai_comment = _ai_text(
        prompt=(f"{tenant.name if tenant else 'Bir kurum'} ({sector_field}) için sektör benchmark analizi. "
                f"Tenant'ta {proc_count} süreç, {kpi_count} PG, {user_count} çalışan var. "
                f"Sektör ortalamaları: {benchmark}. "
                "3-4 cümle ile değerlendirme yap: kurum sektör ortalamasının üstünde mi, altında mı, "
                "hangi alanlarda iyileştirme önemli."),
        fallback=(f"{tenant.name if tenant else 'Kurum'} {sektor_key} sektöründe faaliyet göstermektedir. "
                  f"Tenant'ta {proc_count} süreç ve {kpi_count} performans göstergesi izlenmektedir. "
                  "Sektör benchmarkları ile detaylı karşılaştırma için ilgili PG verilerinin "
                  "güncel ve tam olması gerekmektedir."),
        tid=tid, endpoint="ai_sektor_benchmark", max_tokens=350,
    )

    return jsonify({"success": True, "data": {
        "tenant_name": tenant.name if tenant else "—",
        "sector": sector_field or "—",
        "sektor_key": sektor_key,
        "benchmark": benchmark,
        "tenant_summary": {
            "process_count": proc_count,
            "kpi_count": kpi_count,
            "user_count": user_count,
        },
        "ai_comment": ai_comment,
    }})


