# -*- coding: utf-8 -*-
"""app.utils.process_utils saf periyot/parse yardımcıları regresyon testleri.

Veri Giriş Sihirbazı periyot→tarih eşlemesi ve key türetimi kritik —
yanlış son-gün hesabı KPI verisini yanlış periyoda yazar.
Koşum: .venv/Scripts/python.exe -m unittest tests.test_process_utils_period
"""
import unittest
from datetime import date

from app.utils.process_utils import (
    last_day_of_period,
    data_date_to_period_keys,
    parse_optional_date,
    ensure_int_list,
)


class TestLastDayOfPeriod(unittest.TestCase):
    def test_yillik(self):
        self.assertEqual(last_day_of_period(2026, "yillik"), date(2026, 12, 31))

    def test_ceyrek2(self):
        self.assertEqual(last_day_of_period(2026, "ceyrek", 2), date(2026, 6, 30))

    def test_aylik_subat_normal(self):
        self.assertEqual(last_day_of_period(2026, "aylik", 2), date(2026, 2, 28))

    def test_aylik_subat_artik_yil(self):
        self.assertEqual(last_day_of_period(2024, "aylik", 2), date(2024, 2, 29))

    def test_haftalik_ilk_hafta(self):
        self.assertEqual(last_day_of_period(2026, "haftalik", 1, 3), date(2026, 3, 7))

    def test_gunluk(self):
        self.assertEqual(last_day_of_period(2026, "gunluk", 5, 4), date(2026, 4, 5))

    def test_yil_yoksa_none(self):
        self.assertIsNone(last_day_of_period(0, "yillik"))

    def test_tip_yoksa_none(self):
        self.assertIsNone(last_day_of_period(2026, ""))


class TestDataDateToPeriodKeys(unittest.TestCase):
    def test_mayis_ortasi(self):
        keys = data_date_to_period_keys(date(2026, 5, 15), 2026)
        self.assertIn("ceyrek_2", keys)
        self.assertIn("aylik_5", keys)
        self.assertIn("yillik_1", keys)
        self.assertIn("haftalik_3_5", keys)
        self.assertIn("gunluk_15_5", keys)
        self.assertIn("halfyear_1", keys)

    def test_ikinci_yarim_yil(self):
        keys = data_date_to_period_keys(date(2026, 9, 1), 2026)
        self.assertIn("halfyear_2", keys)

    def test_yil_uyusmazligi_bos(self):
        self.assertEqual(data_date_to_period_keys(date(2025, 5, 15), 2026), [])


class TestParseOptionalDate(unittest.TestCase):
    def test_gecerli(self):
        self.assertEqual(parse_optional_date("2026-06-03"), date(2026, 6, 3))

    def test_bos_none(self):
        self.assertIsNone(parse_optional_date(""))

    def test_gecersiz_none(self):
        self.assertIsNone(parse_optional_date("abc"))

    def test_none_girdi(self):
        self.assertIsNone(parse_optional_date(None))


class TestEnsureIntList(unittest.TestCase):
    def test_karisik_liste(self):
        self.assertEqual(ensure_int_list([1, "2", None, ""]), [1, 2])

    def test_tek_deger(self):
        self.assertEqual(ensure_int_list("5"), [5])

    def test_gecersiz_atlanir(self):
        self.assertEqual(ensure_int_list(["x"]), [])

    def test_none_bos_liste(self):
        self.assertEqual(ensure_int_list(None), [])


if __name__ == "__main__":
    unittest.main()
