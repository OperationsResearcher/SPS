"""Forecast service unit testleri (Sprint 46)."""
import pytest

from app.services.forecast_service import _linear_regression, _standard_error


def test_linear_regression_perfect_uptrend():
    xs = [0, 1, 2, 3, 4]
    ys = [10, 20, 30, 40, 50]
    slope, intercept, r_sq = _linear_regression(xs, ys)
    assert abs(slope - 10.0) < 0.01
    assert abs(intercept - 10.0) < 0.01
    assert r_sq > 0.99  # mükemmel fit


def test_linear_regression_flat():
    xs = [0, 1, 2, 3, 4]
    ys = [50, 50, 50, 50, 50]
    slope, intercept, r_sq = _linear_regression(xs, ys)
    assert abs(slope) < 0.01


def test_linear_regression_downtrend():
    xs = [0, 1, 2, 3]
    ys = [100, 80, 60, 40]
    slope, _, _ = _linear_regression(xs, ys)
    assert slope < -10


def test_linear_regression_single_point():
    """Tek nokta — slope 0, intercept = y."""
    slope, intercept, r_sq = _linear_regression([5], [42])
    assert slope == 0.0
    assert intercept == 42.0


def test_linear_regression_two_points():
    slope, intercept, _ = _linear_regression([0, 1], [10, 20])
    assert abs(slope - 10.0) < 0.01


def test_standard_error_perfect_fit():
    """Tam lineer veri → standart hata ≈ 0."""
    xs = [0, 1, 2, 3, 4]
    ys = [10, 20, 30, 40, 50]
    se = _standard_error(xs, ys, 10.0, 10.0)
    assert se < 0.01


def test_standard_error_noisy():
    xs = [0, 1, 2, 3, 4]
    ys = [10, 18, 32, 39, 51]  # ~10x + noise
    slope, intercept, _ = _linear_regression(xs, ys)
    se = _standard_error(xs, ys, slope, intercept)
    assert se > 0  # noise var
    assert se < 5  # ama makul
