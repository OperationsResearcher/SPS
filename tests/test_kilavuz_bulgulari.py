# -*- coding: utf-8 -*-
"""Kılavuz çalışmasında bulunan iki ürün hatasının regresyon testleri (TASK-335)."""
from werkzeug.security import generate_password_hash

from app.models import db
from app.models.core import User, Tenant, Role


def _giris(client, role_name, pkg=False):
    role = Role(name=role_name)
    t = Tenant(name="T", short_name="t", is_active=True)
    if pkg:
        from app.models.saas import SubscriptionPackage
        p = SubscriptionPackage(name="P", code="p")
        db.session.add(p)
        db.session.commit()
        t.package_id = p.id
    db.session.add_all([role, t])
    db.session.commit()
    u = User(email=f"{role_name}@x.com", first_name="a", last_name="b",
             tenant_id=t.id, role_id=role.id, is_active=True,
             password_hash=generate_password_hash("Abcd1234!"))
    db.session.add(u)
    db.session.commit()
    with client.session_transaction() as s:
        s["_user_id"] = str(u.id)
        s["_fresh"] = True


def test_admin_tum_kurumlar_kullanici_detay_200(client):
    """Admin 'Tüm Kurumlar' (tenant_id yok) seçiliyken 400 değil, liste döner."""
    _giris(client, "Admin")
    r = client.get("/admin/yonetim-paneli/kullanici-detay")
    assert r.status_code == 200
    body = r.get_json()
    assert body["success"] is True
    assert isinstance(body["data"], list)


def test_paket_kapisi_mesaji_nedeni_yanlis_soylemez(client, monkeypatch):
    """Paket+rol birlikte hesaplandığı için ret iletisi 'paketinizde yok' demez."""
    import app_platform.core.module_registry as mr
    monkeypatch.setattr(mr, "get_accessible_modules", lambda user: [])
    _giris(client, "kurum_kullanici", pkg=True)
    r = client.get("/k-plan/individual/scorecard")
    assert r.status_code == 302
    with client.session_transaction() as s:
        msgs = [m for _cat, m in s.get("_flashes", [])]
    assert msgs and all("paketinizde yok" not in m for m in msgs)
    assert "Bu sayfaya erişim yetkiniz yok." in msgs
