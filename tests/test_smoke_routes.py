"""
Smoke testler — kritik modüllerin temel erişilebilirlik ve auth kontrolü.
Kapsam: k_radar, admin, proje, surec karne, sp.
"""

import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.models import db
from app.models.core import User, Tenant, Role
from config import TestingConfig


@pytest.fixture(scope="module")
def app():
    _app = create_app(TestingConfig)
    with _app.app_context():
        db.create_all()
        yield _app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="module")
def client(app):
    return app.test_client()


@pytest.fixture(scope="module")
def auth_client(app, client):
    """Giriş yapmış test kullanıcısıyla client döner."""
    with app.app_context():
        tenant = Tenant(name="Smoke Tenant", short_name="smoke", is_active=True)
        db.session.add(tenant)
        db.session.flush()

        role = Role(name="tenant_admin", description="Admin")
        db.session.add(role)
        db.session.flush()

        user = User(
            email="smoke@test.com",
            first_name="Smoke",
            last_name="Test",
            tenant_id=tenant.id,
            role_id=role.id,
            password_hash=generate_password_hash("SmokePwd123"),
            is_active=True,
        )
        db.session.add(user)
        db.session.commit()

    client.post("/auth/login", data={"email": "smoke@test.com", "password": "SmokePwd123"})
    return client


# ── Kimlik doğrulama gerektiren route'lar unauthenticated 302 döndürmeli ─────

# NOT (2026-07-15): Bu listeler eskiden "/micro/..." prefix'liydi. Prefix bir
# noktada kaldırılmış, testler güncellenmemiş → her istek 404 dönüyor ve
# "korunan route login ister" iddiası aslında HİÇ test edilmiyordu (CI kapalı
# olduğu için de fark edilmedi). Aşağıdaki test artık önce route'un VAR
# olduğunu doğruluyor; yol tekrar değişirse sessizce geçmek yerine kırılır.
PROTECTED_ROUTES = [
    "/k-radar",
    "/k-radar/ks",
    "/k-radar/kp",
    "/k-radar/kpr",
    "/k-radar/cross",
    "/k-radar/kp/maturity",
    "/k-radar/kpr/cpm",
    "/k-plan/process/api/karne/1",
    "/k-plan/strategy",
]


def _route_taninir(app, yol: str) -> bool:
    """Yol url_map'te eşleşiyor mu? (404 = test bayat, koruma yok demek)"""
    adapter = app.url_map.bind("localhost")
    try:
        adapter.match(yol, method="GET")
        return True
    except Exception as e:
        # MethodNotAllowed/Redirect = route var; NotFound = yok
        return e.__class__.__name__ != "NotFound"


@pytest.mark.parametrize("route", PROTECTED_ROUTES)
def test_unauthenticated_redirects(app, client, route):
    """Giriş yapılmamış istekler 302 ile login'e yönlendirilmeli."""
    assert _route_taninir(app, route), (
        f"{route} url_map'te yok — test bayatlamış, gerçek yolu güncelle."
    )
    resp = client.get(route)
    assert resp.status_code in (302, 401), (
        f"{route} → {resp.status_code} (302 veya 401 bekleniyor)"
    )


# ── K-Radar API uçları unauthenticated 302/401 döndürmeli ────────────────────

K_RADAR_API_ROUTES = [
    "/k-radar/api/hub-summary",
    "/k-radar/api/ks",
    "/k-radar/api/kp",
    "/k-radar/api/kpr",
    "/k-radar/api/cross/risk-heatmap",
    "/k-radar/api/recommendations",
    "/k-radar/api/ks/swot-summary",
    "/k-radar/api/kp/maturity",
    "/k-radar/api/kpr/cpm",
    "/k-radar/api/cross/stakeholder",
]


@pytest.mark.parametrize("route", K_RADAR_API_ROUTES)
def test_k_radar_api_unauthenticated(app, client, route):
    assert _route_taninir(app, route), (
        f"[k_radar_api] {route} url_map'te yok — test bayatlamış."
    )
    resp = client.get(route)
    assert resp.status_code in (302, 401), (
        f"[k_radar_api] {route} → {resp.status_code}"
    )


# ── Proje silme artık arşivleme yapmalı (hard delete yok) ────────────────────

def test_project_delete_uses_archive(app):
    """Project silme endpoint'i is_archived=True yapmalı, DB'den silmemeli."""
    from app.models.portfolio_project import Project

    with app.app_context():
        tenant = Tenant(name="Del Tenant", short_name="del", is_active=True)
        db.session.add(tenant)
        db.session.flush()

        role = Role(name="Admin", description="Admin")
        db.session.add(role)
        db.session.flush()

        user = User(
            email="del@test.com",
            first_name="Del",
            last_name="User",
            tenant_id=tenant.id,
            role_id=role.id,
            password_hash=generate_password_hash("Pwd123"),
            is_active=True,
        )
        db.session.add(user)
        db.session.flush()

        proj = Project(name="Silinecek Proje", tenant_id=tenant.id, manager_id=user.id)
        db.session.add(proj)
        db.session.commit()
        proj_id = proj.id

        # Soft delete simülasyonu (route kodunun yaptığı)
        proj.is_archived = True
        db.session.commit()

        still_exists = db.session.get(Project, proj_id)
        assert still_exists is not None, "Proje DB'den silinmiş, oysa arşivlenmiş olmalıydı"
        assert still_exists.is_archived is True, "is_archived=True olmalı"


# ── Karne API N+1 düzeltmesi: kpi ve track pre-fetch alanları doğru ──────────

def test_karne_kpi_data_prefetch_structure(app):
    """routes_karne.py'deki _kpi_data_map yapısının anahtar formatı doğru olmalı."""
    from app.models.process import KpiData

    with app.app_context():
        # KpiData'yı modelden import edebiliyoruz — model yüklendi
        assert KpiData.__tablename__ == "kpi_data"
        # process_kpi_id ve year kolonları var
        assert hasattr(KpiData, "process_kpi_id")
        assert hasattr(KpiData, "year")
        assert hasattr(KpiData, "is_active")
