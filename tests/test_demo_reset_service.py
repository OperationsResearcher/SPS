# -*- coding: utf-8 -*-
"""Demo sıfırlama servisi — DEMİR GUARD ve tablo dışlama koruması.

Bu servis %0 kapsamdaydı ama var olan en yıkıcı kod: tüm public tabloları
TRUNCATE eder. Yanlış ortamda çalışması Yayın verisinin silinmesi demektir
(KURALLAR-MASTER §8.4: "Demo işlemleri YALNIZCA *-demo hedeflerine dokunur").

Buradaki testler o guard'ın gerçekten kapalı olduğunu doğrular. Gerçek
truncate/restore denenmez — mock'lanamayacak kadar yıkıcı; onun yerine
"demo modu KAPALIYKEN hiçbir SQL çalışmıyor" iddiası kanıtlanır.
"""
import pytest

from app.services import demo_reset_service as drs


@pytest.fixture
def db_erisimi_yasak(monkeypatch):
    """DB motoruna ERİŞİLİRSE testi patlatır.

    `db.engine` salt-okunur property olduğu için doğrudan monkeypatch edilemez;
    onun yerine SQLAlchemy sınıfının property'si patch'lenir. Guard delinip
    DB'ye gidilirse AssertionError yükselir → test kırılır.
    """
    from flask_sqlalchemy import SQLAlchemy

    def _patla(_self):
        raise AssertionError(
            "GUARD DELİNDİ: demo modu kapalıyken DB motoruna erişildi!"
        )

    monkeypatch.setattr(SQLAlchemy, "engine", property(_patla))


# ─── DEMİR GUARD: demo modu kapalıyken yıkıcı iş YAPILMAMALI ─────────────────

@pytest.mark.parametrize("fonksiyon", ["snapshot_baseline", "restore_baseline", "fk_safe_tenant_load"])
def test_demo_modu_kapaliyken_yikici_fonksiyonlar_reddeder(app, db_erisimi_yasak, fonksiyon):
    """KOKPITIM_DEMO_MODE yoksa RuntimeError — DB'ye hiç dokunmadan."""
    app.config["KOKPITIM_DEMO_MODE"] = False

    fn = getattr(drs, fonksiyon)
    with app.test_request_context():
        with pytest.raises(RuntimeError, match="KOKPITIM_DEMO_MODE"):
            fn({}) if fonksiyon == "fk_safe_tenant_load" else fn()


def test_demo_modu_hic_tanimli_degilse_de_reddeder(app, db_erisimi_yasak):
    """Config anahtarı hiç yoksa (yerel/Test/Yayın varsayılanı) → fail-closed."""
    app.config.pop("KOKPITIM_DEMO_MODE", None)

    with app.test_request_context():
        with pytest.raises(RuntimeError, match="KOKPITIM_DEMO_MODE"):
            drs.restore_baseline()


def test_trigger_async_reset_demo_disinda_sessizce_no_op(app, monkeypatch):
    """Tetikleyici demo dışında thread bile başlatmamalı."""
    app.config["KOKPITIM_DEMO_MODE"] = False
    baslatilan = []
    monkeypatch.setattr(drs, "safe_restore_baseline", lambda: baslatilan.append(1))

    with app.test_request_context():
        drs.trigger_async_reset()

    assert baslatilan == [], "Demo dışında sıfırlama tetiklenmemeli"


def test_mark_activity_demo_disinda_dbye_dokunmaz(app, db_erisimi_yasak):
    app.config["KOKPITIM_DEMO_MODE"] = False

    with app.test_request_context():
        drs.mark_activity()  # patlamamalı, sessiz no-op


def test_inactivity_sweep_demo_disinda_false_doner(app, db_erisimi_yasak):
    app.config["KOKPITIM_DEMO_MODE"] = False

    with app.test_request_context():
        assert drs.inactivity_sweep() is False


# ─── Dışlanan tablolar: sıfırlama bunlara dokunmamalı ────────────────────────

def test_alembic_version_ve_demo_runtime_dislanir():
    """alembic_version silinirse migration durumu kaybolur; demo_runtime kendi
    izleme durumunu tutar — ikisi de truncate kapsamı DIŞINDA olmalı."""
    assert "alembic_version" in drs._EXCLUDE_TABLES
    assert "demo_runtime" in drs._EXCLUDE_TABLES


def test_public_tables_dislananlari_filtreler():
    """_public_tables dışlanan tabloları döndürmemeli (truncate listesine girmesinler)."""
    class _SahteConn:
        def execute(self, *a, **k):
            class _R:
                def fetchall(self_inner):
                    return [("users",), ("alembic_version",), ("demo_runtime",), ("processes",)]
            return _R()

    tablolar = drs._public_tables(_SahteConn())

    assert tablolar == ["users", "processes"]
    assert "alembic_version" not in tablolar, "Migration durumu truncate edilmemeli"
    assert "demo_runtime" not in tablolar


def test_safe_restore_baseline_istisna_yutar(app, monkeypatch):
    """Tetiklerden çağrılır — patlarsa HTTP isteğini bozmamalı, False dönmeli."""
    def _patla():
        raise RuntimeError("DB gitti")

    monkeypatch.setattr(drs, "restore_baseline", _patla)
    with app.test_request_context():
        assert drs.safe_restore_baseline() is False
