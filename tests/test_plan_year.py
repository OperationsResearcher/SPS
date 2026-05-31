"""Plan year / KpiYearConfig regresyon testleri."""
import pytest

from app.models.plan_year import PlanYear, KpiYearConfig
from app.models.process import Process, ProcessKpi
from app.services.plan_year_service import get_kpi_config, get_kpi_configs_bulk


@pytest.fixture
def plan_year_fixture(db_session, test_tenant):
    process = Process(
        tenant_id=test_tenant.id,
        name="Test Süreç",
        code="TS-01",
        is_active=True,
    )
    db_session.add(process)
    db_session.flush()

    kpi = ProcessKpi(
        process_id=process.id,
        name="Test PG",
        target_value="100",
        unit="%",
        is_active=True,
    )
    db_session.add(kpi)
    db_session.flush()

    plan_year = PlanYear(
        tenant_id=test_tenant.id,
        year=2026,
        name="2026 Plan",
        status="active",
    )
    db_session.add(plan_year)
    db_session.commit()

    return {"process": process, "kpi": kpi, "plan_year": plan_year}


def test_get_kpi_config_fallback_without_year_config(plan_year_fixture):
    kpi = plan_year_fixture["kpi"]
    plan_year = plan_year_fixture["plan_year"]

    cfg = get_kpi_config(kpi, plan_year)

    assert cfg["target_value"] == "100"
    assert cfg["is_included"] is True
    assert cfg.get("_config_source") != "year"


def test_get_kpi_config_uses_year_config_is_included(plan_year_fixture, db_session):
    kpi = plan_year_fixture["kpi"]
    plan_year = plan_year_fixture["plan_year"]

    db_session.add(
        KpiYearConfig(
            plan_year_id=plan_year.id,
            process_kpi_id=kpi.id,
            target_value="200",
            is_included=False,
        )
    )
    db_session.commit()

    cfg = get_kpi_config(kpi, plan_year)

    assert cfg["target_value"] == "200"
    assert cfg["is_included"] is False
    assert cfg["_config_source"] == "year"


def test_get_kpi_config_none_plan_year_defaults_included(plan_year_fixture):
    kpi = plan_year_fixture["kpi"]
    cfg = get_kpi_config(kpi, None)
    assert cfg["is_included"] is True


def test_get_kpi_configs_bulk(plan_year_fixture, db_session):
    kpi = plan_year_fixture["kpi"]
    plan_year = plan_year_fixture["plan_year"]

    db_session.add(
        KpiYearConfig(
            plan_year_id=plan_year.id,
            process_kpi_id=kpi.id,
            is_included=False,
        )
    )
    db_session.commit()

    bulk = get_kpi_configs_bulk([kpi], plan_year)
    assert kpi.id in bulk
    assert bulk[kpi.id]["is_included"] is False
