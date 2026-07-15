# -*- coding: utf-8 -*-
"""Redis erişilebilirlik + güvenli fallback (TASK-254).

ASIL RİSK: `config.py` içinde `CACHE_REDIS_URL` varsayılanı
'redis://localhost:6379/0' — `REDIS_URL` env'i TANIMSIZ olsa bile dolu
görünür. Eski `init_limiter` yalnız "url redis ile mi başlıyor" diye
baktığı için kontrol HER ZAMAN geçiyordu ve limiter var olmayan Redis'e
bağlanmaya çalışıyordu (config.py'deki "her istekte kilitlenir" uyarısı).

Artık URL'in şekline değil Redis'in PING cevabına bakılıyor. Bu testler
fallback'in gerçekten çalıştığını doğrular — Redis'siz ortamda uygulama
AYAKTA kalmalı, sessizce SimpleCache'e düşmeli.
"""
import pytest

from app.utils.redis_health import redis_erisilebilir


class _SahteLogger:
    def __init__(self):
        self.satirlar = []

    def warning(self, msg):
        self.satirlar.append(("warning", str(msg)))

    def error(self, msg):
        self.satirlar.append(("error", str(msg)))

    def info(self, msg):
        self.satirlar.append(("info", str(msg)))


# ─── URL şekli: redis olmayan girdiler ──────────────────────────────────────

@pytest.mark.parametrize("url", [None, "", "memory://", "postgresql://x", "localhost:6379"])
def test_redis_olmayan_url_false(url):
    """'redis' şemasıyla başlamayan hiçbir şey denenmemeli."""
    assert redis_erisilebilir(url) is False


# ─── Asıl senaryo: URL doğru görünüyor ama Redis YOK ────────────────────────

def test_url_dogru_gorunse_de_redis_yoksa_false():
    """TASK-254'ün varlık sebebi. Eski kontrol burada True derdi (url 'redis'
    ile başlıyor) ve limiter var olmayan sunucuya bağlanmaya çalışırdı."""
    logger = _SahteLogger()
    # 6399: kullanılmayan port — bağlantı reddedilir
    sonuc = redis_erisilebilir("redis://127.0.0.1:6399/0", logger)

    assert sonuc is False, "Ping cevaplamayan Redis 'erişilebilir' sayılamaz"
    assert any("yanit vermiyor" in m for _, m in logger.satirlar), (
        "Sessizce False dönmemeli — operatör sebebini görmeli"
    )


def test_erisilemezlik_warning_seviyesinde_loglanir():
    """Redis'siz çalışmak geçerli bir mod (yerel geliştirme) — error değil
    warning. Yayın'da bu satır görünürse asıl sorun deploy env'indedir."""
    logger = _SahteLogger()
    redis_erisilebilir("redis://127.0.0.1:6399/0", logger)

    seviyeler = {s for s, _ in logger.satirlar}
    assert "warning" in seviyeler
    assert "error" not in seviyeler


def test_logger_yoksa_patlamaz():
    """Çağıran logger vermeyebilir."""
    assert redis_erisilebilir("redis://127.0.0.1:6399/0") is False


# ─── Uygulama Redis'siz ayakta kalmalı ──────────────────────────────────────

def test_rediscache_secili_ama_redis_yoksa_simplecache_e_duser():
    """En kritik senaryo: yanlış yapılandırma uygulamayı ÖLDÜRMEMELİ.

    score_engine_service cache'i canlı yolda kullanıyor — RedisCache seçili
    ama Redis yoksa her çağrı 500 üretirdi.
    """
    from app import create_app
    from config import TestingConfig

    class _RedisliConfig(TestingConfig):
        CACHE_TYPE = "RedisCache"
        CACHE_REDIS_URL = "redis://127.0.0.1:6399/0"   # yok

    app = create_app(_RedisliConfig)

    assert app.config["CACHE_TYPE"] == "SimpleCache", (
        "Redis erişilemezken RedisCache'te ısrar etmek her cache çağrısını "
        "500'e çevirirdi"
    )


def test_cache_redis_siz_calisiyor(app):
    """Fallback sonrası cache gerçekten çalışmalı (sessiz bozulma yok)."""
    from app.extensions import cache

    with app.app_context():
        cache.set("task254_test", "deger", timeout=60)
        assert cache.get("task254_test") == "deger"


# ─── Env değişkeni isim uyumu ───────────────────────────────────────────────

@pytest.mark.parametrize("env_adi", ["CACHE_REDIS_URL", "REDIS_URL"])
def test_iki_env_ismi_de_kabul_edilir(monkeypatch, env_adi):
    """`.env.production.example` CACHE_REDIS_URL yazıyordu ama config yalnız
    REDIS_URL okuyordu → örneği birebir uygulayan operatörün ayarı SESSİZCE
    etkisiz kalıyordu. İkisi de çalışmalı."""
    import importlib

    monkeypatch.delenv("CACHE_REDIS_URL", raising=False)
    monkeypatch.delenv("REDIS_URL", raising=False)
    monkeypatch.setenv(env_adi, "redis://ornek-sunucu:6380/3")

    import config as _config
    importlib.reload(_config)

    assert _config.Config.CACHE_REDIS_URL == "redis://ornek-sunucu:6380/3", (
        f"{env_adi} okunmadı — operatörün ayarı sessizce yok sayılır"
    )

    # Diğer testleri etkilememek için modülü temiz haline döndür
    monkeypatch.delenv(env_adi, raising=False)
    importlib.reload(_config)
