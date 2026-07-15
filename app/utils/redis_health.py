# -*- coding: utf-8 -*-
"""Redis erişilebilirlik kontrolü (TASK-254).

NEDEN VAR: `config.py` içinde `CACHE_REDIS_URL` varsayılanı
`redis://localhost:6379/0` — yani `REDIS_URL` env'i TANIMSIZ olsa bile bu
değer DOLU görünür. `security.py::init_limiter` "url redis ile mi başlıyor"
diye baktığı için kontrol her zaman True dönüyor ve limiter var olmayan bir
Redis'e bağlanmaya çalışıyordu. `config.py`'deki "Redis yoksa limiter her
istekte kilitlenir" uyarısı tam olarak bu riski tarif ediyor.

Çözüm: URL'in ŞEKLİNE değil, Redis'in CEVABINA bak. `ping()` atılır; yanıt
yoksa çağıran güvenle memory/SimpleCache'e düşer.

Kontrol bir kez yapılır (uygulama başlangıcı) — her istekte ping atmak
gecikme ekler ve amacı zaten aşar.
"""
from __future__ import annotations

# Süre: başlangıçta bir kez ödenir. Uzun tutmak konteyner açılışını geciktirir.
_PING_TIMEOUT_SN = 2


def redis_erisilebilir(url: str | None, logger=None) -> bool:
    """Redis gerçekten cevap veriyor mu? Bağlantı kurulup PING atılır.

    URL boş/redis olmayan şemadaysa veya redis paketi yoksa False.
    Ping başarısızsa False — çağıran fallback'e düşer.
    """
    if not url or not str(url).startswith("redis"):
        return False
    try:
        import redis as _redis
    except ImportError:
        if logger:
            logger.warning("[redis] `redis` paketi kurulu degil — fallback")
        return False

    try:
        istemci = _redis.from_url(
            str(url),
            socket_connect_timeout=_PING_TIMEOUT_SN,
            socket_timeout=_PING_TIMEOUT_SN,
        )
        istemci.ping()
        return True
    except Exception as e:
        if logger:
            # error değil warning: Redis'siz çalışmak geçerli bir mod (yerel).
            # Yayın'da bu satır görünürse asıl sorun ORADA — deploy env'i eksik.
            logger.warning(f"[redis] {url} yanit vermiyor ({type(e).__name__}) — fallback")
        return False
