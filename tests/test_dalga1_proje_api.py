# -*- coding: utf-8 -*-
"""Dalga 1 / paket C — legacy /api/projeler yetki + kiracı doğrulaması (F-003, C-001, C-002).

NOT: Görev güncellemede atama DEĞİŞİMİ TaskActivity alan uyumsuzluğuna (D-001, Dalga 2)
takılabildiğinden, atama testleri yalnız REDDEDİLEN (400) yolu ve doğrulama öncesi davranışı sınar.
"""
import pytest
from werkzeug.security import generate_password_hash

from app.models import db
from app.models.core import Role, Tenant, User
from app.models.portfolio_project import Project, Task, TaskImpact, project_members
from app.models.process import IndividualPerformanceIndicator


def _login(client, user_id):
    # Fixture app bağlamı g'yi istekler arası paylaştırır; flask-login kullanıcıyı g'de
    # önbellekler. Kullanıcı değişiminde önbelleği temizle.
    from flask import g
    g.pop("_login_user", None)
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


def _user(email, tenant, role):
    u = User(
        email=email, first_name="N", last_name="S", tenant_id=tenant.id, role_id=role.id,
        password_hash=generate_password_hash("TestPassword123"), is_active=True,
    )
    db.session.add(u)
    db.session.flush()
    return u


@pytest.fixture
def ctx(app):
    ta = Tenant(name="A", short_name="a", is_active=True)
    tb = Tenant(name="B", short_name="b", is_active=True)
    db.session.add_all([ta, tb])
    db.session.flush()
    r_admin = Role(name="tenant_admin", description="x")
    r_std = Role(name="standard_user", description="x")
    db.session.add_all([r_admin, r_std])
    db.session.flush()
    admin_a = _user("adm@a.t", ta, r_admin)
    member_a = _user("mem@a.t", ta, r_std)
    outsider_a = _user("out@a.t", ta, r_std)
    user_b = _user("ub@b.t", tb, r_std)
    proj = Project(name="P", tenant_id=ta.id, manager_id=admin_a.id)
    db.session.add(proj)
    db.session.flush()
    db.session.execute(project_members.insert().values(project_id=proj.id, user_id=member_a.id))
    task = Task(title="T", project_id=proj.id, reporter_id=admin_a.id, status="Yapılacak")
    db.session.add(task)
    pg_a = IndividualPerformanceIndicator(user_id=member_a.id, name="pga")
    pg_b = IndividualPerformanceIndicator(user_id=user_b.id, name="pgb")
    db.session.add_all([pg_a, pg_b])
    db.session.commit()
    return dict(admin=admin_a, member=member_a, outsider=outsider_a, user_b=user_b,
                proj=proj, task=task, pg_a=pg_a, pg_b=pg_b)


# ── F-003: yetki ──────────────────────────────────────────────────────────────

def test_proje_olustur_rolsuz_403(client, ctx):
    _login(client, ctx["member"].id)
    r = client.post("/api/projeler", json={"name": "x"})
    assert r.status_code == 403


def test_proje_olustur_yetkili_403_degil(client, ctx):
    _login(client, ctx["admin"].id)
    r = client.post("/api/projeler", json={"name": "x"})
    assert r.status_code != 403  # eksik alan -> 400


def test_proje_klonla_rolsuz_403(client, ctx):
    _login(client, ctx["member"].id)
    r = client.post(f"/api/projeler/{ctx['proj'].id}/klonla", json={"new_name": "y", "new_start_date": "2026-01-01"})
    assert r.status_code == 403


def test_proje_duzenle_uye_403_yonetici_ok(client, ctx):
    pid = ctx["proj"].id
    _login(client, ctx["member"].id)
    assert client.put(f"/api/projeler/{pid}", json={"name": "z"}).status_code == 403
    _login(client, ctx["admin"].id)
    rr = client.put(f"/api/projeler/{pid}", json={"name": "z"}); assert rr.status_code == 200, rr.get_data(as_text=True)


