"""GUV-05/06 — giden istek (SSRF) koruması."""
import socket

import pytest
from werkzeug.security import generate_password_hash

from app.models import db
from app.models.core import Role, Tenant, User
from app.utils import outbound_guard as og


def _fake_dns(monkeypatch, mapping):
    real = socket.getaddrinfo

    def fake(host, port, *a, **k):
        if host not in mapping:  # IP literal'ler gerçek çözümleyiciyle (ağ gerektirmez)
            return real(host, port, *a, **k)
        ips = mapping[host]
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, port)) for ip in ips]
    monkeypatch.setattr(og.socket, "getaddrinfo", fake)


@pytest.mark.parametrize("url", [
    "http://hooks.slack.com/x",              # https değil
    "https://127.0.0.1/x",
    "https://[::1]/x",
    "https://169.254.169.254/latest/meta-data",
    "https://10.0.0.5/x",
    "https://user:pw@hooks.slack.com/x",
    "ftp://hooks.slack.com/x",
    "",
])
def test_validate_rejects(monkeypatch, url):
    _fake_dns(monkeypatch, {"hooks.slack.com": ["34.1.1.1"]})
    ok, err = og.validate_outbound_url(url)
    assert ok is False and err


def test_validate_rejects_hostname_resolving_private(monkeypatch):
    _fake_dns(monkeypatch, {"evil.example": ["127.0.0.1"]})
    assert og.validate_outbound_url("https://evil.example/x")[0] is False


def test_validate_rejects_mixed_resolution(monkeypatch):
    """Bir adres bile iç ağdaysa reddedilir (DNS rebinding karışımı)."""
    _fake_dns(monkeypatch, {"mix.example": ["8.8.8.8", "10.1.2.3"]})
    assert og.validate_outbound_url("https://mix.example/x")[0] is False


def test_validate_accepts_public(monkeypatch):
    _fake_dns(monkeypatch, {"hooks.slack.com": ["34.1.1.1"]})
    assert og.validate_outbound_url("https://hooks.slack.com/services/a") == (True, "")


def test_redirects_not_followed():
    assert og._NoRedirect().redirect_request(None, None, 302, "", {}, "http://127.0.0.1/") is None


@pytest.mark.parametrize("port", [5432, 6379, 22, "abc", None])
def test_smtp_port_allowlist(monkeypatch, port):
    _fake_dns(monkeypatch, {"smtp.example.com": ["34.1.1.1"]})
    assert og.validate_smtp_target("smtp.example.com", port)[0] is False


def test_smtp_private_host_rejected():
    assert og.validate_smtp_target("127.0.0.1", 587)[0] is False


def test_smtp_public_ok(monkeypatch):
    _fake_dns(monkeypatch, {"smtp.example.com": ["34.1.1.1"]})
    assert og.validate_smtp_target("smtp.example.com", 587) == (True, "")


def test_test_smtp_connection_blocks_before_connect(app, monkeypatch):
    import smtplib
    from micro.services.email_service import test_smtp_connection

    def boom(*a, **k):
        raise AssertionError("bağlantı denenmemeli")
    monkeypatch.setattr(smtplib, "SMTP", boom)
    monkeypatch.setattr(smtplib, "SMTP_SSL", boom)
    ok, msg = test_smtp_connection("127.0.0.1", 5432, True, False, "", "")
    assert ok is False and "127.0.0.1" not in msg


def test_slack_sender_blocks_internal(app):
    from app.services.slack_notification import send_slack_message
    r = send_slack_message("x", webhook_url="https://169.254.169.254/x")
    assert r["success"] is False


# ── /k-report/api/anomalies/notify-slack ─────────────────────────────────────
def _login(client, user_id):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


def _user(role_name):
    t = Tenant(name="T", short_name="t", is_active=True)
    r = Role(name=role_name, description=role_name)
    db.session.add_all([t, r])
    db.session.flush()
    u = User(email=f"{role_name}@t.local", first_name="a", last_name="b",
             tenant_id=t.id, role_id=r.id,
             password_hash=generate_password_hash("x"), is_active=True)
    db.session.add(u)
    db.session.commit()
    return u.id


def test_notify_slack_requires_privileged_role(client, app):
    _login(client, _user("standard_user"))
    rv = client.post("/k-report/api/anomalies/notify-slack",
                     json={"webhook_url": "https://hooks.slack.com/x"})
    assert rv.status_code == 403


def test_notify_slack_rejects_internal_url(client, app):
    _login(client, _user("tenant_admin"))
    rv = client.post("/k-report/api/anomalies/notify-slack",
                     json={"webhook_url": "https://127.0.0.1:5432/x"})
    assert rv.status_code == 400
