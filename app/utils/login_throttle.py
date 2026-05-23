"""Login throttle / account lock (Sprint 19.2).

Brute force koruması:
- N başarısız login → account 15 dk lock
- Lock memory cache'de tutulur (production'da Redis önerilir)
- IP bazlı + email bazlı çift sınır
"""
from __future__ import annotations

import time
from collections import defaultdict, deque
from threading import Lock
from typing import Optional


# Konfigürasyon
MAX_ATTEMPTS_PER_EMAIL = 5
MAX_ATTEMPTS_PER_IP = 10
LOCKOUT_DURATION_SEC = 900  # 15 dakika
WINDOW_SEC = 600  # 10 dk pencere

# State
_attempts_email: dict[str, deque] = defaultdict(lambda: deque())
_attempts_ip: dict[str, deque] = defaultdict(lambda: deque())
_locks: dict[str, float] = {}  # email_or_ip → lock_until_ts
_lock = Lock()


def _purge_old(dq: deque, now: float) -> None:
    """Pencere dışındaki kayıtları at."""
    while dq and dq[0] < now - WINDOW_SEC:
        dq.popleft()


def is_locked(email: str, ip: str) -> tuple[bool, Optional[int]]:
    """Hesap veya IP kilitli mi?

    Returns:
        (locked, remaining_sec)
    """
    now = time.time()
    with _lock:
        for key in (email.lower(), ip):
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
    now = time.time()
    email_lc = (email or "").lower()
    with _lock:
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
    with _lock:
        _attempts_email.pop(email.lower(), None)
        _locks.pop(email.lower(), None)


def get_stats(email: str, ip: str) -> dict:
    """Debug için durum bilgisi."""
    now = time.time()
    with _lock:
        return {
            "email_attempts": len(_attempts_email.get(email.lower(), [])),
            "ip_attempts": len(_attempts_ip.get(ip, [])),
            "email_locked_until": _locks.get(email.lower()),
            "ip_locked_until": _locks.get(ip),
            "now": now,
        }
