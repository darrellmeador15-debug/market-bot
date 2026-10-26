"""Measure local signal-processing latency without claiming market-feed latency.

This module measures elapsed time from the moment an event is received by this
process to the moment a signal decision is produced. It cannot measure how long
a quote took to travel from an exchange/vendor to this process.
"""
from dataclasses import dataclass
from math import ceil
from time import perf_counter_ns
from typing import Callable, Iterable


@dataclass(frozen=True)
class LatencySummary:
    count: int
    minimum_ms: float
    median_ms: float
    p95_ms: float
    p99_ms: float
    maximum_ms: float


def measure_processing_ms(events: Iterable, processor: Callable) -> list[float]:
    """Return local processing duration for each event, in milliseconds."""
    samples = []
    for event in events:
        start = perf_counter_ns()
        processor(event)
        elapsed = (perf_counter_ns() - start) / 1_000_000
        samples.append(elapsed)
    return samples


def summarize_ms(samples: Iterable[float]) -> LatencySummary:
    """Summarize non-negative latency samples; reject empty/invalid samples."""
    values = sorted(float(v) for v in samples)
    if not values:
        raise ValueError("at least one latency sample is required")
    if any(v < 0 for v in values):
        raise ValueError("latency samples cannot be negative")

    def percentile(p: float) -> float:
        # Nearest-rank percentile: deterministic and easy to audit.
        index = max(0, ceil(p * len(values)) - 1)
        return values[min(index, len(values) - 1)]

    n = len(values)
    median = (values[(n - 1) // 2] + values[n // 2]) / 2
    return LatencySummary(
        count=n,
        minimum_ms=round(values[0], 6),
        median_ms=round(median, 6),
        p95_ms=round(percentile(0.95), 6),
        p99_ms=round(percentile(0.99), 6),
        maximum_ms=round(values[-1], 6),
    )
