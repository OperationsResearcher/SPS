"""k_rapor modülü smoke test'leri (Sprint 21)."""
import pytest


K_RAPOR_PAGES = [
    "/k-report",
    "/k-report/anomalies",  # Sprint 15
]

K_RAPOR_APIS = [
    "/k-report/api/corporate",
    "/k-report/api/process-pg",
    "/k-report/api/alert",
    "/k-report/api/compliance",
    "/k-report/api/risk",
    "/k-report/api/audit",
    "/k-report/api/k-vektor",
    "/k-report/api/strategic-analysis",
    "/k-report/api/stakeholder",
    "/k-report/api/competition",
    "/k-report/api/anomalies",        # Sprint 14
    "/k-report/api/digest/preview",   # Sprint 18
    "/k-report/api/export-pdf",       # Sprint 11
]

K_RAPOR_POST_APIS = [
    "/k-report/api/digest/send",
    "/k-report/api/anomalies/notify-slack",
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


# ── Katman mimarisi Faz 4 (2026-07-17) ────────────────────────────────────────


@pytest.mark.parametrize("eski,yeni", [
    ("/k-rapor", "/k-report"),
    ("/k-rapor/anomalies", "/k-report/anomalies"),
    ("/reports", "/k-report"),
    ("/reports/cfo-dashboard", "/k-report/cfo-dashboard"),
    ("/reports/esg-report", "/k-report/esg-report"),
])
def test_rapor_legacy_url_307_yonlendiriyor(client, eski, yeni):
    """Eski rapor adresleri kalıcı olarak yeni katmana gider.

    Yayın'da bookmark ve e-posta linkleri var; bu redirect'ler silinmez.
    307 (301 değil): POST gövdesi korunmalı — export/generate uçları POST.
    """
    resp = client.get(eski, follow_redirects=False)
    assert resp.status_code == 307, f"{eski} → {resp.status_code} (307 bekleniyor)"
    assert yeni in resp.headers.get("Location", ""), f"{eski} → {resp.headers.get('Location')}"


@pytest.mark.parametrize("route", ["/reports/daily", "/reports/dashboard"])
def test_dis_api_katman_tasimasindan_etkilenmedi(client, route):
    """ai_bp/api_bp REST uçları kapsam dışı — /k-report'a yönlenmemeli.

    Katman mimarisi UI katmanıdır; dış API sözleşmesi bozulmaz. Bu route'lar
    app_bp değil, kendi blueprint'lerinde. 307 dönerse taşıma onları da
    yutmuş demektir.
    """
    resp = client.get(route, follow_redirects=False)
    assert resp.status_code != 307, f"{route} legacy redirect'e yakalandı"
