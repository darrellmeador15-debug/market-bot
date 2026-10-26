"""Tests for conservative market-data quality gates."""
import unittest
from datetime import datetime, timedelta, timezone
from data_quality import check_bar_quality, can_issue_signal


class DataQualityTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        self.good = dict(timestamp=self.now - timedelta(seconds=2), now=self.now,
                         max_age_seconds=6, price=10.0, open_price=9.8,
                         high=10.2, low=9.7, volume=12000)

    def test_fresh_valid_bar_passes(self):
        result = check_bar_quality(**self.good)
        self.assertTrue(result["ok"])
        self.assertTrue(can_issue_signal(result))

    def test_stale_bar_fails_closed(self):
        args = dict(self.good)
        args["timestamp"] = self.now - timedelta(seconds=6.1)
        result = check_bar_quality(**args)
        self.assertIn("stale_bar", result["problems"])
        self.assertFalse(can_issue_signal(result))

    def test_naive_timestamp_fails(self):
        args = dict(self.good)
        args["timestamp"] = datetime(2026, 1, 1, 11, 59, 59)
        result = check_bar_quality(**args)
        self.assertIn("timestamp_missing_timezone", result["problems"])
        self.assertFalse(result["actionable"])

    def test_future_timestamp_fails(self):
        args = dict(self.good)
        args["timestamp"] = self.now + timedelta(seconds=5)
        result = check_bar_quality(**args)
        self.assertIn("timestamp_in_future", result["problems"])

    def test_invalid_ohlcv_fails(self):
        args = dict(self.good)
        args.update(price=-1, high=9, low=10, volume=-4)
        result = check_bar_quality(**args)
        self.assertIn("invalid_price", result["problems"])
        self.assertIn("high_below_low", result["problems"])
        self.assertIn("negative_volume", result["problems"])

    def test_missing_timestamp_fails(self):
        result = check_bar_quality(None, now=self.now, price=10)
        self.assertIn("missing_or_invalid_timestamp", result["problems"])
        self.assertFalse(can_issue_signal(result))

    def test_malformed_result_fails_closed(self):
        self.assertFalse(can_issue_signal(None))
        self.assertFalse(can_issue_signal({"ok": True, "actionable": True, "problems": ["stale_bar"]}))


if __name__ == "__main__":
    unittest.main()
