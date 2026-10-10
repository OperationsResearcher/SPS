"""Login throttle / account lock (Sprint 19.2).

Brute force koruması:
- N başarısız login → account 15 dk lock
- IP bazlı + email bazlı çift sınır
- Sayaçlar Redis erişilebilirse Redis'te tutulur (GUV-12): gunicorn çoklu worker'da
  ve worker yenilemelerinde (max-requests) sıfırlanmaz. Redis yoksa süreç içi bellek.
"""
from __future__ import annotations

import hashlib
import time
from collections import defaultdict, deque
from threading import Lock
from typing import Optional
import logging

logger = logging.getLogger(__name__)


# Konfigürasyon
MAX_ATTEMPTS_PER_EMAIL = 5
MAX_ATTEMPTS_PER_IP = 10
LOCKOUT_DURATION_SEC = 900  # 15 dakika
WINDOW_SEC = 600  # 10 dk pencere
_MEM_MAX_KEYS = 10_000  # bellek yolunda sınırsız büyümeyi önler (var olmayan e-postalar)

# State (bellek yolu)
_attempts_email: dict[str, deque] = defaultdict(lambda: deque())
_attempts_ip: dict[str, deque] = defaultdict(lambda: deque())
_locks: dict[str, float] = {}  # email_or_ip → lock_until_ts
_lock = Lock()

# Redis yolu — init_backend() ile açılır
_redis = None


def init_backend(app) -> None:
    """Redis erişilebilirse sayaçları oraya taşır (app factory'den bir kez çağrılır)."""
    global _redis
    _redis = None
    if app.testing:
        return
    from app.utils.redis_health import redis_erisilebilir
    url = app.config.get("RATELIMIT_STORAGE_URL")
    if not (url and str(url).startswith("redis")):
        url = app.config.get("CACHE_REDIS_URL") or app.config.get("REDIS_URL")
    if redis_erisilebilir(url, app.logger):
        import redis
        _redis = redis.from_url(str(url), socket_timeout=1, socket_connect_timeout=1)
        app.logger.info("[login_throttle] Redis backend aktif")
    else:
        app.logger.warning(
            "[login_throttle] Redis erişilemiyor — süreç içi bellek (çoklu worker'da gevşek)")


def _key(kind: str, value: str) -> str:
    return "kk:lt:%s:%s" % (kind, hashlib.sha256((value or "").encode("utf-8")).hexdigest()[:32])


def _purge_old(dq: deque, now: float) -> None:
    """Pencere dışındaki kayıtları at."""
    while dq and dq[0] < now - WINDOW_SEC:
        dq.popleft()


def _mem_prune(now: float) -> None:
    """Sözlükler eşiği aşınca süresi geçmiş kayıtları temizle."""
    for store in (_attempts_email, _attempts_ip):
        if len(store) > _MEM_MAX_KEYS:
            for k in [k for k, dq in store.items() if not dq or dq[-1] < now - WINDOW_SEC]:
                del store[k]
    if len(_locks) > _MEM_MAX_KEYS:
        for k in [k for k, until in _locks.items() if until <= now]:
            del _locks[k]


def is_locked(email: str, ip: str) -> tuple[bool, Optional[int]]:
    """Hesap veya IP kilitli mi?

    Returns:
        (locked, remaining_sec)
    """
    if _redis is not None:
        try:
            remaining = max(
                _redis.ttl(_key("le", (email or "").lower())),
                _redis.ttl(_key("li", ip)),
            )
            return (True, int(remaining)) if remaining > 0 else (False, None)
        except Exception as e:
            logger.error(f"is_locked failed: {e}")
    now = time.time()
    with _lock:
        for key in ((email or "").lower(), ip):
            until = _locks.get(key)
            if until and until > now:
                return True, int(until - now)
            if until and until <= now:
                del _locks[key]
    return False, None


def record_failure(email: str, ip: str) -> tuple[bool, int]:
    """Başarısız login kaydet. Lock tetiklendiyse True döner.

    Returns:
        (locked_now, attempts_in_window)
    """
    email_lc = (email or "").lower()
    if _redis is not None:
        try:
            counts = {}
            for kind, value, limit in (("e", email_lc, MAX_ATTEMPTS_PER_EMAIL),
                                       ("i", ip, MAX_ATTEMPTS_PER_IP)):
                fk = _key("f" + kind, value)
                n = _redis.incr(fk)
                if n == 1:
                    _redis.expire(fk, WINDOW_SEC)
                if n >= limit:
                    _redis.set(_key("l" + kind, value), 1, ex=LOCKOUT_DURATION_SEC)
                counts[kind] = n
            locked = bool(_redis.exists(_key("le", email_lc)) or _redis.exists(_key("li", ip)))
            return locked, int(counts["e"])
        except Exception as e:
            logger.error(f"record_failure failed: {e}")
    now = time.time()
    with _lock:
        _mem_prune(now)
        # Email
        dq_e = _attempts_email[email_lc]
        _purge_old(dq_e, now)
        dq_e.append(now)
        if len(dq_e) >= MAX_ATTEMPTS_PER_EMAIL:
            _locks[email_lc] = now + LOCKOUT_DURATION_SEC

        # IP
        dq_i = _attempts_ip[ip]
        _purge_old(dq_i, now)
        dq_i.append(now)
        if len(dq_i) >= MAX_ATTEMPTS_PER_IP:
            _locks[ip] = now + LOCKOUT_DURATION_SEC

        locked = email_lc in _locks or ip in _locks
        return locked, len(dq_e)


def clear_failures(email: str) -> None:
    """Başarılı login sonrası sayaçları sıfırla."""
    email_lc = (email or "").lower()
    if _redis is not None:
        try:
            _redis.delete(_key("fe", email_lc), _key("le", email_lc))
        except Exception as e:
            logger.error(f"clear_failures failed: {e}")
    with _lock:
        _attempts_email.pop(email_lc, None)
        _locks.pop(email_lc, None)


def get_stats(email: str, ip: str) -> dict:
    """Debug için durum bilgisi (bellek yolu)."""
    now = time.time()
    with _lock:
        return {
            "email_attempts": len(_attempts_email.get(email.lower(), [])),
            "ip_attempts": len(_attempts_ip.get(ip, [])),
            "email_locked_until": _locks.get(email.lower()),
            "ip_locked_until": _locks.get(ip),
            "now": now,
        }
