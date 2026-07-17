# -*- coding: utf-8 -*-
"""Hedef Manipülasyonu Radarı (TASK-262).

Rakipler "hedefe ulaştın mı?" sorar; bu servis "hedefin kendisi dürüst mü?"
sorar. Dayanağı `kpi_data_audits.old_target/new_target` (TASK-261).

Testler radarın DOĞRU SORUYU sorduğunu doğrular: aşağı çekilen hedefler,
dönem kapanışına yakın yapılan revizyonlar, tekrar eden düzeltmeler.
"""
from datetime import date, datetime, timedelta, timezone

import pytest
from werkzeug.security import generate_password_hash

from app.models import db
from app.models.core import User, Tenant, Role
from app.models.process import KpiData, KpiDataAudit, Process, ProcessKpi
from app.services.hedef_radar_service import (
    GEC_DEGISIM_GUN,
    _yon,
    hedef_degisimleri,
    radar_ozeti,
)


# ─── Yön tespiti (saf mantık) ───────────────────────────────────────────────

@pytest.mark.parametrize("eski,yeni,beklenen_yon", [
    ("100", "80", "asagi"),
    ("100", "120", "yukari"),
    ("100", "100", "sabit"),
    ("100", "100.5", "sabit"),        # %0.5 → gürültü, anlamlı değil
    ("100", "98", "asagi"),           # %2 → anlamlı
    ("90-100", "80-90", "belirsiz"),  # aralık hedefi → sayıya indirgenemez
    ("-", "80", "belirsiz"),
    ("100", "-", "belirsiz"),
])
def test_yon_tespiti(eski, yeni, beklenen_yon):
    yon, _ = _yon(eski, yeni)
    assert yon == beklenen_yon


def test_sapma_yuzdesi_dogru():
    yon, yuzde = _yon("100", "80")
    assert yon == "asagi"
    assert yuzde == -20.0


def test_virgullu_hedef_okunur():
    """safe_float virgülü nokta sayar (TASK-252 kuralı)."""
    yon, yuzde = _yon("100,0", "80,0")
    assert yon == "asagi" and yuzde == -20.0


# ─── Fixture: gerçekçi senaryo ──────────────────────────────────────────────

@pytest.fixture
def radar_verisi(app):
    """Bir süreç, 2 KPI ve farklı türde hedef revizyonları."""
    with app.app_context():
        t = Tenant(name="Radar T", short_name="radt", is_active=True)
        db.session.add(t)
        db.session.flush()
        r = Role(name="radar_user", description="r")
        db.session.add(r)
        db.session.flush()
        u = User(email="radar@local.test", first_name="Ali", last_name="Veli",
                 tenant_id=t.id, role_id=r.id,
                 password_hash=generate_password_hash("x"), is_active=True)
        db.session.add(u)
        p = Process(name="Satis Sureci", tenant_id=t.id, is_active=True)
        db.session.add(p)
        db.session.flush()
        k1 = ProcessKpi(name="Aylik Satis", process_id=p.id)
        k2 = ProcessKpi(name="Musteri Memnuniyeti", process_id=p.id)
        db.session.add_all([k1, k2])
        db.session.flush()

        bugun = datetime.now(timezone.utc)

        def _veri(kpi, donem_sonu):
            kd = KpiData(process_kpi_id=kpi.id, user_id=u.id, year=2026,
                         data_date=donem_sonu, period_type="aylik", period_no=1,
                         actual_value="80", target_value="100")
            db.session.add(kd)
            db.session.flush()
            return kd

        def _audit(kd, eski, yeni, gun_once):
            a = KpiDataAudit(
                kpi_data_id=kd.id, action_type="UPDATE",
                old_value="80", new_value="80",
                old_target=eski, new_target=yeni,
                action_detail="test", user_id=u.id,
                created_at=bugun - timedelta(days=gun_once),
            )
            db.session.add(a)
            return a

        # 1) GEÇ + AŞAĞI: dönem kapanışına 3 gün kala hedef %20 düşürülmüş
        kd1 = _veri(k1, (bugun + timedelta(days=3)).date())
        _audit(kd1, "100", "80", gun_once=0)

        # 2) Erken + aşağı: kapanışa 60 gün kala (meşru revizyon olabilir)
        kd2 = _veri(k1, (bugun + timedelta(days=60)).date())
        _audit(kd2, "200", "150", gun_once=0)

        # 3) Yukarı revizyon (iyi sinyal)
        kd3 = _veri(k2, (bugun + timedelta(days=30)).date())
        _audit(kd3, "100", "120", gun_once=1)

        # 4) Aynı KPI ikinci kez aşağı → "çok revize edilen"
        _audit(kd1, "80", "70", gun_once=2)

        db.session.commit()
        yield {"tenant_id": t.id, "k1": k1.id, "k2": k2.id}


