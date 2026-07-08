# -*- coding: utf-8 -*-
"""API Routes — cekirdek giris noktasi.

4550 satirlik dosya alan bazli modullere bolundu (2026-07-08). Davranis/URL degismedi.
Blueprint `api.blueprint.api_bp`; asagidaki importlar route'lari yan-etkiyle kaydeder.
"""
from api.blueprint import api_bp  # noqa: F401
from api.helpers import (  # noqa: F401
    _invalidate_executive_dashboard_cache,
    _resolve_project_leader_ids_api,
    _sync_project_leaders_api,
    _notify_project_team_changes_api,
    _parse_date_safe,
)
from api import (  # noqa: E402,F401
    routes_admin,
    routes_ai,
    routes_files,
    routes_pm,
    routes_process,
    routes_projects,
)
