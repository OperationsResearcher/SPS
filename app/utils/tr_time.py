"""Türkiye saati yardımcıları (HATA-21).

Container TZ'si UTC olduğunda `date.today()` TR saatiyle 00:00-03:00 arasında bir önceki
günü verir; o gün girilen PG verisi `as_of` filtresinde dışlanır ve 1 Ocak'ta yıl çözümü kayar.
"""
from datetime import date, datetime
from zoneinfo import ZoneInfo

TR_TZ = ZoneInfo("Europe/Istanbul")


def now_tr() -> datetime:
    """Europe/Istanbul saatinde, tz-aware şimdi."""
    return datetime.now(TR_TZ)


def today_tr() -> date:
    """Europe/Istanbul takvimine göre bugün."""
    return now_tr().date()
