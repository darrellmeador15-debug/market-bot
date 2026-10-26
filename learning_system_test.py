import json
import tempfile
import unittest
from pathlib import Path

from learning_system import analyze_setups, load_memory, propose_review, record_event, summarize_trades


class LearningSystemTests(unittest.TestCase):
    def test_persistent_trade_memory_round_trip(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "memory.jsonl"
            record_event({"event": "TRADE_CLOSED", "symbol": "ABC", "pnl": 12.5}, path)
            rows = load_memory(path)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["symbol"], "ABC")
            self.assertIn("recorded_at", rows[0])

    def test_summary_and_drawdown(self):
        stats = summarize_trades([{"pnl": 10}, {"pnl": -4}, {"pnl": 6}])
        self.assertEqual(stats["closed_trades"], 3)
        self.assertEqual(stats["wins"], 2)
        self.assertEqual(stats["losses"], 1)
        self.assertEqual(stats["realized_pnl"], 12)
        self.assertEqual(stats["max_drawdown_from_trade_sequence"], 4)

    def test_setup_analysis_and_no_auto_updates(self):
        trades = [
            {"pnl": 5, "setup": "breakout"},
            {"pnl": -2, "setup": "breakout"},
            {"pnl": 3, "setup": "pullback"},
        ]
        groups = analyze_setups(trades)
        self.assertEqual(groups["breakout"]["closed_trades"], 2)
        review = propose_review(trades, minimum_trades=3)
        self.assertEqual(review["status"], "REVIEW_READY")
        self.assertFalse(review["automatic_strategy_change"])
        self.assertFalse(review["live_orders_enabled"])

    def test_insufficient_data_is_not_declared_ready(self):
        review = propose_review([{"pnl": 2}], minimum_trades=30)
        self.assertEqual(review["status"], "COLLECT_MORE_DATA")
        self.assertFalse(review["automatic_strategy_change"])

    def test_malformed_memory_is_reported(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "memory.jsonl"
            path.write_text("{bad json}\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_memory(path)


if __name__ == "__main__":
    unittest.main()
