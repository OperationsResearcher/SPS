# -*- coding: utf-8 -*-
"""_resolve_target_for_calculation regresyon testleri (hedef aralık → yön-bazlı tek değer).
Koşum: .venv/Scripts/python.exe -m unittest tests.test_resolve_target

NOT: Binlik-ayraç ('400.000') davranışı bilinçli dışarıda — score-engine '_parse_float'
'.'yi ondalık sayıyor (400.0), oysa karne parser binlik sayıyor (400000). Bu tutarsızlık
ayrı bir domain kararı olarak raporlandı (otonom turda değiştirilmedi).
"""
import unittest

from app.services.score_engine_service import _resolve_target_for_calculation as resolve


class TestResolveTarget(unittest.TestCase):
    def test_tek_sayisal(self):
        self.assertEqual(resolve(20), 20.0)

    def test_aralik_increasing_min(self):
        self.assertEqual(resolve("20-24", "Increasing"), 20.0)

    def test_aralik_decreasing_max(self):
        self.assertEqual(resolve("20-24", "Decreasing"), 24.0)

    def test_virgul_ondalik(self):
        self.assertEqual(resolve("4,5"), 4.5)

    def test_negatif_aralik_increasing(self):
        self.assertEqual(resolve("-10--2", "Increasing"), -10.0)

    def test_negatif_aralik_decreasing(self):
        self.assertEqual(resolve("-10--2", "Decreasing"), -2.0)

    def test_gecersiz(self):
        self.assertIsNone(resolve("abc"))

    def test_none(self):
        self.assertIsNone(resolve(None))


if __name__ == "__main__":
    unittest.main()
