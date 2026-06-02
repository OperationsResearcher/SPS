# -*- coding: utf-8 -*-
"""parse_basari_puani_araliklari (JSON aralık tanımı parser) regresyon testleri.
Koşum: .venv/Scripts/python.exe -m unittest tests.test_karne_araliklar
"""
import json
import unittest

from app.utils.karne_hesaplamalar import parse_basari_puani_araliklari as parse


class TestParseBasariAraliklari(unittest.TestCase):
    def test_string_listesi(self):
        self.assertEqual(parse(json.dumps(["0-49", "50-69", "70-100"])),
                         {1: "0-49", 2: "50-69", 3: "70-100"})

    def test_dict(self):
        self.assertEqual(parse(json.dumps({"1": "0-49", "2": "50-100"})),
                         {1: "0-49", 2: "50-100"})

    def test_aralik_obje_listesi(self):
        # {"aralik": "...", "aciklama": "..."} formatından sadece aralık alınır
        data = [{"aralik": "0-49", "aciklama": "kötü"}, {"aralik": "50-100", "aciklama": "iyi"}]
        self.assertEqual(parse(json.dumps(data)), {1: "0-49", 2: "50-100"})

    def test_bos_ve_none(self):
        self.assertEqual(parse(""), {})
        self.assertEqual(parse(None), {})

    def test_gecersiz_json(self):
        self.assertEqual(parse("{bozuk"), {})

    def test_dict_gecersiz_anahtar_atlanir(self):
        self.assertEqual(parse(json.dumps({"a": "0-49", "2": "50-100"})), {2: "50-100"})


if __name__ == "__main__":
    unittest.main()
