"""Karne hesaplama unit testleri (Sprint 5.4).

Audit bulgu: hesapla_basari_puani() formula değişirse tüm tarihsel
karne'ler inconsistent olur — unit test yoktu. Şimdi var.
"""
import pytest

from app.utils.karne_hesaplamalar import (
    hesapla_basari_puani,
    hesapla_agirlikli_basari_puani,
)


# ─── Edge cases ──────────────────────────────────────────────────────────

def test_none_actual_returns_none():
    assert hesapla_basari_puani(None, {1: "0-40", 5: "91-100"}) is None


def test_empty_intervals_returns_none():
    assert hesapla_basari_puani(50, {}) is None
    assert hesapla_basari_puani(50, None) is None


def test_invalid_actual_returns_none():
    assert hesapla_basari_puani("abc", {1: "0-40"}) is None


# ─── Increasing direction (yüksek değer = iyi) ───────────────────────────

@pytest.mark.parametrize("actual,expected", [
    (20, 1),    # 0-40 aralığı → 1
    (50, 2),    # 41-60 aralığı → 2
    (70, 3),    # 61-75 aralığı → 3
    (85, 4),    # 76-90 aralığı → 4
    (95, 5),    # 91-100 aralığı → 5
    (0, 1),     # alt sınır
    (100, 5),   # üst sınır
])
def test_increasing_direction(actual, expected):
    intervals = {1: "0-40", 2: "41-60", 3: "61-75", 4: "76-90", 5: "91-100"}
    assert hesapla_basari_puani(actual, intervals, direction="Increasing") == expected


def test_increasing_above_max_returns_5():
    intervals = {1: "0-40", 5: "91-100"}
    assert hesapla_basari_puani(120, intervals, direction="Increasing") == 5


def test_increasing_below_min_returns_1():
    intervals = {1: "0-40", 5: "91-100"}
    assert hesapla_basari_puani(-5, intervals, direction="Increasing") == 1


# ─── Decreasing direction (düşük değer = iyi) ─────────────────────────────

@pytest.mark.parametrize("actual,expected", [
    (5, 5),     # 0-10 aralığı → 5 (en iyi)
    (25, 4),    # 11-30
    (40, 3),    # 31-50
    (60, 2),    # 51-70
    (90, 1),    # 71-100 (en kötü)
])
def test_decreasing_direction(actual, expected):
    intervals = {5: "0-10", 4: "11-30", 3: "31-50", 2: "51-70", 1: "71-100"}
    assert hesapla_basari_puani(actual, intervals, direction="Decreasing") == expected


def test_decreasing_above_max_returns_1():
    intervals = {5: "0-10", 1: "71-100"}
    assert hesapla_basari_puani(120, intervals, direction="Decreasing") == 1


def test_decreasing_below_min_returns_5():
    intervals = {5: "0-10", 1: "71-100"}
    assert hesapla_basari_puani(-5, intervals, direction="Decreasing") == 5


# ─── Ağırlıklı puan ──────────────────────────────────────────────────────

@pytest.mark.parametrize("score,weight,expected", [
    (5, 0.2, 1.0),     # %20 ağırlık, 5 puan → 1.0
    (3, 0.5, 1.5),     # %50 ağırlık, 3 puan → 1.5
    (4, 25, 1.0),      # 25 (0-100 ölçeği) = 0.25 → 1.0
    (5, 100, 5.0),     # %100 = 1.0 → 5.0
])
def test_weighted_score(score, weight, expected):
    result = hesapla_agirlikli_basari_puani(score, weight)
    assert result is not None
    assert abs(result - expected) < 0.01


def test_weighted_score_none_inputs():
    assert hesapla_agirlikli_basari_puani(None, 0.5) is None
    assert hesapla_agirlikli_basari_puani(5, None) is None


# ─── Snapshot test (regression) ──────────────────────────────────────────
# Bu test'ler formula değişirse failure verir — tarihsel tutarlılık koruması.

SNAPSHOT_CASES = [
    # (actual, intervals, direction, expected_score)
    (50, {1: "0-40", 2: "41-60", 3: "61-75", 4: "76-90", 5: "91-100"}, "Increasing", 2),
    (78, {1: "0-40", 2: "41-60", 3: "61-75", 4: "76-90", 5: "91-100"}, "Increasing", 4),
    (15, {5: "0-10", 4: "11-30", 3: "31-50", 2: "51-70", 1: "71-100"}, "Decreasing", 4),
]


@pytest.mark.parametrize("actual,intervals,direction,expected", SNAPSHOT_CASES)
def test_snapshot_regression(actual, intervals, direction, expected):
    """Tarihsel hesap snapshot'ı — formula değişikliği bunu kırar."""
    assert hesapla_basari_puani(actual, intervals, direction=direction) == expected
