# -*- coding: utf-8 -*-
"""EFQM Modeli 2025 — Türev Olgunluk Değerlendirmesi.

Kaynak: EFQM Modeli 2025 (KalDer Türkçe çevirisi).
Bu servis Kokpitim verisinden 7 EFQM kriterinin her birine 0-100 olgunluk
skoru türetir, ağırlıklara göre 1000 puanlık toplama indirir ve resmi EFQM
seviye etiketini (İyi/Mükemmel/Dünya Lideri) hesaplar.

EFQM 2025 yapısı:
- YÖN (200 puan):     K1 Amaç/Vizyon/Strateji (100) + K2 Kurum Kültürü ve Liderlik (100)
- UYGULAMA (400 puan): K3 Paydaşlarla Bağ Kurma (100) + K4 Sürdürülebilir Değer Yaratma (200) + K5 Performans ve Dönüşüme Yön Verme (100)
- SONUÇLAR (400 puan): K6 Paydaş Algıları (200) + K7 Stratejik ve Operasyonel Performans (200)

EFQM Tanınma Seviyeleri (toplam 1000 üzerinden):
- 0-299  : Başlangıç / Temel Performans
- 300-499: İyi Performans (Müşteri Odaklılık & Değer Yaratma)
- 500-699: Mükemmel Performans (İnovasyon & Amaç/Vizyon)
- 700+   : Dünya Lideri Performans (Dönüşüm ve Geleceğe Odaklanma)
"""
from __future__ import annotations

import datetime as _dt
import logging
from sqlalchemy import text
from extensions import db

logger = logging.getLogger(__name__)


CRITERIA = [
    # (key, label, dimension, weight)
    ("k1", "Amaç, Vizyon ve Strateji",          "yon",       100),
    ("k2", "Kurum Kültürü ve Liderlik",         "yon",       100),
    ("k3", "Paydaşlarla Bağ Kurma",             "uygulama",  100),
    ("k4", "Sürdürülebilir Değer Yaratma",      "uygulama",  200),
    ("k5", "Performans ve Dönüşüme Yön Verme",  "uygulama",  100),
    ("k6", "Paydaş Algıları",                   "sonuclar",  200),
    ("k7", "Stratejik ve Operasyonel Performans","sonuclar", 200),
]

DIMENSIONS = {
    "yon":      {"label": "Yön",       "color": "#3b82f6", "icon": "fa-compass"},
    "uygulama": {"label": "Uygulama",  "color": "#1e40af", "icon": "fa-cogs"},
    "sonuclar": {"label": "Sonuçlar",  "color": "#10b981", "icon": "fa-chart-line"},
}


def _level_for(total_pts: int) -> dict:
    """EFQM tanınma seviyesi (1000 üzerinden)."""
    if total_pts >= 700:
        return {"label": "Dünya Lideri Performans",
                "tagline": "Dönüşüm ve Geleceğe Yönelik Odaklanma",
                "color": "#059669", "stars": 7, "min": 700, "max": 1000}
    if total_pts >= 600:
        return {"label": "Rol Model Performansı",
                "tagline": "İnovasyon & Veri, Bilgi Birikimi",
                "color": "#10b981", "stars": 6, "min": 600, "max": 699}
    if total_pts >= 500:
        return {"label": "Mükemmel Performans",
                "tagline": "İnovasyon & Amaç / Vizyon",
                "color": "#0ea5e9", "stars": 5, "min": 500, "max": 599}
    if total_pts >= 400:
        return {"label": "Güçlü Performans",
                "tagline": "Strateji ve Değer Yaratma",
                "color": "#6366f1", "stars": 4, "min": 400, "max": 499}
    if total_pts >= 300:
        return {"label": "İyi Performans",
                "tagline": "Müşteri Odaklılık & Değer Yaratma",
                "color": "#8b5cf6", "stars": 3, "min": 300, "max": 399}
    if total_pts >= 200:
        return {"label": "Mükemmellik Yolunda",
                "tagline": "Temel uygulamalar yerleşmekte",
                "color": "#f59e0b", "stars": 2, "min": 200, "max": 299}
    return {"label": "Başlangıç Seviyesi",
            "tagline": "Temel performans — gelişim alanları belirgin",
            "color": "#dc2626", "stars": 1, "min": 0, "max": 199}


