"""Evaluator — runs test cases against the agent and scores results."""

import time
from dataclasses import dataclass, field


@dataclass
class EvalResult:
    test_id: str
    passed: bool
    route_correct: bool
    tools_correct: bool
    relevance_score: float
    correctness_score: float
    latency_ms: float
    response_text: str
    category: str = ""


# Pre-recorded mock responses for mock_mode
_MOCK_RESPONSES = {
    "order": "Your order {order_id} is currently being processed. You can track its status in your account.",
    "returns": "Our return policy allows returns within 30 days of purchase. Items must be in original condition.",
    "product": "Here are the details for the product you asked about. Let me know if you need more information.",
    "general": "Hello! I'm happy to help you today. How can I assist you?",
}


class Evaluator:
    """Runs eval test cases against the orchestrator."""

    def __init__(self, orchestrator=None, mock_mode: bool = True):
        self.orchestrator = orchestrator
        self.mock_mode = mock_mode

    def run_single(self, test_case: dict) -> EvalResult:
        """Run a single test case and return scored result."""
        start = time.time()

        if self.mock_mode:
            route = self._mock_route(test_case["input"])
            response = _MOCK_RESPONSES.get(route, _MOCK_RESPONSES["general"])
        else:
            route = self.orchestrator.route(test_case["input"])
            response = self.orchestrator.chat(test_case["input"])

        latency_ms = (time.time() - start) * 1000

        route_correct = route == test_case["expected_route"]
        tools_correct = True  # In mock mode, assume tools are correct
        contains_pass = all(
            kw.lower() in response.lower() for kw in test_case.get("expected_contains", [])
        )

        relevance_score = 4.0 if route_correct else 2.0
        correctness_score = 4.0 if contains_pass else 2.0

        passed = route_correct and contains_pass

        return EvalResult(
            test_id=test_case["id"],
            passed=passed,
            route_correct=route_correct,
            tools_correct=tools_correct,
            relevance_score=relevance_score,
            correctness_score=correctness_score,
            latency_ms=latency_ms,
            response_text=response,
            category=test_case.get("category", ""),
        )

    def run_all(self, test_cases: list[dict]) -> list[EvalResult]:
        """Run all test cases and return results."""
        return [self.run_single(tc) for tc in test_cases]

    def _mock_route(self, message: str) -> str:
        """Simple keyword-based routing for mock mode."""
        lower = message.lower()
        if any(w in lower for w in ["order", "track", "ship", "deliver", "ord-"]):
            return "order"
        if any(w in lower for w in ["return", "refund", "exchange", "damaged", "replacement"]):
            return "returns"
        if any(w in lower for w in ["product", "price", "stock", "laptop", "phone", "specs", "compare", "charger", "iphone", "samsung", "airpods", "sony"]):
            return "product"
        return "general"
