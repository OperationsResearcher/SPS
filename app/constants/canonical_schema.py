"""Canonical schema vocabulary for cross-domain naming consistency."""

# Domain metric -> canonical physical tables
CANONICAL_TABLES = {
    "tenants": ("tenants",),
    "users": ("users",),
    "roles": ("roles",),
    "process": ("processes",),
    "process_kpi": ("process_kpis",),
    "individual_performance_indicator": ("individual_performance_indicators",),
    "individual_activity": ("individual_activities",),
    "kpi_data": ("kpi_data",),
    "individual_kpi_data": ("individual_kpi_data",),
    "project": ("project",),
    "task": ("task",),
}

# Legacy -> canonical physical table names
LEGACY_TABLE_ALIASES = {
    "surec": "processes",
    "surec_performans_gostergesi": "process_kpis",
    "bireysel_performans_gostergesi": "individual_performance_indicators",
    "bireysel_faaliyet": "individual_activities",
    "performans_gosterge_veri": "kpi_data",  # split handled by migration rules
}

# Backup/preview summary keys shown in UI
SUMMARY_KEYS = (
    "tenants",
    "users",
    "roles",
    "process",
    "process_kpi",
    "individual_performance_indicator",
    "individual_activity",
    "kpi_data",
    "individual_kpi_data",
    "project",
    "task",
)
