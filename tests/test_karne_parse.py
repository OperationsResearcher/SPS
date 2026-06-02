# -*- coding: utf-8 -*-
"""parse_aralik_degeri regresyon testleri (Türkçe sayı biçimi: '.' binlik, ',' ondalık).

Koşum:  .venv/Scripts/python.exe -m unittest tests.test_karne_parse
"""
import unittest

from app.utils.karne_hesaplamalar import parse_aralik_degeri


class TestParseAralikDegeri(unittest.TestCase):
    def test_tamsayi_aralik(self):
        self.assertEqual(parse_aralik_degeri("40-49"), (40.0, 49.0))

    def test_yuzde(self):
        self.assertEqual(parse_aralik_degeri("%80-89"), (80.0, 89.0))

    def test_binlik_ayrac_nokta(self):
        # Türkçe binlik: 400.000 = 400000
        self.assertEqual(parse_aralik_degeri("400.000-449.000"), (400000.0, 449000.0))

    def test_ondalik_virgul(self):
        # Önceki sürümde "4,5" -> "45" oluyordu (regresyon koruması)
        self.assertEqual(parse_aralik_degeri("4,5-9,5"), (4.5, 9.5))

    def test_binlik_ve_ondalik_karisik(self):
        self.assertEqual(parse_aralik_degeri("1.234,56-2.000,00"), (1234.56, 2000.0))

    def test_tek_deger(self):
        self.assertEqual(parse_aralik_degeri("90"), (90.0, 90.0))

    def test_acik_ust_sinir(self):
        self.assertEqual(parse_aralik_degeri("90-"), (90.0, None))

    def test_bos(self):
        self.assertIsNone(parse_aralik_degeri("-"))
        self.assertIsNone(parse_aralik_degeri(""))


if __name__ == "__main__":
    unittest.main()
