# -*- coding: utf-8 -*-
"""Masaüstüm ilk kurulum kontrol listesi (UX-PLANI E / Faz 2.7)."""
from datetime import date

import pytest
from flask import render_template
from flask_login import login_user
from werkzeug.security import generate_password_hash

from app import create_app
from app.models import db
from app.models.core import Role, Strategy, Tenant, User
from app.models.plan_year import PlanYear
from app.models.process import KpiData, Process, ProcessKpi
from app.services.ilk_kurulum_service import adim_durumlari, gizle_ayarla, gizli_mi, kontrol_listesi
from config import TestingConfig


@pytest.fixture
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def _kurum(rol="tenant_admin"):
    t = Tenant(name="T", short_name="t", is_active=True)
    r = Role(name=rol)
    db.session.add_all([t, r])
    db.session.flush()
    u = User(email="u@t.test", password_hash=generate_password_hash("x"), tenant_id=t.id, role_id=r.id, is_active=True)
    db.session.add(u)
    db.session.commit()
    return t, u


def _durum(t):
    return {a["anahtar"]: a["tamam"] for a in adim_durumlari(t.id)}


def test_bos_kurum_hicbir_adim_tamam_degil(app):
    t, u = _kurum()
    assert _durum(t) == {"plan_yili": False, "strateji": False, "surec": False, "pg": False, "veri": False}
    kl = kontrol_listesi(u)
    assert kl["tamam"] == 0 and kl["toplam"] == 5


def test_adimlar_kayitlardan_ilerler_ve_sirayi_korur(app):
    t, u = _kurum()
    py = PlanYear(tenant_id=t.id, year=2026)
    db.session.add(py)
    db.session.flush()
    db.session.add(Strategy(tenant_id=t.id, code="ST1", title="S", plan_year_id=py.id, is_active=True))
    p = Process(tenant_id=t.id, name="P", plan_year_id=py.id, is_active=True)
    db.session.add(p)
    db.session.flush()
    k = ProcessKpi(process_id=p.id, name="PG", code="PG1", period="Aylık", plan_year_id=py.id, is_active=True)
    db.session.add(k)
    db.session.commit()
    assert [a["anahtar"] for a in adim_durumlari(t.id)] == ["plan_yili", "strateji", "surec", "pg", "veri"]
    assert _durum(t) == {"plan_yili": True, "strateji": True, "surec": True, "pg": True, "veri": False}
    db.session.add(KpiData(process_kpi_id=k.id, year=2026, data_date=date(2026, 1, 31), actual_value="5", is_active=True))
    db.session.commit()
    assert kontrol_listesi(u) is None  # hepsi tamam → kendiliğinden kaybolur


def test_gizle_tercihi_kullaniciya_ozel_ve_temayi_ezmez(app):
    t, u = _kurum()
    u.theme_preferences = '{"theme": "dark"}'
    assert not gizli_mi(u) and kontrol_listesi(u) is not None
    gizle_ayarla(u, True)
    db.session.commit()
    assert gizli_mi(u) and kontrol_listesi(u) is None
    assert '"theme": "dark"' in u.theme_preferences


def test_yonetici_olmayan_gormez(app):
    t, u = _kurum(rol="User")
    assert kontrol_listesi(u) is None


def test_sablon_adimlari_ve_gizle_dugmesini_cizer(app):
    t, u = _kurum()
    kl = kontrol_listesi(u)
    with app.test_request_context("/"):
        login_user(u)
        html = render_template("platform/masaustu/_ilk_kurulum.html", ilk_kurulum=kl)
    assert "ilk-kurulum-gizle" in html and "0/5" in html
    assert 'data-card-code="masaustu.ilk_kurulum"' in html
    assert "style=" not in html  # inline stil yasağı


def test_bos_durum_makrosu_eylemli_ve_eylemsiz(app):
    with app.test_request_context("/"):
        h = render_template_string_macro = app.jinja_env.from_string(
            '{% from "platform/_macros/bos_durum.html" import bos_durum %}'
            '{{ bos_durum("fa-sitemap", "Baslik", "Aciklama", "/x", "Git") }}|{{ bos_durum("fa-sitemap", "B2") }}'
        ).render()
    a, b = h.split("|")
    assert 'href="/x"' in a and "Git" in a and "Aciklama" in a
    assert "<a " not in b and "mc-empty-text" not in b
