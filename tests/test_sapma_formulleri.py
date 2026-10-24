# -*- coding: utf-8 -*-
"""Sapma formülleri ortak yön + hedef guard'ına bağlı (Faz 1.3, A8)."""
from pathlib import Path

import pytest

from app.services.score_engine_service import adverse_deviation_pct

KOK = Path(__file__).resolve().parent.parent


@pytest.mark.parametrize("actual,target,yon,beklenen", [
    (80, 100, "Increasing", 20.0),      # artan: hedefin %20 altı = kötü
    (120, 100, "Increasing", -20.0),    # hedefin üstü = iyi (negatif)
    (120, 100, "Decreasing", 20.0),     # azalan: hedefin üstü = kötü (eski kod bunu iyi sayıyordu)
    (80, 100, "Decreasing", -20.0),     # azalan: hedefin altı = iyi
    (120, 100, "azalan", 20.0),         # eş anlamlı yön
    (80, 100, None, 20.0),              # yön yoksa artan
])
def test_yon_dogru(actual, target, yon, beklenen):
    assert adverse_deviation_pct(actual, target, yon) == pytest.approx(beklenen)


@pytest.mark.parametrize("actual,target", [(50, 0), (50, -10), (None, 100), (50, None), ("x", 100)])
def test_gecersiz_girdide_none(actual, target):
    assert adverse_deviation_pct(actual, target, "Increasing") is None


def test_servisler_kendi_formulunu_yazmiyor():
    for f in ("app/services/muda_analyzer.py", "app/services/process_deviation_service.py"):
        src = (KOK / f).read_text("utf-8")
        assert "adverse_deviation_pct" in src, f
        assert "- target) / target" not in src and "- target)/target" not in src, f
