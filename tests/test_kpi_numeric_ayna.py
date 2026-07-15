# -*- coding: utf-8 -*-
"""KpiData sayısal ayna (TASK-252) — *_value ↔ *_numeric senkronizasyonu.

`actual_value`/`target_value` ham metin (serbest format, iş kuralı);
`*_numeric` onların safe_float türevi. İkisi saparsa sessizce yanlış karne
üretilir — bu testler sapmayı yakalar.

Senkron ORM `set` event'i ile sağlanıyor (app/models/process.py sonu).
"""
from datetime import date
from decimal import Decimal

import pytest
from werkzeug.security import generate_password_hash

from app.models import db
from app.models.core import User, Tenant, Role
from app.models.process import Process, ProcessKpi, KpiData


@pytest.fixture
def kpi(app):
    """Veri girişi için minimum zincir: tenant → user → process → kpi."""
    with app.app_context():
        t = Tenant(name="Num T", short_name="numt", is_active=True)
        db.session.add(t)
        db.session.flush()
        r = Role(name="num_user", description="n")
        db.session.add(r)
        db.session.flush()
        u = User(email="num@local.test", first_name="N", last_name="U",
                 tenant_id=t.id, role_id=r.id,
                 password_hash=generate_password_hash("x"), is_active=True)
        db.session.add(u)
        p = Process(name="Surec", tenant_id=t.id, is_active=True)
        db.session.add(p)
        db.session.flush()
        k = ProcessKpi(name="PG", process_id=p.id)
        db.session.add(k)
        db.session.commit()
        yield {"kpi_id": k.id, "user_id": u.id}


def _veri_yaz(kpi, actual=None, target=None):
    kd = KpiData(
        process_kpi_id=kpi["kpi_id"],
        user_id=kpi["user_id"],
        year=2026,
        data_date=date(2026, 1, 31),
        actual_value=actual,
        target_value=target,
    )
    db.session.add(kd)
    db.session.commit()
    return kd


# ─── Sayıya çevrilebilen değerler ────────────────────────────────────────────

@pytest.mark.parametrize("ham,beklenen", [
    ("100", Decimal("100")),
    ("12.5", Decimal("12.5")),
    ("12,5", Decimal("12.5")),      # virgül ondalık — safe_float çeviriyor
    ("-2", Decimal("-2")),
    ("0", Decimal("0")),
    ("  42  ", Decimal("42")),      # boşluklu
])
def test_sayisal_deger_aynaya_yazilir(app, kpi, ham, beklenen):
    with app.app_context():
        kd = _veri_yaz(kpi, actual=ham)
        assert kd.actual_numeric == beklenen, (
            f"'{ham}' → numeric {kd.actual_numeric}, beklenen {beklenen}"
        )
        assert kd.actual_value == ham, "Ham metin DEĞİŞMEMELİ"


# ─── Sayıya indirgenemeyen değerler → NULL (hata değil, iş kuralı) ───────────

@pytest.mark.parametrize("ham", [
    "-",                # veri girilmedi
    "90-100",           # aralık hedefi (DH/HKY yöntemleri metinden okur)
    "%100",             # yüzde işaretli
    "₺100.070.853",  # para birimi + binlik ayraç
    "abc",
    "",
])
def test_indirgenemeyen_deger_null_kalir_ham_korunur(app, kpi, ham):
    with app.app_context():
        kd = _veri_yaz(kpi, actual=ham)
        assert kd.actual_numeric is None, (
            f"'{ham}' sayıya indirgenemez → numeric NULL olmalı, "
            f"{kd.actual_numeric} bulundu"
        )
        assert kd.actual_value == ham, (
            "Ham metin KORUNMALI — kullanıcı girdisi kaybolamaz"
        )


def test_none_deger_null_kalir(app, kpi):
    with app.app_context():
        kd = _veri_yaz(kpi, actual=None)
        assert kd.actual_numeric is None


# ─── Güncelleme: ayna takip etmeli ──────────────────────────────────────────

def test_deger_guncellenince_ayna_da_guncellenir(app, kpi):
    """En kritik senaryo: güncelleme sonrası sapma = sessiz yanlış karne."""
    with app.app_context():
        kd = _veri_yaz(kpi, actual="100")
        assert kd.actual_numeric == Decimal("100")

        kd.actual_value = "250.5"
        db.session.commit()
        assert kd.actual_numeric == Decimal("250.5"), "Ayna güncellemeyi kaçırdı"

        # sayısaldan indirgenemeyene geçiş → ayna NULL'a dönmeli
        kd.actual_value = "-"
        db.session.commit()
        assert kd.actual_numeric is None, (
            "Değer artık sayı değil ama eski numeric kalmış — SAPMA"
        )


def test_target_value_de_aynalanir(app, kpi):
    with app.app_context():
        kd = _veri_yaz(kpi, target="500")
        assert kd.target_numeric == Decimal("500")

        kd.target_value = "90-100"   # aralık hedefine dönüştü
        db.session.commit()
        assert kd.target_numeric is None


# ─── Asıl kazanç: DB tarafında toplama ──────────────────────────────────────

def test_db_tarafinda_avg_calisiyor(app, kpi):
    """TASK-252'nin varlık sebebi: String kolonda bu sorgu İMKANSIZDI."""
    from sqlalchemy import func

    with app.app_context():
        for v in ("10", "20", "30", "-"):   # '-' ortalamaya girmemeli
            _veri_yaz(kpi, actual=v)

        ort = db.session.query(func.avg(KpiData.actual_numeric)).filter(
            KpiData.process_kpi_id == kpi["kpi_id"]
        ).scalar()

        assert float(ort) == 20.0, f"AVG {ort}, beklenen 20.0 ('-' hariç)"
