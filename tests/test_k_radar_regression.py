from datetime import date

from werkzeug.security import generate_password_hash

from app.models import db
from app.models.core import Role, Tenant, User
from app.models.k_radar_domain import (
    A3Report,
    CompetitorAnalysis,
    EvmSnapshot,
    ProcessMaturity,
    RiskHeatmapItem,
    StakeholderMap,
    StakeholderSurvey,
    ValueChainItem,
)
from app.models.k_radar import KRadarRecommendationAction
from app.models.process import KpiData, Process, ProcessKpi
from app.models.portfolio_project import Project, Task


def _login(client, user_id: int):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


def _seed_k_radar_dataset():
    tenant_a = Tenant(name="Tenant A", short_name="ta", is_active=True, k_radar_enabled=True)
    tenant_b = Tenant(name="Tenant B", short_name="tb", is_active=True, k_radar_enabled=True)
    db.session.add_all([tenant_a, tenant_b])
    db.session.flush()

    admin_role = Role(name="Admin", description="Admin")
    viewer_role = Role(name="test_user", description="Viewer")
    db.session.add_all([admin_role, viewer_role])
    db.session.flush()

    admin_user = User(
        email="admin@a.local",
        first_name="Admin",
        last_name="A",
        tenant_id=tenant_a.id,
        role_id=admin_role.id,
        password_hash=generate_password_hash("x"),
        is_active=True,
    )
    viewer_user = User(
        email="viewer@a.local",
        first_name="Viewer",
        last_name="A",
        tenant_id=tenant_a.id,
        role_id=viewer_role.id,
        password_hash=generate_password_hash("x"),
        is_active=True,
    )
    db.session.add_all([admin_user, viewer_user])
    db.session.flush()

    proc_a = Process(tenant_id=tenant_a.id, code="P-A", name="Proc A", is_active=True)
    proc_b = Process(tenant_id=tenant_b.id, code="P-B", name="Proc B", is_active=True)
    db.session.add_all([proc_a, proc_b])
    db.session.flush()

    kpi_a = ProcessKpi(
        process_id=proc_a.id,
        name="KPI A",
        target_value="100",
        weight=1.0,
        is_active=True,
    )
    kpi_b = ProcessKpi(
        process_id=proc_b.id,
        name="KPI B",
        target_value="100",
        weight=1.0,
        is_active=True,
    )
    db.session.add_all([kpi_a, kpi_b])
    db.session.flush()

    db.session.add_all(
        [
            KpiData(
                process_kpi_id=kpi_a.id,
                year=date.today().year,
                data_date=date.today(),
                actual_value="80",
                target_value="100",
                user_id=admin_user.id,
                is_active=True,
            ),
            KpiData(
                process_kpi_id=kpi_b.id,
                year=date.today().year,
                data_date=date.today(),
                actual_value="95",
                target_value="100",
                user_id=admin_user.id,
                is_active=True,
            ),
        ]
    )

    db.session.add_all(
        [
            ProcessMaturity(tenant_id=tenant_a.id, process_id=proc_a.id, maturity_level=4, is_active=True),
            ValueChainItem(tenant_id=tenant_a.id, category="primary", linked_process_id=proc_a.id, title="VC A", is_active=True),
            StakeholderMap(tenant_id=tenant_a.id, name="Paydas A", influence=4, interest=4, is_active=True),
            RiskHeatmapItem(tenant_id=tenant_a.id, title="Risk A", probability=4, impact=4, rpn=16, status="open", is_active=True),
            CompetitorAnalysis(tenant_id=tenant_a.id, competitor_name="Comp A", dimension="price", our_score=70, their_score=80, is_active=True),
            A3Report(tenant_id=tenant_a.id, problem="P1", root_cause_json='{"why":"x"}', is_active=True),
            StakeholderSurvey(tenant_id=tenant_a.id, stakeholder_type="customer", score=4.2, is_active=True),
        ]
    )

    project = Project(tenant_id=tenant_a.id, name="Proj A", manager_id=admin_user.id, is_archived=False, health_score=80)
    db.session.add(project)
    db.session.flush()
    db.session.add(EvmSnapshot(tenant_id=tenant_a.id, project_id=project.id, snapshot_date=date.today(), spi=1.1, cpi=0.9, is_active=True))
    db.session.add(
        Task(
            project_id=project.id,
            title="Task A",
            reporter_id=admin_user.id,
            assignee_id=admin_user.id,
            status="Yapılacak",
            is_archived=False,
        )
    )

    db.session.commit()
    return {"admin": admin_user, "viewer": viewer_user, "tenant_a": tenant_a, "tenant_b": tenant_b}


def test_k_radar_new_endpoints_smoke(client, app):
    with app.app_context():
        seeded = _seed_k_radar_dataset()
        _login(client, seeded["admin"].id)

    urls = [
        "/k-radar/api/ks/hoshin",
        "/k-radar/api/ks/ansoff",
        "/k-radar/api/ks/bcg",
        "/k-radar/api/kpr/evm",
        "/k-radar/api/kpr/risk",
        "/k-radar/api/kpr/resource-capacity",
        "/k-radar/api/kpr/gantt",
        "/k-radar/api/cross/rekabet",
        "/k-radar/api/cross/a3",
        "/k-radar/api/cross/anket",
        "/k-radar/api/recommendations/triggers",
    ]
    for url in urls:
        resp = client.get(url)
        assert resp.status_code == 200, url
        payload = resp.get_json()
        assert payload["success"] is True
        assert "data" in payload