def test_risk_ekle_sil_yetki(client, ctx):
    pid = ctx["proj"].id
    body = {"title": "r", "description": "d", "mitigation_plan": "m"}
    _login(client, ctx["outsider"].id)
    assert client.post(f"/api/projeler/{pid}/riskler", json=body).status_code == 403
    _login(client, ctx["member"].id)
    # NOT: risk oluşturma gövdesi ProjectRisk modeliyle uyumsuz (mitigation_plan/created_by_id yok);
    # ayrı hata, Dalga 2. Burada yalnız yetki kapısının geçildiği (403 değil) doğrulanır.
    assert client.post(f"/api/projeler/{pid}/riskler", json=body).status_code != 403
    from app.models.portfolio_project import ProjectRisk
    risk = ProjectRisk(project_id=pid, title="r")
    db.session.add(risk)
    db.session.commit()
    rid = risk.id
    assert client.delete(f"/api/projeler/{pid}/riskler/{rid}").status_code == 403  # üye silemez
    _login(client, ctx["admin"].id)
    assert client.delete(f"/api/projeler/{pid}/riskler/{rid}").status_code == 200


def test_gorev_olustur_rolsuz_403(client, ctx):
    _login(client, ctx["outsider"].id)
    r = client.post(f"/api/projeler/{ctx['proj'].id}/gorevler", json={"title": "t"})
    assert r.status_code == 403


# ── C-002: kullanıcı kiracı doğrulaması ──────────────────────────────────────

def test_gorev_olustur_yabanci_kiraci_atanan_400(client, ctx):
    _login(client, ctx["member"].id)
    r = client.post(f"/api/projeler/{ctx['proj'].id}/gorevler",
                    json={"title": "t", "assigned_to_id": ctx["user_b"].id})
    assert r.status_code == 400


def test_gorev_olustur_ayni_kiraci_atanan_ok(client, ctx):
    _login(client, ctx["member"].id)
    r = client.post(f"/api/projeler/{ctx['proj'].id}/gorevler",
                    json={"title": "t", "assigned_to_id": ctx["member"].id})
    assert r.status_code == 200


def test_gorev_guncelle_yabanci_kiraci_atanan_400(client, ctx):
    _login(client, ctx["member"].id)
    r = client.put(f"/api/projeler/{ctx['proj'].id}/gorevler/{ctx['task'].id}",
                   json={"assigned_to_id": ctx["user_b"].id})
    assert r.status_code == 400


# ── C-001: PG kiracı doğrulaması ─────────────────────────────────────────────

def test_gorev_guncelle_yabanci_pg_impact_400(client, ctx):
    _login(client, ctx["member"].id)
    r = client.put(f"/api/projeler/{ctx['proj'].id}/gorevler/{ctx['task'].id}",
                   json={"impacts": [{"related_pg_id": ctx["pg_b"].id, "impact_value": "99"}]})
    assert r.status_code == 400
    assert TaskImpact.query.filter_by(task_id=ctx["task"].id).count() == 0


def test_gorev_guncelle_kendi_pg_impact_ok(client, ctx):
    _login(client, ctx["member"].id)
    r = client.put(f"/api/projeler/{ctx['proj'].id}/gorevler/{ctx['task'].id}",
                   json={"impacts": [{"related_pg_id": ctx["pg_a"].id, "impact_value": "5"}]})
    assert r.status_code == 200
    assert TaskImpact.query.filter_by(task_id=ctx["task"].id).count() == 1


def test_handle_task_completion_yabanci_pg_atlanir(app, ctx):
    from services.project_service import handle_task_completion
    from app.models.process import IndividualKpiData
    t = ctx["task"]
    t.status = "Tamamlandı"
    db.session.add(TaskImpact(task_id=t.id, related_pg_id=ctx["pg_b"].id, impact_value="99"))
    db.session.commit()
    handle_task_completion(t, "Yapılacak")
    assert IndividualKpiData.query.filter_by(bireysel_pg_id=ctx["pg_b"].id).count() == 0
