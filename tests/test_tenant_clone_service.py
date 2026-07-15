# -*- coding: utf-8 -*-
"""Tenant klon servisi — Yayın kilidi, kaynak seçimi, kapsam tutarlılığı.

Bu servis %0 kapsamdaydı. Yıkıcı yüzeyi: `_wipe_test_tenant` (DELETE) ve
`clone_tomofiltest` (wipe + yeniden klon). İki savunma testi kritik:
  1. Yayın ortamında ASLA çalışmamalı (_is_production kilidi).
  2. 'tomofiltest' ASLA kaynak seçilmemeli — '%tomofil%' LIKE onu da eşler;
     kendini kaynak alırsa wipe edilmiş veriyi klonlar (veri kaybı).
"""
import pytest

from app.services import tenant_clone_service as tcs


# ─── Yayın kilidi ────────────────────────────────────────────────────────────

def test_yayin_ortaminda_klon_reddedilir(app, monkeypatch):
    """FLASK_ENV=production → klon çalışmamalı (savunma derinliği)."""
    monkeypatch.setenv("FLASK_ENV", "production")

    with app.app_context():
        sonuc = tcs.clone_tomofiltest(dry_run=False)

    assert sonuc["ok"] is False
    assert "Yay" in sonuc["error"], f"Yayın kilidi mesajı bekleniyordu: {sonuc}"


def test_yayin_ortaminda_wipe_reddedilir(app, monkeypatch):
    """_wipe_test_tenant Yayın'da RuntimeError yükseltmeli — DELETE çalışmadan."""
    monkeypatch.setenv("FLASK_ENV", "production")

    with app.app_context():
        with pytest.raises(RuntimeError, match="wipe"):
            tcs._wipe_test_tenant(999, set())


def test_is_production_yalniz_production_degerinde_true(monkeypatch):
    """Kilit yalnız tam 'production' değerinde açılmalı; boş/eksik → non-prod."""
    monkeypatch.setenv("FLASK_ENV", "production")
    assert tcs._is_production() is True

    monkeypatch.setenv("FLASK_ENV", "PRODUCTION")
    assert tcs._is_production() is True, "Büyük/küçük harf duyarsız olmalı"

    monkeypatch.setenv("FLASK_ENV", "development")
    assert tcs._is_production() is False

    monkeypatch.delenv("FLASK_ENV", raising=False)
    assert tcs._is_production() is False, "Tanımsızsa development varsayılır"


# ─── Kaynak seçimi: kendini klonlama tuzağı ──────────────────────────────────

def _tenant_ekle(ad: str, kisa: str):
    """ORM ile kurum ekler (ham SQL zorunlu alanları atlıyor)."""
    from extensions import db
    from app.models.core import Tenant
    t = Tenant(name=ad, short_name=kisa, is_active=True)
    db.session.add(t)
    db.session.commit()
    return t.id


def test_kaynak_secimi_tomofiltesti_asla_secmez(app):
    """'%tomofil%' LIKE 'tomofiltest'i de eşler. Yalnız tomofiltest varsa
    kaynak BULUNAMAMALI — aksi halde hedef kendini kaynak alır."""
    with app.app_context():
        _tenant_ekle("tomofiltest", "tomofiltest")

        kaynak = tcs.find_source_tenant_id()

    assert kaynak is None, (
        "tomofiltest kaynak seçildi! '%tomofil%' LIKE tuzağı — hedef kendini "
        "klonlar ve wipe sonrası veri kaybolur."
    )


def test_kaynak_secimi_gercek_tomofili_bulur_testi_atlar(app):
    """Hem Tomofil hem tomofiltest varken kaynak DAİMA gerçek Tomofil olmalı."""
    with app.app_context():
        tomofil_id = _tenant_ekle("Tomofil", "tomofil")
        test_id = _tenant_ekle("tomofiltest", "tomofiltest")

        kaynak = tcs.find_source_tenant_id()
        hedef = tcs.find_test_tenant_id()

    assert kaynak == tomofil_id, "Kaynak gerçek Tomofil olmalı"
    assert hedef == test_id
    assert kaynak != hedef, "Kaynak ve hedef aynı olamaz (wipe → veri kaybı)"


def test_kaynak_yoksa_klon_temiz_hata_doner(app, monkeypatch):
    """Tomofil yoksa klon sessizce boş kurum yaratmamalı."""
    monkeypatch.setenv("FLASK_ENV", "development")

    with app.app_context():
        sonuc = tcs.clone_tomofiltest(dry_run=True)

    assert sonuc["ok"] is False
    assert "bulunamad" in sonuc["error"].lower()


# ─── Kapsam tutarlılığı ──────────────────────────────────────────────────────

def test_skip_tables_ile_clone_order_cakismaz():
    """Bir tablo hem klonlanıp hem atlanamaz — çelişki sessiz veri sızıntısıdır."""
    clone_tablolari = {t for t, _ in tcs.CLONE_ORDER}
    cakisma = clone_tablolari & tcs.SKIP_TABLES

    assert not cakisma, f"Hem CLONE_ORDER hem SKIP_TABLES'ta: {cakisma}"


def test_clone_order_ebeveyn_cocuktan_once_gelir():
    """_map_X'e atıf yapan tablo, X'ten SONRA gelmeli (temp tablo henüz yoksa
    klon patlar veya sessizce NULL FK üretir)."""
    import re

    gorulen: set[str] = set()
    for tablo, kapsam in tcs.CLONE_ORDER:
        for atif in re.findall(r"_map_(\w+)", kapsam):
            assert atif in gorulen, (
                f"'{tablo}' kapsamı _map_{atif}'e atıf yapıyor ama '{atif}' "
                f"CLONE_ORDER'da daha sonra geliyor — sıra yanlış."
            )
        gorulen.add(tablo)


def test_clone_order_tekrarsiz():
    """Aynı tablo iki kez klonlanırsa satırlar çiftlenir."""
    tablolar = [t for t, _ in tcs.CLONE_ORDER]
    assert len(tablolar) == len(set(tablolar)), "CLONE_ORDER'da tekrar eden tablo var"


def test_sentetik_admin_parolasi_kod_icinde_tek_kaynak():
    """Executor bu sabiti import eder — değişirse iki yerde bozulmasın."""
    assert tcs.SYNTH_ADMIN_EMAIL.endswith("@tomofiltest.local")
    assert tcs.TEST_TENANT_NAME == "tomofiltest"
    assert tcs.SOURCE_NAME_LIKE == "tomofil"