# ─── Radar temel davranışı ──────────────────────────────────────────────────

def test_yalniz_hedefi_degisen_kayitlar_gelir(app, radar_verisi):
    """new_target NULL olanlar (yalnız gerçekleşme değişmiş) radar dışı."""
    with app.app_context():
        kd = KpiData.query.filter_by(process_kpi_id=radar_verisi["k1"]).first()
        db.session.add(KpiDataAudit(
            kpi_data_id=kd.id, action_type="UPDATE",
            old_value="70", new_value="90",
            old_target=None, new_target=None,   # hedef değişmedi
            user_id=kd.user_id,
            created_at=datetime.now(timezone.utc),
        ))
        db.session.commit()

        d = hedef_degisimleri(radar_verisi["tenant_id"])
        assert all(x["yeni_hedef"] is not None for x in d), (
            "Hedefi degismeyen kayit radara girmemeli"
        )


def test_gec_ve_asagi_tespit_ediliyor(app, radar_verisi):
    """ASIL SİNYAL: kapanışa yakın + aşağı = hedef sonuca uyduruluyor olabilir."""
    with app.app_context():
        ozet = radar_ozeti(radar_verisi["tenant_id"])
        assert ozet["gec_ve_asagi"] >= 1, (
            f"Kapanisa 3 gun kala %20 dusurulen hedef yakalanmali: {ozet}"
        )


def test_erken_asagi_revizyon_gec_sayilmaz(app, radar_verisi):
    """Kapanışa 60 gün kala düşürme meşru olabilir — 'geç' işaretlenmemeli."""
    with app.app_context():
        d = hedef_degisimleri(radar_verisi["tenant_id"])
        erken = [x for x in d if x["eski_hedef"] == "200"]
        assert erken, "60 gunluk kayit bulunamadi"
        assert erken[0]["gec_ve_asagi"] is False
        assert erken[0]["kapanisa_kala_gun"] > GEC_DEGISIM_GUN


def test_yon_sayaclari(app, radar_verisi):
    with app.app_context():
        ozet = radar_ozeti(radar_verisi["tenant_id"])
        assert ozet["asagi"] == 3, f"3 asagi revizyon bekleniyor: {ozet}"
        assert ozet["yukari"] == 1
        assert ozet["toplam_degisim"] == 4


def test_ortalama_asagi_sapma(app, radar_verisi):
    """-20%, -25%, -12.5% → ortalama ~-19.2"""
    with app.app_context():
        ozet = radar_ozeti(radar_verisi["tenant_id"])
        assert ozet["ortalama_asagi_sapma"] is not None
        assert ozet["ortalama_asagi_sapma"] < 0, "Asagi sapma negatif olmali"


def test_cok_revize_edilen_kpi_tespit(app, radar_verisi):
    """Aynı KPI 2 kez aşağı revize → tekrar sinyali."""
    with app.app_context():
        ozet = radar_ozeti(radar_verisi["tenant_id"])
        assert ozet["cok_revize_edilen"], "Tekrar eden revizyon yakalanmali"
        ilk = ozet["cok_revize_edilen"][0]
        assert ilk["kpi_adi"] == "Aylik Satis"
        assert ilk["kez"] >= 2


def test_kim_ne_zaman_raporlanir(app, radar_verisi):
    """Yönetim 'kim değiştirdi' görebilmeli."""
    with app.app_context():
        d = hedef_degisimleri(radar_verisi["tenant_id"])
        assert d[0]["kim"] == "Ali Veli"
        assert d[0]["ne_zaman"] is not None


# ─── Tenant izolasyonu — kırmızı çizgi ──────────────────────────────────────

def test_baska_kurumun_verisi_gorunmez(app, radar_verisi):
    """Radar tenant kapsamlı olmalı (cross-tenant sızıntı = TASK-248 dersi)."""
    with app.app_context():
        t2 = Tenant(name="Baska", short_name="bsk", is_active=True)
        db.session.add(t2)
        db.session.commit()

        d = hedef_degisimleri(t2.id)
        assert d == [], "Baska kurumun hedef degisiklikleri gorunmemeli"


