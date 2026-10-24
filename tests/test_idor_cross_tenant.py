# -*- coding: utf-8 -*-
"""Cross-tenant IDOR paketi (Faz 0.9, G5): kurum A oturumu, kurum B'nin ID'lerine erişemez.

Her ID'li GET ucu B'nin verisini DÖNMEMELİ (yanıt gövdesinde B'ye özgü işaret yok) ve
yazma uçları B kayıtlarına yazamamalı. Yeni uç eklendiğinde IDOR_GET listesine eklenir.
"""
import datetime

import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.models import db
from app.models.core import Role, Tenant, User
from app.models.process import KpiData, Process, ProcessKpi
from config import TestingConfig

B_ISARET = "SIR-B-ISARET-XYZ"


class GuardConfig(TestingConfig):
    TENANT_GUARD_MODE = "enforce"


@pytest.fixture
def ortam():
    app = create_app(GuardConfig)
    with app.app_context():
        db.create_all()
        role = Role(name="kurum_kullanici")
        ta = Tenant(name="Kurum A", short_name="ka", is_active=True)
        tb = Tenant(name="Kurum B", short_name="kb", is_active=True)
        db.session.add_all([role, ta, tb])
        db.session.flush()
        ua = User(email="a@a.test", password_hash=generate_password_hash("x"),
                  tenant_id=ta.id, role_id=role.id, is_active=True)
        db.session.add(ua)
        pb = Process(tenant_id=tb.id, name=B_ISARET, is_active=True)
        db.session.add(pb)
        db.session.flush()
        kb = ProcessKpi(process_id=pb.id, name=B_ISARET + "-PG", is_active=True)
        db.session.add(kb)
        db.session.flush()
        db_ = KpiData(process_kpi_id=kb.id, year=2026, data_date=datetime.date(2026, 3, 1),
                      actual_value="77", is_active=True)
        db.session.add(db_)
        db.session.commit()

        client = app.test_client()
        with client.session_transaction() as s:
            s["_user_id"] = str(ua.id)
            s["_fresh"] = True
            s["session_version"] = getattr(ua, "session_version", 0) or 0
        yield app, client, SimpleIds(pb.id, kb.id, db_.id, tb.id)
        db.session.remove()
        db.drop_all()


class SimpleIds:
    def __init__(self, process_id, kpi_id, kpi_data_id, tenant_id):
        self.process_id, self.kpi_id, self.kpi_data_id, self.tenant_id = process_id, kpi_id, kpi_data_id, tenant_id


# {p}=B süreç id, {k}=B PG id, {d}=B kpi_data id
IDOR_GET = [
    "/api/v1/processes/{p}",
    "/api/v1/processes/{p}/kpis",
    "/api/v1/kpi-data/{d}",
    "/api/v1/reports/performance/{p}",
    "/api/v1/analytics/health/{p}",
    "/k-plan/process/api/get/{p}",
    "/k-plan/process/api/karne/{p}",
    "/k-plan/process/api/kpi/list/{p}",
    "/k-plan/process/api/kpi/get/{k}",
    "/k-plan/process/api/kpi-data/list/{k}",
    "/k-plan/process/api/kpi-data/history/{k}",
    "/k-plan/process/{p}/karne",
]


def _oturum_gecerli(client):
    r = client.get("/api/v1/processes")
    return r.status_code == 200


def test_kendi_oturumu_calisiyor(ortam):
    _, client, _ = ortam
    assert _oturum_gecerli(client), "test oturumu kurulamadı; IDOR sonuçları anlamsız olurdu"


@pytest.mark.parametrize("sablon", IDOR_GET)
def test_baska_kurum_verisi_donmez(ortam, sablon):
    _, client, ids = ortam
    url = sablon.format(p=ids.process_id, k=ids.kpi_id, d=ids.kpi_data_id)
    r = client.get(url)
    assert B_ISARET not in r.get_data(as_text=True), f"{url} → B verisi sızdı (HTTP {r.status_code})"
    assert r.status_code != 200 or r.is_json, f"{url} → beklenmeyen 200"


def test_api_kpi_data_yazma_baska_kurum_reddedilir(ortam):
    _, client, ids = ortam
    r = client.post("/api/v1/kpi-data", json={
        "process_kpi_id": ids.kpi_id, "data_date": "2026-04-01",
        "actual_value": 1, "target_value": 1,
    })
    assert r.status_code in (400, 403, 404)
    assert KpiData.query.filter_by(process_kpi_id=ids.kpi_id).count() == 1


def test_api_kpi_data_guncelle_sil_baska_kurum_reddedilir(ortam):
    _, client, ids = ortam
    assert client.patch(f"/api/v1/kpi-data/{ids.kpi_data_id}", json={"actual_value": "0"}).status_code in (403, 404)
    assert client.delete(f"/api/v1/kpi-data/{ids.kpi_data_id}").status_code in (403, 404)
    kd = KpiData.query.get(ids.kpi_data_id)
    assert kd.actual_value == "77" and kd.is_active


def test_pozitif_kontrol_sahibi_kendi_verisini_gorur(ortam):
    """Testin tespit gücü: B'nin kendi kullanıcısı aynı uçlarda B verisini GÖRMELİ."""
    app, _, ids = ortam
    role = Role.query.filter_by(name="kurum_kullanici").first()
    ub = User(email="b@b.test", password_hash=generate_password_hash("x"),
              tenant_id=ids.tenant_id, role_id=role.id, is_active=True)
    db.session.add(ub)
    db.session.commit()
    client = app.test_client()
    with client.session_transaction() as s:
        s["_user_id"] = str(ub.id)
        s["_fresh"] = True
        s["session_version"] = getattr(ub, "session_version", 0) or 0
    r = client.get(f"/api/v1/processes/{ids.process_id}")
    assert r.status_code == 200 and B_ISARET in r.get_data(as_text=True)
