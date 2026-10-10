"""Zamanlayıcıları (APScheduler) yalnız TEK süreçte çalıştırmak için lider seçimi.

Sorun (KOD-02 / PERF-01 / OPS-02): gunicorn 8 worker açar ve her worker `create_app()`
içinde zamanlayıcıları başlatırdı → gece yedeği, erken uyarı, digest ve K-Radar özeti
8 kez çalışıyordu.

Çözüm: PostgreSQL oturum-düzeyi advisory lock. Kilit, süreç ömrü boyunca açık tutulan
AYRI bir bağlantıda alınır; süreç ölünce (max-requests yenilemesi dahil) bağlantı kapanır
ve kilit otomatik düşer. Kilidi alamayan worker'lar arka planda periyodik dener; lider
gidince bir başkası devralır.

Kilit veritabanı bazlıdır: Yayın/Test/Demo farklı DB kullandığı için birbirini engellemez.

Env:
    SCHEDULER_ENABLED=false  → bu süreçte zamanlayıcı ASLA başlamaz (ayrı worker vb.)
"""
from __future__ import annotations

import os
import threading
from typing import Callable

# Rastgele sabit anahtar (bigint). Aynı DB'deki başka advisory lock kullanımlarıyla çakışmasın.
_LOCK_KEY = 7_412_009_318_442
_RETRY_SECONDS = 30

_leader_conn = None  # kilidi tutan bağlantı — referans bırakılırsa kilit düşer


def scheduler_enabled() -> bool:
    return (os.environ.get("SCHEDULER_ENABLED", "true").strip().lower()
            not in ("0", "false", "no", "off"))


def _try_lock(app) -> bool:
    """Kilidi almayı dener. PostgreSQL dışında (yerel SQLite vb.) tek süreç varsayılır."""
    global _leader_conn
    if _leader_conn is not None:
        return True
    from app.models import db

    with app.app_context():
        engine = db.engine
        if engine.dialect.name != "postgresql":
            return True
        conn = engine.connect().execution_options(isolation_level="AUTOCOMMIT")
        try:
            got = bool(conn.exec_driver_sql(
                "SELECT pg_try_advisory_lock(%s)" % int(_LOCK_KEY)
            ).scalar())
        except Exception:
            conn.close()
            raise
        if got:
            _leader_conn = conn
            return True
        conn.close()
        return False


def run_as_leader(app, start_fn: Callable[[], None]) -> bool:
    """`start_fn`'i yalnız lider süreçte çalıştırır.

    Lider olunamazsa arka planda 30 sn'de bir yeniden dener (lider ölünce devralmak için).
    Döner: şimdi lider olundu mu."""
    if not scheduler_enabled():
        app.logger.info("[scheduler] SCHEDULER_ENABLED=false — bu süreçte zamanlayıcı yok")
        return False

    try:
        if _try_lock(app):
            app.logger.info("[scheduler] Lider süreç (pid=%s) — zamanlayıcılar başlıyor", os.getpid())
            start_fn()
            return True
    except Exception as e:  # DB erişilemiyorsa uygulama açılışı bozulmasın
        app.logger.error("[scheduler] lider kilidi alınamadı: %s", e)

    def _watch():
        import time
        while True:
            time.sleep(_RETRY_SECONDS)
            try:
                if _try_lock(app):
                    app.logger.info(
                        "[scheduler] Lider devralındı (pid=%s) — zamanlayıcılar başlıyor", os.getpid())
                    start_fn()
                    return
            except Exception as e:
                app.logger.warning("[scheduler] lider denemesi başarısız: %s", e)

    threading.Thread(target=_watch, name="scheduler-leader-watch", daemon=True).start()
    return False


def is_leader(app) -> bool:
    """Bu surec su an zamanlayici lideri mi (kilidi tutuyor ya da PG disi tek surec)."""
    if not scheduler_enabled():
        return False
    if _leader_conn is not None:
        return True
    try:
        from app.models import db
        with app.app_context():
            return db.engine.dialect.name != "postgresql"
    except Exception:
        return False
