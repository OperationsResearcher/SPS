# -*- coding: utf-8 -*-
"""Admin araçları ortam kilidi + yedek uçlarında CSRF (Faz 0.4, G3)."""
import pytest

from micro.modules.admin import routes_admin_tools as rat


@pytest.mark.parametrize("env,beklenen", [(None, False), ("", False), ("production", False), ("local", True), ("LOCAL", True)])
def test_is_local_acik_bayrak_ister(monkeypatch, env, beklenen):
    monkeypatch.delenv("KOKPITIM_ENV", raising=False)
    monkeypatch.setenv("FLASK_ENV", "development")  # eski varsayılan artık yetmez
    if env is not None:
        monkeypatch.setenv("KOKPITIM_ENV", env)
    assert rat._is_local() is beklenen


def test_yedek_uclari_csrf_muaf_degil(app):
    from app.extensions import csrf

    muaf = set(getattr(csrf, "_exempt_views", set()))
    for ep in ("admin_tools_yedekleme_indir_db", "admin_tools_yedekleme_indir_kod",
               "admin_tools_yedekleme_otomatik_calistir", "admin_tools_yedekleme_geri_yukle_db"):
        view = app.view_functions.get("app_bp." + ep)
        assert view is not None, ep
        assert f"{view.__module__}.{view.__name__}" not in muaf, ep
