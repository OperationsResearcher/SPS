"""Bireysel modül smoke testleri (Sprint 21)."""
import pytest


PAGES = [
    "/k-plan/individual",
    "/k-plan/individual/scorecard",
]

APIS = [
    "/k-plan/individual/api/scorecard",
    "/k-plan/individual/api/scorecard/export-pdf",   # Sprint 11
    "/k-plan/individual/api/alignment-score",
    "/k-plan/individual/api/team-alignment",
]


@pytest.mark.parametrize("route", PAGES + APIS)
def test_bireysel_unauthenticated(client, route):
    resp = client.get(route, follow_redirects=False)
    assert resp.status_code in (302, 401), f"{route} → {resp.status_code}"