def test_k_radar_write_forbidden_for_non_manager(client, app):
    """Yetkisiz kullanıcı paydaş yazamaz.

    Katman mimarisi Faz 3 (2026-07-17): paydaş yazma girdi katmanına taşındı
    (/k-plan/strategy/api/stakeholder). Yetki kontrolü taşımadan etkilenmedi —
    test yeni adresi doğrular.
    """
    with app.app_context():
        seeded = _seed_k_radar_dataset()
        _login(client, seeded["viewer"].id)

    resp = client.post(
        "/k-plan/strategy/api/stakeholder",
        json={"name": "X", "influence": 3, "interest": 3},
    )
    assert resp.status_code == 403
    payload = resp.get_json()
    assert payload["success"] is False


def test_risk_kaynaksiz_girilemez(client, app):
    """Katman ilkesi: HER RİSK BİR KAYNAĞA BAĞLI (TASK-276, Faz 5).

    Kaynaksız / 'manual' / geçersiz kaynak reddedilir. Bu kural kaldırılırsa
    risk konsolidasyonu tekrar kaynağı bilinmeyen kayıtlarla dolar.
    """
    with app.app_context():
        seeded = _seed_k_radar_dataset()
        _login(client, seeded["admin"].id)

    temel = {"title": "Kural Testi", "probability": 3, "impact": 3}

    # kaynak yok
    r = client.post("/k-radar/api/risk/add", json=temel)
    assert r.status_code == 400, f"kaynaksız risk kabul edildi: {r.status_code}"

    # 'manual' artık geçersiz — Faz 5'te kaldırıldı
    r = client.post("/k-radar/api/risk/add", json={**temel, "source_type": "manual"})
    assert r.status_code == 400, "source_type='manual' hâlâ kabul ediliyor"

    # uydurma kaynak
    r = client.post("/k-radar/api/risk/add", json={**temel, "source_type": "xyz"})
    assert r.status_code == 400, "geçersiz kaynak kabul edildi"


def test_risk_gecerli_kaynakla_eklenir(client, app):
    """Geniş kaynak tanımı {swot, pestel, porter, process, project} çalışır.

    Kurumsal-genel riskler zorla projeye değil, doğdukları analize bağlanır
    (Kur Riski → PESTEL). Kaynak listesi daralırsa bu test kırılır.
    """
    with app.app_context():
        seeded = _seed_k_radar_dataset()
        _login(client, seeded["admin"].id)

    for kaynak in ["swot", "pestel", "porter", "process", "project"]:
        r = client.post("/k-radar/api/risk/add", json={
            "title": f"Kaynak testi {kaynak}", "probability": 2,
            "impact": 2, "source_type": kaynak,
        })
        assert r.status_code == 200, f"{kaynak} reddedildi: {r.status_code}"
        assert (r.get_json() or {}).get("success") is True, kaynak


def test_k_radar_teshis_yazma_yuzeyi_yok(client, app):
    """Teşhis katmanında yazma YÜZEYİ kalmadı (Faz 3).

    Eski /k-radar/api/... yazma adresleri girdi katmanına taşındı; teşhiste
    yalnızca okuma kaldı. Bu test katman kuralının kod düzeyinde korunduğunu
    doğrular — biri yazmayı teşhise geri koyarsa kırılır.
    """
    with app.app_context():
        seeded = _seed_k_radar_dataset()
        _login(client, seeded["admin"].id)  # YETKİLİ kullanıcı — yine de yazamamalı

    for url in [
        "/k-radar/api/cross/stakeholder",
        "/k-radar/api/kp/maturity",
        "/k-radar/api/kp/value-chain/items",
    ]:
        resp = client.post(url, json={})
        assert resp.status_code in (404, 405), f"{url} teşhiste yazmaya açık: {resp.status_code}"

        # okuma tarafı çalışmaya devam etmeli
        assert client.get(url).status_code == 200, url


def test_k_radar_tenant_isolation_read(client, app):
    with app.app_context():
        seeded = _seed_k_radar_dataset()
        _login(client, seeded["admin"].id)

    resp = client.get("/k-radar/api/cross/stakeholder")
    assert resp.status_code == 200
    payload = resp.get_json()
    rows = payload["data"]["rows"]
    names = [r["name"] for r in rows]
    assert "Paydas A" in names
    # Tenant B için ek bir kayıt olmadığı gibi, Tenant A dışı veri sızmamalı.
    assert all(name != "Paydas B" for name in names)


def test_k_radar_recommendation_history_and_csv_contract(client, app):
    with app.app_context():
        seeded = _seed_k_radar_dataset()
        db.session.add_all(
            [
                KRadarRecommendationAction(
                    tenant_id=seeded["tenant_a"].id,
                    user_id=seeded["admin"].id,
                    recommendation_key="abc111",
                    recommendation_text="KP-Radar: kritik KPI'lar icin plan",
                    state="approved",
                ),
                KRadarRecommendationAction(
                    tenant_id=seeded["tenant_a"].id,
                    user_id=seeded["admin"].id,
                    recommendation_key="abc222",
                    recommendation_text="KPR-Radar: EVM incelemesi",
                    state="rejected",
                ),
            ]
        )
        db.session.commit()
        _login(client, seeded["admin"].id)

    history = client.get("/k-radar/api/recommendations/history?state=approved&per_page=10&page=1")
    assert history.status_code == 200
    payload = history.get_json()
    assert payload["success"] is True
    items = payload["data"]["items"]
    assert len(items) >= 1
    assert all(i["state"] == "approved" for i in items)
    assert {"page", "per_page", "total", "pages"} <= set(payload["data"]["pagination"].keys())

    csv_resp = client.get("/k-radar/api/recommendations/history.csv?state=approved")
    assert csv_resp.status_code == 200
    body = csv_resp.get_data(as_text=True)
    assert "state,user_id,updated_at,recommendation_text" in body
    assert "approved" in body
