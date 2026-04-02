"""K-Radar smoke check: route + db table quick validation."""

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import create_app
from app.models import db


REQUIRED_ROUTES = [
    "/k-radar",
    "/k-radar/ks",
    "/k-radar/ks/swot",
    "/k-radar/kp",
    "/k-radar/kp/olgunluk",
    "/k-radar/kpr",
    "/k-radar/kpr/cpm",
    "/k-radar/cross",
    "/k-radar/cross/paydas",
    "/k-radar/api/hub-summary",
    "/k-radar/api/ks/swot-summary",
    "/k-radar/api/kp/olgunluk",
    "/k-radar/api/kpr/cpm",
    "/k-radar/api/cross/paydas",
]

REQUIRED_TABLES = [
    "k_radar_recommendation_actions",
    "process_maturity",
    "bottleneck_log",
    "value_chain_items",
    "evm_snapshots",
    "risk_heatmap_items",
    "stakeholder_maps",
    "stakeholder_surveys",
    "a3_reports",
    "competitor_analyses",
]


def main() -> int:
    app = create_app()
    with app.app_context():
        rules = {r.rule for r in app.url_map.iter_rules()}
        route_missing = [r for r in REQUIRED_ROUTES if r not in rules]

        insp = db.inspect(db.engine)
        tables = set(insp.get_table_names())
        table_missing = [t for t in REQUIRED_TABLES if t not in tables]

        print("K-Radar Smoke Check")
        print("- Route missing:", len(route_missing))
        for r in route_missing:
            print("  -", r)
        print("- Table missing:", len(table_missing))
        for t in table_missing:
            print("  -", t)
        if route_missing or table_missing:
            return 1
        print("OK: routes and tables are present.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
