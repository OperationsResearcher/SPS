"""Bakım modu: ortam, DB bayragi ve acil erisim."""

from __future__ import annotations

from flask import Flask

from app.models import db
from app.models.system_setting import SystemSetting

KEY_MAINTENANCE = "maintenance_mode"
_TRUTHY = frozenset({"1", "true", "yes", "on"})


def _truthy(s: str | None) -> bool:
    if s is None:
        return False
    return str(s).strip().lower() in _TRUTHY


def maintenance_override_off(app: Flask) -> bool:
    return bool(app.config.get("MAINTENANCE_OVERRIDE_OFF"))


def maintenance_env_force(app: Flask) -> bool:
    return bool(app.config.get("MAINTENANCE_ENV_FORCE"))


def maintenance_db_enabled() -> bool:
    row = SystemSetting.query.filter_by(key=KEY_MAINTENANCE).first()
    return _truthy(row.value) if row else False


def maintenance_active(app: Flask) -> bool:
    """Bakim sayfasi gosterilmeli mi (istek bazli)."""
    if app.testing:
        return False
    if maintenance_override_off(app):
        return False
    if maintenance_env_force(app):
        return True
    try:
        return maintenance_db_enabled()
    except Exception:
        db.session.rollback()
        return False


def set_maintenance_db(enabled: bool) -> None:
    row = SystemSetting.query.filter_by(key=KEY_MAINTENANCE).first()
    val = "true" if enabled else "false"
    if row:
        row.value = val
    else:
        db.session.add(SystemSetting(key=KEY_MAINTENANCE, value=val))
    db.session.commit()


def maintenance_status_for_admin(app: Flask) -> dict:
    """Yonetim paneli API."""
    db_en = False
    try:
        db_en = maintenance_db_enabled()
    except Exception:
        db.session.rollback()
    env_f = maintenance_env_force(app)
    ov = maintenance_override_off(app)
    return {
        "active": maintenance_active(app),
        "db_enabled": db_en,
        "env_force": env_f,
        "override_off": ov,
        "can_toggle_db": not env_f and not ov,
    }
