# -*- coding: utf-8 -*-
"""
Dalga A — Legacy HTML yollarını platforma yönlendir veya 410 Gone döndür.

Yalnızca GET/HEAD; /api/, /process/api/, statik ve platform yollarına dokunmaz.
"""
from __future__ import annotations

import re

from flask import make_response, redirect, request, url_for

from app.legacy_redirect_config import (
    EXACT_ENDPOINT,
    GONE_PREFIXES,
    LEGACY_HGS_DISABLED_EXACT,
    PREFIX_REWRITE,
    REPORTS_SEGMENT_REWRITE,
)

_SKIP_PREFIXES = (
    "/m/",
    "/static/",
    "/api/",
    "/process/api/",
    "/micro/api/",
    "/auth/",
    "/socket.io",
    "/swagger",
    "/docs",
    "/health",
    "/login",
    "/logout",
    "/marketing",
    "/ozellikler",
    "/blog",
    "/demo",
    "/iletisim",
)

_PROJELER_VIEW_MAP = {
    "kanban": "views/kanban",
    "takvim": "views/calendar",
    "gantt": "views/gantt",
    "raid": "views/raid",
}


def _should_skip(path: str) -> bool:
    if path in ("/process", "/process/") or path.startswith("/process/"):
        return True
    if path.startswith("/surec/"):
        return True
    if path.startswith(_SKIP_PREFIXES):
        return True
    if _is_platform_canonical(path):
        return True
    return False


def _is_platform_canonical(path: str) -> bool:
    """Platform kök yolları — legacy yönlendirme uygulanmaz (/kurum-paneli vb. hariç)."""
    if path in ("/organization", "/individual", "/sp", "/launcher", "/desktop",
                "/surec", "/k-plan", "/k-report"):
        return True
    platform_prefixes = (
        # Katman mimarisi (2026-07-17): girdi + rapor katmanları. Bu önekler
        # platform kanoniktir — legacy dönüşüm ASLA uygulanmaz.
        "/k-plan/",
        "/k-report/",
        "/organization/",
        "/individual/",
        "/sp/",
        "/project/",
        "/desktop/",
        "/surec/",
        "/admin/",
        "/k-radar/",
        "/k_rapor/",
        "/reports/",
        "/analysis/",
        "/launcher/",
        "/settings/",
        "/profile/",
        "/notification/",
    )
    return any(path.startswith(p) for p in platform_prefixes)


def _redirect_endpoint(endpoint: str, code: int = 301):
    return redirect(url_for(endpoint, **request.args), code=code)


def _rewrite_projeler(path: str) -> str | None:
    m = re.match(r"^/projeler/(\d+)(?:/(.*))?$", path)
    if not m:
        return None
    pid, sub = m.group(1), (m.group(2) or "").strip("/")
    if not sub:
        return f"/project/{pid}"
    if sub == "duzenle":
        return f"/project/{pid}/edit"
    if sub.startswith("gorevler/"):
        rest = sub.split("/", 1)[1]
        parts = rest.split("/", 1)
        tid = parts[0]
        if len(parts) > 1 and parts[1] == "duzenle":
            return f"/project/{pid}/task/{tid}/edit"
        if rest == "yeni":
            return f"/project/{pid}/task/new"
        return f"/project/{pid}/task/{tid}"
    view = _PROJELER_VIEW_MAP.get(sub.split("/")[0])
    if view:
        return f"/project/{pid}/{view}"
    return f"/project/{pid}"


def init_legacy_sunset(app) -> None:
    if not app.config.get("LEGACY_SUNSET_ENABLED", True):
        return

    @app.before_request
    def _legacy_sunset_redirect():
        if request.method not in ("GET", "HEAD"):
            return None
        path = request.path or "/"

        # İç Türkçe segment köprüleri: canonical (/reports/, /k-rapor/) muafiyetinden ÖNCE (TASK-204/205).
        # old_seg/new_seg tam yoldur (ör. /k-rapor/api/kurumsal → /k-rapor/api/corporate). Alt yollar da kapsanır.
        for old_seg, new_seg in REPORTS_SEGMENT_REWRITE:
            if path == old_seg or path.startswith(old_seg + "/"):
                target = new_seg + path[len(old_seg):]
                qs = request.query_string.decode()
                if qs:
                    target = f"{target}?{qs}"
                return redirect(target, code=301)

        if _should_skip(path):
            return None

        if path in LEGACY_HGS_DISABLED_EXACT or path.startswith(("/hgs/login/", "/Hgs_mfg/login/")):
            return make_response("Hızlı giriş bu URL'de kullanılmıyor.", 404)

        for prefix in GONE_PREFIXES:
            if path == prefix.rstrip("/") or path.startswith(prefix):
                return make_response(
                    "Legacy sürüm kaldırıldı. Lütfen launcher üzerinden devam edin.",
                    410,
                )

        endpoint = EXACT_ENDPOINT.get(path)
        if endpoint:
            return _redirect_endpoint(endpoint)

        for old_prefix, new_prefix in PREFIX_REWRITE:
            if path.startswith(old_prefix) or path == old_prefix.rstrip("/"):
                target = path.replace(old_prefix, new_prefix, 1) if path.startswith(old_prefix) else new_prefix
                qs = request.query_string.decode()
                if qs:
                    target = f"{target}?{qs}"
                return redirect(target, code=301)

        rewritten = _rewrite_projeler(path)
        if rewritten:
            qs = request.query_string.decode()
            if qs:
                rewritten = f"{rewritten}?{qs}"
            return redirect(rewritten, code=301)

        return None
