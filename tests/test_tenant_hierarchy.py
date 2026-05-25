"""Bayi/Holding hiyerarşisi — güvenlik testleri (Sprint A).

KRİTİK: Bu testler veri sızıntısının ÖNLENDİĞİNİ doğrular.
Her test bir saldırı senaryosunu simüle eder.
"""
from __future__ import annotations

import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.models import db
from app.models.core import User, Tenant, Role
from app.utils.tenant_scope import (
    accessible_tenant_ids,
    is_platform_admin,
    is_dealer_admin,
    is_holding_admin,
    is_holding_user,
    can_manage_sub_tenants,
    is_readonly_for_tenant,
    child_tenant_ids,
    validate_tenant_type,
    can_be_parent,
    check_sub_tenant_limit,
    TENANT_TYPE_NORMAL, TENANT_TYPE_DEALER, TENANT_TYPE_HOLDING,
)
from config import TestingConfig


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def roles(app):
    """Standart rolleri oluştur."""
    admin_role = Role(name="Admin", description="Platform Admin")
    tadmin_role = Role(name="tenant_admin", description="Tenant Admin")
    user_role = Role(name="kurum_kullanici", description="Standart")
    db.session.add_all([admin_role, tadmin_role, user_role])
    db.session.commit()
    return {"admin": admin_role, "tenant_admin": tadmin_role, "user": user_role}


@pytest.fixture
def tenants(app):
    """3 tenant: 1 holding + 2 alt + 1 bayi + 2 alt + 1 normal."""
    holding = Tenant(name="ABC Holding", tenant_type=TENANT_TYPE_HOLDING)
    db.session.add(holding)
    db.session.flush()

    holding_child1 = Tenant(name="ABC Cam", parent_tenant_id=holding.id)
    holding_child2 = Tenant(name="ABC Çelik", parent_tenant_id=holding.id)
    db.session.add_all([holding_child1, holding_child2])
    db.session.flush()

    dealer = Tenant(name="XYZ Bayi", tenant_type=TENANT_TYPE_DEALER)
    db.session.add(dealer)
    db.session.flush()

    dealer_child1 = Tenant(name="Müşteri A", parent_tenant_id=dealer.id)
    dealer_child2 = Tenant(name="Müşteri B", parent_tenant_id=dealer.id)
    db.session.add_all([dealer_child1, dealer_child2])

    standalone = Tenant(name="Bağımsız Şirket")
    db.session.add(standalone)
    db.session.commit()

    return {
        "holding": holding, "holding_child1": holding_child1, "holding_child2": holding_child2,
        "dealer": dealer, "dealer_child1": dealer_child1, "dealer_child2": dealer_child2,
        "standalone": standalone,
    }


def make_user(email, tenant, role):
    """Yardımcı: kullanıcı oluştur."""
    u = User(
        email=email,
        password_hash=generate_password_hash("test123"),
        tenant_id=tenant.id,
        role_id=role.id,
        is_active=True,
    )
    db.session.add(u)
    db.session.commit()
    # tenant + role lazy yüklensin
    u.tenant = tenant
    u.role = role
    return u


# ─── Test 1: Tenant tipi tanıma ──────────────────────────────────────────────

def test_tenant_type_defaults_to_normal(app):
    t = Tenant(name="Test")
    db.session.add(t)
    db.session.commit()
    assert t.tenant_type == TENANT_TYPE_NORMAL
    assert t.parent_tenant_id is None
    assert not t.is_dealer
    assert not t.is_holding
    assert not t.is_parent_capable


def test_tenant_properties(app, tenants):
    assert tenants["holding"].is_holding
    assert tenants["holding"].is_parent_capable
    assert not tenants["holding"].is_sub_tenant

    assert tenants["dealer"].is_dealer
    assert tenants["dealer"].is_parent_capable

    assert tenants["holding_child1"].is_sub_tenant
    assert tenants["holding_child1"].parent_tenant_id == tenants["holding"].id

    assert not tenants["standalone"].is_parent_capable
    assert not tenants["standalone"].is_sub_tenant


# ─── Test 2: accessible_tenant_ids ───────────────────────────────────────────

def test_platform_admin_sees_all(app, roles, tenants):
    admin = make_user("admin@kokpitim.com", tenants["standalone"], roles["admin"])
    # Platform admin → None döner (yani tümüne erişim)
    assert accessible_tenant_ids(admin) is None
    assert is_platform_admin(admin)


def test_normal_user_sees_only_own_tenant(app, roles, tenants):
    user = make_user("u@test.com", tenants["standalone"], roles["user"])
    ids = accessible_tenant_ids(user)
    assert ids == [tenants["standalone"].id]


