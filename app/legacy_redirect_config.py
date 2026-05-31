# -*- coding: utf-8 -*-
"""Legacy HTML yönlendirme tablosu — middleware ve main deprecated decorator ortak."""
from __future__ import annotations

EXACT_ENDPOINT: dict[str, str] = {
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

PREFIX_REWRITE: list[tuple[str, str]] = [
    ("/projeler/", "/project/"),
    ("/v3/kurum-paneli/visual", "/kurum"),
    ("/v3/kurum-paneli", "/kurum"),
    ("/v3/skor-motoru", "/kurum"),
]

GONE_PREFIXES = ("/v2/", "/v2", "/v3/", "/v3", "/bsc/", "/bsc")

LEGACY_HGS_DISABLED_EXACT = frozenset({"/hgs", "/hizli-giris", "/Hgs_mfg", "/Hgs_mfg"})
