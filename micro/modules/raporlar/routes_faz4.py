"""Faz 4 — Sektörel paketler + AI NLP + sektör benchmark."""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone, date as _date

from flask import render_template, jsonify, request, current_app, send_file
from flask_login import login_required, current_user
from sqlalchemy import func, and_, or_, text, select
from sqlalchemy.orm import joinedload

from platform_core import app_bp
from app.extensions import csrf
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
from flask_babel import gettext as _

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


@app_bp.route("/reports/sectoral")
@login_required
def raporlar_sektorel():
    return render_template("platform/reports/sektorel.html", sektorler=SEKTOR_CATALOG)


@app_bp.route("/reports/sectoral/<code>")
@login_required
def raporlar_sektorel_detay(code):
    pkg = _load_sektor(code)
    if not pkg:
        return render_template("platform/reports/sektorel.html",
                               sektorler=SEKTOR_CATALOG,
                               error=f"\"{code}\" {_('sektörü için hazır paket henüz yok.')}"), 404
    return render_template("platform/reports/sektorel_detay.html",
                           code=code, package=pkg)


@app_bp.route("/reports/api/sectoral/<code>")
@login_required
def raporlar_api_sektorel(code):
    pkg = _load_sektor(code)
    if not pkg:
        return jsonify({"success": False, "message": f"{code} bulunamadı"}), 404
    return jsonify({"success": True, "package": pkg})


# ─── AI-01: AI Doğal Dil Sorgu (pattern-based + free) ───────────────────────

@app_bp.route("/reports/nlp-query")
@login_required
def raporlar_nlp_query():
    return render_template("platform/reports/nlp_query.html")


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


@app_bp.route("/reports/api/nlp-query/patterns")
@login_required
def raporlar_api_nlp_patterns():
    return jsonify({"success": True, "patterns": _NLP_PATTERNS})


@app_bp.route("/reports/api/nlp-query", methods=["GET", "POST"])
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
                        "columns": [_("Kod"), _("PG Adı"), _("Ort. Başarı %"), _("Ölçüm")],
                        "rows": [[r["code"], r["name"], r["avg_score"], r["count"]] for r in result],
                        "summary": f"{_date.today().year} {_('yılı en yüksek 5 PG')}"})

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
                        "columns": [_("Kod"), _("PG Adı"), _("Ort. Başarı %"), _("Ölçüm")],
                        "rows": [[r[0] or "—", r[1], round(r[2] or 0, 1), r[3]] for r in rows],
                        "summary": f"{_date.today().year} {_('yılı en düşük 5 PG')}"})

    if pattern_id == "process_health":
        active_py = get_active_plan_year_for_user(current_user)
        try:
            today = _date.today()
            proc_scores, _unused = compute_process_scores_internal(
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
                        "columns": [_("Kod"), _("Süreç"), _("Sağlık Skoru")],
                        "rows": [[r["code"], r["name"], r["score"] if r["score"] is not None else "—"] for r in result[:30]],
                        "summary": f"{len(result)} {_('süreç sağlık skoru sıralı')}"})

    if pattern_id == "active_initiatives":
        inits = Initiative.query.filter_by(tenant_id=tid, is_active=True).filter(
            Initiative.status.in_(["in_progress", "planned"])).order_by(Initiative.priority).all()
        return jsonify({"success": True, "type": "table",
                        "columns": [_("Kod"), _("Ad"), _("Durum"), _("Öncelik"), _("Bütçe"), _("İlerleme %")],
                        "rows": [[i.code or "—", i.name, i.status, i.priority,
                                  f"{float(i.budget_total or 0):,.0f} ₺", i.progress_pct or 0] for i in inits],
                        "summary": f"{len(inits)} {_('aktif/planlanan initiative')}"})

    if pattern_id == "overdue_activities":
        overdue = ProcessActivity.query.options(joinedload(ProcessActivity.process)).join(Process).filter(
            Process.tenant_id == tid, ProcessActivity.is_active.is_(True),
            ProcessActivity.end_at < datetime.now(timezone.utc),
            ProcessActivity.status != "Tamamlandı",
        ).order_by(ProcessActivity.end_at).limit(20).all()
        return jsonify({"success": True, "type": "table",
                        "columns": [_("Faaliyet"), _("Süreç"), _("Son Tarih"), _("Durum")],
                        "rows": [[a.name or "—",
                                  a.process.code if a.process else "—",
                                  a.end_at.strftime("%d.%m.%Y") if a.end_at else "—",
                                  a.status or "—"] for a in overdue],
                        "summary": f"{len(overdue)} {_('geciken faaliyet (top 20)')}"})

    if pattern_id == "kpi_data_volume":
        rows = db.session.query(
            ProcessKpi.code, ProcessKpi.name, func.count(KpiData.id).label("cnt"),
        ).join(KpiData, KpiData.process_kpi_id == ProcessKpi.id
        ).join(Process, Process.id == ProcessKpi.process_id
        ).filter(Process.tenant_id == tid, KpiData.is_active.is_(True)
        ).group_by(ProcessKpi.code, ProcessKpi.name
        ).order_by(func.count(KpiData.id).desc()).limit(10).all()
        return jsonify({"success": True, "type": "table",
                        "columns": [_("Kod"), _("PG"), _("Ölçüm Sayısı")],
                        "rows": [[r[0] or "—", r[1], r[2]] for r in rows],
                        "summary": _("En çok ölçüm yapılan 10 PG")})

    if pattern_id == "department_user_count":
        rows = db.session.query(User.department, func.count(User.id)).filter(
            User.tenant_id == tid, User.is_active.is_(True),
        ).group_by(User.department).order_by(func.count(User.id).desc()).all()
        return jsonify({"success": True, "type": "table",
                        "columns": [_("Departman"), _("Kullanıcı Sayısı")],
                        "rows": [[r[0] or _("(belirsiz)"), r[1]] for r in rows],
                        "summary": f"{len(rows)} {_('farklı departman')}"})

    if pattern_id == "high_risks":
        from app.models.k_radar_domain import RiskHeatmapItem
        risks = RiskHeatmapItem.query.filter_by(tenant_id=tid, is_active=True).filter(
            RiskHeatmapItem.rpn >= 10).order_by(RiskHeatmapItem.rpn.desc()).all()
        return jsonify({"success": True, "type": "table",
                        "columns": [_("Risk"), _("Olasılık"), _("Etki"), _("RPN"), _("Durum")],
                        "rows": [[r.title, r.probability, r.impact, r.rpn, r.status or "Open"] for r in risks],
                        "summary": f"{_('RPN ≥ 10 olan')} {len(risks)} {_('risk')}"})

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
        return jsonify({"success": True, "type": "text", "summary": _("AI Analizi"),
                        "text": ai_response})

    return jsonify({"success": False, "message": _("Pattern veya sorgu metni gerekli")}), 400


