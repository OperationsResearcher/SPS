# -*- coding: utf-8 -*-
"""score_engine_service saf fonksiyon regresyon testleri (DB gerektirmez).

Koşum:  .venv/Scripts/python.exe -m unittest tests.test_score_engine_pure
"""
import unittest

from app.services.score_engine_service import (
    compute_pg_score,
    _default_weight,
    _resolve_target_for_calculation,
)


class TestComputePgScore(unittest.TestCase):
    def test_increasing_tam(self):
        self.assertEqual(compute_pg_score(100, 100, "Increasing"), 100.0)

    def test_increasing_yari(self):
        self.assertEqual(compute_pg_score(100, 50, "Increasing"), 50.0)

    def test_increasing_ust_clamp(self):
        self.assertEqual(compute_pg_score(100, 150, "Increasing"), 100.0)

    def test_decreasing_daha_iyi(self):
        # Azalan: düşük gerçekleşen daha iyi → 100'e clamp
        self.assertEqual(compute_pg_score(100, 50, "Decreasing"), 100.0)

    def test_decreasing_sifir_gerceklesen(self):
        self.assertEqual(compute_pg_score(100, 0, "Decreasing"), 100.0)

    def test_none_girdi(self):
        self.assertIsNone(compute_pg_score(None, 50))
        self.assertIsNone(compute_pg_score(100, None))

    def test_sifir_hedef(self):
        self.assertIsNone(compute_pg_score(0, 50))


class TestDefaultWeight(unittest.TestCase):
    def test_kardes_yok(self):
        self.assertEqual(_default_weight(None, 0), 100.0)

    def test_acik_agirlik(self):
        self.assertEqual(_default_weight(30, 4), 30.0)

    def test_agirlik_clamp(self):
        self.assertEqual(_default_weight(150, 4), 100.0)

    def test_esit_bolusum(self):
        self.assertEqual(_default_weight(None, 4), 25.0)

    def test_sifir_agirlik_esit_bolusum(self):
        self.assertEqual(_default_weight(0, 5), 20.0)


class TestResolveTarget(unittest.TestCase):
    def test_tek_deger(self):
        self.assertEqual(_resolve_target_for_calculation(20), 20.0)

    def test_aralik_increasing_min(self):
        self.assertEqual(_resolve_target_for_calculation("20-24", "Increasing"), 20.0)

    def test_aralik_decreasing_max(self):
        self.assertEqual(_resolve_target_for_calculation("20-24", "Decreasing"), 24.0)

    def test_negatif_aralik(self):
        self.assertEqual(_resolve_target_for_calculation("-10--2", "Increasing"), -10.0)

    def test_none(self):
        self.assertIsNone(_resolve_target_for_calculation(None))


if __name__ == "__main__":
    unittest.main()
