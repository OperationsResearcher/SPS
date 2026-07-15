# -*- coding: utf-8 -*-
"""Analiz ekranı tahmini — kanonik motora devir (TASK-256).

ÖNCEKİ DURUM (gerçek veriyle doğrulandı, 2026-07-15):
  - `AnalyticsService.get_forecast` ham metni pandas'a veriyordu →
    `.mean()` string kolonda '81.79'+'70.29'+'87.83' = '81.7970.2987.83'
    birleştirip TypeError fırlatıyordu. Analiz ekranındaki tahmin ÇALIŞMIYORDU.
  - Route `process_id` geçiriyordu ama servis `kpi_id` bekliyordu → 380
    süreçten 366'sında "veri yok", ID çakışan 14'ünde YANLIŞ KPI'ın tahmini.
  - Route hatayı `except` ile yutuyordu → sebep log'a bile düşmüyordu.

Artık tek kanonik motor: `forecast_service.forecast_kpi` (regresyon + %95 CI).
"""
from datetime import date, timedelta

import pytest
from werkzeug.security import generate_password_hash

from app.models import db
from app.models.core import User, Tenant, Role
from app.models.process import Process, ProcessKpi, KpiData
from app.services.analytics_service import AnalyticsService


@pytest.fixture
def surec(app):
    """Süreç + 2 KPI (biri çok verili, biri az) + trend veren ölçümler."""
    with app.app_context():
        t = Tenant(name="Fc T", short_name="fct", is_active=True)
        db.session.add(t)
        db.session.flush()
        r = Role(name="fc_user", description="f")
        db.session.add(r)
        db.session.flush()
        u = User(email="fc@local.test", first_name="F", last_name="C",
                 tenant_id=t.id, role_id=r.id,
                 password_hash=generate_password_hash("x"), is_active=True)
        db.session.add(u)
        p = Process(name="Surec", tenant_id=t.id, is_active=True)
        db.session.add(p)
        db.session.flush()

        ana = ProcessKpi(name="Ana Gosterge", process_id=p.id)
        yan = ProcessKpi(name="Yan Gosterge", process_id=p.id)
        db.session.add_all([ana, yan])
        db.session.flush()

        # Ana KPI: 12 nokta, net artan trend (10, 20, 30 …)
        for i in range(12):
            db.session.add(KpiData(
                process_kpi_id=ana.id, user_id=u.id, year=2026,
                data_date=date(2026, 1, 1) + timedelta(days=30 * i),
                period_type="aylik", period_no=i + 1,
                actual_value=str((i + 1) * 10), target_value="100",
            ))
        # Yan KPI: yalnız 3 nokta → "en çok veri" kuralı Ana'yı seçmeli
        for i in range(3):
            db.session.add(KpiData(
                process_kpi_id=yan.id, user_id=u.id, year=2026,
                data_date=date(2026, 1, 1) + timedelta(days=30 * i),
                period_type="aylik", period_no=i + 1,
                actual_value="5", target_value="10",
            ))
        db.session.commit()
        yield {"process_id": p.id, "ana_id": ana.id, "yan_id": yan.id, "user_id": u.id}


# ─── Asıl regresyon: eskiden TypeError atıyordu ─────────────────────────────

def test_surec_tahmini_patlamiyor_ve_sonuc_veriyor(app, surec):
    """Eski kod burada TypeError fırlatıyordu (pandas string .mean())."""
    with app.app_context():
        r = AnalyticsService.get_forecast(surec["process_id"], periods=3)

        assert r["forecast"], f"Tahmin uretilmedi: {r.get('message')}"
        assert len(r["forecast"]) == 3


def test_process_id_kpi_id_karisikligi_duzeldi(app, surec):
    """Servis artık SÜREÇ alıyor (route zaten öyle geçiriyordu).

    Eski kod `process_id`'yi `process_kpi_id` diye sorguluyordu → süreç
    ID'si tesadüfen bir KPI ID'sine denk gelmiyorsa "veri yok" (yerelde
    380 süreçten 366'sı), denk geliyorsa BAŞKA sürecin KPI'ı gösteriliyordu.
    Doğru davranış: süreç ID'si sürecin KENDİ KPI'larına çözülmeli.
    """
    with app.app_context():
        r = AnalyticsService.get_forecast(surec["process_id"], periods=2)
        # Seçilen KPI bu sürece ait olmalı — başka bir tablodan gelmemeli
        assert r["kpi_id"] in (surec["ana_id"], surec["yan_id"]), (
            f"Secilen kpi_id={r['kpi_id']} bu surece ait degil "
            f"(surecin KPI'lari: {surec['ana_id']}, {surec['yan_id']})"
        )
        assert r["forecast"], "Surec ID'si dogru cozulmeliydi"


def test_en_cok_veriye_sahip_kpi_secilir(app, surec):
    """12 noktalı Ana, 3 noktalı Yan'a tercih edilmeli (en güvenilir trend)."""
    with app.app_context():
        r = AnalyticsService.get_forecast(surec["process_id"])
        assert r["kpi_id"] == surec["ana_id"]
        assert r["kpi_name"] == "Ana Gosterge"


