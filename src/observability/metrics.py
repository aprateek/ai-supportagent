"""Metrics — collects counters, latencies, and operational metrics."""

import time
from collections import defaultdict
from dataclasses import dataclass, field


class MetricsCollector:
    """Collects and reports operational metrics."""

    def __init__(self):
        self._counters: dict[str, int] = defaultdict(int)
        self._histograms: dict[str, list[float]] = defaultdict(list)
        self._start_times: dict[str, float] = {}

    def increment(self, name: str, value: int = 1) -> None:
        """Increment a counter."""
        self._counters[name] += value

    def record(self, name: str, value: float) -> None:
        """Record a value in a histogram."""
        self._histograms[name].append(value)

    def start_timer(self, name: str) -> None:
        """Start a named timer."""
        self._start_times[name] = time.time()

    def stop_timer(self, name: str) -> float:
        """Stop a named timer and record the duration in ms."""
        if name not in self._start_times:
            return 0.0
        duration_ms = (time.time() - self._start_times.pop(name)) * 1000
        self.record(f"{name}_ms", duration_ms)
        return duration_ms

    def get_counter(self, name: str) -> int:
        return self._counters.get(name, 0)

    def get_histogram_stats(self, name: str) -> dict:
        """Get stats for a histogram: count, min, max, avg, p50, p95, p99."""
        values = self._histograms.get(name, [])
        if not values:
            return {"count": 0}
        sorted_v = sorted(values)
        n = len(sorted_v)
        return {
            "count": n,
            "min": round(sorted_v[0], 2),
            "max": round(sorted_v[-1], 2),
            "avg": round(sum(sorted_v) / n, 2),
            "p50": round(sorted_v[n // 2], 2),
            "p95": round(sorted_v[int(n * 0.95)], 2) if n > 1 else round(sorted_v[-1], 2),
            "p99": round(sorted_v[int(n * 0.99)], 2) if n > 1 else round(sorted_v[-1], 2),
        }

    def summary(self) -> dict:
        """Full metrics summary."""
        return {
            "counters": dict(self._counters),
            "histograms": {name: self.get_histogram_stats(name) for name in self._histograms},
        }

    def reset(self) -> None:
        """Reset all metrics."""
        self._counters.clear()
        self._histograms.clear()
        self._start_times.clear()
