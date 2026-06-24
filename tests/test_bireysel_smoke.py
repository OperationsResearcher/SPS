"""Bireysel modül smoke testleri (Sprint 21)."""
import pytest


PAGES = [
    "/individual",
    "/individual/scorecard",
]

APIS = [
    "/individual/api/scorecard",
    "/individual/api/scorecard/export-pdf",   # Sprint 11
    "/individual/api/alignment-score",
    "/individual/api/team-alignment",
]


@pytest.mark.parametrize("route", PAGES + APIS)
def test_bireysel_unauthenticated(client, route):
    resp = client.get(route, follow_redirects=False)
    assert resp.status_code in (302, 401), f"{route} → {resp.status_code}"
