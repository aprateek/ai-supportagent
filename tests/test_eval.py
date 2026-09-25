"""Phase 9 tests: verify LLM-judge, evaluator, tracing, and metrics."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


class TestLLMJudge:
    """Test scoring (uses mock fallback when Bedrock unavailable)."""

    def test_scores_in_range(self):
        from src.eval.llm_judge import LLMJudge
        judge = LLMJudge()
        # With no Bedrock, falls back to mock 3-5 range
        score = judge.score_relevance("Where is my order?", "Your order shipped.")
        assert 0.0 <= score <= 5.0

    def test_correctness_in_range(self):
        from src.eval.llm_judge import LLMJudge
        judge = LLMJudge()
        score = judge.score_correctness("30 day return policy", "You can return within 30 days")
        assert 0.0 <= score <= 5.0


class TestEvaluator:
    """Test the eval harness in mock mode."""

    def test_run_single_mock(self):
        from src.eval.evaluator import Evaluator, EvalResult
        ev = Evaluator(mock_mode=True)
        tc = {"id": "t1", "input": "Where is my order?", "expected_route": "order",
              "expected_contains": [], "category": "order_status"}
        result = ev.run_single(tc)
        assert isinstance(result, EvalResult)
        assert result.route_correct is True

    def test_run_all(self):
        from src.eval.evaluator import Evaluator
        ev = Evaluator(mock_mode=True)
        cases = [
            {"id": "t1", "input": "track order ORD-1", "expected_route": "order", "expected_contains": [], "category": "order"},
            {"id": "t2", "input": "return policy?", "expected_route": "returns", "expected_contains": [], "category": "returns"},
        ]
        results = ev.run_all(cases)
        assert len(results) == 2

    def test_load_test_cases(self):
        from src.eval import load_test_cases
        cases = load_test_cases()
        assert len(cases) > 0
        assert "input" in cases[0]
        assert "expected_route" in cases[0]


class TestTracer:
    """Test span-based tracing."""

    def test_trace_and_spans_nest(self):
        from src.observability.tracer import Tracer
        tracer = Tracer()
        trace = tracer.start_trace("request")
        span = tracer.start_span("guard", parent=trace)
        tracer.end_span(span)
        spans = tracer.get_trace(trace.trace_id)
        assert len(spans) == 2
        # child span references parent
        child = [s for s in spans if s["name"] == "guard"][0]
        assert child["parent_id"] == trace.span_id

    def test_span_duration_recorded(self):
        from src.observability.tracer import Tracer
        tracer = Tracer()
        trace = tracer.start_trace("request")
        tracer.end_span(trace)
        spans = tracer.get_trace(trace.trace_id)
        assert spans[0]["duration_ms"] >= 0


class TestMetrics:
    """Test metrics collection and percentiles."""

    def test_counter(self):
        from src.observability.metrics import MetricsCollector
        m = MetricsCollector()
        m.increment("requests")
        m.increment("requests")
        assert m.get_counter("requests") == 2

    def test_histogram_percentiles(self):
        from src.observability.metrics import MetricsCollector
        m = MetricsCollector()
        for v in [100, 200, 300, 400, 500]:
            m.record("latency_ms", v)
        stats = m.get_histogram_stats("latency_ms")
        assert stats["count"] == 5
        assert stats["min"] == 100
        assert stats["max"] == 500
        assert "p95" in stats and "p99" in stats
