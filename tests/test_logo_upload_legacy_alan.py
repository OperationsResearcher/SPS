# -*- coding: utf-8 -*-
"""Legacy `/api/kurum/upload-logo` ucu var olmayan `Tenant.logo_url` alanına yazıp her istekte 500 veriyordu.

Artık modern kurum ayarlarıyla aynı depolamayı kullanır (instance/uploads/tenant_logos + `Tenant.logo_path`).
Gerçek dosya yazımı tarayıcıda doğrulandı (TASK-327); burada kaynak düzeyinde regresyon koruması.
"""
import re
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
KAYNAK = (KOK / "api" / "routes_admin.py").read_text(encoding="utf-8")


def _rota_govdesi() -> str:
    a = KAYNAK.index("def api_kurum_upload_logo")
    b = KAYNAK.index("@api_bp.route", a)
    govde = KAYNAK[a:b]
    return govde.split('"""', 2)[2]  # docstring hariç yalnız kod


def test_tenant_modelinde_logo_url_yok_logo_path_var():
    from app.models.core import Tenant

    assert not hasattr(Tenant, "logo_url")
    assert hasattr(Tenant, "logo_path") and hasattr(Tenant, "logo_updated_at")


def test_legacy_logo_ucu_modern_alani_kullanir():
    g = _rota_govdesi()
    assert not re.search(r"\.logo_url\b", g), "var olmayan Tenant.logo_url kullanılıyor"
    assert "logo_path" in g and "tenant_logos" in g
    assert "validate_uploaded_image" in g, "magic-byte doğrulaması şart"
    assert "static/uploads/logos" not in g and "'static'" not in g, "herkese açık static klasörüne yazılmamalı"
