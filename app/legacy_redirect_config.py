# -*- coding: utf-8 -*-
"""Legacy HTML yönlendirme tablosu — middleware ve main deprecated decorator ortak."""
from __future__ import annotations

EXACT_ENDPOINT: dict[str, str] = {
    "/masaustu-launcher": "app_bp.launcher",
    "/bireysel": "app_bp.bireysel_karne",
    "/bireysel/karne": "app_bp.bireysel_karne",
    "/profil": "app_bp.profil",
    "/bildirim": "app_bp.bildirim",
    "/ayarlar": "app_bp.ayarlar",
    "/ayarlar/hesap": "app_bp.ayarlar_hesap",
    "/ayarlar/eposta": "app_bp.ayarlar_eposta",
    "/ayarlar/zamanlanmis-raporlar": "app_bp.scheduled_reports_page",
    "/dashboard": "app_bp.masaustu",
    "/surec-karnesi": "app_bp.surec",
    "/surec-paneli": "app_bp.surec",
    "/gorevlerim": "app_bp.bireysel_karne",
    "/performans-kartim": "app_bp.bireysel_karne",
    "/kurum-paneli": "app_bp.kurum",
    "/kurum-yonetim": "app_bp.kurum_ayarlar",
    "/admin-panel": "app_bp.yonetim_paneli",
    "/projeler": "app_bp.project_list",
    "/projeler/yeni": "app_bp.project_new",
    "/stratejik-planlama-akisi": "app_bp.sp",
    "/stratejik-planlama-akisi/dinamik": "app_bp.sp_flow",
    "/stratejik-asistan": "app_bp.sp",
    "/redmine": "app_bp.bireysel_karne",
    "/bireysel-panel": "app_bp.bireysel_karne",
    "/easy-login": "public_login",
    "/login-user": "public_login",
}

# raporlar iç Türkçe segment köprüleri (TASK-204). Canonical /reports/ muafiyetinden ÖNCE
# uygulanır (legacy_sunset _legacy_sunset_redirect başında). Hem /reports/<TR> hem (kök
# köprüsünden gelen) /raporlar/<TR> bu segmentleri yeni İngilizce karşılığına 301'ler.
REPORTS_SEGMENT_REWRITE: list[tuple[str, str]] = [
    ("/reports/bireysel-karne-batch", "/reports/individual-scorecard-batch"),
    ("/reports/bireysel-hizalama", "/reports/individual-alignment"),
    ("/reports/operasyon-istatistik", "/reports/operation-statistics"),
    ("/reports/departman-performans", "/reports/department-performance"),
    ("/reports/yonetici-liderlik", "/reports/executive-leadership"),
    ("/reports/k-vektor-carpiklik", "/reports/k-vector-skewness"),
    ("/reports/strateji-hikayesi", "/reports/strategy-story"),
    ("/reports/stratejik-yillik", "/reports/strategic-annual"),
    ("/reports/yatirimci-sunum", "/reports/investor-presentation"),
    ("/reports/hizalama-sankey", "/reports/alignment-sankey"),
    ("/reports/hedef-revizyon", "/reports/target-revision"),
    ("/reports/muda-analizi", "/reports/muda-analysis"),
    ("/reports/sabah-ozeti", "/reports/morning-summary"),
    ("/reports/evrim-filmi", "/reports/evolution-film"),
    ("/reports/ai-danisman", "/reports/ai-advisor"),
    ("/reports/ai-sunum", "/reports/ai-presentation"),
    ("/reports/esg-yonetim", "/reports/esg-management"),
    ("/reports/esg-rapor", "/reports/esg-report"),
    ("/reports/audit-paketi", "/reports/audit-package"),
    ("/reports/veri-kalitesi", "/reports/data-quality"),
    ("/reports/onay-zinciri", "/reports/approval-chain"),
    ("/reports/pg-proje-etki", "/reports/pg-project-impact"),
    ("/reports/sektorel", "/reports/sectoral"),
    ("/reports/iki-fa", "/reports/two-fa"),
]

PREFIX_REWRITE: list[tuple[str, str]] = [
    ("/raporlar/", "/reports/"),
    ("/raporlar", "/reports"),
    ("/analiz/", "/analysis/"),
    ("/analiz", "/analysis"),
    ("/projeler/", "/project/"),
    ("/v3/kurum-paneli/visual", "/kurum"),
    ("/v3/kurum-paneli", "/kurum"),
    ("/v3/skor-motoru", "/kurum"),
]

GONE_PREFIXES = ("/v2/", "/v2", "/v3/", "/v3", "/bsc/", "/bsc")

LEGACY_HGS_DISABLED_EXACT = frozenset({"/hgs", "/hizli-giris", "/Hgs_mfg", "/Hgs_mfg"})
