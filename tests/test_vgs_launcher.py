"""Launcher Yeni Veri Giriş Sihirbazı — katalog yetkisi ve kart."""
from datetime import date

from werkzeug.security import generate_password_hash

from app.models import db
from app.models.core import Role, Tenant, User
from app.models.plan_year import PlanYear
from app.models.process import KpiData, Process, ProcessKpi


def _login(client, user_id: int):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


def test_vgs_catalog_unauthenticated(client):
    resp = client.get("/k-plan/process/api/vgs-launcher/catalog?year=2026", follow_redirects=False)
    assert resp.status_code in (302, 401)


def test_launcher_page_has_vgs_card(client, app):
    with app.app_context():
        t = Tenant(name="Lvgs T", short_name="lvgs", is_active=True)
        db.session.add(t)
        db.session.flush()
        r = Role(name="standard_user", description="u")
        db.session.add(r)
        db.session.flush()
        u = User(
            email="lvgs-card@local.test",
            first_name="L",
            last_name="V",
            tenant_id=t.id,
            role_id=r.id,
            password_hash=generate_password_hash("x"),
            is_active=True,
        )
        db.session.add(u)
        db.session.commit()
        uid = u.id
    _login(client, uid)
    with client.session_transaction() as sess:
        sess["sp_active_year"] = 2026
    resp = client.get("/desktop-launcher")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "Yeni Veri Giriş Sihirbazı" in html
    assert 'id="lvgs-open"' in html
    assert html.find('id="lvgs-open"') > html.find("fa-calendar-days")
    assert "vgs-launcher/catalog" in html
    assert 'data-default-year="2026"' in html


def test_catalog_hides_non_member_process(client, app):
    with app.app_context():
        t = Tenant(name="Lvgs M", short_name="lvgsm", is_active=True)
        db.session.add(t)
        db.session.flush()
        r = Role(name="standard_user", description="u")
        db.session.add(r)
        db.session.flush()
        u = User(
            email="lvgs-member@local.test",
            first_name="Uye",
            last_name="Kisi",
            tenant_id=t.id,
            role_id=r.id,
            password_hash=generate_password_hash("x"),
            is_active=True,
        )
        db.session.add(u)
        db.session.flush()
        mine = Process(name="Uye Surec", code="U1", tenant_id=t.id, is_active=True)
        other = Process(name="Yabanci Surec", code="Y1", tenant_id=t.id, is_active=True)
        db.session.add_all([mine, other])
        db.session.flush()
        mine.members.append(u)
        py = PlanYear(tenant_id=t.id, year=2026, name="2026", status="active")
        sealed = PlanYear(tenant_id=t.id, year=2021, name="2021", status="closed")
        db.session.add_all([py, sealed])
        db.session.commit()
        uid = u.id
        mine_id = mine.id
        other_id = other.id
    _login(client, uid)
    resp = client.get("/k-plan/process/api/vgs-launcher/catalog?year=2026")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert data["sealed"] is False
    ids = [p["id"] for p in data["processes"]]
    assert mine_id in ids
    assert other_id not in ids

    sealed_resp = client.get("/k-plan/process/api/vgs-launcher/catalog?year=2021")
    assert sealed_resp.status_code == 200
    sealed_data = sealed_resp.get_json()
    assert sealed_data["sealed"] is True
    sealed_ids = [p["id"] for p in sealed_data["processes"]]
    assert mine_id in sealed_ids
    assert other_id not in sealed_ids


def test_kpi_history_returns_rows(client, app):
    with app.app_context():
        t = Tenant(name="Lvgs H", short_name="lvgsh", is_active=True)
        db.session.add(t)
        db.session.flush()
        r = Role(name="standard_user", description="u")
        db.session.add(r)
        db.session.flush()
        u = User(
            email="lvgs-hist@local.test",
            first_name="Hist",
            last_name="User",
            tenant_id=t.id,
            role_id=r.id,
            password_hash=generate_password_hash("x"),
            is_active=True,
        )
        db.session.add(u)
        db.session.flush()
        p = Process(name="Hist Surec", code="H1", tenant_id=t.id, is_active=True)
        db.session.add(p)
        db.session.flush()
        p.members.append(u)
        kpi = ProcessKpi(name="EFQM", process_id=p.id, is_active=True)
        db.session.add(kpi)
        db.session.flush()
        db.session.add(KpiData(
            process_kpi_id=kpi.id,
            user_id=u.id,
            year=2026,
            data_date=date(2026, 9, 8),
            period_type="ceyrek",
            period_no=3,
            actual_value="42",
            is_active=True,
        ))
        db.session.commit()
        uid = u.id
        kid = kpi.id
    _login(client, uid)
    resp = client.get(
        f"/k-plan/process/api/kpi-data/history/{kid}",
        headers={"Accept": "application/json"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert len(data["data"]) == 1
    assert data["data"][0]["actual_value"] == "42"
    assert data["data"][0]["entered_by_name"]


def test_kpi_data_add_does_not_fail_on_tenant_nameerror(client, app):
    with app.app_context():
        t = Tenant(name="Lvgs A", short_name="lvgsa", is_active=True)
        db.session.add(t)
        db.session.flush()
        r = Role(name="standard_user", description="u")
        db.session.add(r)
        db.session.flush()
        u = User(
            email="lvgs-add@local.test",
            first_name="Add",
            last_name="User",
            tenant_id=t.id,
            role_id=r.id,
            password_hash=generate_password_hash("x"),
            is_active=True,
        )
        db.session.add(u)
        db.session.flush()
        py = PlanYear(tenant_id=t.id, year=2026, name="2026", status="active")
        db.session.add(py)
        db.session.flush()
        p = Process(name="Add Surec", code="A1", tenant_id=t.id, is_active=True, plan_year_id=py.id)
        db.session.add(p)
        db.session.flush()
        p.members.append(u)
        kpi = ProcessKpi(name="PG", process_id=p.id, is_active=True, plan_year_id=py.id)
        db.session.add(kpi)
        db.session.commit()
        uid = u.id
        kid = kpi.id
    _login(client, uid)
    resp = client.post(
        "/k-plan/process/api/kpi-data/add",
        json={
            "kpi_id": kid,
            "year": 2026,
            "period_type": "ceyrek",
            "period_no": 3,
            "actual_value": "222",
            "data_date": "2026-09-08",
        },
        headers={"Accept": "application/json"},
    )
    data = resp.get_json()
    assert resp.status_code == 200, data
    assert data["success"] is True

