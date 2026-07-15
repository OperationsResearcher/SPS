# -*- coding: utf-8 -*-
"""Modül kullanım özeti (TASK-263) — audit_logs'tan paketleme kanıtı.

`audit_logs` 5 aydır kimin neyi değiştirdiğini tutuyordu ama HİÇ okunmuyordu
(tek okuyan: kullanıcının kendi giriş geçmişi). Bu servis o veriyi paketleme
kararına (hangi modül hangi tier'a) kanıt yapar.

⚠️ SINIR: AuditLogger yalnız CRUD + login kaydediyor; sayfa görüntüleme (GET)
izlenmiyor → "hangi modülde İŞ YAPILIYOR" der, "hangi ekran ziyaret ediliyor"
demez. Testler bu sınırı da doğrular (yanlış beklenti kurulmasın).
"""
from datetime import datetime, timedelta, timezone

import pytest

from app.models import db
from app.models.audit import AuditLog
from app.models.core import Tenant
from app.services.admin_logs_service import modul_kullanim_ozeti


def _log(action, resource_type, user_id, tenant_id=None, gun_once=1, username=None):
    kayit = AuditLog(
        action=action,
        resource_type=resource_type,
        user_id=user_id,
        tenant_id=tenant_id,
        username=username or f"u{user_id}@x.com",
        created_at=datetime.now(timezone.utc) - timedelta(days=gun_once),
    )
    db.session.add(kayit)
    return kayit


@pytest.fixture
def audit_verisi(app):
    with app.app_context():
        t = Tenant(name="Audit T", short_name="audt", is_active=True)
        db.session.add(t)
        db.session.commit()

        # PG Veri Girişi: 3 işlem, 2 kullanıcı
        _log("CREATE", "PG Veri Girişi", 1, t.id)
        _log("UPDATE", "PG Veri Girişi", 1, t.id)
        _log("CREATE", "PG Veri Girişi", 2, t.id)
        # Kullanıcı Yönetimi: 1 işlem, 1 kullanıcı
        _log("CREATE", "Kullanıcı Yönetimi", 1, t.id)
        # GÜVENLİK (login) — modül sayılmamalı
        _log("OTURUM AÇMA", "GÜVENLİK", 1, t.id)
        _log("OTURUM AÇMA", "GÜVENLİK", 3, t.id)
        # Pencere DIŞI (200 gün önce) — sayılmamalı
        _log("CREATE", "Eski Modül", 9, t.id, gun_once=200)
        db.session.commit()
        yield t.id


def test_modul_listesi_islem_sayisina_gore_sirali(app, audit_verisi):
    with app.app_context():
        r = modul_kullanim_ozeti(90)
        adlar = [m["ad"] for m in r["moduller"]]
        assert adlar[0] == "PG Veri Girişi", f"En cok kullanilan basta olmali: {adlar}"
        assert r["moduller"][0]["islem"] == 3
        assert r["moduller"][0]["kullanici"] == 2, "Farkli kullanici sayilmali"


def test_guvenlik_kayitlari_modul_sayilmaz(app, audit_verisi):
    """Login/logout modül kullanımı değil — listeye girmemeli."""
    with app.app_context():
        r = modul_kullanim_ozeti(90)
        assert "GÜVENLİK" not in [m["ad"] for m in r["moduller"]]


def test_pencere_disi_kayit_sayilmaz(app, audit_verisi):
    """200 gün önceki kayıt 90 günlük pencereye girmemeli."""
    with app.app_context():
        r = modul_kullanim_ozeti(90)
        assert "Eski Modül" not in [m["ad"] for m in r["moduller"]]

        # Pencere genişletilince görünmeli
        r2 = modul_kullanim_ozeti(365)
        assert "Eski Modül" in [m["ad"] for m in r2["moduller"]]


def test_aktif_ve_yazan_kullanici_ayri_sayilir(app, audit_verisi):
    """Asıl bulgu: giriş yapan ≠ iş yapan. Paketleme kararının kalbi."""
    with app.app_context():
        r = modul_kullanim_ozeti(90)
        # Oturum açan: user 1 ve 3 → 2
        assert r["aktif_kullanici"] == 2
        # CRUD yapan: user 1 ve 2 → 2
        assert r["yazan_kullanici"] == 2


def test_tomofiltest_haric_tutulur(app):
    """İzole test kurumu gerçek kullanım sayısını şişirmemeli."""
    with app.app_context():
        t = Tenant(name="tomofiltest", short_name="tomofiltest", is_active=True)
        db.session.add(t)
        db.session.commit()

        _log("CREATE", "Sahte Modül", 5, t.id)
        db.session.commit()

        r = modul_kullanim_ozeti(90)
        assert "Sahte Modül" not in [m["ad"] for m in r["moduller"]], (
            "tomofiltest kayitlari gercek kullanim sayilmamali"
        )


def test_kapsam_notu_donuyor(app, audit_verisi):
    """Sınır açıkça belirtilmeli — 'ekran ziyareti' sanılmasın."""
    with app.app_context():
        r = modul_kullanim_ozeti(90)
        assert "kapsam_notu" in r
        assert "GET" in r["kapsam_notu"] or "sayfa görüntüleme" in r["kapsam_notu"]


def test_bos_veride_patlamaz(app):
    with app.app_context():
        r = modul_kullanim_ozeti(90)
        assert r["moduller"] == []
        assert r["aktif_kullanici"] == 0
        assert r["yazan_kullanici"] == 0
