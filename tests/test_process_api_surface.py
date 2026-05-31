"""Dalga B4 — süreç API canonical yüzey (micro, legacy process_bp kapalı)."""


def test_process_bp_disabled_by_default(app):
  assert app.config.get("LEGACY_PROCESS_BP_ENABLED") is False


def test_micro_process_kpi_list_route_exists(app):
  rules = {r.rule: r.endpoint for r in app.url_map.iter_rules()}
  assert "/process/api/kpi/list/<int:process_id>" in rules
  assert rules["/process/api/kpi/list/<int:process_id>"].startswith("app_bp.")


def test_micro_favorite_kpi_toggle_route_exists(app):
  rules = {r.rule: r.endpoint for r in app.url_map.iter_rules()}
  assert "/process/api/favorite-kpi/toggle" in rules
  assert rules["/process/api/favorite-kpi/toggle"] == "app_bp.surec_api_favorite_kpi_toggle"


def test_micro_process_page_exists(app):
  rules = {r.rule for r in app.url_map.iter_rules()}
  assert "/process" in rules
  assert "/surec" in rules or any("/surec" in r for r in rules)
