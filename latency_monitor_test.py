import unittest

from latency_monitor import measure_processing_ms, summarize_ms


class LatencyMonitorTests(unittest.TestCase):
    def test_measures_each_event(self):
        seen = []
        samples = measure_processing_ms([1, 2, 3], seen.append)
        self.assertEqual(seen, [1, 2, 3])
        self.assertEqual(len(samples), 3)
        self.assertTrue(all(v >= 0 for v in samples))

    def test_summary_percentiles(self):
        summary = summarize_ms(range(1, 101))
        self.assertEqual(summary.count, 100)
        self.assertEqual(summary.minimum_ms, 1)
        self.assertEqual(summary.median_ms, 50.5)
        self.assertEqual(summary.p95_ms, 95)
        self.assertEqual(summary.p99_ms, 99)
        self.assertEqual(summary.maximum_ms, 100)

    def test_empty_samples_rejected(self):
        with self.assertRaises(ValueError):
            summarize_ms([])

    def test_negative_samples_rejected(self):
        with self.assertRaises(ValueError):
            summarize_ms([1, -0.1])


if __name__ == "__main__":
    unittest.main()
