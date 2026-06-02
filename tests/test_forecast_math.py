# -*- coding: utf-8 -*-
"""forecast_service saf regresyon matematiği regresyon testleri.
Koşum: .venv/Scripts/python.exe -m unittest tests.test_forecast_math
"""
import unittest

from app.services.forecast_service import _linear_regression, _standard_error


class TestLinearRegression(unittest.TestCase):
    def test_tam_dogru_y_2x(self):
        slope, intercept, r_sq = _linear_regression([1., 2., 3., 4.], [2., 4., 6., 8.])
        self.assertEqual(slope, 2.0)
        self.assertEqual(intercept, 0.0)
        self.assertEqual(r_sq, 1.0)

    def test_tam_dogru_y_2x_arti_1(self):
        slope, intercept, r_sq = _linear_regression([1., 2., 3., 4.], [3., 5., 7., 9.])
        self.assertEqual((slope, intercept, r_sq), (2.0, 1.0, 1.0))

    def test_duz_cizgi(self):
        # sabit ys → eğim 0, r² 0 (varyans yok)
        self.assertEqual(_linear_regression([1., 2., 3.], [5., 5., 5.]), (0.0, 5.0, 0.0))

    def test_tek_nokta(self):
        self.assertEqual(_linear_regression([1.], [7.]), (0.0, 7.0, 0.0))

    def test_bos(self):
        self.assertEqual(_linear_regression([], []), (0.0, 0.0, 0.0))

    def test_ayni_x(self):
        # tüm x aynı → den_x=0 → eğim 0, intercept y_mean
        self.assertEqual(_linear_regression([2., 2., 2.], [1., 2., 3.]), (0.0, 2.0, 0.0))


class TestStandardError(unittest.TestCase):
    def test_tam_dogru_sifir_hata(self):
        xs, ys = [1., 2., 3., 4.], [2., 4., 6., 8.]
        slope, intercept, _ = _linear_regression(xs, ys)
        self.assertEqual(_standard_error(xs, ys, slope, intercept), 0.0)


if __name__ == "__main__":
    unittest.main()
