"""Takvim: üst yönetim kapsamı, yıl süzgeci, atama, taşıma ve iCal akışı."""
from datetime import date, datetime, timedelta

import pytest
from werkzeug.security import generate_password_hash

from app.models import db
from app.models.core import Role, Tenant, User
from app.models.plan_year import PlanYear
from app.models.process import (
    IndividualActivity,
    Process,
    ProcessActivity,
    ProcessActivityAssignee,
    process_members,
)


def _login(client, user):
    with client.session_transaction() as s:
        s["_user_id"] = str(user.id)
        s["_fresh"] = True
        s["sv"] = 0


@pytest.fixture
def kurum(app, client):
    t = Tenant(name="T", short_name="t", is_active=True)
    r_top = Role(name="tenant_admin", description="ta")
    r_std = Role(name="standard_user", description="su")
    db.session.add_all([t, r_top, r_std])
    db.session.flush()
    py25 = PlanYear(tenant_id=t.id, year=2025, status="active")
    py26 = PlanYear(tenant_id=t.id, year=2026, status="active")
    db.session.add_all([py25, py26])

    def mk(email, role):
        u = User(email=email, first_name=email.split("@")[0], last_name="x", tenant_id=t.id,
                 role_id=role.id, password_hash=generate_password_hash("x"), is_active=True)
        db.session.add(u)
        return u

    top, ali, veli = mk("top@t.local", r_top), mk("ali@t.local", r_std), mk("veli@t.local", r_std)
    db.session.flush()
    # Aynı süreç iki yılın kopyası olarak vardır
    p25 = Process(name="Satis", code="SR1", tenant_id=t.id, is_active=True, plan_year_id=py25.id)
    p26 = Process(name="Satis", code="SR1", tenant_id=t.id, is_active=True, plan_year_id=py26.id)
    db.session.add_all([p25, p26])
    db.session.flush()
    db.session.execute(process_members.insert().values(process_id=p26.id, user_id=ali.id))
    gun = date.today()
    act = ProcessActivity(process_id=p26.id, name="Gorusme", start_date=gun, end_date=gun,
                          status="Planlandı", is_active=True, plan_year_id=py26.id)
    veli_is = IndividualActivity(user_id=veli.id, name="VeliIs", start_date=gun, end_date=gun, is_active=True)
    db.session.add_all([act, veli_is])
    db.session.commit()
    return {"top": top, "ali": ali, "veli": veli, "p25": p25, "p26": p26, "act": act, "veli_is": veli_is}


def _events(client, url="/api/calendar/events/org"):
    gun = date.today()
    rv = client.get(f"{url}?start={gun - timedelta(days=3)}&end={gun + timedelta(days=3)}")
    assert rv.status_code == 200, rv.data[:200]
    return rv.get_json()["events"]


def test_ust_yonetim_kurum_takvimini_gorur(client, kurum):
    _login(client, kurum["top"])
    ids = {e["id"] for e in _events(client)}
    assert f"process-{kurum['act'].id}" in ids
    assert f"indiv-{kurum['veli_is'].id}" in ids  # başkasının bireysel görevi de görünür
    # masaüstü uç noktası da aynı kapsam
    assert f"indiv-{kurum['veli_is'].id}" in {e["id"] for e in _events(client, "/api/calendar/events")}


def test_standart_kullanici_kurum_ucundan_sizamaz(client, kurum):
    _login(client, kurum["veli"])
    ids = {e["id"] for e in _events(client)}
    assert f"process-{kurum['act'].id}" not in ids  # veli o sürecin üyesi değil
    assert f"indiv-{kurum['veli_is'].id}" in ids  # kendi görevi
    _login(client, kurum["ali"])
    ids = {e["id"] for e in _events(client)}
    assert f"process-{kurum['act'].id}" in ids
    assert f"indiv-{kurum['veli_is'].id}" not in ids