# ─── AI-10: AI Sektör Benchmark ────────────────────────────────────────────

@app_bp.route("/reports/sektor-benchmark")
@login_required
def raporlar_sektor_benchmark():
    return render_template("platform/reports/sektor_benchmark.html")


# ─── Mock sektör ortalamaları ───────────────────────────────────────────────

_SEKTOR_BENCHMARKS = {
    "otomotiv": {
        "OEE": 65, "PPM Defect": 80, "OTIF": 88, "NPS": 45, "EBITDA": 12,
        "Stok Devir": 8, "Patent": 4, "Calisan Devir": 14,
        "CO2": 18000, "eNPS": 25,
    },
    "saglik": {
        "Bekleme Suresi": 25, "Memnuniyet": 78, "Doluluk": 68,
        "Enfeksiyon": 4, "Mortalite": 2.3, "Hekim Devir": 18,
    },
    "finans": {
        "NIM": 3.8, "Cost_Income": 55, "ROE": 14, "NPL": 4.5,
        "CAR": 12.5, "NPS": 42, "Mobil_Adopsyon": 65,
    },
}

# Türkçe etiketler ve birimler
_BENCHMARK_META = {
    "OEE":           {"tr": "Ekipman Verimliliği (OEE)",       "birim": "%"},
    "PPM Defect":    {"tr": "PPM Hata Oranı",                   "birim": "PPM"},
    "OTIF":          {"tr": "Zamanında & Tam Teslimat",          "birim": "%"},
    "NPS":           {"tr": "Net Tavsiye Skoru (NPS)",           "birim": "puan"},
    "EBITDA":        {"tr": "FAVÖK Marjı",                       "birim": "%"},
    "Stok Devir":    {"tr": "Stok Devir Hızı",                   "birim": "x/yıl"},
    "Patent":        {"tr": "Yıllık Patent Sayısı",              "birim": "adet"},
    "Calisan Devir": {"tr": "Çalışan Devir Oranı",               "birim": "%"},
    "CO2":           {"tr": "Karbon Emisyonu",                   "birim": "tCO₂e"},
    "eNPS":          {"tr": "Çalışan Memnuniyet Skoru (eNPS)",  "birim": "puan"},
    "Bekleme Suresi":{"tr": "Ortalama Bekleme Süresi",           "birim": "dk"},
    "Memnuniyet":    {"tr": "Hasta Memnuniyeti",                 "birim": "%"},
    "Doluluk":       {"tr": "Yatak Doluluk Oranı",               "birim": "%"},
    "Enfeksiyon":    {"tr": "Hastane Enfeksiyon Oranı",          "birim": "‰"},
    "Mortalite":     {"tr": "Hastane İçi Mortalite",             "birim": "%"},
    "Hekim Devir":   {"tr": "Hekim Devir Oranı",                 "birim": "%"},
    "NIM":           {"tr": "Net Faiz Marjı (NIM)",              "birim": "%"},
    "Cost_Income":   {"tr": "Maliyet / Gelir Oranı",             "birim": "%"},
    "ROE":           {"tr": "Özkaynak Karlılığı (ROE)",          "birim": "%"},
    "NPL":           {"tr": "Takipteki Kredi Oranı (NPL)",       "birim": "%"},
    "CAR":           {"tr": "Sermaye Yeterlilik Oranı (CAR)",    "birim": "%"},
    "Mobil_Adopsyon":{"tr": "Mobil Bankacılık Kullanımı",        "birim": "%"},
}

