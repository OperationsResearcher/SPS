# -*- coding: utf-8 -*-
"""Ekim 2026 denetimi P0 düzeltmeleri — GV-001, GV-002, GV-006 regresyon testleri."""
import pytest

from app.utils.outbound_guard import validate_llm_base_url


# ── GV-002: LLM base_url SSRF ────────────────────────────────────────────────

@pytest.mark.parametrize("url", [
    "http://169.254.169.254/latest/meta-data",   # bulut metadata
    "http://[fe80::1]/v1",                        # link-local
    "http://0.0.0.0/v1",
    "ftp://8.8.8.8/v1",                           # şema
    "https://user:pw@8.8.8.8/v1",                 # kullanıcı bilgisi
])
def test_base_url_her_zaman_reddedilir(url):
    assert validate_llm_base_url(url, allow_private=True)[0] is False
    assert validate_llm_base_url(url, allow_private=False)[0] is False


@pytest.mark.parametrize("url", ["http://10.0.0.5:11434/v1", "http://127.0.0.1:11434/v1",
                                 "http://192.168.1.10/v1"])
def test_ozel_ag_yalniz_izinle(url):
    assert validate_llm_base_url(url, allow_private=False)[0] is False
    assert validate_llm_base_url(url, allow_private=True)[0] is True


def test_genel_ip_kabul():
    assert validate_llm_base_url("https://8.8.8.8/v1")[0] is True
    assert validate_llm_base_url("")[0] is True


def test_provider_base_url_openai_yerel_llm_dusmez():
    """Önceden call_llm openai için base_url iletmiyordu → Yerel LLM verisi OpenAI'a gidiyordu."""
    from app.services.llm_gateway import _provider_base_url
    assert _provider_base_url("openai", "http://10.0.0.5:11434/v1") == "http://10.0.0.5:11434/v1"
    assert _provider_base_url("openai", None) is None
    assert _provider_base_url("openrouter", None) == "https://openrouter.ai/api/v1"
    assert _provider_base_url("gemini", "http://x") is None


def _resolved(base_url):
    return {"source": "tenant", "provider": "openai", "model": "m", "api_key": "k",
            "base_url": base_url, "count_against_system_quota": False}


def test_call_llm_base_url_iletir_ve_ozel_agi_engeller(app, monkeypatch):
    from app.services import llm_gateway as gw
    calls = []

    def fake_caller(**kw):
        calls.append(kw)
        return "OK", {}

    monkeypatch.setitem(gw.PROVIDERS["openai"], "caller", fake_caller)
    monkeypatch.setattr(gw, "log_usage", lambda *a, **k: None, raising=False)

    with app.app_context():
        # Bulut varsayılanı: özel ağ engelli → sağlayıcı hiç çağrılmaz
        app.config["LLM_ALLOW_PRIVATE_BASE_URL"] = False
        monkeypatch.setattr(gw, "_resolve_provider", lambda t: _resolved("http://10.0.0.5:11434/v1"))
        r = gw.call_llm(1, "test", "merhaba")
        assert calls == []
        assert r.get("source") == "blocked_base_url"

        # Kurum içi kurulum: izinli → base_url çağrıya iletilir
        app.config["LLM_ALLOW_PRIVATE_BASE_URL"] = True
        gw.call_llm(1, "test", "merhaba")
        assert calls and calls[-1]["base_url"] == "http://10.0.0.5:11434/v1"


# ── GV-001: doküman merkezi uçları kapalı ────────────────────────────────────

def _login(client, user):
    with client.session_transaction() as s:
        s["_user_id"] = str(user.id)
        s["_fresh"] = True


def test_dokuman_merkezi_indir_ve_sil_kapali(client, test_user):
    _login(client, test_user)
    for method, url in [("get", "/api/dokuman-merkezi/1/indir"), ("delete", "/api/dokuman-merkezi/1")]:
        rv = getattr(client, method)(url)
        assert rv.status_code in (501, 404), (url, rv.status_code)
        assert rv.status_code != 200


# ── GV-006: açık yönlendirme ─────────────────────────────────────────────────

@pytest.mark.parametrize("bad", ["//evil.com", "/\evil.com", "https://evil.com", "/\/evil.com"])
def test_login_next_harici_adrese_gitmez(client, test_user, bad):
    rv = client.post(f"/login?next={bad}",
                     data={"email": "test@example.com", "password": "TestPassword123"})
    loc = rv.headers.get("Location", "")
    assert "evil.com" not in loc


def test_login_next_gorece_adres_korunur(client, test_user):
    """Kontrol testi: giriş gerçekten başarılı ve güvenli göreli next korunuyor."""
    rv = client.post("/login?next=/k-plan", data={"email": "test@example.com",
                                                   "password": "TestPassword123"})
    assert rv.status_code == 302
    assert rv.headers["Location"].endswith("/k-plan")