def test_kisi_ve_surec_suzgeci(client, kurum):
    _login(client, kurum["top"])
    gun = date.today()
    q = f"start={gun - timedelta(days=3)}&end={gun + timedelta(days=3)}"
    ids = {e["id"] for e in client.get(f"/api/calendar/events/org?{q}&user_id={kurum['veli'].id}").get_json()["events"]}
    assert ids == {f"indiv-{kurum['veli_is'].id}"}
    ids = {e["id"] for e in client.get(f"/api/calendar/events/org?{q}&process_id={kurum['p26'].id}").get_json()["events"]}
    assert f"process-{kurum['act'].id}" in ids and f"indiv-{kurum['veli_is'].id}" not in ids


def test_surec_listesi_secili_yila_gore_tekrarsiz(client, kurum):
    _login(client, kurum["top"])
    with client.session_transaction() as s:
        s["sp_active_year"] = 2026
    procs = client.get("/api/calendar/quick-create-meta").get_json()["processes"]
    assert [p["id"] for p in procs] == [kurum["p26"].id]
    with client.session_transaction() as s:
        s["sp_active_year"] = 2025
    procs = client.get("/api/calendar/quick-create-meta").get_json()["processes"]
    assert [p["id"] for p in procs] == [kurum["p25"].id]


def test_ust_yonetim_surec_uyesi_olmayana_atar(client, kurum):
    _login(client, kurum["top"])
    gun = date.today()
    rv = client.post("/k-plan/process/api/activity/add", json={
        "process_id": kurum["p26"].id, "name": "Atama",
        "start_at": f"{gun}T09:00", "end_at": f"{gun}T10:00",
        "assignee_ids": [kurum["veli"].id],
    })
    assert rv.status_code == 200, rv.data[:300]
    act_id = rv.get_json()["id"]
    uids = {a.user_id for a in ProcessActivityAssignee.query.filter_by(activity_id=act_id)}
    assert uids == {kurum["veli"].id}


def test_standart_kullanici_baskasina_atayamaz(client, kurum):
    _login(client, kurum["ali"])
    gun = date.today()
    rv = client.post("/k-plan/process/api/activity/add", json={
        "process_id": kurum["p26"].id, "name": "Atama",
        "start_at": f"{gun}T09:00", "end_at": f"{gun}T10:00",
        "assignee_ids": [kurum["veli"].id],
    })
    assert rv.status_code == 200
    uids = {a.user_id for a in ProcessActivityAssignee.query.filter_by(activity_id=rv.get_json()["id"])}
    assert uids == {kurum["ali"].id}


def test_bireysel_atama_yalniz_ust_yonetim(client, kurum):
    gun = str(date.today())
    _login(client, kurum["ali"])
    rv = client.post("/k-plan/individual/api/activity/add",
                     json={"name": "X", "start_date": gun, "end_date": gun, "assignee_id": kurum["veli"].id})
    assert rv.status_code == 403
    _login(client, kurum["top"])
    rv = client.post("/k-plan/individual/api/activity/add",
                     json={"name": "Y", "start_date": gun, "end_date": gun, "assignee_id": kurum["veli"].id})
    assert rv.status_code == 200
    assert IndividualActivity.query.get(rv.get_json()["id"]).user_id == kurum["veli"].id


def test_surukle_birak_yetkisi(client, kurum):
    yarin = date.today() + timedelta(days=1)
    body = {"id": f"process-{kurum['act'].id}", "start": str(yarin), "end": str(yarin + timedelta(days=1)), "all_day": True}
    _login(client, kurum["veli"])  # süreçte yok
    assert client.post("/api/calendar/event/move", json=body).status_code in (403, 404)
    _login(client, kurum["top"])
    assert client.post("/api/calendar/event/move", json=body).status_code == 200
    assert ProcessActivity.query.get(kurum["act"].id).start_date == yarin


def test_ical_abonelik_akisi(client, kurum):
    _login(client, kurum["top"])
    url = client.get("/api/calendar/ical-link").get_json()["url"]
    path = url.split("://", 1)[1].split("/", 1)[1]
    with client.session_transaction() as s:
        s.clear()
    rv = client.get("/" + path)
    assert rv.status_code == 200
    assert rv.mimetype == "text/calendar"
    text = rv.data.decode("utf-8")
    assert "BEGIN:VCALENDAR" in text and "Gorusme" in text and "VeliIs" in text
    assert client.get("/takvim/ical/bozuk.ics").status_code == 404
