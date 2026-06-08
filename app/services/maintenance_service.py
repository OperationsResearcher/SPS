"""Bakım modu: ortam, DB bayragi ve acil erisim."""

from __future__ import annotations

import threading
import time

from flask import Flask

from app.models import db
from app.models.system_setting import SystemSetting

KEY_MAINTENANCE = "maintenance_mode"
_TRUTHY = frozenset({"1", "true", "yes", "on"})
_DEFAULT_DB_CACHE_TTL_SECONDS = 5.0
_CACHE_LOCK = threading.Lock()
_MAINTENANCE_CACHE_VALUE: bool | None = None
_MAINTENANCE_CACHE_EXPIRES_AT = 0.0


def _truthy(s: str | None) -> bool:
    if s is None:
        return False
    return str(s).strip().lower() in _TRUTHY


def maintenance_override_off(app: Flask) -> bool:
    return bool(app.config.get("MAINTENANCE_OVERRIDE_OFF"))


def maintenance_env_force(app: Flask) -> bool:
    return bool(app.config.get("MAINTENANCE_ENV_FORCE"))


def _maintenance_db_cache_ttl(app: Flask) -> float:
    raw_ttl = app.config.get(
        "MAINTENANCE_DB_CACHE_TTL_SECONDS",
        _DEFAULT_DB_CACHE_TTL_SECONDS,
    )
    try:
        ttl = float(raw_ttl)
    except (TypeError, ValueError):
        return _DEFAULT_DB_CACHE_TTL_SECONDS
    return ttl if ttl >= 0 else 0.0


def _invalidate_maintenance_cache() -> None:
    global _MAINTENANCE_CACHE_VALUE, _MAINTENANCE_CACHE_EXPIRES_AT
    with _CACHE_LOCK:
        _MAINTENANCE_CACHE_VALUE = None
        _MAINTENANCE_CACHE_EXPIRES_AT = 0.0


def maintenance_db_enabled(app: Flask, force_refresh: bool = False) -> bool:
    global _MAINTENANCE_CACHE_VALUE, _MAINTENANCE_CACHE_EXPIRES_AT
    ttl = _maintenance_db_cache_ttl(app)
    now = time.monotonic()

    if not force_refresh and ttl > 0:
        with _CACHE_LOCK:
            if (
                _MAINTENANCE_CACHE_VALUE is not None
                and now < _MAINTENANCE_CACHE_EXPIRES_AT
            ):
                return _MAINTENANCE_CACHE_VALUE

    row = SystemSetting.query.filter_by(key=KEY_MAINTENANCE).first()
    value = _truthy(row.value) if row else False

    if ttl > 0:
        with _CACHE_LOCK:
            _MAINTENANCE_CACHE_VALUE = value
            _MAINTENANCE_CACHE_EXPIRES_AT = now + ttl

    return value


def maintenance_active(app: Flask) -> bool:
    """Bakim sayfasi gosterilmeli mi (istek bazli)."""
    if app.testing:
        return False
    if maintenance_override_off(app):
        return False
    if maintenance_env_force(app):
        return True
    try:
        return maintenance_db_enabled(app)
    except Exception as e:
        db.session.rollback()
        import logging; logging.getLogger(__name__).warning(f"[maintenance_active] DB kontrol hatası: {e}")
        return False


def set_maintenance_db(enabled: bool) -> None:
    row = SystemSetting.query.filter_by(key=KEY_MAINTENANCE).first()
    val = "true" if enabled else "false"
    if row:
        row.value = val
    else:
        db.session.add(SystemSetting(key=KEY_MAINTENANCE, value=val))
    db.session.commit()
    _invalidate_maintenance_cache()


def maintenance_status_for_admin(app: Flask) -> dict:
    """Yonetim paneli API."""
    db_en = False
    try:
        db_en = maintenance_db_enabled(app, force_refresh=True)
    except Exception as e:
        db.session.rollback()
        import logging; logging.getLogger(__name__).warning(f"[maintenance_status_for_admin] DB kontrol hatası: {e}")
    env_f = maintenance_env_force(app)
    ov = maintenance_override_off(app)
    return {
        "active": maintenance_active(app),
        "db_enabled": db_en,
        "env_force": env_f,
        "override_off": ov,
        "can_toggle_db": not env_f and not ov,
    }
