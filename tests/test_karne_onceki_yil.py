# -*- coding: utf-8 -*-
"""hesapla_onceki_yil_ortalamasi regresyon testleri.

Karne karşılaştırmalarında önceki yıl ortalaması; geçersiz/eksik değerler
sessizce atlanmalı, hiç geçerli değer yoksa None dönmeli.
Koşum: .venv/Scripts/python.exe -m unittest tests.test_karne_onceki_yil
"""
import unittest

from app.utils.karne_hesaplamalar import hesapla_onceki_yil_ortalamasi as ort


class TestOncekiYilOrtalamasi(unittest.TestCase):
    def test_bos_liste_none(self):
        self.assertIsNone(ort([]))

    def test_none_girdi_none(self):
        self.assertIsNone(ort(None))

    def test_sayilar(self):
        self.assertEqual(ort([10, 20, 30]), 20.0)

    def test_string_sayi_karisik(self):
        # geçersiz 'x' atlanır → (10+20)/2
        self.assertEqual(ort(["10", "x", 20]), 15.0)

    def test_hepsi_gecersiz_none(self):
        self.assertIsNone(ort(["a", "b"]))

    def test_tek_deger(self):
        self.assertEqual(ort([5]), 5.0)

    def test_virgullu_string_atlanir(self):
        # float('5,5') → ValueError → atlanır → geçerli yok → None
        self.assertIsNone(ort(["5,5"]))

    def test_float_degerler(self):
        self.assertEqual(ort([2.5, 7.5]), 5.0)


if __name__ == "__main__":
    unittest.main()
