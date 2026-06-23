"""Modül-bazlı smoke test'ler.

Sprint 3.6 — audit'te kapsam %0 olarak tespit edilen modüller için:
- k_rapor, bireysel, admin, marketing, kurum, masaustu

Hedef: login sonrası ana sayfa render olabiliyor mu, kritik API'lar 401/302 dönüyor mu.
Detaylı flow testleri ayrı dosyalarda olabilir.
"""
import pytest


# Test edilen modüllerin ana sayfaları (login redirect bekleniyor)
PAGE_ROUTES = [
    "/k-rapor",
    "/individual/scorecard",
    "/admin/yonetim-paneli",
    "/admin/users",
    "/admin/tenants",
    "/organization",
    "/masaustu",
    "/sp",
    "/process",
    "/k-radar",
]

# JSON API endpoint'ler (login redirect bekleniyor)
API_ROUTES = [
    "/k-rapor/api/corporate",
    "/k-rapor/api/process-pg",
    "/k-rapor/api/alert",
    "/k-rapor/api/export-pdf",  # Sprint 11.3
    "/individual/api/scorecard",
    "/individual/api/scorecard/export-pdf",  # Sprint 11.3
    "/organization/api/overview",
    "/sp/api/plan-years",
    "/k-radar/api/hub-summary",
]


@pytest.mark.parametrize("route", PAGE_ROUTES)
def test_unauthenticated_page_redirects(client, route):
    """Login olmadan sayfaya erişim 302 (login redirect) veya 401 dönmeli."""
    resp = client.get(route, follow_redirects=False)
    assert resp.status_code in (302, 401), (
        f"{route} → {resp.status_code} (302 veya 401 bekleniyor)"
    )


@pytest.mark.parametrize("route", API_ROUTES)
def test_unauthenticated_api_returns_401_or_redirects(client, route):
    """Login olmadan API'ye erişim 302 veya 401 dönmeli."""
    resp = client.get(route, follow_redirects=False)
    assert resp.status_code in (302, 401), (
        f"{route} → {resp.status_code} (302 veya 401 bekleniyor)"
    )
