# -*- coding: utf-8 -*-
"""hesapla_agirlikli_basari_puani regresyon testleri.
Koşum: .venv/Scripts/python.exe -m unittest tests.test_karne_agirlik
"""
import unittest
from app.utils.karne_hesaplamalar import hesapla_agirlikli_basari_puani as agirlikli


class TestAgirlikliBasariPuani(unittest.TestCase):
    def test_integer_agirlik_yuzde(self):
        # agirlik > 1 → /100 normalize: 4 * 0.50 = 2.0
        self.assertEqual(agirlikli(4, 50), 2.0)

    def test_float_agirlik(self):
        self.assertEqual(agirlikli(4, 0.5), 2.0)

    def test_tam_agirlik(self):
        self.assertEqual(agirlikli(5, 100), 5.0)

    def test_sifir_agirlik(self):
        self.assertEqual(agirlikli(3, 0), 0.0)

    def test_none_puan(self):
        self.assertIsNone(agirlikli(None, 50))

    def test_none_agirlik(self):
        self.assertIsNone(agirlikli(4, None))


if __name__ == "__main__":
    unittest.main()
