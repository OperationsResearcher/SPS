# -*- coding: utf-8 -*-
"""Dalga 3 / adim 1 — tek hesap motoru çekirdeği (A-001..A-007, A-011, A-021)."""
import calendar
from datetime import date
from types import SimpleNamespace as NS

import pytest

from app.models import db
from app.models.core import Tenant
from app.models.plan_year import KpiYearConfig, PlanYear
from app.models.process import KpiData, Process, ProcessKpi
from app.services.score_engine_service import (
    _parse_float, achievement, aggregate_actuals, calculate_kpi_detail,
    calculate_kpi_score, calculate_process_score, entry_in_scope,
    normalize_aggregation_method, normalize_direction, parse_tr_number,
    period_start, weighted_average,
)
from app.utils.karne_hesaplamalar import (
    hesapla_agirlikli_basari_puani, hesapla_basari_puani,
)


# ---- A-003 ------------------------------------------------------------
@pytest.mark.parametrize("s,beklenen", [
    ("1.234", 1234.0), ("1.234.567", 1234567.0), ("1.234,5", 1234.5),
    ("12,5", 12.5), ("%90", 90.0), ("₺100.070", 100070.0), ("-1.500,25", -1500.25),
    ("42", 42.0), (" 7 ", 7.0), ("0,125", 0.125),
    ("98.75", None), ("1.2.3", None), ("0.125", None), ("1,234.5", None),
    ("abc", None), ("-", None), ("", None), (None, None),
])
def test_parse_tr_number(s, beklenen):
    assert parse_tr_number(s) == beklenen


@pytest.mark.parametrize("s,beklenen", [
    ("0.125", 0.125), ("98.750", 98.75), ("2.375", 2.375), ("3.999", 3.999),
    ("1.234,5", 1234.5), ("₺100.070.853", 100070853.0), ("%90", 90.0),
    (5, 5.0), (None, None), ("x", None),
])
def test_parse_float_stored_kanonik_dogrudan(s, beklenen):
    assert _parse_float(s) == beklenen


# ---- A-004 / A-005 ----------------------------------------------------
def test_bant_boslugu_alt_banda_duser():
    b = {1: '0-9', 2: '10-49', 3: '50-79', 4: '80-99', 5: '100-'}
    assert hesapla_basari_puani(99.5, b) == 4
    assert hesapla_basari_puani(79.5, b) == 3
    assert hesapla_basari_puani(9.5, b) == 1
    assert hesapla_basari_puani(11, {1: '1-10', 5: '12-20'}) == 1


def test_agirlik_birimi_tek():
    assert hesapla_agirlikli_basari_puani(4, 1) == pytest.approx(0.04)
    assert hesapla_agirlikli_basari_puani(4, 2) == pytest.approx(0.08)
    assert hesapla_agirlikli_basari_puani(4, 100) == pytest.approx(4.0)


def test_weighted_average_normalize_ve_none():
    assert weighted_average([(100, 60), (0, 20), (0, 20)]) == 60.0
    assert weighted_average([(80, 1), (None, 50)]) == 80.0
    assert weighted_average([(None, 10), (None, 10)]) is None
    assert weighted_average([(100, 30), (50, 70)]) == 65.0
    assert weighted_average([(100, None), (0, None)]) == 50.0


# ---- A-011 / A-021 ----------------------------------------------------
def test_achievement_kurallari():
    assert achievement(50, 100, 'Increasing') == 50.0
    assert achievement(150, 100, 'Increasing') == 100.0
    assert achievement(0, 5, 'Decreasing') == 100.0       # Karar 5
    assert achievement(0, 0, 'Decreasing') == 100.0       # Karar 4
    assert achievement(2, 0, 'Decreasing') == 0.0
    assert achievement(5, 0, 'Increasing') is None
    assert achievement(10, 5, 'Decreasing') == 50.0
    assert achievement(-5, -10, 'Increasing') is None     # negatif hedef: puanlanmaz
    assert achievement(-10, -20, 'Increasing') is None
    assert achievement(None, 5) is None
    assert achievement(10, 5, 'Azalan') == 50.0           # eş anlamlı yön
    assert achievement(10, 5, 'lower_is_better') == 50.0


