"""Reporter — generates evaluation reports from EvalResults."""

import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.eval.evaluator import EvalResult


class Reporter:
    """Generates summary reports from evaluation results."""

    def __init__(self, results: list[EvalResult]):
        self.results = results

    def summary(self) -> dict:
        """Generate summary statistics."""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        route_correct = sum(1 for r in self.results if r.route_correct)

        by_category = defaultdict(lambda: {"total": 0, "passed": 0, "avg_latency_ms": 0.0})
        for r in self.results:
            cat = r.category or "uncategorized"
            by_category[cat]["total"] += 1
            if r.passed:
                by_category[cat]["passed"] += 1
            by_category[cat]["avg_latency_ms"] += r.latency_ms

        for cat in by_category:
            n = by_category[cat]["total"]
            by_category[cat]["avg_latency_ms"] = round(by_category[cat]["avg_latency_ms"] / n, 2)
            by_category[cat]["pass_rate"] = round(by_category[cat]["passed"] / n, 3)

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": round(passed / total, 3) if total else 0,
            "route_accuracy": round(route_correct / total, 3) if total else 0,
            "avg_relevance": round(sum(r.relevance_score for r in self.results) / total, 2) if total else 0,
            "avg_correctness": round(sum(r.correctness_score for r in self.results) / total, 2) if total else 0,
            "avg_latency_ms": round(sum(r.latency_ms for r in self.results) / total, 2) if total else 0,
            "by_category": dict(by_category),
        }

    def print_report(self) -> None:
        """Print formatted report to stdout."""
        s = self.summary()
        print("=" * 60)
        print("  EVALUATION REPORT")
        print("=" * 60)
        print(f"  Total: {s['total']}  |  Passed: {s['passed']}  |  Failed: {s['failed']}")
        print(f"  Pass Rate: {s['pass_rate']*100:.1f}%")
        print(f"  Route Accuracy: {s['route_accuracy']*100:.1f}%")
        print(f"  Avg Relevance: {s['avg_relevance']}/5.0")
        print(f"  Avg Correctness: {s['avg_correctness']}/5.0")
        print(f"  Avg Latency: {s['avg_latency_ms']:.1f}ms")
        print("-" * 60)
        print("  BY CATEGORY:")
        for cat, stats in s["by_category"].items():
            print(f"    {cat}: {stats['passed']}/{stats['total']} passed "
                  f"({stats['pass_rate']*100:.0f}%) | {stats['avg_latency_ms']:.1f}ms avg")
        print("=" * 60)

        # Print failures
        failures = [r for r in self.results if not r.passed]
        if failures:
            print(f"\n  FAILURES ({len(failures)}):")
            for r in failures:
                print(f"    ✗ {r.test_id} — route_ok={r.route_correct}")

    def to_json(self, path: str) -> None:
        """Save report as JSON."""
        report = self.summary()
        report["details"] = [
            {
                "test_id": r.test_id,
                "passed": r.passed,
                "route_correct": r.route_correct,
                "relevance_score": r.relevance_score,
                "correctness_score": r.correctness_score,
                "latency_ms": round(r.latency_ms, 2),
                "category": r.category,
            }
            for r in self.results
        ]
        with open(path, "w") as f:
            json.dump(report, f, indent=2)
