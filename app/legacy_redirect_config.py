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
    "/kurum": "app_bp.kurum",
    "/masaustu": "app_bp.masaustu",
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

# İç Türkçe segment köprüleri (TASK-204/205). Canonical (/reports/, /k-rapor/) muafiyetinden
# ÖNCE uygulanır (legacy_sunset _legacy_sunset_redirect başında) — aksi halde canonical yollar
# redirect'ten muaf tutulur ve köprü çalışmaz. Eski TR segment → yeni İngilizce segment, 301.
REPORTS_SEGMENT_REWRITE: list[tuple[str, str]] = [
    # k-radar iç Türkçe segmentleri (TASK-208). Kök /k-radar ürün adı KALIR; kart-kodu/?tab DOKUNULMADI.
    ("/k-radar/cross/paydas", "/k-radar/cross/stakeholder"),
    ("/k-radar/api/cross/paydas", "/k-radar/api/cross/stakeholder"),
    ("/k-radar/kp/deger-zinciri", "/k-radar/kp/value-chain"),
    ("/k-radar/api/kp/deger-zinciri", "/k-radar/api/kp/value-chain"),
    ("/k-radar/kp/kapasite", "/k-radar/kp/capacity"),
    ("/k-radar/api/kp/kapasite", "/k-radar/api/kp/capacity"),
    ("/k-radar/kp/olgunluk", "/k-radar/kp/maturity"),
    ("/k-radar/api/kp/olgunluk", "/k-radar/api/kp/maturity"),
    ("/k-radar/kpr/kaynak-kapasite", "/k-radar/kpr/resource-capacity"),
    ("/k-radar/api/kpr/kaynak-kapasite", "/k-radar/api/kpr/resource-capacity"),
    ("/k-radar/api/ks/strateji-real", "/k-radar/api/ks/strategy-real"),
    # masaustu→desktop iç segment: danisman→advisor (TASK-212). /masaustu/ prefix kuralı kökü çevirir,
    # bu tam-yol köprü iç segmenti de düzeltir (canonical /desktop/ muafiyetinden önce).
    ("/masaustu/api/koe-danisman-ai", "/desktop/api/koe-advisor-ai"),
    # k-rapor kalan iç API segmentleri (TASK-210). Kök /k-rapor ürün adı KALIR.
    ("/k-rapor/api/faaliyet-matris", "/k-rapor/api/activity-matrix"),
    ("/k-rapor/api/faaliyet", "/k-rapor/api/activity"),
    ("/k-rapor/api/bireysel", "/k-rapor/api/individual"),
    ("/k-rapor/api/rekabet", "/k-rapor/api/competition"),
    ("/k-rapor/api/aktivite-takvim", "/k-rapor/api/activity-calendar"),
    ("/k-rapor/api/kurum-karsilastirma", "/k-rapor/api/org-comparison"),
    ("/k-rapor/api/sorumlu-analiz", "/k-rapor/api/responsible-analysis"),
    ("/k-rapor/api/bildirim-analiz", "/k-rapor/api/notification-analysis"),
    # PG→PI: Performans Göstergesi İngilizcesi PI (Performance Indicator) — URL segmenti (TASK-209).
    # Kod/DB (pg_id, ProcessKpi), data-* attribute ADLARI ve KART kodları DOKUNULMADI.
    ("/individual/api/pg/", "/individual/api/pi/"),
    ("/reports/pg-project-impact", "/reports/pi-project-impact"),
    ("/reports/api/pg-project-impact", "/reports/api/pi-project-impact"),
    ("/k-rapor/api/pg-dagilim", "/k-rapor/api/pi-dagilim"),
    # sp plan-yıl grubu (TASK-213). Sayfa GET'leri + api. gorev/proje iç segment tam-yol (uzun-önce).
    ("/sp/sihirbaz/yeni-yil", "/sp/wizard/new-year"),
    ("/sp/api/sihirbaz/yeni-yil/preview", "/sp/api/wizard/new-year/preview"),
    ("/sp/api/sihirbaz/yeni-yil/uygula", "/sp/api/wizard/new-year/apply"),
    ("/sp/donemler", "/sp/periods"),
    ("/sp/api/donem-karsilastir", "/sp/api/period-compare"),
    ("/sp/rapor/donemsel", "/sp/report/periodic"),
    ("/sp/api/proje/gorev/", "/sp/api/project/task/"),
    ("/sp/api/proje", "/sp/api/project"),
    # sp iç Türkçe segmentleri (TASK-207). Plan-yıl grubu TASK-213'te çevrildi.
    ("/sp/strateji-proje-matris", "/sp/strategy-project-matrix"),
    ("/sp/strateji-haritasi", "/sp/strategy-map"),
    ("/sp/api/strateji-haritasi", "/sp/api/strategy-map"),
    ("/sp/ayarlar/ai", "/sp/settings/ai"),
    ("/sp/scenarios/kiyas", "/sp/scenarios/compare"),
    ("/sp/api/exec-ai-ozet", "/sp/api/exec-ai-summary"),
    ("/sp/api/savas-odasi/fronts", "/sp/api/war-room/fronts"),
    ("/sp/misyon", "/sp/mission"),
    ("/sp/vizyon", "/sp/vision"),
    ("/sp/degerler", "/sp/values"),
    # kurum → organization (TASK-211): kök çevrildi. Eski TR iç segmentleri (TASK-206) doğrudan yeni köke.
    ("/kurum/ayarlar", "/organization/settings"),
    ("/kurum/api/kimlik", "/organization/api/identity"),
    ("/kurum/settings", "/organization/settings"),
    ("/kurum/api/identity", "/organization/api/identity"),
    ("/kurum/api/overview", "/organization/api/overview"),
    # k-rapor iç API segmentleri (TASK-205). Kök /k-rapor ürün adı olarak KALIR.
    ("/k-rapor/api/kurumsal", "/k-rapor/api/corporate"),
    ("/k-rapor/api/surec-pg", "/k-rapor/api/process-pg"),
    ("/k-rapor/api/uyum", "/k-rapor/api/compliance"),
    ("/k-rapor/api/veri-durumu", "/k-rapor/api/data-status"),
    ("/k-rapor/api/denetim", "/k-rapor/api/audit"),
    ("/k-rapor/api/uyari", "/k-rapor/api/alert"),
    ("/k-rapor/api/stratejik-analiz", "/k-rapor/api/strategic-analysis"),
    ("/k-rapor/api/strateji-kapsama", "/k-rapor/api/strategy-coverage"),
    ("/k-rapor/api/paydas", "/k-rapor/api/stakeholder"),
    # raporlar iç segmentleri (TASK-204):
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
    ("/reports/pg-proje-etki", "/reports/pi-project-impact"),
    ("/reports/sektorel", "/reports/sectoral"),
    ("/reports/iki-fa", "/reports/two-fa"),
]

PREFIX_REWRITE: list[tuple[str, str]] = [
    ("/kurum/", "/organization/"),  # kurum→organization alt yolları (TASK-211); /kurum exact EXACT_ENDPOINT'te
    ("/masaustu/", "/desktop/"),    # masaustu→desktop alt yolları (TASK-212); /masaustu exact EXACT_ENDPOINT'te
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