def test_normalize_direction():
    for d in ('azalan', 'DECREASING', 'Azalan', 'lower_is_better'):
        assert normalize_direction(d) == 'Decreasing'
    for d in (None, '', 'Increasing', 'artan'):
        assert normalize_direction(d) == 'Increasing'


# ---- A-006 ------------------------------------------------------------
@pytest.mark.parametrize("etiket,kod", [
    ('AVG', 'AVG'), ('Ortalama', 'AVG'), ('ortalama', 'AVG'),
    ('SUM', 'SUM'), ('Toplama', 'SUM'), ('toplam', 'SUM'),
    ('Son Değer', 'LAST'), ('son deger', 'LAST'), ('LAST', 'LAST'),
])
def test_toplama_yontemi_etiketleri(etiket, kod):
    assert normalize_aggregation_method(etiket) == kod


def test_aggregate_actuals():
    assert aggregate_actuals([6, 5.5, 4], 'AVG') == pytest.approx(5.1666, abs=1e-3)
    assert aggregate_actuals([6, 5.5, 4], 'SUM') == 15.5
    assert aggregate_actuals([6, 5.5, 4], 'Son Değer') == 6


# ---- A-007 ------------------------------------------------------------
def _e(year, pt, pn, pm, dd):
    return NS(year=year, period_type=pt, period_no=pn, period_month=pm, data_date=dd)


def test_tarih_kesimi_cari_donem_dahil():
    bugun = date(2026, 9, 10)
    assert entry_in_scope(_e(2026, 'aylik', 9, None, date(2026, 9, 30)), bugun)
    assert entry_in_scope(_e(2026, 'yillik', 1, None, date(2026, 12, 31)), bugun)
    assert entry_in_scope(_e(2026, 'ceyrek', 3, None, date(2026, 9, 30)), bugun)
    assert not entry_in_scope(_e(2026, 'aylik', 10, None, date(2026, 10, 31)), bugun)
    assert not entry_in_scope(_e(2026, 'ceyrek', 4, None, date(2026, 12, 31)), bugun)
    assert entry_in_scope(_e(2026, None, None, None, date(2026, 9, 1)), bugun)
    assert not entry_in_scope(_e(2026, None, None, None, date(2026, 9, 30)), bugun)


def test_period_start():
    assert period_start(2026, 'ceyrek', 3) == date(2026, 7, 1)
    assert period_start(2026, 'aylik', 2) == date(2026, 2, 1)
    assert period_start(2026, 'yillik', 1) == date(2026, 1, 1)
    assert period_start(2026, None) is None


# ---- DB'li: A-001 / A-002 / soft delete / genel API ------------------
AS_OF = date(2026, 9, 10)


def _kur():
    t = Tenant(name="T1", short_name="t1", is_active=True)
    db.session.add(t)
    db.session.flush()
    py = PlanYear(tenant_id=t.id, year=2026, status="active")
    db.session.add(py)
    db.session.flush()
    return t, py


def _proc(t, py, name, parent=None, weight=None):
    p = Process(tenant_id=t.id, name=name, parent_id=parent.id if parent else None,
                weight=weight, plan_year_id=py.id, is_active=True)
    db.session.add(p)
    db.session.flush()
    return p


def _kpi(p, py, name, hedef="100", yon="Increasing", yontem="Ortalama", weight=None):
    k = ProcessKpi(process_id=p.id, name=name, target_value=hedef, direction=yon,
                   data_collection_method=yontem, weight=weight, plan_year_id=py.id,
                   is_active=True)
    db.session.add(k)
    db.session.flush()
    return k


