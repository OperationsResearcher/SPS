"""k_rapor modülü smoke test'leri (Sprint 21)."""
import pytest


K_RAPOR_PAGES = [
    "/k-rapor",
    "/k-rapor/anomalies",  # Sprint 15
]

K_RAPOR_APIS = [
    "/k-rapor/api/corporate",
    "/k-rapor/api/process-pg",
    "/k-rapor/api/alert",
    "/k-rapor/api/compliance",
    "/k-rapor/api/risk",
    "/k-rapor/api/audit",
    "/k-rapor/api/k-vektor",
    "/k-rapor/api/strategic-analysis",
    "/k-rapor/api/stakeholder",
    "/k-rapor/api/rekabet",
    "/k-rapor/api/anomalies",        # Sprint 14
    "/k-rapor/api/digest/preview",   # Sprint 18
    "/k-rapor/api/export-pdf",       # Sprint 11
]

K_RAPOR_POST_APIS = [
    "/k-rapor/api/digest/send",
    "/k-rapor/api/anomalies/notify-slack",
]


@pytest.mark.parametrize("route", K_RAPOR_PAGES + K_RAPOR_APIS)
def test_k_rapor_unauthenticated_get(client, route):
    """GET endpoint'ler login olmadan 302/401."""
    resp = client.get(route, follow_redirects=False)
    assert resp.status_code in (302, 401), f"{route} → {resp.status_code}"


@pytest.mark.parametrize("route", K_RAPOR_POST_APIS)
def test_k_rapor_unauthenticated_post(client, route):
    """POST endpoint'ler login olmadan 302/401/400."""
    resp = client.post(route, follow_redirects=False)
    # POST'lar 405 dönebilir (CSRF) — yine de güvenli
    assert resp.status_code in (302, 401, 405, 400), f"{route} → {resp.status_code}"
