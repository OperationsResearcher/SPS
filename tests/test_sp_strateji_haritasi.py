"""SP strateji haritası — şablon endpoint ve API."""
import pytest
from werkzeug.security import generate_password_hash

from app.models import db
from app.models.core import Role, Tenant, User, Strategy


def _login(client, user_id: int):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


@pytest.fixture
def sp_user(app):
    with app.app_context():
        t = Tenant(name="SP T", short_name="sp", is_active=True)
        db.session.add(t)
        db.session.flush()
        role = Role(name="kurum_kullanici", description="u")
        db.session.add(role)
        db.session.flush()
        u = User(
            email="sp@local.test",
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
        yield u.id


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
