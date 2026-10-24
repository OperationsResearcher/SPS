# -*- coding: utf-8 -*-
"""UX-PLANI G / Faz 2.10: ağır sayfalarda inline `style=` sınıfa taşındı; toplam sayı yalnız azalır.

Taşınan sayfalar `scripts/port_araclari/g_arac.py` ile üretildi (dogrula.py: HEAD ile etiket-etiket aynı
efektif stil). Kalanlar bilinçli inline: gizli-başlangıç (display:none…), Jinja'lı, url(), !important,
ve #id kuralıyla özgüllük çakışması (ör. masaustu #masaustu-calendar).
"""
import re
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent / "ui"
SABLON = KOK / "templates" / "platform"
CSS = KOK / "static" / "platform" / "css"
SAYFALAR = {
    "k_rapor/index.html": "g_k_rapor_index.css",
    "masaustu/index.html": "g_masaustu_index.css",
    "sp/exec_dashboard.html": "g_sp_exec_dashboard.css",
    "surec/index.html": "g_surec_index.css",
    "admin/loglar.html": "g_admin_loglar.css",
    "admin/hata_kontrolu.html": "g_admin_hata_kontrolu.css",
    "admin/holding_drilldown.html": "g_admin_holding_drilldown.css",
    "admin/sub_tenants.html": "g_admin_sub_tenants.css",
    "raporlar/sektorel_detay.html": "g_raporlar_sektorel_detay.css",
    "sp/blue_ocean.html": "g_sp_blue_ocean.css",
    "raporlar/initiative_bubble.html": "g_raporlar_initiative_bubble.css",
    "admin/holding_dashboard.html": "g_admin_holding_dashboard.css",
    "bireysel/karne.html": "g_bireysel_karne.css",
    "admin/sub_tenants_usage.html": "g_admin_sub_tenants_usage.css",
    "k_radar/ks.html": "g_k_radar_ks.css",
    "sp/vrio.html": "g_sp_vrio.css",
    "sp/index.html": "g_sp_index.css",
    "auth/profil.html": "g_auth_profil.css",
    "ayarlar/zamanlanmis_raporlar.html": "g_ayarlar_zamanlanmis_raporlar.css",
    "raporlar/pg_proje_etki.html": "g_raporlar_pg_proje_etki.css",
    "project/list.html": "g_project_list.css",
    "masaustu/yonetim_ozeti.html": "g_masaustu_yonetim_ozeti.css",
    "admin/users.html": "g_admin_users.css",
    "ayarlar/index.html": "g_ayarlar_index.css",
    "sp/donemler.html": "g_sp_donemler.css",
    "admin/yedekleme.html": "g_admin_yedekleme.css",
    "admin/kilavuz_olusturucu.html": "g_admin_kilavuz_olusturucu.css",
    "sp/ceyreklik_review.html": "g_sp_ceyreklik_review.css",
    "admin/istatistikler.html": "g_admin_istatistikler.css",
    "raporlar/risk_heatmap.html": "g_raporlar_risk_heatmap.css",
    "k_radar/kp.html": "g_k_radar_kp.css",
}
STIL = re.compile(r'\sstyle="')

# Yalnız küçülür: yeni inline style eklemek bu testi kırar; sayfa temizledikçe düşür.
BASELINE = 2630


def test_toplam_inline_stil_artmadi():
    n = sum(len(STIL.findall(f.read_text(encoding="utf-8-sig"))) for f in SABLON.rglob("*.html"))
    assert n <= BASELINE, f"inline style= {n} > baseline {BASELINE}: sınıfa taşı (g_arac.py)"


def test_sayfalar_stil_dosyasina_baglanir():
    for rel, css in SAYFALAR.items():
        ham = (SABLON / rel).read_text(encoding="utf-8-sig")
        assert css in ham, f"{rel} → {css} bağlı değil"
        assert (CSS / css).exists(), css


def test_uretilen_css_dengeli():
    for css in SAYFALAR.values():
        t = (CSS / css).read_text(encoding="utf-8")
        assert t.count("{") == t.count("}"), css
        assert not re.search(r"\{\{|\{%", t), f"{css} içinde Jinja kalmış"
