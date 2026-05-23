# -*- coding: utf-8 -*-
"""Kayıtlı olmayan legacy endpoint'ler için platform URL fallback."""
from __future__ import annotations

from flask import url_for
from werkzeug.routing import BuildError

# Eski blueprint endpoint → platform endpoint
_LEGACY_ENDPOINT_FALLBACK: dict[str, str] = {
    "dashboard_bp.index": "app_bp.masaustu",
    "dashboard_bp.tenant_dashboard": "app_bp.kurum",
    "dashboard_bp.performans_kartim": "app_bp.bireysel_karne",
    "process_bp.index": "app_bp.surec",
    "main.dashboard": "app_bp.masaustu",
    # Sprint 36 — strategy_bp sunset
    "strategy_bp.strategic_planning_flow": "app_bp.sp_flow",
    "strategy_bp.strategic_planning_dynamic": "app_bp.sp_dynamic_flow",
    "strategy_bp.api_strategic_planning_graph": "app_bp.sp_api_graph",
}


def safe_url_for(endpoint: str, **values) -> str:
    try:
        return url_for(endpoint, **values)
    except BuildError:
        fallback = _LEGACY_ENDPOINT_FALLBACK.get(endpoint, "app_bp.launcher")
        return url_for(fallback, **values)
