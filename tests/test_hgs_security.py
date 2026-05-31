"""HGS bypass — production'da kapalı olmalı."""
import pytest

from config import ProductionConfig, TestingConfig


def test_production_config_disables_hgs_bypass():
    assert ProductionConfig.HGS_BYPASS_ENABLED is False


def test_hgs_login_blocked_when_flag_off(client, app, test_user, monkeypatch):
    monkeypatch.setitem(app.config, "HGS_BYPASS_ENABLED", False)
    monkeypatch.setitem(app.config, "DEBUG", False)
    client.get(f"/MfG_hgs/login/{test_user.id}", follow_redirects=True)
    with client.session_transaction() as sess:
        assert sess.get("_user_id") != str(test_user.id)


def test_hgs_public_paths_404(client):
    for path in ("/hgs", "/Hgs_mfg", "/hgs/login/1"):
        rv = client.get(path)
        assert rv.status_code == 404