def _veri(k, deger, ay=9):
    d = KpiData(process_kpi_id=k.id, year=2026,
                data_date=date(2026, ay, calendar.monthrange(2026, ay)[1]),
                period_type='aylik', period_no=ay, period_month=ay,
                actual_value=str(deger), is_active=True)
    db.session.add(d)
    db.session.flush()
    return d


def test_ust_surec_olculmediyse_none(app):
    t, py = _kur()
    ust = _proc(t, py, "Ust")
    c1 = _proc(t, py, "C1", ust)
    c2 = _proc(t, py, "C2", ust)
    k1 = _kpi(c1, py, "k1")
    _kpi(c2, py, "k2")
    assert calculate_process_score(ust.id, py.id, AS_OF) is None
    assert calculate_process_score(c1.id, py.id, AS_OF) is None
    _veri(k1, 80)   # Eylül verisi: dönem sonu 30 Eylül > 10 Eylül ama dönem başlamış
    assert calculate_process_score(ust.id, py.id, AS_OF) == 80.0


def test_cocuklu_surecin_kendi_pgleri_hesaba_girer(app):
    t, py = _kur()
    ust = _proc(t, py, "Ust")
    c1 = _proc(t, py, "C1", ust)
    _veri(_kpi(c1, py, "c"), 100)
    _veri(_kpi(ust, py, "kendi"), 50)
    assert calculate_process_score(ust.id, py.id, AS_OF) == 75.0


def test_yillik_config_is_included_ve_weight(app):
    t, py = _kur()
    p = _proc(t, py, "P")
    a = _kpi(p, py, "A", weight=50)
    b = _kpi(p, py, "B", weight=50)
    _veri(a, 100)
    _veri(b, 0)
    assert calculate_process_score(p.id, py.id, AS_OF) == 50.0
    cfg = KpiYearConfig(plan_year_id=py.id, process_kpi_id=b.id, is_included=False)
    db.session.add(cfg)
    db.session.flush()
    assert calculate_process_score(p.id, py.id, AS_OF) == 100.0
    assert calculate_kpi_score(b.id, py.id, AS_OF) is None
    cfg.is_included = True
    cfg.weight = 90
    db.session.add(KpiYearConfig(plan_year_id=py.id, process_kpi_id=a.id,
                                 is_included=True, weight=10))
    db.session.flush()
    assert calculate_process_score(p.id, py.id, AS_OF) == 10.0


def test_soft_delete_pg_ve_veri(app):
    t, py = _kur()
    p = _proc(t, py, "P")
    k = _kpi(p, py, "A")
    d = _veri(k, 80)
    assert calculate_kpi_score(k.id, py.id, AS_OF) == 80.0
    d.is_active = False
    db.session.flush()
    assert calculate_kpi_score(k.id, py.id, AS_OF) is None
    d.is_active = True
    k.is_active = False
    db.session.flush()
    assert calculate_kpi_score(k.id, py.id, AS_OF) is None
    assert calculate_process_score(p.id, py.id, AS_OF) is None


def test_kpi_detail_sum_azalan_ve_ondalik(app):
    t, py = _kur()
    p = _proc(t, py, "P")
    k = _kpi(p, py, "S", hedef="120", yontem="SUM")
    for ay in (7, 8, 9):
        _veri(k, 10, ay)
    det = calculate_kpi_detail(k.id, py.id, AS_OF)
    assert det['actual'] == 30.0 and det['score'] == 25.0 and det['method'] == 'SUM'
    z = _kpi(p, py, "Z", hedef="5", yon="Decreasing")
    _veri(z, 0)
    assert calculate_kpi_score(z.id, py.id, AS_OF) == 100.0
    o = _kpi(p, py, "O", hedef="0.9")
    _veri(o, "0.125")
    assert calculate_kpi_score(o.id, py.id, AS_OF) == pytest.approx(13.89)
