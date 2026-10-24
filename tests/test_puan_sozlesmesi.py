# -*- coding: utf-8 -*-
"""Puan sözleşmesi tutarlılığı (Faz 1.2, A7): oran 0-100, bant 1-5."""
from hypothesis import given, settings, strategies as st

from app.services.score_engine_service import achievement
from app.utils.karne_hesaplamalar import hesapla_basari_puani

SAYI = st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
YON = st.sampled_from(["Increasing", "Decreasing", "increasing", "decreasing", "Artan", "Azalan", None])

ARALIKLAR = {1: "0-20", 2: "20-40", 3: "40-60", 4: "60-80", 5: "80-100"}


@settings(max_examples=300, deadline=None)
@given(SAYI, SAYI, YON)
def test_oran_0_100_veya_none(actual, target, yon):
    r = achievement(actual, target, yon or "Increasing")
    assert r is None or 0.0 <= r <= 100.0


@settings(max_examples=200, deadline=None)
@given(SAYI, st.sampled_from(["Increasing", "Decreasing"]))
def test_bant_1_5_veya_none(deger, yon):
    p = hesapla_basari_puani(deger, ARALIKLAR, yon)
    assert p is None or p in (1, 2, 3, 4, 5)


def test_bant_araliksiz_none():
    assert hesapla_basari_puani(50, None) is None
    assert hesapla_basari_puani(None, ARALIKLAR) is None
