# -*- coding: utf-8 -*-
"""Masaüstüm 'veri girişi bekleyen PG'lerim' (UX-PLANI B / Faz 2.3)."""
from datetime import date

import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.models import db
from app.models.core import Role, Tenant, User
from app.models.plan_year import PlanYear
from app.models.process import KpiData, Process, ProcessKpi, process_leaders
from app.services.bekleyen_pg_service import bekleyen_pg_listesi, tamamlanmis_donemler
from config import TestingConfig


@pytest.fixture
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.mark.parametrize("tur,bugun,beklenen", [
    ("Aylık", date(2026, 4, 15), ["aylik_1", "aylik_2", "aylik_3"]),     # nisan: cari ay sayılmaz
    ("Aylık", date(2026, 1, 20), []),                                     # ocak: bitmiş ay yok
    ("Çeyreklik", date(2026, 8, 1), ["ceyrek_1", "ceyrek_2"]),
    ("Yarıyıllık", date(2026, 7, 1), ["halfyear_1"]),
    ("Yarıyıllık", date(2026, 6, 30), []),
    ("Yıllık", date(2026, 12, 31), []),                                   # yıllık kapsam dışı
    ("Haftalık", date(2026, 5, 5), []),
    (None, date(2026, 5, 5), []),
])
def test_tamamlanmis_donemler(tur, bugun, beklenen):
    assert [a for a, _ in tamamlanmis_donemler(tur, bugun)] == beklenen


def _kurum(rol="tenant_admin", tip=None):
    t = Tenant(name="T", short_name="t", is_active=True, **({"tenant_type": tip} if tip else {}))
    r = Role(name=rol)
    db.session.add_all([t, r])
    db.session.flush()
    u = User(email="u@t.test", password_hash=generate_password_hash("x"), tenant_id=t.id, role_id=r.id, is_active=True)
    db.session.add(u)
    db.session.flush()
    py = PlanYear(tenant_id=t.id, year=2026)
    db.session.add(py)
    db.session.flush()
    return t, u, py


def _pg(t, py, ad, period="Aylık", lider=None):
    p = Process(tenant_id=t.id, name="Süreç " + ad, plan_year_id=py.id, is_active=True)
    db.session.add(p)
    db.session.flush()
    k = ProcessKpi(process_id=p.id, name=ad, code=ad[:3], period=period, plan_year_id=py.id, is_active=True)
    db.session.add(k)
    db.session.flush()
    if lider is not None:
        db.session.execute(process_leaders.insert().values(process_id=p.id, user_id=lider.id))
    return p, k


def test_eksik_donemler_listelenir_girilenler_dusulur(app):
    t, u, py = _kurum()
    _, k1 = _pg(t, py, "Ciro", lider=u)
    _, k2 = _pg(t, py, "Memnuniyet", lider=u)
    db.session.add(KpiData(process_kpi_id=k2.id, year=2026, data_date=date(2026, 1, 31), actual_value="5", is_active=True))
    db.session.add(KpiData(process_kpi_id=k2.id, year=2026, data_date=date(2026, 2, 28), actual_value="6", is_active=True))
    db.session.commit()
    s = bekleyen_pg_listesi(u, bugun=date(2026, 4, 10))
    assert s["toplam"] == 2
    by = {r["name"]: r for r in s["items"]}
    assert by["Ciro"]["eksik"] == ["Ocak", "Şubat", "Mart"]
    assert by["Memnuniyet"]["eksik"] == ["Mart"]
    assert s["items"][0]["name"] == "Ciro"  # çok eksik olan önce


def test_lider_veya_uye_olmayan_ve_baska_yil_gorunmez(app):
    t, u, py = _kurum()
    _pg(t, py, "Sahipsiz")  # lider/üye yok
    py25 = PlanYear(tenant_id=t.id, year=2025)
    db.session.add(py25)
    db.session.flush()
    _pg(t, py25, "EskiYil", lider=u)
    db.session.commit()
    assert bekleyen_pg_listesi(u, bugun=date(2026, 4, 10))["items"] == []


def _kart_render(app, bekleyen):
    """Kart bloğunu şablondan ayıklayıp bağımsız render eder (Masaüstüm'ün tüm bağlamı gerekmesin)."""
    from pathlib import Path

    src = (Path(__file__).resolve().parent.parent / "ui/templates/platform/masaustu/index.html").read_text("utf-8")
    bas = src.index("{# ── Veri girişi bekleyen PG'lerim")
    bit = src.index("{# ── Benim Görevlerim")
    with app.test_request_context("/"):
        return app.jinja_env.from_string(src[bas:bit]).render(bekleyen_pg=bekleyen, url_for=lambda *a, **k: "/karne", _=lambda s, **k: s)


def test_kart_veri_yokken_gorunmez(app):
    assert "masaustu.bekleyen_pg" not in _kart_render(app, {"items": [], "toplam": 0})


def test_kart_veri_varken_gorunur(app):
    html = _kart_render(app, {"items": [{"code": "PG1", "name": "Ciro", "process_id": 1, "process_name": "Satış",
                                          "eksik": ["Ocak", "Şubat", "Mart", "Nisan"], "eksik_sayi": 4}], "toplam": 1})
    assert "masaustu.bekleyen_pg" in html and "Ciro" in html and "+1" in html
