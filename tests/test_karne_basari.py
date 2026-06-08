# -*- coding: utf-8 -*-
"""Karne başarı puanı (1-5) ve aralık kontrolü regresyon testleri.

Koşum:  .venv/Scripts/python.exe -m unittest tests.test_karne_basari
"""
import unittest

from app.utils.karne_hesaplamalar import deger_aralikta_mi, hesapla_basari_puani

# Artan yönlü örnek aralıklar (puan -> aralık)
ARALIK_INC = {1: "0-49", 2: "50-69", 3: "70-79", 4: "80-89", 5: "90-100"}
# Azalan yönlü (düşük iyi): 5=en iyi (düşük), 1=en kötü (yüksek)
ARALIK_DEC = {5: "0-9", 4: "10-19", 3: "20-29", 2: "30-39", 1: "40-100"}


class TestDegerAraliktaMi(unittest.TestCase):
    def test_none_aralik(self):
        self.assertFalse(deger_aralikta_mi(50, None))

    def test_kapali_aralik_icinde(self):
        self.assertTrue(deger_aralikta_mi(50, (40, 60)))

    def test_kapali_aralik_disinda(self):
        self.assertFalse(deger_aralikta_mi(70, (40, 60)))

    def test_sinir_dahil(self):
        self.assertTrue(deger_aralikta_mi(40, (40, 60)))
        self.assertTrue(deger_aralikta_mi(60, (40, 60)))

    def test_acik_ust_sinir(self):
        self.assertTrue(deger_aralikta_mi(1000, (90, None)))
        self.assertFalse(deger_aralikta_mi(50, (90, None)))


class TestHesaplaBasariPuani(unittest.TestCase):
    def test_artan_band_ici(self):
        self.assertEqual(hesapla_basari_puani(95, ARALIK_INC, "Increasing"), 5)
        self.assertEqual(hesapla_basari_puani(75, ARALIK_INC, "Increasing"), 3)
        self.assertEqual(hesapla_basari_puani(45, ARALIK_INC, "Increasing"), 1)

    def test_artan_ust_sinir_asimi(self):
        self.assertEqual(hesapla_basari_puani(105, ARALIK_INC, "Increasing"), 5)

    def test_artan_alt_sinir_alti(self):
        self.assertEqual(hesapla_basari_puani(-5, ARALIK_INC, "Increasing"), 1)

    def test_none_deger(self):
        self.assertIsNone(hesapla_basari_puani(None, ARALIK_INC, "Increasing"))

    def test_bos_aralik(self):
        self.assertIsNone(hesapla_basari_puani(50, {}, "Increasing"))

    def test_azalan_band_ici(self):
        self.assertEqual(hesapla_basari_puani(5, ARALIK_DEC, "Decreasing"), 5)
        self.assertEqual(hesapla_basari_puani(45, ARALIK_DEC, "Decreasing"), 1)

    def test_azalan_ust_sinir_asimi(self):
        self.assertEqual(hesapla_basari_puani(105, ARALIK_DEC, "Decreasing"), 1)


if __name__ == "__main__":
    unittest.main()
