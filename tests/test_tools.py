"""Phase 6 tests: verify tool functions and ALL_TOOLS registry."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.tools import ALL_TOOLS


class TestToolRegistry:
    """Test ALL_TOOLS list."""

    def test_all_tools_count(self):
        assert len(ALL_TOOLS) == 9

    def test_all_tools_are_callable(self):
        for tool in ALL_TOOLS:
            assert callable(tool)


class TestOrderTools:
    """Test order lookup and history tools."""

    def test_lookup_existing_order(self):
        from src.tools.order_tools import lookup_order
        result = lookup_order.invoke({"order_id": "ORD-12345"})
        assert "ORD-12345" in result
        assert "shipped" in result.lower() or "FedEx" in result

    def test_lookup_missing_order(self):
        from src.tools.order_tools import lookup_order
        result = lookup_order.invoke({"order_id": "ORD-99999"})
        assert "not found" in result.lower()

    def test_order_history(self):
        from src.tools.order_tools import get_order_history
        result = get_order_history.invoke({"customer_email": "alice@example.com"})
        assert "ORD-12345" in result

    def test_order_history_unknown_customer(self):
        from src.tools.order_tools import get_order_history
        result = get_order_history.invoke({"customer_email": "nobody@example.com"})
        assert "No orders found" in result


class TestKnowledgeTools:
    """Test knowledge base search."""

    def test_return_policy_search(self):
        from src.tools.knowledge_tools import search_knowledge_base
        result = search_knowledge_base.invoke({"query": "return policy"})
        assert "30 days" in result

    def test_shipping_search(self):
        from src.tools.knowledge_tools import search_knowledge_base
        result = search_knowledge_base.invoke({"query": "shipping cost"})
        assert "Standard" in result or "shipping" in result.lower()


class TestActionTools:
    """Test escalation tool."""

    def test_escalate_returns_confirmation(self):
        from src.tools.action_tools import escalate_to_human
        result = escalate_to_human.invoke({"reason": "customer upset", "customer_id": "alice"})
        assert "Escalation created" in result
        assert "alice" in result


class TestEmailTools:
    """Test email tools return confirmations."""

    def test_send_order_confirmation(self):
        from src.tools.email_tools import send_order_confirmation
        result = send_order_confirmation.invoke({"order_id": "ORD-123", "customer_email": "a@b.com"})
        assert "confirmation" in result.lower()
        assert "a@b.com" in result

    def test_send_return_label(self):
        from src.tools.email_tools import send_return_label
        result = send_return_label.invoke({"order_id": "ORD-123", "customer_email": "a@b.com"})
        assert "return label" in result.lower()
