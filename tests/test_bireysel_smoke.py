"""Bireysel modül smoke testleri (Sprint 21)."""
import pytest


PAGES = [
    "/bireysel",
    "/bireysel/karne",
]

APIS = [
    "/bireysel/api/karne",
    "/bireysel/api/karne/export-pdf",   # Sprint 11
    "/bireysel/api/hizalama-skoru",
    "/bireysel/api/ekip-hizalama",
]


@pytest.mark.parametrize("route", PAGES + APIS)
def test_bireysel_unauthenticated(client, route):
    resp = client.get(route, follow_redirects=False)
    assert resp.status_code in (302, 401), f"{route} → {resp.status_code}"
