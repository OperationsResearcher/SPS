# -*- coding: utf-8 -*-
"""UTC saklanan anların Avrupa/İstanbul gösterimi.

DB'de DateTime genelde naive UTC (timezone=True yok). isoformat() Zsuz
dönünce tarayıcı bunu yerel sanıyor: 12:29 girişi 09:29 görünüyor.

Kural: naive datetime = UTC. Tam saatli gösterim Europe/Istanbul.
Takvim günü (date) kaydırılmaz.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Optional, Union
from zoneinfo import ZoneInfo

ISTANBUL = ZoneInfo("Europe/Istanbul")

DateLike = Union[datetime, date]


def assume_utc(dt: datetime) -> datetime:
    """Naive ise UTC kabul et; aware ise UTC'ye çevir."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def to_istanbul(dt: datetime) -> datetime:
    return assume_utc(dt).astimezone(ISTANBUL)


def isoformat_utc(dt: Optional[DateLike]) -> Optional[str]:
    """JSON API: an için Z'li UTC ISO; salt tarih için YYYY-MM-DD."""
    if dt is None:
        return None
    if isinstance(dt, datetime):
        utc = assume_utc(dt)
        return utc.isoformat().replace("+00:00", "Z")
    if isinstance(dt, date):
        return dt.isoformat()
    return None


def format_istanbul(dt: Optional[DateLike], with_time: bool = True) -> Optional[str]:
    """Kullanıcıya: 08.09.2026 12:29 — with_time=False ise yalnız gün."""
    if dt is None:
        return None
    if isinstance(dt, datetime):
        local = to_istanbul(dt)
        if with_time:
            return local.strftime("%d.%m.%Y %H:%M")
        return local.strftime("%d.%m.%Y")
    if isinstance(dt, date):
        return dt.strftime("%d.%m.%Y")
    return None