_SEKTOR_NAME_TR = {
    "otomotiv": "Otomotiv / Yan Sanayi",
    "saglik":   "Sağlık / Hastane",
    "finans":   "Finans / Bankacılık",
}


def _sektor_context(tid, tenant, sektor_override: str | None = None):
    """Ortak tenant + sektör bağlam hesabı.
    sektor_override: istek parametresinden gelen kullanıcı seçimi (öncelikli).
    """
    sector_field = (tenant.sector or "").lower() if tenant else ""

    # Öncelik: 1) kullanıcı seçimi, 2) tenant.sector eşleşmesi, 3) None (bilinmiyor)
    if sektor_override and sektor_override in _SEKTOR_BENCHMARKS:
        sektor_key = sektor_override
    elif "sağlık" in sector_field or "hastane" in sector_field:
        sektor_key = "saglik"
    elif "finans" in sector_field or "banka" in sector_field:
        sektor_key = "finans"
    elif "otomotiv" in sector_field or "araç" in sector_field or "araç" in sector_field:
        sektor_key = "otomotiv"
    else:
        sektor_key = None  # bilinmiyor — kullanıcı seçmeli
    benchmark = []
    if sektor_key:
        benchmark_raw = _SEKTOR_BENCHMARKS.get(sektor_key, {})
        for k, v in benchmark_raw.items():
            meta = _BENCHMARK_META.get(k, {"tr": k, "birim": ""})
            benchmark.append({"key": k, "tr": meta["tr"], "birim": meta["birim"], "deger": v})
    proc_count = Process.query.filter_by(tenant_id=tid, is_active=True).count()
    kpi_count = (ProcessKpi.query.join(Process)
                 .filter(Process.tenant_id == tid, Process.is_active == True,
                         ProcessKpi.is_active.is_(True)).count())
    user_count = User.query.filter_by(tenant_id=tid, is_active=True).count()
    return {
        "sector_field": sector_field,
        "sektor_key": sektor_key,
        "sektor_adi": _SEKTOR_NAME_TR.get(sektor_key, "") if sektor_key else None,
        "benchmark": benchmark,
        "proc_count": proc_count,
        "kpi_count": kpi_count,
        "user_count": user_count,
        "sektor_secilmedi": sektor_key is None,
    }


@app_bp.route("/reports/api/sektor-benchmark")
@login_required
def raporlar_api_sektor_benchmark():
    tid = _tid_or_none()
    if not tid:
        return jsonify({"success": False, "message": "Tenant yok"}), 400
    tenant = db.session.get(Tenant, tid)
    sektor_override = request.args.get("sektor") or None
    ctx = _sektor_context(tid, tenant, sektor_override)
    return jsonify({"success": True, "data": {
        "tenant_name":    tenant.name if tenant else "—",
        "sektor_key":     ctx["sektor_key"],
        "sektor_adi":     ctx["sektor_adi"],
        "sector":         ctx["sector_field"] or "—",
        "benchmark":      ctx["benchmark"],
        "sektor_secilmedi": ctx["sektor_secilmedi"],
        "sektor_listesi": [
            {"key": k, "adi": v} for k, v in _SEKTOR_NAME_TR.items()
        ],
        "tenant_summary": {
            "process_count": ctx["proc_count"],
            "kpi_count":     ctx["kpi_count"],
            "user_count":    ctx["user_count"],
        },
    }})


