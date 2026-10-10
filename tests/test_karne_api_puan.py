"""Faz 1B — karne API'si: açık uçlu aralık (KMF) + bant formatı (Tomofil) + yıllık özet."""
import json
from datetime import date

import pytest
from werkzeug.security import generate_password_hash

from app.models import db
from app.models.core import Role, Tenant, User
from app.models.process import KpiData, Process, ProcessKpi

KMF_ARALIK = json.dumps({"1": "-4", "2": "5-9", "3": "10-14", "4": "15-19", "5": "20-"})
BANT = json.dumps([
    {"min": 8.8, "max": None, "puan": 100}, {"min": 8, "max": 8.8, "puan": 90},
    {"min": 7.2, "max": 8, "puan": 70}, {"min": 5.6, "max": 7.2, "puan": 50},
    {"min": None, "max": 5.6, "puan": 20},
])


@pytest.fixture
def karne(app, client):
    t = Tenant(name="T", short_name="t", is_active=True)
    r = Role(name="tenant_admin", description="ta")
    db.session.add_all([t, r])
    db.session.flush()
    u = User(email="ta@t.local", first_name="a", last_name="b", tenant_id=t.id, role_id=r.id,
             password_hash=generate_password_hash("x"), is_active=True)
    p = Process(name="P", tenant_id=t.id, is_active=True)
    db.session.add_all([u, p])
    db.session.flush()

    def pg(name, method, direction, target, bpa):
        k = ProcessKpi(process_id=p.id, name=name, code=name, is_active=True, target_value=target,
                       data_collection_method=method, direction=direction, basari_puani_araliklari=bpa,
                       period="Aylık", unit="adet")
        db.session.add(k)
        db.session.flush()
        return k

    def veri(k, degerler):
        for i, v in enumerate(degerler, 1):
            db.session.add(KpiData(process_kpi_id=k.id, year=2026, data_date=date(2026, i, 15),
                                   actual_value=str(v), target_value=k.target_value, is_active=True))

    kmf = pg("KMF330", "Toplama", "Increasing", "12", KMF_ARALIK)
    veri(kmf, [5, 7])                       # toplam 12 → "10-14" → 3 (eskiden 1)
    bant = pg("TOM1", "Ortalama", "Increasing", "8", BANT)
    veri(bant, [7.4, 7.56])                 # ortalama 7.48 → 70 (eskiden puansız)
    azalan = pg("IS_KAZASI", "Toplama", "Decreasing", "0", json.dumps({"1": "4-", "2": "1-3", "3": "0", "4": "-", "5": "-"}))
    veri(azalan, [0, 0])
    db.session.commit()

    with client.session_transaction() as s:
        s["_user_id"] = str(u.id)
        s["_fresh"] = True
        s["sv"] = 0
    return {"pid": p.id, "kmf": kmf.id, "bant": bant.id, "azalan": azalan.id}


def _kpis(client, pid):
    rv = client.get(f"/k-plan/process/api/karne/{pid}?year=2026")
    assert rv.status_code == 200, rv.data[:200]
    return {k["id"]: k for k in rv.get_json()["kpis"]}


def test_acik_uclu_aralik_dogru_puan(client, karne):
    k = _kpis(client, karne["pid"])[karne["kmf"]]
    assert float(k["year_rollup"]) == 12.0
    assert k["basari_puani"] == 3          # eskiden 1
    assert k["basari_olcek"] == "1-5"


def test_bant_formati_0_100_puan_ve_olcek(client, karne):
    k = _kpis(client, karne["pid"])[karne["bant"]]
    assert k["basari_puani"] == 70.0       # eskiden None
    assert k["basari_olcek"] == "0-100"


def test_bant_puani_yoksa_none_js_yedek_yok(client, karne):
    """Puan üretilemiyorsa sunucu None döner; istemci '—' gösterir (JS hesabı kaldırıldı)."""
    with client.session_transaction():
        pass
    k = ProcessKpi.query.get(karne["bant"])
    k.basari_puani_araliklari = None
    db.session.commit()
    kp = _kpis(client, karne["pid"])[karne["bant"]]
    assert kp["basari_puani"] is None and kp["basari_olcek"] is None


def test_js_yedek_hesabi_geri_gelmedi():
    """Karar 3: Toplama'yı tüm periyot anahtarlarını toplayarak şişiren JS yedeği kaldırıldı."""
    import pathlib
    js = pathlib.Path(__file__).resolve().parent.parent / "ui" / "static" / "platform" / "js"
    tablo = (js / "pg_tablo_modal.js").read_text(encoding="utf-8")
    surec = (js / "surec.js").read_text(encoding="utf-8")
    assert "allVals.reduce" not in tablo
    assert "hesaplaBasariPuaniMicro(pct" not in surec
    assert "kkBasariPuanHtml" in tablo and "kkBasariPuanHtml" in surec
