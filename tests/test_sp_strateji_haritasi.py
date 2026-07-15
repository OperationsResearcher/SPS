"""SP strateji haritası — şablon endpoint ve API."""
import pytest
from werkzeug.security import generate_password_hash

from app.models import db
from app.models.core import Role, Tenant, User, Strategy


def _login(client, user_id: int):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


def _sp_kullanici(rol_adi: str, email: str):
    """Verilen rolde, bir stratejisi olan kullanıcı üretir; id döner."""
    t = Tenant(name=f"SP {rol_adi}", short_name=f"sp{rol_adi[:4]}", is_active=True)
    db.session.add(t)
    db.session.flush()
    role = Role.query.filter_by(name=rol_adi).first()
    if not role:
        role = Role(name=rol_adi, description=rol_adi)
        db.session.add(role)
        db.session.flush()
    u = User(
        email=email,
        first_name="SP",
        last_name="User",
        tenant_id=t.id,
        role_id=role.id,
        password_hash=generate_password_hash("x"),
        is_active=True,
    )
    db.session.add(u)
    db.session.add(Strategy(tenant_id=t.id, title="S1", code="ST1", is_active=True))
    db.session.commit()
    return u.id


@pytest.fixture
def sp_user(app):
    """SP modülünü görebilen kullanıcı.

    2026-07-15: Eskiden rol "kurum_kullanici" idi — roles.py'de TANIMLI OLMAYAN
    uydurma bir rol. TASK-245 ile /sp rol kapısına alınınca (module_visibility:
    "sp" → PRIVILEGED_ROLES) bu testler 302/403 almaya başladı. Kod doğruydu,
    test bayattı. Artık gerçek rol kullanılıyor.
    """
    with app.app_context():
        yield _sp_kullanici("executive_manager", "sp.exec@local.test")


@pytest.fixture
def sp_yetkisiz_user(app):
    """SP modülünü GÖREMEMESİ gereken standart kullanıcı."""
    with app.app_context():
        yield _sp_kullanici("standard_user", "sp.std@local.test")


def test_strateji_haritasi_page_renders(client, sp_user):
    _login(client, sp_user)
    rv = client.get("/sp/strategy-map")
    assert rv.status_code == 200
    assert b"strateji-harita-container" in rv.data
    assert b"strateji-harita-data" in rv.data
    assert b"sp_index" not in rv.data


def test_strateji_haritasi_api(client, sp_user):
    _login(client, sp_user)
    rv = client.get("/sp/api/strategy-map")
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["success"] is True
    assert len(data["nodes"]) >= 1


def test_sp_rol_kapisi_standart_kullaniciyi_engeller(client, sp_yetkisiz_user):
    """TASK-245 rol kapısı: SP üst yönetime özel (module_visibility "sp").

    Sayfa → /desktop redirect (302), API → 403. Kapı kaldırılırsa bu test kırılır.
    """
    _login(client, sp_yetkisiz_user)
    assert client.get("/sp/strategy-map").status_code == 302
    assert client.get("/sp/api/strategy-map").status_code == 403
