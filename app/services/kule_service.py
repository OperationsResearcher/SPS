"""Kule yardımcı sistemi — backend servis katmanı.

Tur YAML dosyalarını yükler, kullanıcı durumlarını yönetir.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml
from flask import current_app

from app.extensions import db
from app.models.tour import UserTourProgress


_TOURS_DIR_NAME = "tours"


def _tours_dir() -> Path:
    """docs/tours/ klasörünün mutlak yolu."""
    root = Path(current_app.root_path).parent
    return root / "docs" / _TOURS_DIR_NAME


def load_tour(tour_key: str) -> Optional[dict]:
    """`docs/tours/<key>.yaml` dosyasını okur, dict olarak döner.

    Yoksa None döner; bozuksa logger'a yazar ve None döner.
    """
    safe_key = "".join(ch for ch in tour_key if ch.isalnum() or ch in ("_", "-"))
    if not safe_key or safe_key != tour_key:
        return None

    path = _tours_dir() / f"{safe_key}.yaml"
    if not path.exists():
        return None

    try:
        with path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except Exception as exc:  # pragma: no cover
        current_app.logger.warning(f"[kule] tour load failed for {tour_key}: {exc}")
        return None

    if not isinstance(data, dict) or data.get("key") != safe_key:
        current_app.logger.warning(f"[kule] tour key mismatch: file={safe_key} content={data.get('key')}")
        return None

    return data


def get_or_create_progress(user_id: int, tour_key: str) -> UserTourProgress:
    """Mevcut kayıt varsa döner, yoksa pending olarak oluşturur."""
    row = UserTourProgress.query.filter_by(user_id=user_id, tour_key=tour_key).first()
    if row:
        return row
    row = UserTourProgress(user_id=user_id, tour_key=tour_key, status="pending")
    db.session.add(row)
    db.session.commit()
    return row


def mark_seen(user_id: int, tour_key: str) -> UserTourProgress:
    row = get_or_create_progress(user_id, tour_key)
    row.seen_count = (row.seen_count or 0) + 1
    db.session.commit()
    return row


def mark_complete(user_id: int, tour_key: str) -> UserTourProgress:
    row = get_or_create_progress(user_id, tour_key)
    row.status = "completed"
    row.completed_at = datetime.utcnow()
    db.session.commit()
    return row


def mark_dismiss(user_id: int, tour_key: str) -> UserTourProgress:
    row = get_or_create_progress(user_id, tour_key)
    row.status = "dismissed"
    row.dismissed_at = datetime.utcnow()
    db.session.commit()
    return row


def restart_tour(user_id: int, tour_key: str) -> UserTourProgress:
    row = get_or_create_progress(user_id, tour_key)
    row.status = "pending"
    row.completed_at = None
    row.dismissed_at = None
    db.session.commit()
    return row


def is_audience_allowed(tour: dict, user_role: Optional[str]) -> bool:
    """Tur audience listesi role uyuyor mu?"""
    audience = tour.get("audience") or []
    if not audience:
        return True
    return (user_role or "") in audience