def test_holding_admin_sees_self_and_children(app, roles, tenants):
    h_admin = make_user("ceo@abc.com", tenants["holding"], roles["tenant_admin"])
    ids = accessible_tenant_ids(h_admin)
    expected = {tenants["holding"].id, tenants["holding_child1"].id, tenants["holding_child2"].id}
    assert set(ids) == expected


def test_dealer_admin_sees_only_own_tenant_NOT_subs(app, roles, tenants):
    """KRİTİK: Bayi alt-tenant verisini GÖREMEMELI."""
    d_admin = make_user("bayi@xyz.com", tenants["dealer"], roles["tenant_admin"])
    ids = accessible_tenant_ids(d_admin)
    # Bayi sadece kendi tenant'ını görür
    assert ids == [tenants["dealer"].id]
    # Alt-tenantlar erişilebilir id listesinde OLMAMALI
    assert tenants["dealer_child1"].id not in ids
    assert tenants["dealer_child2"].id not in ids


def test_sub_tenant_user_does_not_see_parent(app, roles, tenants):
    """KRİTİK: Alt-tenant kullanıcısı parent'ı veya kardeşlerini göremez."""
    user = make_user("u@cam.com", tenants["holding_child1"], roles["user"])
    ids = accessible_tenant_ids(user)
    assert ids == [tenants["holding_child1"].id]
    assert tenants["holding"].id not in ids
    assert tenants["holding_child2"].id not in ids


def test_unauthenticated_returns_empty(app, roles, tenants):
    """Kimlik doğrulanmamış → hiçbir tenant'a erişim yok."""
    # Mock unauthenticated user
    class FakeUser:
        is_authenticated = False
    assert accessible_tenant_ids(FakeUser()) == []


# ─── Test 3: child_tenant_ids ────────────────────────────────────────────────

def test_child_tenant_ids(app, tenants):
    children = child_tenant_ids(tenants["holding"].id)
    assert set(children) == {tenants["holding_child1"].id, tenants["holding_child2"].id}


def test_child_tenant_ids_excludes_inactive(app, tenants):
    tenants["holding_child1"].is_active = False
    db.session.commit()
    children = child_tenant_ids(tenants["holding"].id)
    assert tenants["holding_child1"].id not in children
    assert tenants["holding_child2"].id in children


# ─── Test 4: Read-only kontrol ───────────────────────────────────────────────

def test_holding_admin_readonly_on_subtenant(app, roles, tenants):
    """Holding admin alt-tenant'a baktığında readonly."""
    h_admin = make_user("ceo@abc.com", tenants["holding"], roles["tenant_admin"])
    # Kendi tenant → readonly DEĞİL
    assert not is_readonly_for_tenant(tenants["holding"].id, h_admin)
    # Alt-tenant → readonly EVET
    assert is_readonly_for_tenant(tenants["holding_child1"].id, h_admin)


def test_normal_user_not_readonly_on_own_tenant(app, roles, tenants):
    user = make_user("u@test.com", tenants["standalone"], roles["tenant_admin"])
    assert not is_readonly_for_tenant(tenants["standalone"].id, user)


def test_platform_admin_never_readonly(app, roles, tenants):
    admin = make_user("admin@kokpitim.com", tenants["standalone"], roles["admin"])
    assert not is_readonly_for_tenant(tenants["holding"].id, admin)
    assert not is_readonly_for_tenant(tenants["dealer"].id, admin)


# ─── Test 5: can_manage_sub_tenants ──────────────────────────────────────────

def test_dealer_admin_can_manage_subs(app, roles, tenants):
    d_admin = make_user("d@xyz.com", tenants["dealer"], roles["tenant_admin"])
    assert can_manage_sub_tenants(d_admin)


def test_holding_admin_can_manage_subs(app, roles, tenants):
    h_admin = make_user("h@abc.com", tenants["holding"], roles["tenant_admin"])
    assert can_manage_sub_tenants(h_admin)


def test_normal_admin_cannot_manage_subs(app, roles, tenants):
    """Normal tenant'ın admin'i alt-tenant açamaz."""
    n_admin = make_user("a@std.com", tenants["standalone"], roles["tenant_admin"])
    assert not can_manage_sub_tenants(n_admin)


def test_normal_user_cannot_manage_subs(app, roles, tenants):
    user = make_user("u@dealer.com", tenants["dealer"], roles["user"])
    assert not can_manage_sub_tenants(user)


# ─── Test 6: Validasyon ──────────────────────────────────────────────────────

def test_validate_tenant_type_accepts_valid(app):
    assert validate_tenant_type("normal") == "normal"
    assert validate_tenant_type("dealer") == "dealer"
    assert validate_tenant_type("holding") == "holding"
    assert validate_tenant_type("NORMAL") == "normal"  # case-insensitive
    assert validate_tenant_type("") == "normal"  # boş → default


