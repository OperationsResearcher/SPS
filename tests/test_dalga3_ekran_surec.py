# -*- coding: utf-8 -*-
"""Dalga 3 / adim 2a — Karne API, score-detail, process health ve bireysel: TEK motor."""
from datetime import date

import pytest
from werkzeug.security import generate_password_hash

from app.models import db
from app.models.core import Role, Tenant, User
from app.models.process import KpiData, Process, ProcessKpi
from app.services.process_health_service import calculate_process_health_score
from app.services.score_engine_service import _score_pgs, weighted_average
from app.utils.tr_time import today_tr

YIL = today_tr().year


@pytest.fixture
def fx(app, client):
    t = Tenant(name="T", short_name="t", is_active=True)
    r = Role(name="tenant_admin", description="ta")
    db.session.add_all([t, r])
    db.session.flush()
    u = User(email="ta@t.local", first_name="a", last_name="b", tenant_id=t.id, role_id=r.id,
             password_hash=generate_password_hash("x"), is_active=True)
    p = Process(name="P", tenant_id=t.id, is_active=True, progress=0)
    db.session.add_all([u, p])
    db.session.flush()

    def pg(name, yontem, yon, hedef, vals, weight=None):
        k = ProcessKpi(process_id=p.id, name=name, code=name, is_active=True, target_value=hedef,
                       data_collection_method=yontem, direction=yon, period="Aylık",
                       unit="adet", weight=weight)
        db.session.add(k)
        db.session.flush()
        for i, v in enumerate(vals, 1):
            db.session.add(KpiData(process_kpi_id=k.id, year=YIL, data_date=date(YIL, i, 1),
                                   actual_value=v, is_active=True))
        return k

    ks = {
        "sum": pg("SUM1", "SUM", "Increasing", "120", ["10", "10", "10"], 50),
        "avg": pg("AVG1", "Ortalama", "Increasing", "10", ["4", "5,5", "6"], 50),
        "last": pg("LAST1", "Son Değer", "Increasing", "10", ["2", "8"]),
        "azalan0": pg("AZ0", "Toplama", "Decreasing", "5", ["0", "0"]),
        "azalan": pg("AZ", "Ortalama", "Decreasing", "5", ["10", "10"]),
        "yuzde": pg("YZ", "AVG", "Increasing", "100", ["%90", "%70"]),
        "bos": pg("BOS", "Ortalama", "Increasing", "10", []),
    }
    db.session.commit()
    with client.session_transaction() as s:
        s["_user_id"] = str(u.id)
        s["_fresh"] = True
        s["sv"] = 0
    return {"pid": p.id, "ks": {n: k.id for n, k in ks.items()}}


def _motor(fx):
    rows = _score_pgs(list(ProcessKpi.query.filter_by(process_id=fx["pid"]).all()),
                      YIL, today_tr(), None, {})
    return rows


def test_karne_motorla_ayni_skor_ve_deger(client, fx):
    rv = client.get(f"/k-plan/process/api/karne/{fx['pid']}?year={YIL}")
    assert rv.status_code == 200
    kp = {k["id"]: k for k in rv.get_json()["kpis"]}
    rows = _motor(fx)
    for ad, kid in fx["ks"].items():
        assert kp[kid]["achievement"] == rows[kid]["score"], ad
        exp = rows[kid]["actual"]
        got = kp[kid]["year_rollup"]
        assert (got is None) == (exp is None), ad
        if exp is not None:
            assert got == pytest.approx(exp, abs=1e-6), ad
    assert kp[fx["ks"]["sum"]]["achievement"] == 25.0
    assert kp[fx["ks"]["last"]]["achievement"] == 80.0
    assert kp[fx["ks"]["azalan0"]]["achievement"] == 100.0       # A-010 backend yönü
    assert kp[fx["ks"]["azalan"]]["achievement"] == 50.0
    assert kp[fx["ks"]["yuzde"]]["year_rollup"] == 80.0           # %90/%70 çözülür
    assert kp[fx["ks"]["bos"]]["achievement"] is None             # ölçülmedi != 0
    assert kp[fx["ks"]["bos"]]["year_rollup"] is None


def test_score_detail_motorla_ayni(client, fx):
    rows = _motor(fx)
    for ad, kid in fx["ks"].items():
        rv = client.get(f"/k-plan/process/api/kpi/{kid}/score-detail?year={YIL}")
        assert rv.status_code == 200, ad
        j = rv.get_json()
        assert j["achievement"] == rows[kid]["score"], ad
        exp = rows[kid]["actual"]
        assert (j["rollup_value"] is None) == (exp is None), ad
        if exp is not None:
            assert j["rollup_value"] == pytest.approx(exp, abs=1e-4), ad
    assert client.get(
        f"/k-plan/process/api/kpi/{fx['ks']['sum']}/score-detail?year={YIL}"
    ).get_json()["rollup_method"] == "SUM"


def test_health_motorla_ayni_pg_orani(app, fx):
    rows = _motor(fx)
    pairs = [(rows[i]["score"], rows[i]["weight"]) for i in fx["ks"].values()]
    beklenen = weighted_average(pairs)
    h = calculate_process_health_score(fx["pid"], YIL)
    assert h["detay"]["pg_hedef_ulasma_orani"] == pytest.approx(beklenen, abs=0.06)
    assert h["detay"]["veri_girilen_pg"] == sum(1 for s, _ in pairs if s is not None)
    assert h["detay"]["pg_sayisi"] == len(pairs)


def test_health_sum_yontemi_motor_gibi(app, fx):
    """A-008: SUM, aylık [10,10,10], hedef 120 -> %25 (eskiden ortalamaya düşerdi)."""
    for n in ("avg", "last", "azalan0", "azalan", "yuzde", "bos"):
        ProcessKpi.query.get(fx["ks"][n]).is_active = False
    db.session.commit()
    h = calculate_process_health_score(fx["pid"], YIL)
    assert h["detay"]["pg_hedef_ulasma_orani"] == 25.0


def test_health_hicbir_olcum_yoksa_veri_yok(app, fx):
    for n in list(fx["ks"]):
        ProcessKpi.query.get(fx["ks"][n]).is_active = False
    db.session.commit()
    h = calculate_process_health_score(fx["pid"], YIL)
    assert h["durum"] == "Veri yok" and h["detay"]["pg_hedef_ulasma_orani"] is None


def test_kanban_js_azalan_sifir_100():
    import pathlib
    js = (pathlib.Path(__file__).resolve().parent.parent / "ui/static/platform/js/surec.js"
          ).read_text(encoding="utf-8")
    assert 'k.direction === "Decreasing" && compareVal <= 0' in js
    assert "compareVal > 0 ? Math.round((skorTarget / compareVal)" not in js
