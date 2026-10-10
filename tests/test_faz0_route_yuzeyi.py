"""Faz 0 — kaldırılan / kilitlenen yüzeyler için regresyon."""


def test_legacy_pg_veri_sil_kaldirildi(app):
    """GUV-07: kurum kontrolsüz hard delete ucu geri gelmemeli."""
    rules = [r.rule for r in app.url_map.iter_rules()]
    assert not any(r.startswith("/api/pg-veri/sil") for r in rules)


def test_kod_arsivi_sir_dosyalarini_dislar(tmp_path):
    """GUV-08: .env, anahtar ve dump dosyaları kod yedeğine girmez."""
    from app.services import yedekleme_service as Y

    (tmp_path / "app.py").write_text("x")
    (tmp_path / ".env").write_text("SECRET_KEY=x")
    (tmp_path / ".env.production").write_text("SECRET_KEY=x")
    (tmp_path / "server.pem").write_text("k")
    (tmp_path / "db.dump").write_text("d")
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / ".env").write_text("SECRET_KEY=x")
    (tmp_path / "backups").mkdir()
    (tmp_path / "backups" / "eski.dump").write_text("d")

    girenler = {rel for rel, _ in Y._iter_code_files(str(tmp_path), None)}
    assert girenler == {"app.py"}


def _login_admin(client, app):
    from werkzeug.security import generate_password_hash
    from app.models import db
    from app.models.core import Role, Tenant, User

    t = Tenant(name="T", short_name="t", is_active=True)
    r = Role(name="Admin", description="a")
    db.session.add_all([t, r])
    db.session.flush()
    u = User(email="a@t.local", first_name="a", last_name="b", tenant_id=t.id,
             role_id=r.id, password_hash=generate_password_hash("x"), is_active=True)
    db.session.add(u)
    db.session.commit()
    with client.session_transaction() as sess:
        sess["_user_id"] = str(u.id)
        sess["_fresh"] = True


def test_yedek_indirme_yayinda_kilitli(client, app, monkeypatch):
    """GUV-08: FLASK_ENV=production iken DB/kod yedeği web'den indirilemez."""
    _login_admin(client, app)
    monkeypatch.setenv("FLASK_ENV", "production")
    assert client.post("/admin/araclar/yedekleme/indir/db").status_code == 403
    assert client.post("/admin/araclar/yedekleme/indir/kod").status_code == 403
    assert client.get("/admin/araclar/yedekleme/indir-dosya?file=x.dump").status_code == 403


def test_xss_masaustu_ve_risk_isi_haritasi_kacisli():
    """GUV-09: kullanıcı girdisi olan alanlar innerHTML'e kaçışsız basılmamalı."""
    import pathlib
    import re

    kok = pathlib.Path(__file__).resolve().parent.parent / "ui" / "static" / "platform" / "js"
    masaustu = (kok / "masaustu.js").read_text(encoding="utf-8")
    ham = re.findall(r"\$\{(?:k|a|p)\.(?:kpi_name|process_name|name)\}", masaustu)
    assert ham == [], f"kaçışsız alan: {ham}"

    risk = (kok / "reports" / "risk_heatmap.js").read_text(encoding="utf-8")
    assert "${items.map(r=>r.title)" not in risk  # title="..." ham basılıyordu
