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
from flask_babel import gettext as _
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
    """EFQM-BENZERİ olgunluk bandı (1000 üzerinden) — TANINMA SEVİYESİ DEĞİL.

    M11 (2026-07-21): Docstring eskiden "EFQM tanınma seviyesi" diyordu.
    Bu yanıltıcı: EFQM tanınma seviyeleri (Recognised by EFQM, 3/4/5 Star …)
    kurumun KENDİ hesabıyla verilmez — bağımsız EFQM değerlendiricileri
    tarafından RADAR mantığıyla yürütülen bir değerlendirme sonucunda verilir.

    Buradaki bantlar kurumun kendi verisinden TÜRETİLMİŞ bir olgunluk
    göstergesidir. Kriter ağırlıkları EFQM 2025 dağılımıyla örtüşüyor
    (doğrulandı) ama sonuç resmî bir seviye DEĞİLDİR.

    Ayrıca eski docstring DÖRT seviye tanımlarken fonksiyon YEDİ bant
    döndürüyordu — belge ile kod çelişiyordu. Yedi bant korunuyor (UI
    `stars` alanını okuyor), belge koda uyduruldu.
    """
    if total_pts >= 700:
        return {"label": _("Dünya Lideri Performans"),
                "tagline": _("Dönüşüm ve Geleceğe Yönelik Odaklanma"),
                "color": "#059669", "stars": 7, "min": 700, "max": 1000}
    if total_pts >= 600:
        return {"label": _("Rol Model Performansı"),
                "tagline": _("İnovasyon & Veri, Bilgi Birikimi"),
                "color": "#10b981", "stars": 6, "min": 600, "max": 699}
    if total_pts >= 500:
        return {"label": _("Mükemmel Performans"),
                "tagline": _("İnovasyon & Amaç / Vizyon"),
                "color": "#0ea5e9", "stars": 5, "min": 500, "max": 599}
    if total_pts >= 400:
        return {"label": _("Güçlü Performans"),
                "tagline": _("Strateji ve Değer Yaratma"),
                "color": "#6366f1", "stars": 4, "min": 400, "max": 499}
    if total_pts >= 300:
        return {"label": _("İyi Performans"),
                "tagline": _("Müşteri Odaklılık & Değer Yaratma"),
                "color": "#8b5cf6", "stars": 3, "min": 300, "max": 399}
    if total_pts >= 200:
        return {"label": _("Mükemmellik Yolunda"),
                "tagline": _("Temel uygulamalar yerleşmekte"),
                "color": "#f59e0b", "stars": 2, "min": 200, "max": 299}
    return {"label": _("Başlangıç Seviyesi"),
            "tagline": _("Temel performans — gelişim alanları belirgin"),
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
    # py_clause: SP/exec_dashboard ile aynı — seçili yıl VEYA legacy (plan_year_id IS NULL)
    # include_null=True (app.utils.plan_year_filter). KMF Yayın: strateji/süreç NULL etiketli.
    py_clause = (
        "AND (plan_year_id = :py OR plan_year_id IS NULL)" if plan_year_id else ""
    )
    p_py_clause = (
        "AND (p.plan_year_id = :py OR p.plan_year_id IS NULL)" if plan_year_id else ""
    )
    py_params = {"py": plan_year_id} if plan_year_id else {}

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

    # Tenant identity — vizyon/amaç/değerler/etik/kalite (K1.1 / K2.1)
    # Öncelik: seçili yılın tenant_year_identities satırı; boş alanlar → tenants
    # (SP ekranı ile aynı fallback — KMF gibi yıllık satırı olmayan kurumlar)
    identity_filled = 0
    values_ethics_filled = 0
    identity_fields = (
        "vision", "purpose", "core_values", "code_of_ethics", "quality_policy",
    )
    identity_vals = {f: "" for f in identity_fields}
    try:
        if plan_year_id:
            row = db.session.execute(text("""
                SELECT vision, purpose, core_values, code_of_ethics, quality_policy
                FROM tenant_year_identities
                WHERE tenant_id=:t AND plan_year_id=:py
                LIMIT 1
            """), {"t": tenant_id, "py": plan_year_id}).fetchone()
            if row:
                for f in identity_fields:
                    identity_vals[f] = (getattr(row, f, None) or "").strip()
        trow = db.session.execute(text("""
            SELECT vision, purpose, core_values, code_of_ethics, quality_policy
            FROM tenants WHERE id=:t LIMIT 1
        """), {"t": tenant_id}).fetchone()
        if trow:
            for f in identity_fields:
                if not identity_vals[f]:
                    identity_vals[f] = (getattr(trow, f, None) or "").strip()
        identity_filled = sum(1 for f in identity_fields if identity_vals[f])
        values_ethics_filled = sum(
            1 for f in ("core_values", "code_of_ethics") if identity_vals[f]
        )
    except Exception:
        identity_filled = 0
        values_ethics_filled = 0

    # K1.2 — Ekosistem: SWOT veya PESTEL (içerikli kayıt; biri yeterli)
    def _nonempty_json_text(col: str) -> str:
        return (
            f"({col} IS NOT NULL AND btrim({col}) <> '' "
            f"AND btrim({col}) NOT IN ('[]', 'null', 'NULL'))"
        )

    swot_content = " OR ".join(
        _nonempty_json_text(c)
        for c in ("strengths", "weaknesses", "opportunities", "threats")
    )
    pestel_content = " OR ".join(
        _nonempty_json_text(c)
        for c in (
            "political", "economic", "social",
            "technological", "environmental", "legal",
        )
    )
    swot_n = _scalar(
        "SELECT count(*) FROM swot_analyses WHERE tenant_id=:t "
        + ("AND (plan_year_id=:py OR plan_year_id IS NULL) " if plan_year_id else "")
        + "AND (" + swot_content + ")",
        {"t": tenant_id, **py_params},
    )
    pestel_n = _scalar(
        "SELECT count(*) FROM pestel_analyses WHERE tenant_id=:t "
        + ("AND (plan_year_id=:py OR plan_year_id IS NULL) " if plan_year_id else "")
        + "AND (" + pestel_content + ")",
        {"t": tenant_id, **py_params},
    )
    ecosystem_ok = (swot_n + pestel_n) > 0

    # K1.4 — PMS iskeleti: aktif süreç + aktif PG; veri satırı bonus
    pms_proc_kpi = _scalar(
        "SELECT count(*) FROM process_kpis k "
        "JOIN processes p ON k.process_id=p.id "
        "WHERE p.tenant_id=:t AND p.is_active=true AND k.is_active=true "
        + p_py_clause,
        {"t": tenant_id, **py_params},
    )
    pms_with_data = _scalar(
        "SELECT count(*) FROM kpi_data kd "
        "JOIN process_kpis k ON kd.process_kpi_id=k.id "
        "JOIN processes p ON k.process_id=p.id "
        "WHERE p.tenant_id=:t AND p.is_active=true AND k.is_active=true "
        "AND kd.is_active=true "
        + p_py_clause,
        {"t": tenant_id, **py_params},
    )

    # Kullanıcı/rol çeşitliliği (K2.3 + K3 proxy)
    user_count = _scalar(
        "SELECT count(*) FROM users WHERE tenant_id=:t AND is_active=true",
        {"t": tenant_id})
    role_diversity = _scalar(
        "SELECT count(DISTINCT role_id) FROM users WHERE tenant_id=:t AND is_active=true AND role_id IS NOT NULL",
        {"t": tenant_id})
    department_count = _scalar(
        "SELECT count(DISTINCT department) FROM users WHERE tenant_id=:t AND department IS NOT NULL AND department != ''",
        {"t": tenant_id})

    # K2.2 — süreç lideri ataması (process_leaders)
    proc_with_leader = _scalar(
        "SELECT count(DISTINCT p.id) FROM processes p "
        "JOIN process_leaders pl ON pl.process_id=p.id "
        "WHERE p.tenant_id=:t AND p.is_active=true " + p_py_clause,
        {"t": tenant_id, **py_params},
    )
    leader_ratio = (proc_with_leader / process_count) if process_count > 0 else 0.0

    # K2.4 — iyileştirme kültürü: maturity veya A3
    maturity_n = _scalar(
        "SELECT count(*) FROM process_maturity WHERE tenant_id=:t AND is_active=true",
        {"t": tenant_id},
    )
    a3_n = _scalar(
        "SELECT count(*) FROM a3_reports WHERE tenant_id=:t AND is_active=true",
        {"t": tenant_id},
    )
    improve_ok = (maturity_n + a3_n) > 0

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
    # A-012: K7.1 PG hedef başarısı — motorun PG başarısı (yön, yıl, yıllık hedef, parse);
    # birim PG (satır değil): skoru >= 100 olan PG / ölçülmüş PG.
    on_target_pct = 0.0
    try:
        from app.services import pg_year_scores as _pys
        from app.models.plan_year import PlanYear as _PY
        from app.utils.tr_time import today_tr as _today_tr
        _py = db.session.get(_PY, plan_year_id) if plan_year_id else None
        _yr = _py.year if _py else _today_tr().year
        _rows, _pgs = _pys.score_rows(tenant_id, _yr)
        _tot, _on, _cmp = _pys.on_target_stats(_rows, [p.id for p in _pgs])
        on_target_pct = (_on * 100.0 / _cmp) if _cmp else 0.0
    except Exception as e:
        logger.warning("efqm K7.1 motor hesabı başarısız: %s", e)

    # OKR
    okr_count = _scalar("""SELECT count(*) FROM okr_objectives WHERE tenant_id=:t AND is_active=true""",
                       {"t": tenant_id})

    # Initiative (girişim)
    initiative_count = _scalar("""SELECT count(*) FROM initiatives WHERE tenant_id=:t AND is_active=true""",
                              {"t": tenant_id})
    init_completed = _scalar("""SELECT count(*) FROM initiatives WHERE tenant_id=:t AND is_active=true AND status='completed'""",
                            {"t": tenant_id})

    # K3 — paydaş haritası + anket
    stake_map_n = _scalar(
        "SELECT count(*) FROM stakeholder_maps WHERE tenant_id=:t AND is_active=true "
        + py_clause,
        {"t": tenant_id, **py_params},
    )
    stake_map_quality_n = _scalar(
        "SELECT count(*) FROM stakeholder_maps WHERE tenant_id=:t AND is_active=true "
        "AND influence IS NOT NULL AND interest IS NOT NULL "
        + py_clause,
        {"t": tenant_id, **py_params},
    )
    stake_map_quality_ratio = (
        (stake_map_quality_n / stake_map_n) if stake_map_n > 0 else 0.0
    )
    stake_survey_n = _scalar(
        "SELECT count(*) FROM stakeholder_surveys WHERE tenant_id=:t AND is_active=true",
        {"t": tenant_id},
    )

    # K4.1 — strateji hizası (süreç link + girişim strategy_id)
    proc_strat_linked = _scalar(
        "SELECT count(DISTINCT p.id) FROM processes p "
        "JOIN process_sub_strategy_links l ON l.process_id=p.id "
        "WHERE p.tenant_id=:t AND p.is_active=true " + p_py_clause,
        {"t": tenant_id, **py_params},
    )
    proc_align_ratio = (
        (proc_strat_linked / process_count) if process_count > 0 else 0.0
    )
    init_strat_linked = _scalar(
        "SELECT count(*) FROM initiatives WHERE tenant_id=:t AND is_active=true "
        "AND strategy_id IS NOT NULL",
        {"t": tenant_id},
    )
    init_align_ratio = (
        (init_strat_linked / initiative_count) if initiative_count > 0 else 0.0
    )

    # Risk (K5)
    risk_total = _scalar(
        "SELECT count(*) FROM risk_heatmap_items WHERE tenant_id=:t AND is_active=true",
        {"t": tenant_id})
    risk_critical = _scalar(
        "SELECT count(*) FROM risk_heatmap_items WHERE tenant_id=:t AND is_active=true "
        "AND (COALESCE(probability,0) * COALESCE(impact,0)) >= 16",
        {"t": tenant_id})

    # Faaliyet (K5)
    activity_total = _scalar("""
        SELECT count(*) FROM process_activities a JOIN processes p ON a.process_id=p.id
        WHERE p.tenant_id=:t AND a.is_active=true
    """, {"t": tenant_id})
    activity_overdue = _scalar("""
        SELECT count(*) FROM process_activities a JOIN processes p ON a.process_id=p.id
        WHERE p.tenant_id=:t AND a.is_active=true
          AND a.status != 'Tamamlandı' AND a.end_date < CURRENT_DATE
    """, {"t": tenant_id})
    activity_completed = _scalar("""
        SELECT count(*) FROM process_activities a JOIN processes p ON a.process_id=p.id
        WHERE p.tenant_id=:t AND a.is_active=true AND a.status = 'Tamamlandı'
    """, {"t": tenant_id})

    # Dönüşüm — devam eden girişim (K5.3)
    init_in_progress = _scalar(
        "SELECT count(*) FROM initiatives WHERE tenant_id=:t AND is_active=true "
        "AND status='in_progress'",
        {"t": tenant_id},
    )

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
            except (ValueError, TypeError) as e:
                logger.warning(f"compute_efqm_assessment failed: {e}")
    except Exception as _e:
        logger.error("[efqm] KPI-327 özdeğerlendirme verisi alınamadı (tenant=%s): %s", tenant_id, _e)

    # ── Kriter skorlarını türet (her biri 0-100) ─────────────────────────────
    # Her bileşen: (etiket, ham_değer_metni, katkı_puanı_0-100_ölçeğinde, bu_bileşenin_ağırlığı)
    # katkı_puanı zaten weight ile çarpılmış haldedir (0-weight aralığında); toplamı k_score'a eşittir.
    sub_components = {}

    # K1 — Amaç, Vizyon ve Strateji (EFQM 2025 · 100)
    # 1.1 kimlik 30 · 1.2 ekosistem (SWOT|PESTEL) 20 · 1.3 strateji yapısı 30 · 1.4 PMS 20
    # Plan: docs/kontrol/EFQM-K1-PLAN.md
    k1_c1 = (identity_filled / 5.0) * 30
    k1_c2 = 20.0 if ecosystem_ok else 0.0
    k1_c3a = min(1.0, strat_count / 6.0) * 15
    k1_c3b = min(1.0, sub_strat_count / 16.0) * 15
    k1_c3 = k1_c3a + k1_c3b
    k1_c4a = 10.0 if pms_proc_kpi > 0 else 0.0
    k1_c4b = 10.0 if pms_with_data > 0 else 0.0
    k1_c4 = k1_c4a + k1_c4b
    k1 = _clip(k1_c1 + k1_c2 + k1_c3 + k1_c4)
    eco_raw = (
        _("SWOT/PESTEL var")
        if ecosystem_ok
        else _("SWOT/PESTEL yok")
    )
    sub_components["k1"] = [
        {
            "label": _("1.1 Amaç/Vizyon/Değerler/Etik/Kalite"),
            "raw": f"{identity_filled}/5",
            "score": round(k1_c1, 1),
            "max": 30,
        },
        {
            "label": _("1.2 Ekosistem (SWOT veya PESTEL)"),
            "raw": eco_raw,
            "score": round(k1_c2, 1),
            "max": 20,
        },
        {
            "label": _("1.3 Ana + alt strateji yapısı"),
            "raw": f"{int(strat_count)}/6 · {int(sub_strat_count)}/16",
            "score": round(k1_c3, 1),
            "max": 30,
        },
        {
            "label": _("1.4 PMS (süreç+PG + veri)"),
            "raw": (
                f"PG:{int(pms_proc_kpi)} · veri:{'var' if pms_with_data else 'yok'}"
            ),
            "score": round(k1_c4, 1),
            "max": 20,
        },
    ]

    # K2 — Kurum Kültürü ve Liderlik (EFQM 2025 · 100)
    # 2.1 değer/etik 30 · 2.2 lider oranı 35 · 2.3 örgüt çeşitliliği 20 · 2.4 maturity|A3 15
    # Plan: docs/kontrol/EFQM-K2-PLAN.md
    k2_c1 = (values_ethics_filled / 2.0) * 30
    k2_c2 = leader_ratio * 35
    k2_c3a = min(1.0, role_diversity / 5.0) * 10
    k2_c3b = min(1.0, department_count / 6.0) * 10
    k2_c3 = k2_c3a + k2_c3b
    k2_c4 = 15.0 if improve_ok else 0.0
    k2 = _clip(k2_c1 + k2_c2 + k2_c3 + k2_c4)
    improve_raw = (
        _("maturity/A3 var")
        if improve_ok
        else _("maturity/A3 yok")
    )
    sub_components["k2"] = [
        {
            "label": _("2.1 Değerler ve etik"),
            "raw": f"{values_ethics_filled}/2",
            "score": round(k2_c1, 1),
            "max": 30,
        },
        {
            "label": _("2.2 Süreç lideri ataması"),
            "raw": f"{int(proc_with_leader)}/{int(process_count)}",
            "score": round(k2_c2, 1),
            "max": 35,
        },
        {
            "label": _("2.3 Rol + departman çeşitliliği"),
            "raw": f"rol:{int(role_diversity)}/5 · dep:{int(department_count)}/6",
            "score": round(k2_c3, 1),
            "max": 20,
        },
        {
            "label": _("2.4 İyileştirme (maturity veya A3)"),
            "raw": improve_raw,
            "score": round(k2_c4, 1),
            "max": 15,
        },
    ]

    # K3 — Paydaşlarla Bağ Kurma (EFQM 2025 · 100)
    # 3.1 harita 35 · 3.2 harita niteliği 20 · 3.3 anket 25 · 3.4 OKR+girişim 20
    # Plan: docs/kontrol/EFQM-K3-PLAN.md
    k3_c1 = min(1.0, stake_map_n / 8.0) * 35
    k3_c2 = stake_map_quality_ratio * 20
    k3_c3 = min(1.0, stake_survey_n / 3.0) * 25
    k3_c4a = min(1.0, okr_count / 5.0) * 10
    k3_c4b = min(1.0, initiative_count / 15.0) * 10
    k3_c4 = k3_c4a + k3_c4b
    k3 = _clip(k3_c1 + k3_c2 + k3_c3 + k3_c4)
    sub_components["k3"] = [
        {
            "label": _("3.1 Paydaş haritası"),
            "raw": f"{int(stake_map_n)}/8",
            "score": round(k3_c1, 1),
            "max": 35,
        },
        {
            "label": _("3.2 Harita niteliği (etki+ilgi)"),
            "raw": f"{int(stake_map_quality_n)}/{int(stake_map_n)}",
            "score": round(k3_c2, 1),
            "max": 20,
        },
        {
            "label": _("3.3 Dinleme (paydaş anketi)"),
            "raw": f"{int(stake_survey_n)}/3",
            "score": round(k3_c3, 1),
            "max": 25,
        },
        {
            "label": _("3.4 Eylem bağı (OKR + girişim)"),
            "raw": f"OKR:{int(okr_count)}/5 · girişim:{int(initiative_count)}/15",
            "score": round(k3_c4, 1),
            "max": 20,
        },
    ]

    # K4 — Sürdürülebilir Değer Yaratma (EFQM 2025 · iç 100 · ağırlık 200)
    # 4.1 hiza 30 · 4.2 portföy 25 · 4.3 teslim 25 · 4.4 ölçüm 20 — BSC yok
    # Plan: docs/kontrol/EFQM-K4-PLAN.md
    init_completion = (init_completed / initiative_count * 100) if initiative_count else 0
    k4_c1a = proc_align_ratio * 15
    k4_c1b = init_align_ratio * 15
    k4_c1 = k4_c1a + k4_c1b
    k4_c2 = min(1.0, initiative_count / 10.0) * 25
    k4_c3 = (init_completion / 100.0) * 25
    k4_c4 = min(1.0, kpi_with_data / 30.0) * 20
    k4 = _clip(k4_c1 + k4_c2 + k4_c3 + k4_c4)
    sub_components["k4"] = [
        {
            "label": _("4.1 Hiza (süreç + girişim-strateji)"),
            "raw": (
                f"süreç:{int(proc_strat_linked)}/{int(process_count)} · "
                f"girişim:{int(init_strat_linked)}/{int(initiative_count)}"
            ),
            "score": round(k4_c1, 1),
            "max": 30,
        },
        {
            "label": _("4.2 Değer portföyü (girişim)"),
            "raw": f"{int(initiative_count)}/10",
            "score": round(k4_c2, 1),
            "max": 25,
        },
        {
            "label": _("4.3 Değer teslimi (tamamlanma)"),
            "raw": f"%{round(init_completion, 1)}",
            "score": round(k4_c3, 1),
            "max": 25,
        },
        {
            "label": _("4.4 Değer ölçümü (veri girilen PG)"),
            "raw": f"{int(kpi_with_data)}/30",
            "score": round(k4_c4, 1),
            "max": 20,
        },
    ]

    # K5 — Performans ve Dönüşüme Yön Verme (EFQM 2025 · 100)
    # 5.1 izleme 25 · 5.2 risk 30 · 5.3 dönüşüm 25 · 5.4 operasyon 20
    # Plan: docs/kontrol/EFQM-K5-PLAN.md — boş risk/faaliyet = 0
    data_disc = (kpi_with_data / kpi_total * 100) if kpi_total else 0
    k5_c1 = (data_disc / 100.0) * 25
    if risk_total > 0:
        k5_c2a = min(1.0, risk_total / 5.0) * 15
        k5_c2b = (1.0 - (risk_critical / risk_total)) * 15
        k5_c2 = k5_c2a + k5_c2b
    else:
        k5_c2 = 0.0
    improve_depth = maturity_n + a3_n
    k5_c3a = min(1.0, init_in_progress / 5.0) * 15
    k5_c3b = min(1.0, improve_depth / 3.0) * 10
    k5_c3 = k5_c3a + k5_c3b
    if activity_total > 0:
        overdue_penalty = max(0.0, 100.0 - activity_overdue * 5)
        k5_c4 = (overdue_penalty / 100.0) * 20
    else:
        overdue_penalty = 0.0
        k5_c4 = 0.0
    k5 = _clip(k5_c1 + k5_c2 + k5_c3 + k5_c4)
    sub_components["k5"] = [
        {
            "label": _("5.1 Performans izleme (PG veri oranı)"),
            "raw": f"%{round(data_disc, 1)}",
            "score": round(k5_c1, 1),
            "max": 25,
        },
        {
            "label": _("5.2 Risk sistemi"),
            "raw": f"risk:{int(risk_total)} · kritik:{int(risk_critical)}",
            "score": round(k5_c2, 1),
            "max": 30,
        },
        {
            "label": _("5.3 Dönüşüm (girişim + maturity/A3)"),
            "raw": (
                f"devam:{int(init_in_progress)}/5 · "
                f"iyilestirme:{int(improve_depth)}/3"
            ),
            "score": round(k5_c3, 1),
            "max": 25,
        },
        {
            "label": _("5.4 Operasyon disiplini"),
            "raw": (
                f"faaliyet:{int(activity_total)} · gecikme:{int(activity_overdue)}"
            ),
            "score": round(k5_c4, 1),
            "max": 20,
        },
    ]

    # K6 — Paydaş Algıları (EFQM 2025 · iç 100 · ağırlık 200)
    # 6.1 tip çeşitliliği 35 · 6.2 ortalama skor 40 · 6.3 derinlik 25 — BSC yok
    # Plan: docs/kontrol/EFQM-K6-PLAN.md
    stake_type_n = _scalar(
        "SELECT count(DISTINCT stakeholder_type) FROM stakeholder_surveys "
        "WHERE tenant_id=:t AND is_active=true "
        "AND stakeholder_type IS NOT NULL AND btrim(stakeholder_type) <> ''",
        {"t": tenant_id},
    )
    survey_score_avg = None
    try:
        row = db.session.execute(text("""
            SELECT avg(score) AS avg_score
            FROM stakeholder_surveys
            WHERE tenant_id=:t AND is_active=true AND score IS NOT NULL
        """), {"t": tenant_id}).fetchone()
        if row and row.avg_score is not None:
            survey_score_avg = float(row.avg_score)
    except Exception:
        survey_score_avg = None

    k6_c1 = min(1.0, stake_type_n / 4.0) * 35
    if survey_score_avg is not None:
        # 0–100 varsayımı; taşan değerleri kırp
        k6_c2 = (_clip(survey_score_avg, 0, 100) / 100.0) * 40
    else:
        k6_c2 = 0.0
    k6_c3 = min(1.0, stake_survey_n / 5.0) * 25
    k6 = _clip(k6_c1 + k6_c2 + k6_c3)
    score_raw = (
        f"%{round(survey_score_avg, 1)}"
        if survey_score_avg is not None
        else _("skor yok")
    )
    sub_components["k6"] = [
        {
            "label": _("6.1 Algı kapsamı (paydaş tipi)"),
            "raw": f"{int(stake_type_n)}/4",
            "score": round(k6_c1, 1),
            "max": 35,
        },
        {
            "label": _("6.2 Algı skoru (anket ort.)"),
            "raw": score_raw,
            "score": round(k6_c2, 1),
            "max": 40,
        },
        {
            "label": _("6.3 Dinleme derinliği"),
            "raw": f"{int(stake_survey_n)}/5",
            "score": round(k6_c3, 1),
            "max": 25,
        },
    ]

    # K7 — Stratejik ve Operasyonel Performans (EFQM 2025 · iç 100 · ağırlık 200)
    # 7.1 PG hedef 50 · 7.2 girişim sonucu 25 · 7.3 faaliyet sonucu 25 — data_disc yok
    # Plan: docs/kontrol/EFQM-K7-PLAN.md
    activity_completion = (
        (activity_completed / activity_total * 100) if activity_total else 0
    )
    k7_c1 = (on_target_pct / 100.0) * 50
    k7_c2 = (init_completion / 100.0) * 25
    k7_c3 = (activity_completion / 100.0) * 25
    k7 = _clip(k7_c1 + k7_c2 + k7_c3)
    sub_components["k7"] = [
        {
            "label": _("7.1 PG hedef başarısı"),
            "raw": f"%{round(on_target_pct, 1)}",
            "score": round(k7_c1, 1),
            "max": 50,
        },
        {
            "label": _("7.2 Stratejik sonuç (girişim)"),
            "raw": f"{int(init_completed)}/{int(initiative_count)}",
            "score": round(k7_c2, 1),
            "max": 25,
        },
        {
            "label": _("7.3 Operasyonel sonuç (faaliyet)"),
            "raw": f"{int(activity_completed)}/{int(activity_total)}",
            "score": round(k7_c3, 1),
            "max": 25,
        },
    ]

    scores = {"k1": k1, "k2": k2, "k3": k3, "k4": k4, "k5": k5, "k6": k6, "k7": k7}

    # ── Puanları ağırlıklı 1000 ölçekli toplama indir ───────────────────────
    criteria_out = []
    dim_totals = {"yon": {"pts": 0, "max": 0},
                  "uygulama": {"pts": 0, "max": 0},
                  "sonuclar": {"pts": 0, "max": 0}}
    total_pts = 0

    notes = {
        "k1": _(
            "1.1 kimlik (yıl satırı + tenants fallback) · 1.2 SWOT veya PESTEL · "
            "1.3 strateji/alt strateji · 1.4 süreç+PG ve veri. Seçili plan yılı "
            "(+ etiketsiz legacy kayıtlar)."
        ),
        "k2": _("Değer/etik (yıl+tenants), süreç lideri oranı, örgüt çeşitliliği, maturity/A3."),
        "k3": _("Paydaş haritası, dinleme anketi, OKR/girişim eylem bağı."),
        "k4": _("Strateji hizası, girişim portföyü/teslimi, veri girilen PG."),
        "k5": _("PG izleme oranı, risk sistemi, dönüşüm (girişim/maturity/A3), operasyon disiplini."),
        "k6": _("Paydaş anketi: tip kapsamı, ortalama skor, dinleme derinliği."),
        "k7": _("PG hedef başarısı, girişim tamamlanma, faaliyet tamamlanma — sonuç proxy."),
    }

    for key, label, dim, weight in CRITERIA:
        sc = scores[key]
        pts = round(sc / 100.0 * weight)
        # Alt bileşenleri de kriterin ağırlık ölçeğine (weight) orantılı taşı —
        # böylece her bileşenin nihai 1000 puanlık toplama katkısı görülebilir.
        scaled_subs = [
            {
                "label": sc_item["label"],
                "raw": sc_item["raw"],
                "points": round(sc_item["score"] / 100.0 * weight, 1),
                "max_points": round(sc_item["max"] / 100.0 * weight, 1),
            }
            for sc_item in sub_components.get(key, [])
        ]
        criteria_out.append({
            "key": key, "label": label, "dimension": dim, "weight": weight,
            "score_pct": round(sc, 1), "points": pts,
            "note": notes[key],
            "sub_components": scaled_subs,
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
        "title": _("Genel durum"),
        "text": _("Toplam %(pts)s/1000 puan — <b>%(label)s</b> seviyesinde. "
                  "EFQM 2025 doktrini gereği %(tagline)s bu seviyede ön plana çıkıyor.") % {
                  "pts": total_pts, "label": level['label'], "tagline": level['tagline'].lower()},
    })
    for w in weakest:
        narrative.append({
            "title": _("Gelişim alanı: %(label)s (%%%(pct).0f)") % {"label": w['label'], "pct": w['score_pct']},
            "text": w["note"],
        })
    if strongest:
        narrative.append({
            "title": _("Güçlü yön: %(label)s (%%%(pct).0f)") % {"label": strongest[-1]['label'], "pct": strongest[-1]['score_pct']},
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
            "note": _("Kuruluşun KPI-327 üzerinden manuel EFQM özdeğerlendirme puanı. "
                      "Bu modüldeki türev puan ile karşılaştırılabilir."),
        }

    # Seçili yıl etiketi (UI)
    plan_year_label = None
    plan_year_year = None
    if plan_year_id:
        try:
            py_row = db.session.execute(text(
                "SELECT year, name FROM plan_years WHERE id=:id LIMIT 1"
            ), {"id": plan_year_id}).fetchone()
            if py_row:
                plan_year_year = int(py_row.year) if py_row.year is not None else None
                plan_year_label = (py_row.name or "").strip() or (
                    str(plan_year_year) if plan_year_year else None
                )
        except Exception as e:
            logger.error(f"compute_efqm_assessment failed: {e}")

    return {
        "tenant_id": tenant_id,
        "plan_year_id": plan_year_id,
        "plan_year_year": plan_year_year,
        "plan_year_label": plan_year_label,
        "generated_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "total_points": total_pts,
        "max_points": 1000,
        "level": level,
        "criteria": criteria_out,
        "dimensions": dim_totals,
        "narrative": narrative,
        "kpi_327": kpi_327_info,
        "model_version": "EFQM 2025",
        # M11 (2026-07-21): kullanıcı neye baktığını bilmeli. Kriter
        # ağırlıkları EFQM 2025 dağılımıyla örtüşüyor (doğrulandı) ama bu
        # bir ÖZ-DEĞERLENDİRMEDİR; EFQM tanınma seviyeleri bağımsız
        # değerlendiricilerce RADAR yordamıyla verilir.
        # "Türetilmiş, resmî değil" demek aracı zayıflatmaz — metodolojik
        # olgunluk sinyali verir.
        "methodology_note": _(
            "Bu değerlendirme EFQM 2025 kriter ağırlıklarından uyarlanmış bir "
            "ÖZ-DEĞERLENDİRMEDİR; resmî bir EFQM tanınma seviyesi DEĞİLDİR. "
            "Resmî tanınma, bağımsız EFQM değerlendiricileri tarafından RADAR "
            "yordamıyla yürütülen bir değerlendirme gerektirir."
        ),
        "is_official_assessment": False,
        "radar": {
            "results":      _("Sonuçlar — paydaş algıları ve stratejik/operasyonel performans"),
            "approach":     _("Yaklaşım — sağlam temelli ve uyumlu yön + uygulama"),
            "deployment":   _("Yayılım — uygulamanın tutarlı, esnek ve zamanında yapılması"),
            "assessment":   _("Değerlendirme — etkililik ve verimlilik içgörüleri"),
            "refinement":   _("İyileştirme — sürekli öğrenme ile yaklaşımı uyarlama"),
        },
    }


def summarize_efqm_for_card(
    tenant_id: int, plan_year_id: int | None = None
) -> dict:
    """KD11 hub kartı özeti — modal ile aynı motor (`compute_efqm_assessment`).

    Kart alanları (geriye uyumlu anahtarlar):
      criterion_coverage: skoru > 0 olan kriter sayısı (0–7)
      readiness_score: total_points / 10 → 0–100 (1000 ölçeğin yüzdesi)
    """
    assessment = compute_efqm_assessment(tenant_id, plan_year_id)
    total = int(assessment.get("total_points") or 0)
    hit = sum(
        1
        for c in (assessment.get("criteria") or [])
        if float(c.get("score_pct") or 0) > 0
    )
    level = assessment.get("level") or {}
    return {
        "criterion_coverage": hit,
        "criterion_total": 7,
        "readiness_score": min(100, round(total / 10.0)),
        "total_points": total,
        "max_points": 1000,
        "level_label": level.get("label"),
        "plan_year_id": assessment.get("plan_year_id"),
        "plan_year_year": assessment.get("plan_year_year"),
        "plan_year_label": assessment.get("plan_year_label"),
        "is_official_assessment": False,
        "model_version": assessment.get("model_version") or "EFQM 2025",
    }
