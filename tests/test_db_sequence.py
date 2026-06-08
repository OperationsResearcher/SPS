# -*- coding: utf-8 -*-
"""db_sequence saf yardımcıları regresyon testleri (PK-duplicate tespiti + identifier guard).
Koşum: .venv/Scripts/python.exe -m unittest tests.test_db_sequence
"""
import unittest

from app.utils.db_sequence import is_pk_duplicate, _validate_identifier


class TestIsPkDuplicate(unittest.TestCase):
    def test_pkey_eslesme(self):
        err = Exception('duplicate key value violates unique constraint "kpi_data_pkey"')
        self.assertTrue(is_pk_duplicate(err, "kpi_data"))

    def test_generic_arti_tablo(self):
        err = Exception("duplicate key value violates unique constraint on processes")
        self.assertTrue(is_pk_duplicate(err, "processes"))

    def test_ilgisiz_hata(self):
        self.assertFalse(is_pk_duplicate(Exception("connection refused"), "kpi_data"))

    def test_bos_tablo_generic(self):
        self.assertTrue(is_pk_duplicate(Exception("duplicate key value violates unique constraint"), ""))


class TestValidateIdentifier(unittest.TestCase):
    def test_gecerli(self):
        self.assertEqual(_validate_identifier("kpi_data", "table"), "kpi_data")

    def test_tire_reddedilir(self):
        with self.assertRaises(ValueError):
            _validate_identifier("kpi-data", "table")

    def test_bosluk_reddedilir(self):
        with self.assertRaises(ValueError):
            _validate_identifier("kpi data", "table")

    def test_sql_injection_reddedilir(self):
        with self.assertRaises(ValueError):
            _validate_identifier("x; DROP TABLE users", "table")

    def test_bos_reddedilir(self):
        with self.assertRaises(ValueError):
            _validate_identifier("", "table")


if __name__ == "__main__":
    unittest.main()