def test_validate_tenant_type_rejects_invalid(app):
    with pytest.raises(ValueError):
        validate_tenant_type("admin")
    with pytest.raises(ValueError):
        validate_tenant_type("super_holding")


def test_can_be_parent(app, tenants):
    ok, err = can_be_parent(tenants["holding"])
    assert ok and err is None

    ok, err = can_be_parent(tenants["dealer"])
    assert ok and err is None

    # Normal tenant parent olamaz
    ok, err = can_be_parent(tenants["standalone"])
    assert not ok
    assert "dealer" in err.lower() or "holding" in err.lower()

    # Alt-tenant başka alt-tenant açamaz (önce tip kontrolüne takılır)
    # holding_child1.tenant_type='normal' olduğu için "yalnızca dealer/holding" hatası
    ok, err = can_be_parent(tenants["holding_child1"])
    assert not ok

    # Eğer alt-tenant'ın tipi dealer olsaydı bile iç içe kontrolüne takılırdı
    tenants["holding_child1"].tenant_type = "dealer"
    db.session.commit()
    ok, err = can_be_parent(tenants["holding_child1"])
    assert not ok
    assert "iç içe" in err.lower() or "hiyerarşi" in err.lower()

    # Pasif tenant parent olamaz
    tenants["dealer"].is_active = False
    db.session.commit()
    ok, err = can_be_parent(tenants["dealer"])
    assert not ok


def test_sub_tenant_limit(app, tenants):
    # Bayi default sınırsız
    ok, err = check_sub_tenant_limit(tenants["dealer"])
    assert ok and err is None

    # Limit koy: 2 mevcut, limit 2 → dolu
    tenants["dealer"].sub_tenant_limit = 2
    db.session.commit()
    ok, err = check_sub_tenant_limit(tenants["dealer"])
    assert not ok
    assert "dolu" in err.lower()

    # Limit 5 → boş yer var
    tenants["dealer"].sub_tenant_limit = 5
    db.session.commit()
    ok, err = check_sub_tenant_limit(tenants["dealer"])
    assert ok


# ─── Test 7: SALDIRI SENARYOLARI (en kritik) ─────────────────────────────────

def test_attack_dealer_admin_cannot_read_subtenant_data_via_helper(app, roles, tenants):
    """SALDIRI: Bayi admin alt-tenant id'sini bilse bile veri sorgusu ÇEKEMEZ.

    Senaryo: Bayi 'XYZ' admin'i, alt-tenant 'Müşteri A' id'sini biliyor.
    accessible_tenant_ids() ona o tenant'ı vermez.
    """
    d_admin = make_user("attacker@xyz.com", tenants["dealer"], roles["tenant_admin"])
    ids = accessible_tenant_ids(d_admin)
    # KRİTİK: alt tenant id'leri YOK
    assert tenants["dealer_child1"].id not in (ids or [])
    assert tenants["dealer_child2"].id not in (ids or [])


def test_attack_sub_tenant_user_cannot_escalate_to_parent(app, roles, tenants):
    """SALDIRI: Alt-tenant kullanıcısı parent'ın verisine erişmeye çalışır.

    Senaryo: 'Müşteri A' standart kullanıcısı, 'XYZ Bayi' verilerini görmek ister.
    """
    user = make_user("u@musteri-a.com", tenants["dealer_child1"], roles["user"])
    ids = accessible_tenant_ids(user)
    assert tenants["dealer"].id not in ids
    assert tenants["dealer_child2"].id not in ids
    assert ids == [tenants["dealer_child1"].id]


def test_attack_holding_admin_cannot_see_unrelated_tenants(app, roles, tenants):
    """SALDIRI: ABC Holding admin'i XYZ Bayi'nin alt-tenantlarını görmek ister."""
    h_admin = make_user("h@abc.com", tenants["holding"], roles["tenant_admin"])
    ids = accessible_tenant_ids(h_admin)
    # Sadece kendi children
    assert tenants["dealer"].id not in ids
    assert tenants["dealer_child1"].id not in ids
    assert tenants["standalone"].id not in ids


def test_attack_normal_admin_cannot_escalate_via_role(app, roles, tenants):
    """SALDIRI: Normal tenant_admin platform-wide erişim sağlamaya çalışır."""
    n_admin = make_user("n@std.com", tenants["standalone"], roles["tenant_admin"])
    ids = accessible_tenant_ids(n_admin)
    assert ids == [tenants["standalone"].id]
    assert not is_platform_admin(n_admin)
    assert not is_holding_user(n_admin)
    assert not is_dealer_admin(n_admin)
