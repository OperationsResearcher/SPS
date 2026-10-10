"""GUV-11 — pasif kullanıcı ve parola değişimi açık oturumları düşürmeli."""
from werkzeug.security import generate_password_hash

from app.models import db
from app.models.core import Role, Tenant, User


def _mk(email="u@t.local"):
    t = Tenant(name="T", short_name="t", is_active=True)
    r = Role(name="standard_user", description="s")
    db.session.add_all([t, r])
    db.session.flush()
    u = User(email=email, first_name="a", last_name="b", tenant_id=t.id, role_id=r.id,
             password_hash=generate_password_hash("Eski-Parola-1"), is_active=True)
    db.session.add(u)
    db.session.commit()
    return u.id


def _cookie_login(client, uid, sv=0):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(uid)
        sess["_fresh"] = True
        sess["sv"] = sv


def _authed(client):
    """Korumalı bir sayfa: girişliyse 200, değilse login'e 302.

    Test app context'i istekler arasında yaşadığı için Flask-Login'in `g` önbelleğini
    temizleriz; üretimde her istek zaten taze `g` alır."""
    from flask import g
    g.pop("_login_user", None)
    return client.get("/profile", follow_redirects=False).status_code


def test_aktif_kullanici_oturumu_gecerli(client, app):
    uid = _mk()
    _cookie_login(client, uid)
    assert _authed(client) == 200


def test_pasife_alinan_kullanici_oturumu_duser(client, app):
    uid = _mk()
    _cookie_login(client, uid)
    assert _authed(client) == 200
    u = db.session.get(User, uid)
    u.is_active = False
    db.session.commit()
    assert _authed(client) in (301, 302, 401)


def test_parola_degisince_eski_oturum_duser(client, app):
    uid = _mk()
    _cookie_login(client, uid, sv=0)
    assert _authed(client) == 200
    u = db.session.get(User, uid)
    u.password_hash = generate_password_hash("Yeni-Parola-2")
    db.session.commit()
    assert db.session.get(User, uid).session_version == 1
    assert _authed(client) in (301, 302, 401)  # çalınmış eski çerez geçersiz


def test_baska_alan_degisince_surum_artmaz(app):
    uid = _mk()
    u = db.session.get(User, uid)
    u.job_title = "Uzman"
    db.session.commit()
    assert db.session.get(User, uid).session_version == 0


def test_login_sonrasi_oturuma_surum_yazilir(client, app):
    _mk("login@t.local")
    rv = client.post("/login", data={"email": "login@t.local", "password": "Eski-Parola-1"})
    assert rv.status_code in (200, 302)
    with client.session_transaction() as sess:
        assert "_user_id" in sess, "giriş başarısız — test geçersiz"
        assert sess.get("sv") == 0