@app_bp.route("/reports/api/sektor-benchmark/ai-yorum", methods=["POST"])
@login_required
@csrf.exempt
def raporlar_api_sektor_benchmark_ai():
    """AI yorumu isteğe bağlı — butona basılınca çağrılır."""
    tid = _tid_or_none()
    if not tid:
        return jsonify({"success": False, "message": "Tenant yok"}), 400
    tenant = db.session.get(Tenant, tid)
    body = request.get_json(silent=True) or {}
    sektor_override = body.get("sektor") or request.args.get("sektor") or None
    ctx = _sektor_context(tid, tenant, sektor_override)
    if ctx["sektor_secilmedi"]:
        return jsonify({"success": False, "message": _("Lütfen önce bir sektör seçin.")}), 400
    bench_str = "\n".join(f"  - {b['tr']}: {b['deger']} {b['birim']}" for b in ctx["benchmark"])
    kurum_adi = tenant.name if tenant else "Kurum"
    yorum = _ai_text(
        prompt=(
            f"Sen bir kurumsal performans danışmanısın.\n\n"
            f"Kurum: {kurum_adi}\n"
            f"Sektör: {ctx['sektor_adi']}\n"
            f"Sistemde takip edilen: {ctx['proc_count']} süreç, {ctx['kpi_count']} PG, "
            f"{ctx['user_count']} çalışan\n\n"
            f"Aşağıdaki değerler bu sektörün GENEL ORTALAMALARIDIR. "
            f"{kurum_adi}'nın bu metriklerdeki gerçek ölçüm değerleri henüz sisteme girilmemiştir.\n"
            f"Sektör ortalamaları:\n{bench_str}\n\n"
            f"YAPILMAMASI GEREKEN: Kurumun bu metriklerde nerede durduğunu varsayarak karşılaştırma yapmak.\n"
            f"YAPILMASI GEREKEN: Türkçe 3-4 cümle ile şunları açıkla:\n"
            f"1. Bu sektörde hangi metrikler en kritik ve neden?\n"
            f"2. {ctx['proc_count']} süreç ve {ctx['kpi_count']} PG takip eden bir kurum "
            f"benchmark karşılaştırması yapabilmek için hangi verileri sisteme girmeli?\n"
            f"3. İlk odaklanılması önerilen 1-2 metrik."
        ),
        fallback=(
            f"{kurum_adi}, {ctx['sektor_adi']} sektöründe {ctx['proc_count']} süreç ve "
            f"{ctx['kpi_count']} PG ile faaliyet göstermektedir. "
            f"Gerçek benchmark karşılaştırması yapabilmek için OEE, OTIF, PPM ve NPS gibi "
            f"operasyonel metriklerin PG olarak sisteme eklenmesi ve düzenli ölçüm yapılması gerekmektedir. "
            f"İlk adım olarak süreç bazlı OEE ve teslimat performansı takibinin kurulması önerilir."
        ),
        tid=tid, endpoint="ai_sektor_benchmark", max_tokens=450,
    )
    return jsonify({"success": True, "yorum": yorum})


@app_bp.route("/reports/api/ai-status")
@login_required
def raporlar_api_ai_status():
    """Kullanıcının AI kota durumu — BYOK vs sistem anahtarı."""
    tid = _tid_or_none()
    if not tid:
        return jsonify({"success": False}), 400
    byok = False
    provider = None
    try:
        from app.models.tenant_llm_config import TenantLLMConfig
        cfg = TenantLLMConfig.query.filter_by(tenant_id=tid, is_active=True).first()
        if cfg and cfg.api_key_encrypted:
            byok = True
            provider = cfg.provider
    except Exception:
        pass
    if byok:
        return jsonify({"success": True, "byok": True, "provider": provider or "custom",
                        "label": f"{_('Kendi API anahtarınız')} ({(provider or 'AI').capitalize()}) — {_('Sınırsız')}"})
    # Sistem anahtarı — kota özeti
    try:
        from app.services.llm_quota_service import get_tenant_usage_summary, DEFAULT_LIMITS
        s = get_tenant_usage_summary(tid)
        today = s["today"]
        remain = max(0, today["limit"] - today["used"])
        return jsonify({
            "success": True, "byok": False,
            "paused": s["paused"],
            "today_used": today["used"],
            "today_limit": today["limit"],
            "today_remain": remain,
            "label": f"{_('Sistem API · Bugün')} {remain}/{today['limit']} {_('hak kaldı')}",
        })
    except Exception:
        return jsonify({"success": True, "byok": False, "today_remain": None,
                        "label": _("Sistem API")})


