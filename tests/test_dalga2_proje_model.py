# -*- coding: utf-8 -*-
"""Dalga 2 / paket A — proje modülü model uyumu (D-001..D-004)."""
import io
import json
import os

import pytest
from werkzeug.security import generate_password_hash

from app.models import db
from app.models.core import Role, Tenant, User
from app.models.portfolio_project import (
    Project, ProjectFile, ProjectRisk, Task, TaskActivity,
)


def _login(client, user_id):
    from flask import g
    g.pop("_login_user", None)
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


@pytest.fixture
def ctx(app):
    t = Tenant(name="A", short_name="a", is_active=True)
    db.session.add(t)
    db.session.flush()
    role = Role(name="tenant_admin", description="x")
    db.session.add(role)
    db.session.flush()
    admin = User(email="adm@a.t", first_name="N", last_name="S", tenant_id=t.id, role_id=role.id,
                 password_hash=generate_password_hash("TestPassword123"), is_active=True)
    db.session.add(admin)
    db.session.flush()
    proj = Project(name="P", tenant_id=t.id, manager_id=admin.id)
    db.session.add(proj)
    db.session.flush()
    task = Task(title="T", project_id=proj.id, reporter_id=admin.id, status="Yapılacak")
    db.session.add(task)
    db.session.commit()
    return dict(admin=admin, proj=proj, task=task)


def test_gorev_put_kalici_ve_aktivite(client, ctx):
    _login(client, ctx["admin"].id)
    pid, tid = ctx["proj"].id, ctx["task"].id
    r = client.put(f"/api/projeler/{pid}/gorevler/{tid}", json={"title": "Yeni Baslik", "status": "Devam Ediyor"})
    assert r.status_code == 200, r.get_data(as_text=True)
    db.session.expire_all()
    t = db.session.get(Task, tid)
    assert t.title == "Yeni Baslik"
    assert t.status == "Devam Ediyor"
    acts = TaskActivity.query.filter_by(task_id=tid).all()
    assert acts
    assert any(a.activity_type == "updated" and json.loads(a.details)["field"] == "title" for a in acts)


def test_risk_ekle_guncelle(client, ctx):
    _login(client, ctx["admin"].id)
    pid = ctx["proj"].id
    r = client.post(f"/api/projeler/{pid}/riskler",
                    json={"title": "r", "description": "d", "mitigation_plan": "m", "impact": 5, "probability": 4})
    assert r.status_code == 200, r.get_data(as_text=True)
    assert r.get_json()["risk"]["risk_score"] == 20
    assert ProjectRisk.query.filter_by(project_id=pid, title="r").count() == 1
    rid = ProjectRisk.query.filter_by(project_id=pid).first().id
    r = client.put(f"/api/projeler/{pid}/riskler/{rid}", json={"impact": 2, "status": "Closed"})
    assert r.status_code == 200, r.get_data(as_text=True)
    lst = client.get(f"/api/projeler/{pid}/riskler")
    assert lst.status_code == 200, lst.get_data(as_text=True)
    assert lst.get_json()["risks"][0]["risk_score"] == 8


def test_proje_dosyasi_yukle_listele_indir(client, ctx):
    _login(client, ctx["admin"].id)
    pid = ctx["proj"].id
    r = client.post(f"/api/projeler/{pid}/dosyalar",
                    data={"files": (io.BytesIO(b"merhaba dunya"), "not.txt")},
                    content_type="multipart/form-data")
    assert r.status_code == 200, r.get_data(as_text=True)
    lst = client.get(f"/api/projeler/{pid}/dosyalar")
    assert lst.status_code == 200, lst.get_data(as_text=True)
    files = lst.get_json()["files"]
    assert len(files) == 1 and files[0]["file_name"] == "not.txt"
    dl = client.get(f"/api/projeler/{pid}/dosyalar/{files[0]['id']}/indir")
    assert dl.status_code == 200
    assert dl.data == b"merhaba dunya"
    pf = db.session.get(ProjectFile, files[0]["id"])
    try:
        os.remove(os.path.join("static", "uploads", "project_files", os.path.basename(pf.file_path)))
    except OSError:
        pass


def test_proje_klonla(client, ctx):
    _login(client, ctx["admin"].id)
    pid = ctx["proj"].id
    db.session.add(ProjectRisk(project_id=pid, title="rr", impact="High", probability="Low", status="Open"))
    db.session.add(ProjectFile(project_id=pid, uploader_id=ctx["admin"].id, filename="a.txt", file_path="/static/x/a.txt"))
    db.session.commit()
    r = client.post(f"/api/projeler/{pid}/klonla", json={"new_name": "Kopya P", "new_start_date": "2026-01-01"})
    assert r.status_code == 200, r.get_data(as_text=True)
    new = Project.query.filter_by(name="Kopya P").first()
    assert new is not None and new.source_project_id == pid
    assert ProjectRisk.query.filter_by(project_id=new.id).count() == 1
    assert ProjectFile.query.filter_by(project_id=new.id).count() == 1


def test_project_risk_hesaplanan_skor_ve_seviye():
    from app.models.portfolio_project import ProjectRisk
    r = ProjectRisk(title="x", impact="High", probability="5")
    assert r.risk_score == 25 and r.risk_level == "Kritik"
    r2 = ProjectRisk(title="y", impact="low", probability=None)
    assert r2.risk_score == 1 and r2.risk_level == "Düşük"
