# -*- coding: utf-8 -*-
"""Numeric helpers — KpiData.actual_value / target_value String kolonları için
güvenli float dönüşümü."""
from __future__ import annotations
from typing import Any, Optional


def safe_float(val: Any) -> Optional[float]:
    """String veya sayıyı float'a çevirir; başarısızsa None.

    KpiData.actual_value ve target_value `String(100)` tip — sayısal işlem
    yapmadan önce bu helper'dan geçmeli, aksi halde TypeError patlar.
    """
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip().replace(',', '.')
    if not s:
        return None
    try:
        return float(s)
    except (ValueError, TypeError):
        return None
