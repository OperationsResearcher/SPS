# -*- coding: utf-8 -*-
"""entity_exists_in_year regresyon testleri (tarih-egemen plan year doktrini).
Koşum: .venv/Scripts/python.exe -m unittest tests.test_date_sovereign
"""
import unittest
from types import SimpleNamespace

from app.services.date_sovereign import entity_exists_in_year


def _ent(pyid):
    return SimpleNamespace(plan_year_id=pyid)


def _py(pid):
    return SimpleNamespace(id=pid)


class TestEntityExistsInYear(unittest.TestCase):
    def test_entity_none(self):
        self.assertFalse(entity_exists_in_year(None, _py(5)))

    def test_plan_year_none(self):
        self.assertFalse(entity_exists_in_year(_ent(5), None))

    def test_global_entity_her_yil(self):
        # plan_year_id yok → global, her yıl geçerli
        self.assertTrue(entity_exists_in_year(_ent(None), _py(5)))

    def test_ayni_yil(self):
        self.assertTrue(entity_exists_in_year(_ent(5), _py(5)))

    def test_farkli_yil(self):
        self.assertFalse(entity_exists_in_year(_ent(5), _py(3)))

    def test_string_pyid_int_coercion(self):
        self.assertTrue(entity_exists_in_year(_ent("5"), _py(5)))


if __name__ == "__main__":
    unittest.main()
