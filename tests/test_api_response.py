# -*- coding: utf-8 -*-
"""app.utils.api_response merkezi yanıt yardımcıları regresyon testleri.

ok/err/paginated sözleşmesi (success bayrağı, durum kodu, sayfalama matematiği)
API tüketicileri için kararlı kalmalı.
Koşum: .venv/Scripts/python.exe -m unittest tests.test_api_response
"""
import unittest

from flask import Flask

from app.utils.api_response import ok, err, paginated


class _CtxCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = Flask(__name__)
        cls.ctx = cls.app.app_context()
        cls.ctx.push()

    @classmethod
    def tearDownClass(cls):
        cls.ctx.pop()


class TestOk(_CtxCase):
    def test_data_ve_mesaj(self):
        resp, status = ok({"x": 1}, "tamam")
        self.assertEqual(status, 200)
        body = resp.get_json()
        self.assertTrue(body["success"])
        self.assertEqual(body["data"], {"x": 1})
        self.assertEqual(body["message"], "tamam")

    def test_bos_data_anahtar_yok(self):
        resp, status = ok()
        body = resp.get_json()
        self.assertTrue(body["success"])
        self.assertNotIn("data", body)
        self.assertNotIn("message", body)

    def test_ozel_durum_kodu(self):
        _, status = ok({"a": 1}, status=201)
        self.assertEqual(status, 201)


class TestErr(_CtxCase):
    def test_varsayilan_400(self):
        resp, status = err("hata")
        self.assertEqual(status, 400)
        self.assertFalse(resp.get_json()["success"])

    def test_kod_ve_durum(self):
        resp, status = err("yok", 404, "NOT_FOUND")
        self.assertEqual(status, 404)
        self.assertEqual(resp.get_json()["code"], "NOT_FOUND")

    def test_kod_yoksa_anahtar_yok(self):
        resp, _ = err("hata")
        self.assertNotIn("code", resp.get_json())


class TestPaginated(_CtxCase):
    def test_orta_sayfa(self):
        resp, status = paginated([1, 2], 25, 2, 10)
        self.assertEqual(status, 200)
        p = resp.get_json()["pagination"]
        self.assertEqual(p["pages"], 3)        # ceil(25/10)
        self.assertTrue(p["has_next"])
        self.assertTrue(p["has_prev"])

    def test_bos_liste(self):
        resp, _ = paginated([], 0, 1, 10)
        p = resp.get_json()["pagination"]
        self.assertEqual(p["pages"], 0)
        self.assertFalse(p["has_next"])
        self.assertFalse(p["has_prev"])

    def test_son_sayfa_has_next_false(self):
        resp, _ = paginated([1], 21, 3, 10)
        p = resp.get_json()["pagination"]
        self.assertEqual(p["pages"], 3)
        self.assertFalse(p["has_next"])

    def test_ekstra_alan_birlesir(self):
        resp, _ = paginated([], 0, 1, 10, filtre="aktif")
        self.assertEqual(resp.get_json()["filtre"], "aktif")


if __name__ == "__main__":
    unittest.main()
