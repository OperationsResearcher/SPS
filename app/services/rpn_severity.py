# -*- coding: utf-8 -*-
"""RPN şiddet sınıflaması — tek kaynak (T1 / hesap-doğruluk 2026-07-23).

Eşikler (kullanıcı kararı 5C):
  >= 16 → critical
  >= 10 → high
  >=  5 → medium
  else  → low

Özet kartlardaki ``high_risk_count`` = critical + high (rpn >= 10).
"""
from __future__ import annotations

from typing import Optional

RPN_CRITICAL = 16
RPN_HIGH = 10
RPN_MEDIUM = 5


def classify_rpn(rpn: Optional[int | float]) -> str:
    if rpn is None:
        return "low"
    try:
        v = int(rpn)
    except (TypeError, ValueError):
        return "low"
    if v >= RPN_CRITICAL:
        return "critical"
    if v >= RPN_HIGH:
        return "high"
    if v >= RPN_MEDIUM:
        return "medium"
    return "low"


def is_high_or_critical(rpn: Optional[int | float]) -> bool:
    """Özet 'yüksek risk' sayacı — critical + high."""
    return classify_rpn(rpn) in ("critical", "high")
