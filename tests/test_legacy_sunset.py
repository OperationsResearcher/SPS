"""Legacy sunset middleware — yönlendirme ve 410."""
import pytest


def _login(client, email="test@example.com", password="TestPassword123"):
    return client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=True,
    )


@pytest.mark.parametrize(
    "path,expected_fragment",
    [
        ("/dashboard", "/desktop"),
        ("/projeler", "/project"),
        ("/kurum-paneli", "/organization"),
    ],
)
def test_legacy_sunset_redirects(client, test_user, path, expected_fragment):
    _login(client)
    rv = client.get(path, follow_redirects=False)
    assert rv.status_code in (301, 302, 303, 307, 308)
    assert expected_fragment in (rv.location or "")


@pytest.mark.parametrize("path", ["/v2/masam", "/v2", "/bsc"])
def test_legacy_sunset_gone(client, path):
    rv = client.get(path, follow_redirects=False)
    assert rv.status_code == 410


def test_legacy_sunset_skips_process_api(client, app, test_user):
    """Platform /process/api yolları middleware'den muaf."""
    with app.app_context():
        from app.middleware.legacy_sunset import _should_skip

        assert _should_skip("/process/api/kpi/list/1") is True
        assert _should_skip("/dashboard") is False
