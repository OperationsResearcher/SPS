"""K-Radar endpoint response-time baseline (local).

Kullanim:
  python scripts/k_radar_perf_baseline.py
"""

from __future__ import annotations

import os
import sys
import time
from statistics import mean


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import create_app  # noqa: E402
from config import TestingConfig  # noqa: E402
from app.models import db  # noqa: E402
from app.models.core import Tenant, Role, User  # noqa: E402


def _seed_auth_user():
    tenant = Tenant(name="Perf Tenant", short_name="perf", is_active=True)
    role = Role(name="Admin", description="Admin")
    user = User(
        email="perf@local",
        first_name="Perf",
        last_name="User",
        tenant_id=1,
        role_id=1,
        password_hash="x",
        is_active=True,
    )
    db.session.add(tenant)
    db.session.flush()
    user.tenant_id = tenant.id
    db.session.add(role)
    db.session.flush()
    user.role_id = role.id
    db.session.add(user)
    db.session.commit()
    return user.id


def _timed_get(client, user_id: int, url: str, repeat: int = 3) -> tuple[int, float]:
    elapsed = []
    code = 0
    for _ in range(repeat):
        with client.session_transaction() as sess:
            sess["_user_id"] = str(user_id)
            sess["_fresh"] = True
        t0 = time.perf_counter()
        resp = client.get(url)
        t1 = time.perf_counter()
        code = resp.status_code
        elapsed.append((t1 - t0) * 1000.0)
    return code, mean(elapsed)


def main():
    app = create_app(TestingConfig)
    urls = [
        "/k-radar/api/hub-summary",
        "/k-radar/api/recommendations",
        "/k-radar/api/recommendations/history",
        "/k-radar/api/kp/darbogaz",
        "/k-radar/api/kpr/evm",
        "/k-radar/api/cross/risk-heatmap",
    ]
    with app.app_context():
        db.create_all()
        user_id = _seed_auth_user()
        client = app.test_client()
        print("K-Radar Perf Baseline (ms)")
        print("-" * 50)
        for url in urls:
            code, avg_ms = _timed_get(client, user_id, url, repeat=3)
            print(f"{url:<38} status={code:<3} avg={avg_ms:7.2f} ms")


if __name__ == "__main__":
    main()
