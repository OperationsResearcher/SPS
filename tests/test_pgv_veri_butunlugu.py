"""Faz 1C — PGV veri bütünlüğü: HATA-01 (retry'da değer kaybı), HATA-18 (çift tık), HATA-24 (bireysel PG tekilliği)."""
from datetime import date
from unittest.mock import patch

import pytest
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from app.models import db
from app.models.core import Role, Tenant, User
from app.models.plan_year import PlanYear
from app.models.process import (
    IndividualPerformanceIndicator, KpiData, KpiDataAudit, Process, ProcessKpi,
)

MOD = "micro.modules.surec.routes_kpi_data"


@pytest.fixture
def ortam(app, client):
    t = Tenant(name="T", short_name="t", is_active=True)
    r = Role(name="tenant_admin", description="ta")
    db.session.add_all([t, r])
    db.session.flush()
    u = User(email="ta@t.local", first_name="a", last_name="b", tenant_id=t.id, role_id=r.id,
             password_hash=generate_password_hash("x"), is_active=True)
    db.session.add(PlanYear(tenant_id=t.id, year=2026, status="active"))
    p = Process(name="P", tenant_id=t.id, is_active=True)
    db.session.add_all([u, p])
    db.session.flush()
    k = ProcessKpi(process_id=p.id, name="PG", code="PG1", is_active=True, target_value="100",
                   data_collection_method="Ortalama", direction="Increasing", period="Aylık", unit="adet")
    db.session.add(k)
    db.session.flush()
    d = KpiData(process_kpi_id=k.id, year=2026, data_date=date(2026, 3, 31), period_type="aylik",
                period_no=3, actual_value="10", target_value="100", is_active=True, user_id=u.id)
    db.session.add(d)
    db.session.commit()
    with client.session_transaction() as s:
        s["_user_id"] = str(u.id)
        s["_fresh"] = True
        s["sv"] = 0
    return {"uid": u.id, "kpi": k.id, "data": d.id}


def test_guncelleme_retry_degeri_kaybetmez(client, ortam):
    """Sequence kayması → ilk commit PK hatası → ikinci deneme yeni değeri yazmalı."""
    gercek = db.session.commit
    durum = {"n": 0}

    def commit_bir_kez_patlar():
        durum["n"] += 1
        if durum["n"] == 1:
            raise Exception("duplicate key value violates unique constraint kpi_data_pkey")
        return gercek()

    with patch(f"{MOD}.is_pk_duplicate", return_value=True), \
         patch(f"{MOD}.sync_kpi_data_related_sequences"), \
         patch.object(db.session, "commit", side_effect=commit_bir_kez_patlar):
        rv = client.post(f"/k-plan/process/api/kpi-data/update/{ortam['data']}",
                         json={"actual_value": "77"})
    assert rv.status_code == 200, rv.data[:200]
    assert durum["n"] >= 2
    db.session.expire_all()
    assert db.session.get(KpiData, ortam["data"]).actual_value == "77"
    assert KpiDataAudit.query.filter_by(kpi_data_id=ortam["data"], action_type="UPDATE").count() == 1


def _ekle(client, ortam, deger):
    return client.post("/k-plan/process/api/kpi-data/add", json={
        "kpi_id": ortam["kpi"], "year": 2026, "period_type": "aylik", "period_no": 4,
        "period_month": 4, "data_date": "2026-04-30", "actual_value": deger,
    })


def test_cift_tik_ayni_veriyi_iki_kez_yazmaz(client, ortam):
    assert _ekle(client, ortam, "55").status_code == 200
    rv = _ekle(client, ortam, "55")
    assert rv.status_code == 200 and rv.get_json().get("duplicate_ignored") is True
    n = KpiData.query.filter_by(process_kpi_id=ortam["kpi"], data_date=date(2026, 4, 30)).count()
    assert n == 1


def test_farkli_deger_yeni_kayit_olur(client, ortam):
    """Toplama yöntemli PG'lerde bir dönemde birden çok kayıt meşrudur."""
    _ekle(client, ortam, "55")
    _ekle(client, ortam, "60")
    n = KpiData.query.filter_by(process_kpi_id=ortam["kpi"], data_date=date(2026, 4, 30)).count()
    assert n == 2


def test_bireysel_pg_ayni_kaynak_iki_kez_aktif_olamaz(client, ortam):
    def yeni():
        return IndividualPerformanceIndicator(user_id=ortam["uid"], name="B", source="Süreç",
                                              source_process_kpi_id=ortam["kpi"], is_active=True)
    db.session.add(yeni())
    db.session.commit()
    db.session.add(yeni())
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_bireysel_pg_pasif_kayit_tekilligi_engellemez(client, ortam):
    eski = IndividualPerformanceIndicator(user_id=ortam["uid"], name="B", source="Süreç",
                                          source_process_kpi_id=ortam["kpi"], is_active=False)
    db.session.add(eski)
    db.session.commit()
    db.session.add(IndividualPerformanceIndicator(user_id=ortam["uid"], name="B2", source="Süreç",
                                                  source_process_kpi_id=ortam["kpi"], is_active=True))
    db.session.commit()


def test_testlerde_error_log_dosyasi_acilmaz(app):
    """HATA-26: TESTING iken RotatingFileHandler('error.log') eklenmez."""
    from logging.handlers import RotatingFileHandler
    assert not [h for h in app.logger.handlers if isinstance(h, RotatingFileHandler)]
