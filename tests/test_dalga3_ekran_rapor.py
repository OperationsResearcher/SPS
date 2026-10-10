# -*- coding: utf-8 -*-
"""Dalga 3 / adim 2b — rapor, EFQM, SP ve harici API: TEK motor (A-009/012/014/016, B-005)."""
from datetime import date

import pytest
from werkzeug.security import generate_password_hash

from app.models import db
from app.models.core import Role, Strategy, SubStrategy, Tenant, User
from app.models.process import KpiData, Process, ProcessKpi, ProcessSubStrategyLink
from app.services.score_engine_service import _score_pgs
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

    def pg(name, yontem, yon, hedef, vals):
        k = ProcessKpi(process_id=p.id, name=name, code=name, is_active=True, target_value=hedef,
                       data_collection_method=yontem, direction=yon, period="Aylık", unit="adet")
        db.session.add(k)
        db.session.flush()
        for i, v in enumerate(vals, 1):
            db.session.add(KpiData(process_kpi_id=k.id, year=YIL, data_date=date(YIL, i, 1),
                                   actual_value=v, target_value=hedef, is_active=True))
        return k

    az = pg("AZ", "Ortalama", "Decreasing", "5", ["2", "2", "2"])        # hedefte (100)
    sm = pg("SM", "SUM", "Increasing", "120", ["10", "10", "10"])        # %25
    s = Strategy(tenant_id=t.id, code="S1", title="S", is_active=True)
    db.session.add(s)
    db.session.flush()
    ss1 = SubStrategy(strategy_id=s.id, code="S1.1", title="a", is_active=True)
    ss2 = SubStrategy(strategy_id=s.id, code="S1.2", title="b", is_active=True)
    db.session.add_all([ss1, ss2])
    db.session.flush()
    db.session.add_all([ProcessSubStrategyLink(process_id=p.id, sub_strategy_id=ss1.id),
                        ProcessSubStrategyLink(process_id=p.id, sub_strategy_id=ss2.id)])
    db.session.commit()
    with client.session_transaction() as ses:
        ses["_user_id"] = str(u.id)
        ses["_fresh"] = True
        ses["sv"] = 0
    return {"tid": t.id, "pid": p.id, "az": az.id, "sm": sm.id}


def _motor(fx):
    pgs = ProcessKpi.query.filter_by(process_id=fx["pid"]).all()
    return _score_pgs(pgs, YIL, today_tr(), None, {})


def test_savas_azalan_pg_dogru_ve_fanout_yok(app, fx):
    from micro.modules.sp.routes_exec_advisor import _PROCESS_SQL, _SUBSTRAT_SQL, _savas_rank
    r = _savas_rank(_PROCESS_SQL, fx["tid"], YIL)
    # 2 PG: azalan %100 (hedefte), SUM %25 -> PG başına tek değer: %50
    assert r["top"][0]["on_target_pct"] == 50.0 and r["top"][0]["pg_total"] == 2
    r2 = _savas_rank(_SUBSTRAT_SQL, fx["tid"], YIL)
    assert all(x["on_target_pct"] == 50.0 and x["pg_total"] == 2 for x in r2["top"])


def test_exec_strategy_scores_motorla_ayni(client, fx):
    rv = client.get(f"/k-plan/strategy/api/exec-strategy-scores?year={YIL}")
    assert rv.status_code == 200, rv.data
    it = rv.get_json()["data"]["all"][0]
    assert it["on_target_pct"] == 50.0 and it["pg_total"] == 2 and it["comparable"] == 2


def test_exec_trend_azalan_pg_hedefte(client, fx):
    rv = client.get("/k-plan/strategy/api/exec-trend")
    assert rv.status_code == 200, rv.data
    vals = [v for v in rv.get_json()["data"]["values"] if v is not None]
    assert vals and vals[-1] == 50.0


def test_efqm_k71_yonlu_pg(app, fx):
    from app.services.efqm_assessment import compute_efqm_assessment
    res = compute_efqm_assessment(fx["tid"])
    assert "%50.0" in repr(res)  # eski satır sayımında azalan PG ters sayılırdı


def test_k_rapor_alert_ve_dagilim_motorla_ayni(client, fx):
    m = _motor(fx)
    rv = client.get(f"/k-report/api/alert?year={YIL}")
    assert rv.status_code == 200, rv.data
    d = rv.get_json()
    kritik = (d.get("data") or d).get("kritik_pg")
    assert [k["kpi_id"] for k in kritik] == [fx["sm"]]
    assert kritik[0]["pct"] == round(m[fx["sm"]]["score"], 1) == 25.0
    rv = client.get(f"/k-report/api/pi-dagilim?year={YIL}")
    assert rv.status_code == 200, rv.data
    sc = {x["kpi_id"]: x["pct"] for x in rv.get_json()["data"]["scatter"]}
    assert sc == {fx["az"]: 100.0, fx["sm"]: 25.0}


def test_api_v1_gecersiz_sayi_400_turkce_kabul(client, fx):
    def post(**kw):
        body = {"kpi_id": fx["az"], "period_no": 7}
        body.update(kw)
        return client.post("/api/v1/kpi-data", json=body)
    assert post(actual_value="abc").status_code == 400
    assert post(actual_value="").status_code == 400
    assert post(actual_value="1.2.3").status_code == 400
    assert post(actual_value="1.234,5", year=YIL, data_date=f"{YIL}-03-05").status_code == 201
    e = KpiData.query.filter_by(process_kpi_id=fx["az"], period_no=7).first()
    assert e.actual_value == "1234.5" and e.year == YIL and e.data_date == date(YIL, 3, 5)
    assert post(actual_value="3", year=YIL - 1, data_date=f"{YIL}-03-05").status_code == 400


def test_a016_gecmis_yil_duzeltmesi_calculated_score_ezmez(app, fx):
    from app.services.pg_year_scores import recalc_after_data_change
    k = db.session.get(ProcessKpi, fx["sm"])
    k.calculated_score = 77.0
    db.session.commit()
    recalc_after_data_change(fx["tid"], YIL - 1)
    db.session.expire_all()
    assert db.session.get(ProcessKpi, fx["sm"]).calculated_score == 77.0