def _scalar(sql: str, params: dict) -> float:
    try:
        v = db.session.execute(text(sql), params).scalar()
        return float(v or 0)
    except Exception:
        return 0.0


def _bool(v) -> int:
    return 1 if v else 0


def _clip(x: float, lo: float = 0, hi: float = 100) -> float:
    return max(lo, min(hi, x))


def compute_efqm_assessment(tenant_id: int, plan_year_id: int | None = None) -> dict:
    """Tenant için EFQM 2025 türev değerlendirmesi.

    Returns:
        {
          'total_points': 0-1000,
          'level': {...},
          'criteria': [{key, label, dimension, weight, score_pct, points, ...}],
          'dimensions': {yon: {pts, max}, ...},
          'narrative': [{title, text}, ...],
          'kpi_327': {target, latest_value, gap} | None,
        }
    """
    # py_clause: sadece sabit SQL string + named parameter — kullanıcı girdisi yoktur
    # f-string kullanımı yerine koşullu parametrik sorgu güvenlidir
    py_clause    = "AND plan_year_id = :py"   if plan_year_id else ""
    p_py_clause  = "AND p.plan_year_id = :py" if plan_year_id else ""
    py_params    = {"py": plan_year_id}        if plan_year_id else {}

    # ── Veri toplama ─────────────────────────────────────────────────────────
    strat_count = _scalar(
        "SELECT count(*) FROM strategies WHERE tenant_id=:t AND is_active=true " + py_clause,
        {"t": tenant_id, **py_params})
    sub_strat_count = _scalar(
        "SELECT count(*) FROM sub_strategies WHERE strategy_id IN "
        "(SELECT id FROM strategies WHERE tenant_id=:t AND is_active=true " + py_clause + ") "
        "AND is_active=true",
        {"t": tenant_id, **py_params})
    process_count = _scalar(
        "SELECT count(*) FROM processes WHERE tenant_id=:t AND is_active=true " + py_clause,
        {"t": tenant_id, **py_params})

    # Tenant identity — vizyon/amaç tanımlı mı?
    identity_filled = 0
    try:
        row = db.session.execute(text("""
            SELECT vision, purpose, core_values, code_of_ethics
            FROM tenant_year_identities
            WHERE tenant_id=:t AND (plan_year_id=:py OR :py IS NULL)
            LIMIT 1
        """), {"t": tenant_id, "py": plan_year_id}).fetchone()
        if row:
            identity_filled = sum(_bool(getattr(row, f, None)) for f in
                                  ("vision","purpose","core_values","code_of_ethics"))
    except Exception:
        identity_filled = 0

    # Kullanıcı/rol çeşitliliği (kültür+liderlik göstergesi)
    user_count = _scalar(
        "SELECT count(*) FROM users WHERE tenant_id=:t AND is_active=true",
        {"t": tenant_id})
    role_diversity = _scalar(
        "SELECT count(DISTINCT role_id) FROM users WHERE tenant_id=:t AND is_active=true AND role_id IS NOT NULL",
        {"t": tenant_id})
    department_count = _scalar(
        "SELECT count(DISTINCT department) FROM users WHERE tenant_id=:t AND department IS NOT NULL AND department != ''",
        {"t": tenant_id})

    # PG verisi
    kpi_total = _scalar(
        f"SELECT count(*) FROM process_kpis k JOIN processes p ON k.process_id=p.id "
        "WHERE p.tenant_id=:t AND k.is_active=true AND p.is_active=true " + p_py_clause,
        {"t": tenant_id, **py_params})
    kpi_with_data = _scalar(
        "SELECT count(DISTINCT process_kpi_id) FROM kpi_data WHERE process_kpi_id IN "
        "(SELECT k.id FROM process_kpis k JOIN processes p ON k.process_id=p.id "
        "WHERE p.tenant_id=:t AND k.is_active=true " + p_py_clause + ") "
        "AND is_active=true",
        {"t": tenant_id, **py_params})
    on_target_pct = _scalar("""
        SELECT COALESCE(
          sum(CASE WHEN kd.actual_value ~ '^-?[0-9]+\\.?[0-9]*$' AND kd.target_value ~ '^-?[0-9]+\\.?[0-9]*$'
                     AND kd.actual_value::float >= kd.target_value::float THEN 1 ELSE 0 END) * 100.0 /
          NULLIF(sum(CASE WHEN kd.actual_value ~ '^-?[0-9]+\\.?[0-9]*$' AND kd.target_value ~ '^-?[0-9]+\\.?[0-9]*$' THEN 1 ELSE 0 END), 0),
        0)
        FROM kpi_data kd JOIN process_kpis k ON kd.process_kpi_id=k.id JOIN processes p ON k.process_id=p.id
        WHERE p.tenant_id=:t AND kd.is_active=true
    """, {"t": tenant_id})

    # OKR
    okr_count = _scalar("""SELECT count(*) FROM okr_objectives WHERE tenant_id=:t AND is_active=true""",
                       {"t": tenant_id})

    # Initiative (girişim)
    initiative_count = _scalar("""SELECT count(*) FROM initiatives WHERE tenant_id=:t AND is_active=true""",
                              {"t": tenant_id})
    init_completed = _scalar("""SELECT count(*) FROM initiatives WHERE tenant_id=:t AND is_active=true AND status='completed'""",
                            {"t": tenant_id})

    # BSC perspektif denge (K4 değer yaratma göstergesi)
    bsc_assigned = 0
    bsc_balance = 0
    try:
        rows = db.session.execute(text("""
            SELECT perspective, count(*) c
            FROM bsc_kpi_perspectives
            WHERE tenant_id=:t AND (plan_year_id=:py OR :py IS NULL)
            GROUP BY perspective
        """), {"t": tenant_id, "py": plan_year_id}).fetchall()
        counts = {r.perspective: int(r.c) for r in rows}
        bsc_assigned = sum(counts.values())
        if bsc_assigned > 0:
            from app.services.bsc_auto_classifier import balance_score
            bsc_balance, _ = balance_score(counts)
    except Exception:
        bsc_balance = 0

    # Risk (K5)
    risk_open = _scalar(
        "SELECT count(*) FROM risk_heatmap_items WHERE tenant_id=:t AND is_active=true AND status != 'Closed'",
        {"t": tenant_id})
    risk_critical = _scalar(
        "SELECT count(*) FROM risk_heatmap_items WHERE tenant_id=:t AND is_active=true "
        "AND (COALESCE(probability,0) * COALESCE(impact,0)) >= 16",
        {"t": tenant_id})

    # Faaliyet (K5)
    activity_overdue = _scalar("""
        SELECT count(*) FROM process_activities a JOIN processes p ON a.process_id=p.id
        WHERE p.tenant_id=:t AND a.is_active=true
          AND a.status != 'Tamamlandı' AND a.end_date < CURRENT_DATE
    """, {"t": tenant_id})

    # KPI 327 — EFQM Özdeğerlendirme Puanı (Tomofil için)
    kpi_327 = None
    try:
        row = db.session.execute(text("""
            SELECT k.id, k.target_value, k.name,
                   (SELECT actual_value FROM kpi_data kd
                    WHERE kd.process_kpi_id=k.id AND kd.is_active=true
                    ORDER BY kd.data_date DESC LIMIT 1) as latest
            FROM process_kpis k JOIN processes p ON k.process_id=p.id
            WHERE p.tenant_id=:t AND (k.code = 'KPI-327' OR k.name ILIKE '%efqm%özdeğer%'
                                       OR k.name ILIKE '%efqm özdeger%')
            LIMIT 1
        """), {"t": tenant_id}).fetchone()
        if row:
            try:
                tgt = float(row.target_value or 0)
                act = float(row.latest or 0) if row.latest else None
                kpi_327 = {"id": row.id, "name": row.name,
                           "target": tgt, "latest": act,
                           "gap": (act - tgt) if act is not None else None}
            except (ValueError, TypeError):
                pass
    except Exception as _e:
        logger.error("[efqm] KPI-327 özdeğerlendirme verisi alınamadı (tenant=%s): %s", tenant_id, _e)

    # ── Kriter skorlarını türet (her biri 0-100) ─────────────────────────────
    # K1 — Amaç, Vizyon ve Strateji
    # Bileşenler: vizyon/amaç tanımlı mı (40), strateji sayısı (30), sub-strateji yapı (30)
    k1 = (
        (identity_filled / 4.0) * 40 +
        min(1.0, strat_count / 6.0) * 30 +
        min(1.0, sub_strat_count / 16.0) * 30
    )
    k1 = _clip(k1)

    # K2 — Kurum Kültürü ve Liderlik
    # Bileşenler: kullanıcı tabanı (30), rol çeşitliliği (35), departman çeşitliliği (35)
    k2 = (
        min(1.0, user_count / 50.0) * 30 +
        min(1.0, role_diversity / 5.0) * 35 +
        min(1.0, department_count / 6.0) * 35
    )
    k2 = _clip(k2)

    # K3 — Paydaşlarla Bağ Kurma
    # Bileşenler: çalışan sayısı (25), OKR objektif (25), initiative (25), strateji-paydaş bağ (25)
    k3 = (
        min(1.0, user_count / 50.0) * 25 +
        min(1.0, okr_count / 5.0) * 25 +
        min(1.0, initiative_count / 15.0) * 25 +
        min(1.0, strat_count / 6.0) * 25
    )
    k3 = _clip(k3)

    # K4 — Sürdürülebilir Değer Yaratma
    # Bileşenler: BSC perspektif denge (40), initiative + tamamlanma (30), PG portföy büyüklüğü (30)
    init_completion = (init_completed / initiative_count * 100) if initiative_count else 0
    k4 = (
        (bsc_balance / 100.0) * 40 +
        min(1.0, initiative_count / 15.0) * 15 +
        (init_completion / 100.0) * 15 +
        min(1.0, kpi_total / 50.0) * 30
    )
    k4 = _clip(k4)

    # K5 — Performans ve Dönüşüme Yön Verme
    # Bileşenler: veri giriş disiplini (40), risk yönetimi (20), gecikme yönetimi (40)
    data_disc = (kpi_with_data / kpi_total * 100) if kpi_total else 0
    risk_score = 100 - min(100, risk_critical * 20)  # kritik risk azaldıkça yüksek
    overdue_penalty = max(0, 100 - activity_overdue * 5)  # 20+ gecikme = 0
    k5 = (
        (data_disc / 100.0) * 40 +
        (risk_score / 100.0) * 20 +
        (overdue_penalty / 100.0) * 40
    )
    k5 = _clip(k5)

    # K6 — Paydaş Algıları (Kokpitim'de doğrudan algı verisi yok → düşük baz skor)
    # Bileşenler: müşteri odaklı PG var mı (proxy: BSC müşteri perspektifi atama), çalışan PG'si
    persp_data = db.session.execute(text("""
        SELECT perspective, count(*) c FROM bsc_kpi_perspectives
        WHERE tenant_id=:t GROUP BY perspective
    """), {"t": tenant_id}).fetchall() if True else []
    persp_map = {r.perspective: int(r.c) for r in persp_data} if persp_data else {}
    customer_proxy = min(1.0, persp_map.get("musteri", 0) / 10.0)
    employee_proxy = min(1.0, persp_map.get("ogrenme", 0) / 10.0)
    # Algı verisi yokluğu büyük gap — bu nedenle baz puan düşük
    k6 = (
        customer_proxy * 30 +
        employee_proxy * 30 +
        # İş/Toplum/Tedarikçi algıları için veri yok — sabit 20 baz
        20
    )
    k6 = _clip(k6)

    # K7 — Stratejik ve Operasyonel Performans
    # Bileşenler: PG hedef üstü oranı (60), veri girilen PG oranı (40)
    k7 = (
        (on_target_pct / 100.0) * 60 +
        (data_disc / 100.0) * 40
    )
    k7 = _clip(k7)

    scores = {"k1": k1, "k2": k2, "k3": k3, "k4": k4, "k5": k5, "k6": k6, "k7": k7}

    # ── Puanları ağırlıklı 1000 ölçekli toplama indir ───────────────────────
    criteria_out = []
    dim_totals = {"yon": {"pts": 0, "max": 0},
                  "uygulama": {"pts": 0, "max": 0},
                  "sonuclar": {"pts": 0, "max": 0}}
    total_pts = 0

    notes = {
        "k1": "Plan yılı, vizyon/amaç tanımı, strateji-alt strateji yapısı.",
        "k2": "Çalışan tabanı, rol çeşitliliği ve departman dağılımı.",
        "k3": "Paydaş kategorileri: çalışan, OKR objektif, girişim, strateji bağı.",
        "k4": "BSC perspektif dengesi (Kaplan-Norton ideal %25), girişim portföyü, PG portföy büyüklüğü.",
        "k5": "Veri giriş disiplini, kritik risk yönetimi, gecikmiş faaliyet kontrolü.",
        "k6": "Doğrudan paydaş algı anketi yok — BSC müşteri/öğrenme perspektifi atamaları proxy. Bu kriter en yüksek gelişim alanı.",
        "k7": "Hedef üstü ölçüm oranı (sürdürülebilirlik) + ölçülen PG kapsamı.",
    }

    for key, label, dim, weight in CRITERIA:
        sc = scores[key]
        pts = round(sc / 100.0 * weight)
        criteria_out.append({
            "key": key, "label": label, "dimension": dim, "weight": weight,
            "score_pct": round(sc, 1), "points": pts,
            "note": notes[key],
        })
        dim_totals[dim]["pts"] += pts
        dim_totals[dim]["max"] += weight
        total_pts += pts

    level = _level_for(total_pts)

    # ── Narrative öneriler (hangi alanlar zayıf?) ───────────────────────────
    sorted_c = sorted(criteria_out, key=lambda c: c["score_pct"])
    weakest = sorted_c[:2]
    strongest = sorted_c[-2:]
    narrative = []
    narrative.append({
        "title": "Genel durum",
        "text": f"Toplam {total_pts}/1000 puan — <b>{level['label']}</b> seviyesinde. "
                f"EFQM 2025 doktrini gereği {level['tagline'].lower()} bu seviyede ön plana çıkıyor.",
    })
    for w in weakest:
        narrative.append({
            "title": f"Gelişim alanı: {w['label']} (%{w['score_pct']:.0f})",
            "text": w["note"],
        })
    if strongest:
        narrative.append({
            "title": f"Güçlü yön: {strongest[-1]['label']} (%{strongest[-1]['score_pct']:.0f})",
            "text": strongest[-1]["note"],
        })

    # KPI 327 EFQM özdeğerlendirme puanı varsa: 0-1000 ölçeğine taşı + bilgi notu
    kpi_327_info = None
    if kpi_327 and kpi_327["latest"] is not None:
        kpi_327_info = {
            "kpi_id": kpi_327["id"], "name": kpi_327["name"],
            "manual_score": kpi_327["latest"],
            "manual_target": kpi_327["target"],
            "manual_gap": kpi_327["gap"],
            "note": "Kuruluşun KPI-327 üzerinden manuel EFQM özdeğerlendirme puanı. "
                    "Bu modüldeki türev puan ile karşılaştırılabilir.",
        }

    return {
        "tenant_id": tenant_id,
        "plan_year_id": plan_year_id,
        "generated_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "total_points": total_pts,
        "max_points": 1000,
        "level": level,
        "criteria": criteria_out,
        "dimensions": dim_totals,
        "narrative": narrative,
        "kpi_327": kpi_327_info,
        "model_version": "EFQM 2025",
        "radar": {
            "results":      "Sonuçlar — paydaş algıları ve stratejik/operasyonel performans",
            "approach":     "Yaklaşım — sağlam temelli ve uyumlu yön + uygulama",
            "deployment":   "Yayılım — uygulamanın tutarlı, esnek ve zamanında yapılması",
            "assessment":   "Değerlendirme — etkililik ve verimlilik içgörüleri",
            "refinement":   "İyileştirme — sürekli öğrenme ile yaklaşımı uyarlama",
        },
    }
