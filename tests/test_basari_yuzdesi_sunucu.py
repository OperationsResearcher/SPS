# -*- coding: utf-8 -*-
"""Başarı yüzdesi yalnız sunucu motorundan (Faz 1.1, A2)."""
import re
from pathlib import Path

import pytest

from app.services.score_engine_service import achievement

KOK = Path(__file__).resolve().parent.parent


@pytest.mark.xfail(reason="KalDer P10 farkı: ana projede surec.js hâlâ istemcide yüzde hesaplıyor (computeKpiYearlyMetrics); sunucu achievement() tek kaynağa taşıma iş kararı bekliyor (docs/kontrol/KALDER-KARNE-MOTORU-KIYAS.md)", strict=False)
def test_surec_js_yuzde_hesaplamiyor():
    src = (KOK / "ui/static/platform/js/surec.js").read_text("utf-8")
    govde = src[src.index("function computeKpiYearlyMetrics"):src.index("function healthBand")]
    assert "k.achievement" in govde
    assert not re.search(r"Math\.(min|round)\([^;]*\*\s*100", govde), "istemcide yüzde formülü geri geldi"


# İstemci formülünün sunucudan ayrıştığı sınır durumlar: tek doğru kaynak achievement().
@pytest.mark.parametrize("actual,target,yon,beklenen", [
    (50, 100, "Increasing", 50.0),
    (150, 100, "Increasing", 100.0),        # üst sınır
    (-5, 100, "Increasing", 0.0),           # alt sınır (istemci negatif üretiyordu)
    (10, 0, "Increasing", None),            # sıfır hedef artanda puanlanmaz
    (10, -5, "Increasing", None),           # negatif hedef puanlanmaz
    (0, 100, "Decreasing", 100.0),          # azalanda gerçek<=0 → tam puan
    (0, 0, "Decreasing", 100.0),
    (5, 0, "Decreasing", 0.0),
    (200, 100, "Decreasing", 50.0),
])
def test_achievement_sinir_durumlari(actual, target, yon, beklenen):
    assert achievement(actual, target, yon) == beklenen
