"""Phase 7 tests: verify multi-agent routing and orchestrator graph."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


class TestRouterFallback:
    """Test the keyword fallback routing (no Bedrock needed)."""

    def test_valid_routes_constant(self):
        from src.agents.orchestrator import VALID_ROUTES
        assert VALID_ROUTES == {"order", "returns", "product", "general"}

    def test_router_prompt_lists_categories(self):
        from src.agents.orchestrator import ROUTER_PROMPT
        for cat in ["order", "returns", "product", "general"]:
            assert cat in ROUTER_PROMPT


class TestClassifyIntent:
    """Test intent classification with mocked LLM."""

    @patch("src.agents.orchestrator._get_llm")
    def test_classify_order(self, mock_llm):
        from src.agents.orchestrator import classify_intent
        resp = MagicMock()
        resp.content = "order"
        mock_llm.return_value.invoke.return_value = resp
        assert classify_intent("Where is ORD-123?") == "order"

    @patch("src.agents.orchestrator._get_llm")
    def test_classify_returns(self, mock_llm):
        from src.agents.orchestrator import classify_intent
        resp = MagicMock()
        resp.content = "returns"
        mock_llm.return_value.invoke.return_value = resp
        assert classify_intent("I want a refund") == "returns"

    @patch("src.agents.orchestrator._get_llm")
    def test_invalid_route_falls_back_to_keyword(self, mock_llm):
        from src.agents.orchestrator import classify_intent
        resp = MagicMock()
        resp.content = "not_a_valid_route"  # LLM returns garbage
        mock_llm.return_value.invoke.return_value = resp
        # Falls back to keyword matching — "return" keyword → returns
        assert classify_intent("I want to return this") == "returns"

    @patch("src.agents.orchestrator._get_llm")
    def test_fallback_defaults_to_general(self, mock_llm):
        from src.agents.orchestrator import classify_intent
        resp = MagicMock()
        resp.content = "garbage"
        mock_llm.return_value.invoke.return_value = resp
        assert classify_intent("hello there") == "general"
