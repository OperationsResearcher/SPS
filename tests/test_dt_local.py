# -*- coding: utf-8 -*-
import unittest
from datetime import date, datetime, timezone

from app.utils.dt_local import format_istanbul, isoformat_utc, to_istanbul


class TestDtLocal(unittest.TestCase):
    def test_naive_utc_isoformat_z(self):
        dt = datetime(2026, 9, 8, 9, 29, 0)
        self.assertTrue(isoformat_utc(dt).endswith("Z"))
        self.assertIn("09:29:00", isoformat_utc(dt))

    def test_naive_utc_istanbul_display(self):
        dt = datetime(2026, 9, 8, 9, 29, 0)
        self.assertEqual(format_istanbul(dt), "08.09.2026 12:29")
        self.assertEqual(to_istanbul(dt).hour, 12)

    def test_aware_utc(self):
        dt = datetime(2026, 9, 8, 9, 29, 0, tzinfo=timezone.utc)
        self.assertEqual(format_istanbul(dt), "08.09.2026 12:29")

    def test_date_only_no_shift(self):
        self.assertEqual(isoformat_utc(date(2021, 12, 31)), "2021-12-31")
        self.assertEqual(format_istanbul(date(2021, 12, 31)), "31.12.2021")

    def test_none(self):
        self.assertIsNone(isoformat_utc(None))
        self.assertIsNone(format_istanbul(None))


if __name__ == "__main__":
    unittest.main()
