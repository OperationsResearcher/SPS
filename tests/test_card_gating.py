# -*- coding: utf-8 -*-
"""Kart-düzeyi paket zorlaması (app/utils/package_gating.py) testleri.

Karar: KART-KATMANI-TASARIM.md revizyonu (2026-07-08) — paket dışı kart komple gizlenir.
"""
import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.models import db
from app.models.core import User, Tenant, Role
from app.models.saas import (
    SystemCard,
    SystemComponent,
    SystemModule,
    ModuleComponentSlug,
    SubscriptionPackage,
)
from app.utils.package_gating import allowed_component_slugs, hidden_card_codes
from config import TestingConfig


@pytest.fixture
def app():
    app = create_app(TestingConfig)
    ctx = app.app_context()
    ctx.push()
    db.create_all()
    yield app
    db.session.remove()
    db.drop_all()
    ctx.pop()


def _seed(app):
    """İki modül/bileşen/kart; paket yalnız birini içerir."""
    role_user = Role(name="kurum_kullanici")
    role_admin = Role(name="Admin")
    comp_a = SystemComponent(code="comp_a", name="A")
    comp_b = SystemComponent(code="comp_b", name="B")
    mod_a = SystemModule(code="mod_a", name="Mod A")
    mod_b = SystemModule(code="mod_b", name="Mod B")
    db.session.add_all([role_user, role_admin, comp_a, comp_b, mod_a, mod_b])
    db.session.flush()
    db.session.add_all([
        ModuleComponentSlug(module_id=mod_a.id, component_slug="comp_a"),
        ModuleComponentSlug(module_id=mod_b.id, component_slug="comp_b"),
    ])
    pkg = SubscriptionPackage(name="Başlangıç", code="baslangic")
    pkg.modules.append(mod_a)  # paket yalnız mod_a'yı içerir
    tenant = Tenant(name="T", short_name="t", is_active=True)
    db.session.add_all([pkg, tenant])
    db.session.flush()
    tenant.package_id = pkg.id
    user = User(email="u@t.test", password_hash=generate_password_hash("x"),
                tenant_id=tenant.id, role_id=role_user.id, is_active=True)
    admin = User(email="a@t.test", password_hash=generate_password_hash("x"),
                 role_id=role_admin.id, is_active=True)
    cards = [
        SystemCard(code="sayfa.kart_a", name="Kart A", component_id=comp_a.id, is_active=True),
        SystemCard(code="sayfa.kart_b", name="Kart B", component_id=comp_b.id, is_active=True),
        SystemCard(code="sayfa.kart_bagsiz", name="Bağsız", component_id=None, is_active=True),
    ]
    db.session.add_all([user, admin] + cards)
    db.session.commit()
    return user, admin


def test_paket_disi_kart_gizlenir(app):
    user, _ = _seed(app)
    slugs = allowed_component_slugs(user)
    assert slugs == {"comp_a"}
    hidden = hidden_card_codes(["sayfa.kart_a", "sayfa.kart_b", "sayfa.kart_bagsiz"], slugs)
    assert hidden == ["sayfa.kart_b"]  # yalnız paket dışı; bağsız kart fail-open


def test_admin_hicbir_kart_gizlenmez(app):
    _, admin = _seed(app)
    assert allowed_component_slugs(admin) is None
    assert hidden_card_codes(["sayfa.kart_b"], None) == []


def test_paketsiz_tenant_fail_open(app):
    user, _ = _seed(app)
    user.tenant.package_id = None
    db.session.commit()
    assert allowed_component_slugs(user) is None


def test_atanmamis_component_fail_open(app):
    """Component hiçbir modüle atanmamışsa kart görünür kalır (sabit alanlar)."""
    user, _ = _seed(app)
    comp_c = SystemComponent(code="comp_c", name="C")
    db.session.add(comp_c)
    db.session.flush()
    db.session.add(SystemCard(code="sayfa.kart_c", name="C", component_id=comp_c.id, is_active=True))
    db.session.commit()
    hidden = hidden_card_codes(["sayfa.kart_c"], allowed_component_slugs(user))
    assert hidden == []
