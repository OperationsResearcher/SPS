# -*- coding: utf-8 -*-
"""
Process Utilities
Süreç yönetimi için yardımcı fonksiyonlar.
Eski proje process_utils adaptasyonu (tenant_id, Process, User, SubStrategy).
"""
import calendar
from datetime import date, datetime

from app.models.process import Process
from app.models.core import User, SubStrategy, Strategy


def last_day_of_period(
    year: int,
    period_type: str,
    period_no: int = 1,
    period_month: int | None = None
) -> date | None:
    """
    Seçilen periyodun son gününü döndürür.
    Veri Giriş Sihirbazı ile girilen veriler bu tarihe kaydedilir.
    """
    if not year or not period_type:
        return None
    pt = (period_type or '').lower().strip()
    pn = int(period_no) if period_no is not None else 1
    pm = int(period_month) if period_month is not None else None
    try:
        if pt == 'yillik':
            return date(year, 12, 31)
        if pt == 'ceyrek':
            month_end = {1: 3, 2: 6, 3: 9, 4: 12}.get(pn, 12)
            _, last = calendar.monthrange(year, month_end)
            return date(year, month_end, last)
        if pt == 'aylik':
            m = max(1, min(12, pn))
            _, last = calendar.monthrange(year, m)
            return date(year, m, last)
        if pt == 'haftalik' and pm is not None:
            m = max(1, min(12, pm))
            _, last = calendar.monthrange(year, m)
            week_ends = [7, 14, 21, 28, last]
            day = week_ends[min(pn - 1, 4)] if 1 <= pn <= 5 else last
            return date(year, m, min(day, last))
        if pt == 'gunluk' and pm is not None:
            m = max(1, min(12, pm))
            _, last = calendar.monthrange(year, m)
            day = max(1, min(pn, last))
            return date(year, m, day)
    except (ValueError, TypeError):
        pass
    return None


def data_date_to_period_keys(d: date, year: int) -> list[str]:
    """
    Bir data_date'ten tüm periyot anahtarlarını türetir.
    Bu sayede veri hangi periyotta girilmiş olursa olsun tüm gösterimlerde görünür.
    """
    if not d or d.year != year:
        return []
    keys = []
    month = d.month
    day = d.day
    quarter = (month - 1) // 3 + 1
    keys.append(f'ceyrek_{quarter}')
    keys.append(f'aylik_{month}')
    keys.append('yillik_1')
    _, last_day = calendar.monthrange(year, month)
    week_in_month = ((day - 1) // 7) + 1
    week_in_month = min(week_in_month, 5)
    keys.append(f'haftalik_{week_in_month}_{month}')
    keys.append(f'gunluk_{day}_{month}')
    return keys


def parse_optional_date(value: object):
    """Tarih string'ini date objesine çevirir."""
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return datetime.strptime(text, '%Y-%m-%d').date()
    except ValueError:
        return None


def ensure_int_list(value: object) -> list:
    """Değeri int listesine çevirir."""
    if value is None:
        return []
    if isinstance(value, list):
        raw = value
    else:
        raw = [value]
    out = []
    for item in raw:
        if item is None:
            continue
        text = str(item).strip()
        if not text:
            continue
        try:
            out.append(int(text))
        except (ValueError, TypeError):
            continue
    return out


def validate_same_tenant_user_ids(tenant_id: int, user_ids: list) -> list:
    """Kullanıcıların aynı tenant'a ait olduğunu doğrular."""
    if not user_ids:
        return []
    ids = ensure_int_list(user_ids)
    users = User.query.filter(User.tenant_id == tenant_id, User.id.in_(ids)).all()
    if len(users) != len(set(ids)):
        raise ValueError('Seçilen kullanıcılar tenant ile uyuşmuyor veya bulunamadı')
    return users


def validate_same_tenant_sub_strategies(tenant_id: int, strategy_ids: list) -> list:
    """Stratejilerin aynı tenant'a ait olduğunu doğrular."""
    if not strategy_ids:
        return []
    ids = ensure_int_list(strategy_ids)
    strategies = (
        SubStrategy.query
        .join(Strategy)
        .filter(Strategy.tenant_id == tenant_id, SubStrategy.id.in_(ids))
        .all()
    )
    if len(strategies) != len(set(ids)):
        raise ValueError('Seçilen stratejiler tenant ile uyuşmuyor veya bulunamadı')
    return strategies


def process_descendant_ids(process_id: int) -> set:
    """Bir sürecin tüm alt süreç (çocuk, torun, ...) id'lerini döndürür."""
    out = set()
    stack = [process_id]
    while stack:
        pid = stack.pop()
        children = Process.query.filter_by(parent_id=pid, is_active=True).all()
        for c in children:
            if c.id not in out:
                out.add(c.id)
                stack.append(c.id)
    return out


def validate_process_parent_id(
    process_id: int | None,
    parent_id_raw,
    tenant_id: int
) -> int | None:
    """Üst süreç (parent_id) geçerli mi kontrol eder."""
    if parent_id_raw is None or parent_id_raw == '' or (
        isinstance(parent_id_raw, list) and not parent_id_raw
    ):
        return None
    try:
        parent_id = int(parent_id_raw) if not isinstance(parent_id_raw, int) else parent_id_raw
    except (ValueError, TypeError):
        return None
    if parent_id <= 0:
        return None
    parent = Process.query.filter_by(id=parent_id, is_active=True).first()
    if not parent or parent.tenant_id != tenant_id:
        raise ValueError('Üst süreç aynı tenant''a ait olmalı ve bulunmalıdır')
    if process_id and parent_id == process_id:
        raise ValueError('Bir süreç kendi üst süreci olamaz')
    if process_id and parent_id in process_descendant_ids(process_id):
        raise ValueError('Üst süreç seçimi döngü oluşturmaz (alt sürecinizi üst süreç yapamazsınız)')
    return parent_id
