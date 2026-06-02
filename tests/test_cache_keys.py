# -*- coding: utf-8 -*-
"""Cache anahtarı format regresyon testleri (invalidation tutarlılığı için).
Koşum: .venv/Scripts/python.exe -m unittest tests.test_cache_keys
"""
import unittest
from app.utils.cache_utils import cache_key_for_model, CACHE_KEYS


class TestCacheKeys(unittest.TestCase):
    def test_model_key_tenantli(self):
        self.assertEqual(cache_key_for_model("Process", 123, tenant_id=1),
                         "model_Process_123_tenant_1")

    def test_model_key_tenantsiz(self):
        self.assertEqual(cache_key_for_model("Process", 123), "model_Process_123")

    def test_vision_score_key(self):
        self.assertEqual(CACHE_KEYS["vision_score"](1, 2026), "vision_score_1_2026")

    def test_process_list_key(self):
        self.assertEqual(CACHE_KEYS["process_list"](5), "process_list_5")

    def test_process_detail_key(self):
        self.assertEqual(CACHE_KEYS["process_detail"](9, 5), "process_9_5")

    def test_kpi_list_key(self):
        self.assertEqual(CACHE_KEYS["kpi_list"](7), "kpi_list_7")

    def test_strategy_user_list_keys(self):
        self.assertEqual(CACHE_KEYS["strategy_list"](3), "strategy_list_3")
        self.assertEqual(CACHE_KEYS["user_list"](3), "user_list_3")


if __name__ == "__main__":
    unittest.main()