def test_hangi_kpi_kullanildigi_raporlanir(app, surec):
    """Kullanıcı neye baktığını bilmeli — süreçte çok KPI olabilir."""
    with app.app_context():
        r = AnalyticsService.get_forecast(surec["process_id"])
        assert r.get("kpi_name"), "kpi_name cikitida yok"
        assert r.get("kpi_id"), "kpi_id cikitida yok"


# ─── Tahminin kalitesi ──────────────────────────────────────────────────────

def test_artan_trend_dogru_tespit_ediliyor(app, surec):
    """10,20,30…120 → net artış."""
    with app.app_context():
        r = AnalyticsService.get_forecast(surec["process_id"])
        assert r["trend_direction"] == "up"
        assert r["r_squared"] > 0.99, "Mukemmel dogrusal veride R² ~1 olmali"


def test_guven_etiketi_r2_ye_dayaniyor(app, surec):
    """Eski kod sabit 'medium'/'low' yazıyordu (veriye bakmadan)."""
    with app.app_context():
        r = AnalyticsService.get_forecast(surec["process_id"])
        # R² ~1 → high
        assert r["forecast"][0]["confidence"] == "high"


def test_guven_araligi_donuyor(app, surec):
    with app.app_context():
        r = AnalyticsService.get_forecast(surec["process_id"])
        ilk = r["forecast"][0]
        assert ilk["confidence_low"] is not None
        assert ilk["confidence_high"] is not None
        assert ilk["confidence_low"] <= ilk["forecast_value"] <= ilk["confidence_high"]


def test_tahmin_gelecege_bakiyor(app, surec):
    """Artan seride tahmin son gözlemden büyük olmalı."""
    with app.app_context():
        r = AnalyticsService.get_forecast(surec["process_id"])
        assert r["forecast"][0]["forecast_value"] > 120, (
            f"Son deger 120; tahmin {r['forecast'][0]['forecast_value']}"
        )


# ─── Veri yetersiz / yok ────────────────────────────────────────────────────

def test_verisiz_surec_temiz_mesaj_doner(app, surec):
    """Patlamamalı — anlaşılır mesaj dönmeli."""
    with app.app_context():
        p = Process(name="Bos", tenant_id=1, is_active=True)
        db.session.add(p)
        db.session.commit()

        r = AnalyticsService.get_forecast(p.id)
        assert r["forecast"] == []
        assert "gösterge yok" in r["message"] or "veri" in r["message"].lower()


def test_indirgenemez_deger_tahmine_girmez(app, surec):
    """'-' (veri girilmedi) örneğe dahil edilmemeli."""
    with app.app_context():
        db.session.add(KpiData(
            process_kpi_id=surec["ana_id"], user_id=surec["user_id"], year=2026,
            data_date=date(2027, 1, 1), period_type="aylik",
            actual_value="-",   # numeric NULL kalır
        ))
        db.session.commit()

        r = AnalyticsService.get_forecast(surec["process_id"])
        assert r["forecast"], "'-' satiri tahmini bozmamali"
        assert r["samples"] == 12, f"'-' ornege dahil edilmemeli, samples={r['samples']}"


def test_virgullu_deger_tahmine_DAHIL_edilir(app, surec):
    """TASK-256'nın asıl kazancı: eski kod `float('12,5')` deyip ValueError
    alıyor ve satırı SESSİZCE atlıyordu. actual_numeric (safe_float türevi)
    virgülü nokta sayar → değer tahmine girer.

    Bu test ham `float()`'a dönülürse KIRILIR — koruma budur.
    """
    with app.app_context():
        # Yeni KPI: hepsi virgüllü. Eski kod hiçbirini parse edemez → "veri yok".
        p_id = surec["process_id"]
        k = ProcessKpi(name="Virgullu", process_id=p_id)
        db.session.add(k)
        db.session.flush()
        for i in range(14):   # Ana'dan (12) fazla → "en çok veri" bunu seçsin
            db.session.add(KpiData(
                process_kpi_id=k.id, user_id=surec["user_id"], year=2026,
                data_date=date(2026, 1, 1) + timedelta(days=30 * i),
                period_type="aylik", period_no=i + 1,
                actual_value=f"{(i + 1) * 10},5",   # '10,5' '20,5' …
            ))
        db.session.commit()

        r = AnalyticsService.get_forecast(p_id)

        assert r["kpi_id"] == k.id, "En cok veriye sahip KPI secilmeliydi"
        assert r["forecast"], (
            "Virgullu degerler tahmine girmeli — ham float() ile bu satirlar "
            "sessizce atlanip 'veri yok' donerdi"
        )
        assert r["samples"] == 14, (
            f"14 virgullu deger de ornege girmeli, samples={r['samples']}"
        )
        assert r["trend_direction"] == "up"