# ─── Sınır: dürüstlük ───────────────────────────────────────────────────────

def test_veri_notu_sinirlari_soyluyor(app, radar_verisi):
    """Radar niyet okumaz — çıktı bunu açıkça söylemeli."""
    with app.app_context():
        ozet = radar_ozeti(radar_verisi["tenant_id"])
        not_ = ozet["veri_notu"]
        assert "niyet" in not_.lower()
        assert "TASK-261" in not_ or "2026-07-15" in not_


def test_bos_veride_patlamaz(app):
    with app.app_context():
        t = Tenant(name="Bos", short_name="bos", is_active=True)
        db.session.add(t)
        db.session.commit()

        ozet = radar_ozeti(t.id)
        assert ozet["toplam_degisim"] == 0
        assert ozet["ortalama_asagi_sapma"] is None
        assert ozet["cok_revize_edilen"] == []


# ─── GERÇEK YAZMA YOLU — radarın asıl koruması ──────────────────────────────
# Yukarıdaki testler audit kaydını ELLE üretiyor; yazma yolu bozulsa bile
# geçerler (denendi: hedef izi kapatıldı → 20/20 hâlâ geçti). Aşağıdaki test
# gerçek API'yi çağırır: /process/api/kpi-data/update hedef izini yazmazsa
# radar sessizce boş kalır ve kimse fark etmez.

def test_gercek_api_hedef_izini_yaziyor(app, radar_verisi):
    """En kritik test: gerçek veri girişi yolu old_target/new_target yazmalı.

    Doğrulandı (uçtan uca, gerçek DB): hedef 280 → 210 API'den değiştirildi,
    radar "aşağı -25.0%" olarak yakaladı.
    """
    with app.app_context():
        kd = KpiData.query.filter_by(process_kpi_id=radar_verisi["k1"]).first()
        kd.target_value = "100"
        db.session.commit()
        kd_id, uid = kd.id, kd.user_id

        onceki = radar_ozeti(radar_verisi["tenant_id"])["toplam_degisim"]

        c = app.test_client()
        with c.session_transaction() as s:
            s["_user_id"] = str(uid)
            s["_fresh"] = True

        r = c.post(f"/k-plan/process/api/kpi-data/update/{kd_id}", json={"target_value": "75"})
        assert r.status_code == 200, (
            f"API cagrisi basarisiz: {r.status_code} {r.data[:120]}"
        )

        db.session.expire_all()
        sonra = radar_ozeti(radar_verisi["tenant_id"])

        assert sonra["toplam_degisim"] == onceki + 1, (
            "Gercek API'den yapilan hedef degisikligi radara DUSMEDI — "
            "routes_kpi_data.py old_target/new_target yazmiyor olabilir"
        )
        yeni = [d for d in sonra["degisimler"] if d["yeni_hedef"] == "75"]
        assert yeni, "Yeni hedef radarda yok"
        assert yeni[0]["eski_hedef"] == "100"
        assert yeni[0]["yon"] == "asagi"
        assert yeni[0]["sapma_yuzde"] == -25.0


def test_gercek_api_hedef_degismezse_iz_birakmaz(app, radar_verisi):
    """Yalnız gerçekleşme değişince hedef izi NULL kalmalı — aksi halde
    radar 'hedef değişti' sanır ve yanlış alarm üretir."""
    with app.app_context():
        kd = KpiData.query.filter_by(process_kpi_id=radar_verisi["k2"]).first()
        kd_id, uid = kd.id, kd.user_id

        onceki = radar_ozeti(radar_verisi["tenant_id"])["toplam_degisim"]

        c = app.test_client()
        with c.session_transaction() as s:
            s["_user_id"] = str(uid)
            s["_fresh"] = True

        r = c.post(f"/k-plan/process/api/kpi-data/update/{kd_id}", json={"actual_value": "95"})
        assert r.status_code == 200

        db.session.expire_all()
        sonra = radar_ozeti(radar_verisi["tenant_id"])["toplam_degisim"]
        assert sonra == onceki, (
            "Yalniz gerceklesme degisti ama radar 'hedef degisti' saydi"
        )
