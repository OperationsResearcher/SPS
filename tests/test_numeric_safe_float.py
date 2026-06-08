# -*- coding: utf-8 -*-
"""app.utils.numeric.safe_float regresyon testleri.

KpiData.actual_value/target_value String(100) kolonları sayısal işleme
sokulmadan önce buradan geçer — davranış sözleşmesi kilitleniyor.
Koşum: .venv/Scripts/python.exe -m unittest tests.test_numeric_safe_float
"""
import unittest

from app.utils.numeric import safe_float


class TestSafeFloat(unittest.TestCase):
    def test_none(self):
        self.assertIsNone(safe_float(None))

    def test_int(self):
        self.assertEqual(safe_float(5), 5.0)

    def test_float(self):
        self.assertEqual(safe_float(2.5), 2.5)

    def test_turkce_ondalik_virgul(self):
        self.assertEqual(safe_float("3,14"), 3.14)

    def test_negatif_virgul(self):
        self.assertEqual(safe_float("-3,5"), -3.5)

    def test_sayisal_string(self):
        self.assertEqual(safe_float("42"), 42.0)

    def test_bos_string_none(self):
        self.assertIsNone(safe_float(""))

    def test_bosluk_strip(self):
        self.assertEqual(safe_float("  7  "), 7.0)

    def test_gecersiz_metin_none(self):
        self.assertIsNone(safe_float("abc"))

    def test_binlik_ayracli_none(self):
        # Bilinen sınır: '1.000,50' → çoklu nokta → None (binlik ayraç desteklenmez)
        self.assertIsNone(safe_float("1.000,50"))

    def test_bilimsel_gosterim(self):
        self.assertEqual(safe_float("1e3"), 1000.0)

    def test_bool_int_gibi(self):
        # bool, int alt sınıfı → True 1.0 olur (mevcut davranış)
        self.assertEqual(safe_float(True), 1.0)


if __name__ == "__main__":
    unittest.main()
