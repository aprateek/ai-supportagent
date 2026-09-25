"""Phase 11: Prometheus metrics collection."""

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class MetricSnapshot:
    """A single metric measurement."""
    name: str
    value: float
    timestamp: datetime
    labels: dict = field(default_factory=dict)


class MetricsCollector:
    """Collect and export metrics (Prometheus format)."""

    def __init__(self):
        self.counters = defaultdict(int)
        self.gauges = defaultdict(float)
        self.histograms = defaultdict(list)

    def increment_counter(self, name: str, value: int = 1):
        """Increment a counter metric."""
        self.counters[name] += value

    def set_gauge(self, name: str, value: float):
        """Set a gauge metric."""
        self.gauges[name] = value

    def record_histogram(self, name: str, value: float):
        """Record a histogram value."""
        self.histograms[name].append(value)

    def export_prometheus(self) -> str:
        """Export metrics in Prometheus text format."""
        lines = []
        for name, value in self.counters.items():
            lines.append(f"{name}_total {value}")
        for name, value in self.gauges.items():
            lines.append(f"{name} {value}")
        for name, values in self.histograms.items():
            if values:
                lines.append(f"{name}_count {len(values)}")
                lines.append(f"{name}_sum {sum(values)}")
                lines.append(f"{name}_avg {sum(values) / len(values):.2f}")
        return "\n".join(lines)

    def get_p95(self, metric_name: str) -> float | None:
        """Get 95th percentile for a histogram."""
        values = self.histograms.get(metric_name, [])
        if not values:
            return None
        sorted_vals = sorted(values)
        idx = int(len(sorted_vals) * 0.95)
        return sorted_vals[idx]
