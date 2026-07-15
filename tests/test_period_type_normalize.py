# -*- coding: utf-8 -*-
"""period_type kanonik biçim (TASK-253).

DB'de iki ayrı sözlük vardı: 'aylik' (365.925) vs 'Aylık' (202) → GROUP BY
aynı dönemi iki kovaya bölüyordu. Kanonik biçim ASCII küçük harf; yazma
anında ORM `set` event'i ile normalize edilir.

CHECK constraint YOK — kod 6 farklı değer üretiyor (JS 'halfyear' dahil);
tanınmayanı reddetmek çalışan girişi kırardı. Tanınmayan değer olduğu gibi
kalır (görünür), sessizce yanlış kovaya atılmaz.
"""
from datetime import date

import pytest
from werkzeug.security import generate_password_hash

from app.constants.periods import PERIOD_TYPES, normalize_period_type
from app.models import db
from app.models.core import User, Tenant, Role
from app.models.process import Process, ProcessKpi, KpiData


# ─── Saf normalizasyon kuralı ───────────────────────────────────────────────

@pytest.mark.parametrize("ham,beklenen", [
    ("Aylık", "aylik"),
    ("aylık", "aylik"),
    ("AYLIK", "aylik"),
    ("  Aylık  ", "aylik"),        # boşluklu
    ("aylik", "aylik"),            # zaten kanonik
    ("Çeyreklik", "ceyrek"),
    ("çeyrek", "ceyrek"),
    ("ceyreklik", "ceyrek"),
    ("Yıllık", "yillik"),
    ("YILLIK", "yillik"),
    ("Haftalık", "haftalik"),
    ("Günlük", "gunluk"),
    ("halfyear", "halfyear"),      # JS üretiyor — kanonik kabul
])
def test_normalize_kanonik_bicime_cevirir(ham, beklenen):
    assert normalize_period_type(ham) == beklenen


def test_normalize_bos_ve_none():
    assert normalize_period_type(None) is None
    assert normalize_period_type("") is None
    assert normalize_period_type("   ") is None


def test_taninmayan_deger_degistirilmez():
    """Sessizce yanlış kovaya atmaktansa ham hâliyle görünür kalsın."""
    assert normalize_period_type("bilinmeyen_donem") == "bilinmeyen_donem"


def test_kanonik_kume_tutarli():
    """_ESLEME'nin her hedefi PERIOD_TYPES'ta olmalı."""
    for ham in ("Aylık", "Çeyreklik", "Yıllık", "Haftalık", "Günlük", "halfyear"):
        assert normalize_period_type(ham) in PERIOD_TYPES


def test_iki_yazim_da_ayni_kanonige_gider():
    """'AYLIK'.lower() → 'aylik' (ASCII i) ama 'Aylık'.lower() → 'aylık'
    (Türkçe ı). İKİ FARKLI string — eşleme tablosu ikisini de tutmalı,
    yoksa biri sessizce eşleşmez."""
    assert normalize_period_type("AYLIK") == "aylik"     # ASCII yol
    assert normalize_period_type("Aylık") == "aylik"     # Türkçe yol
    assert normalize_period_type("YILLIK") == "yillik"
    assert normalize_period_type("Yıllık") == "yillik"


# ─── ORM entegrasyonu: yazma anında normalize ───────────────────────────────

@pytest.fixture
def kpi(app):
    with app.app_context():
        t = Tenant(name="Per T", short_name="pert", is_active=True)
        db.session.add(t)
        db.session.flush()
        r = Role(name="per_user", description="p")
        db.session.add(r)
        db.session.flush()
        u = User(email="per@local.test", first_name="P", last_name="U",
                 tenant_id=t.id, role_id=r.id,
                 password_hash=generate_password_hash("x"), is_active=True)
        db.session.add(u)
        p = Process(name="S", tenant_id=t.id, is_active=True)
        db.session.add(p)
        db.session.flush()
        k = ProcessKpi(name="PG", process_id=p.id)
        db.session.add(k)
        db.session.commit()
        yield {"kpi_id": k.id, "user_id": u.id}


def _yaz(kpi, period_type):
    kd = KpiData(process_kpi_id=kpi["kpi_id"], user_id=kpi["user_id"],
                 year=2026, data_date=date(2026, 1, 31),
                 period_type=period_type, actual_value="1")
    db.session.add(kd)
    db.session.commit()
    return kd


def test_orm_yazarken_normalize_eder(app, kpi):
    """Asıl regresyon: 'Aylık' bir daha DB'ye girmemeli."""
    with app.app_context():
        kd = _yaz(kpi, "Aylık")
        assert kd.period_type == "aylik"


def test_orm_guncellerken_de_normalize_eder(app, kpi):
    with app.app_context():
        kd = _yaz(kpi, "aylik")
        kd.period_type = "Çeyreklik"
        db.session.commit()
        assert kd.period_type == "ceyrek"


def test_group_by_tek_kovada_toplaniyor(app, kpi):
    """TASK-253'ün varlık sebebi: aynı dönem iki kovaya bölünüyordu."""
    from sqlalchemy import func

    with app.app_context():
        for pt in ("Aylık", "aylik", "AYLIK", "  aylık "):
            _yaz(kpi, pt)

        kovalar = db.session.query(
            KpiData.period_type, func.count()
        ).filter(KpiData.process_kpi_id == kpi["kpi_id"]).group_by(KpiData.period_type).all()

        assert len(kovalar) == 1, f"Tek kova bekleniyordu, {kovalar} bulundu"
        assert kovalar[0] == ("aylik", 4)


# ─── user_id artık nullable: ölçüm kullanıcıdan bağımsız yaşar ──────────────

def test_user_id_null_olabilir(app, kpi):
    """Kullanıcı silinince ÖLÇÜM kaybolmamalı (202 orphan'ın dersi)."""
    with app.app_context():
        kd = KpiData(process_kpi_id=kpi["kpi_id"], user_id=None,
                     year=2026, data_date=date(2026, 2, 28),
                     period_type="aylik", actual_value="5")
        db.session.add(kd)
        db.session.commit()   # NOT NULL olsaydı burada patlardı
        assert kd.id is not None
        assert kd.user_id is None
