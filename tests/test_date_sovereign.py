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


class TestMirrorPlanYearFromSource(unittest.TestCase):
    def test_none_args(self):
        from app.services.date_sovereign import mirror_plan_year_from_source
        self.assertFalse(mirror_plan_year_from_source(None, _ent(1)))
        self.assertFalse(mirror_plan_year_from_source(_ent(1), None))

    def test_zaten_hizali(self):
        from app.services.date_sovereign import mirror_plan_year_from_source
        m = _ent(None)
        self.assertFalse(mirror_plan_year_from_source(m, _ent(None)))
        self.assertIsNone(m.plan_year_id)
        m2 = _ent(4)
        self.assertFalse(mirror_plan_year_from_source(m2, _ent(4)))
        self.assertEqual(m2.plan_year_id, 4)

    def test_aktif_yil_damgasi_kaynak_null_olur(self):
        from app.services.date_sovereign import mirror_plan_year_from_source
        m = _ent(1)  # 2026 damgası
        self.assertTrue(mirror_plan_year_from_source(m, _ent(None)))
        self.assertIsNone(m.plan_year_id)

    def test_kaynak_yilina_cekilir(self):
        from app.services.date_sovereign import mirror_plan_year_from_source
        m = _ent(1)
        self.assertTrue(mirror_plan_year_from_source(m, _ent(2)))
        self.assertEqual(m.plan_year_id, 2)


if __name__ == "__main__":
    unittest.main()
