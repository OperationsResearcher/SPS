# -*- coding: utf-8 -*-
"""Proje modülü — kurumlar arası (cross-tenant) yetki sızıntısı regresyonu.

tenant_admin / executive_manager KURUM-BAŞINA rollerdir. Bir kurumun yöneticisi
başka kurumun projesine/görevine erişememelidir. Platform Admin ("Admin") ise
tenant üstüdür ve erişebilir.
"""

import pytest
from werkzeug.security import generate_password_hash

from app.models import db
from app.models.core import User, Tenant, Role
from app.models.portfolio_project import Project, Task
from micro.modules.proje.permissions import (
    user_can_access_project,
    user_can_edit_tasks,
    user_can_manage_task,
    user_is_project_leader,
)


def _tenant(name):
    t = Tenant(name=name, short_name=name.lower(), is_active=True)
    db.session.add(t)
    db.session.commit()
    return t


def _user(email, tenant, role):
    u = User(
        email=email,
        first_name="T",
        last_name="U",
        tenant_id=tenant.id,
        role_id=role.id,
        password_hash=generate_password_hash("Pw123456!"),
        is_active=True,
    )
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture
def iki_kurum(app):
    """A ve B kurumu; her birinde executive_manager + A'da bir proje/görev."""
    roles = {}
    for rn in ("executive_manager", "Admin", "standard_user"):
        r = Role(name=rn, description=rn)
        db.session.add(r)
        roles[rn] = r
    db.session.commit()

    a = _tenant("KurumA")
    b = _tenant("KurumB")

    a_exec = _user("a.exec@x.com", a, roles["executive_manager"])
    b_exec = _user("b.exec@x.com", b, roles["executive_manager"])
    platform_admin = _user("admin@x.com", a, roles["Admin"])

    proj = Project(name="A Projesi", kurum_id=a.id, manager_id=a_exec.id)
    db.session.add(proj)
    db.session.commit()

    task = Task(
        title="A Gorevi",
        project_id=proj.id,
        assignee_id=a_exec.id,
        reporter_id=a_exec.id,
        status="Beklemede",
    )
    db.session.add(task)
    db.session.commit()

    return {
        "a_exec": a_exec,
        "b_exec": b_exec,
        "platform_admin": platform_admin,
        "proj": proj,
        "task": task,
    }


def test_kendi_kurumunun_yoneticisi_erisir(iki_kurum):
    d = iki_kurum
    assert user_can_access_project(d["a_exec"], d["proj"]) is True
    assert user_can_edit_tasks(d["a_exec"], d["proj"]) is True
    assert user_can_manage_task(d["a_exec"], d["proj"], d["task"]) is True
    assert user_is_project_leader(d["a_exec"], d["proj"]) is True


def test_baska_kurumun_yoneticisi_erisemez(iki_kurum):
    """Asıl regresyon: B kurumunun exec'i A'nın projesine dokunamaz."""
    d = iki_kurum
    assert user_can_access_project(d["b_exec"], d["proj"]) is False
    assert user_can_edit_tasks(d["b_exec"], d["proj"]) is False
    assert user_is_project_leader(d["b_exec"], d["proj"]) is False


def test_baska_kurumun_yoneticisi_gorev_silemez(iki_kurum):
    """project_task_delete bu fonksiyona dayanır — cross-tenant silme kapalı."""
    d = iki_kurum
    assert user_can_manage_task(d["b_exec"], d["proj"], d["task"]) is False


def test_platform_admin_tenant_ustu(iki_kurum):
    """Admin (platform) tüm kurumları görür — bypass korunmalı."""
    d = iki_kurum
    assert user_can_access_project(d["platform_admin"], d["proj"]) is True
    assert user_can_manage_task(d["platform_admin"], d["proj"], d["task"]) is True
