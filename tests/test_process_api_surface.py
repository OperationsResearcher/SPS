"""Dalga B4 — süreç API canonical yüzey (micro, legacy process_bp silindi).

2026-07-15: `app/routes/process.py` (1806 satır) silindi. Flag ile kapalı,
lazy import edilen ve testi "kapalı olmalı" diyen ölü koddu. Aşağıdaki test
dosyanın geri gelmemesini korur.
"""
import os


def test_legacy_process_module_stays_deleted():
  """app/routes/process.py silindi — micro/surec canonical, geri eklenmemeli."""
  assert not os.path.exists(os.path.join("app", "routes", "process.py")), (
      "Legacy app/routes/process.py geri gelmiş. Süreç işi micro/surec'e yazılır."
  )


def test_micro_process_kpi_list_route_exists(app):
  rules = {r.rule: r.endpoint for r in app.url_map.iter_rules()}
  assert "/k-plan/process/api/kpi/list/<int:process_id>" in rules
  assert rules["/k-plan/process/api/kpi/list/<int:process_id>"].startswith("app_bp.")


def test_micro_favorite_kpi_toggle_route_exists(app):
  rules = {r.rule: r.endpoint for r in app.url_map.iter_rules()}
  assert "/k-plan/process/api/favorite-kpi/toggle" in rules
  assert rules["/k-plan/process/api/favorite-kpi/toggle"] == "app_bp.surec_api_favorite_kpi_toggle"


def test_micro_process_page_exists(app):
  rules = {r.rule for r in app.url_map.iter_rules()}
  assert "/k-plan/process" in rules
  assert "/surec" in rules or any("/surec" in r for r in rules)
