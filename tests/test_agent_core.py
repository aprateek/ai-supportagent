"""Phase 4 tests: verify the LangGraph agent loop — state, routing, retry safety."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.agents.state import AgentState


class TestAgentState:
    """Test agent state definition."""

    def test_state_has_required_fields(self):
        state: AgentState = {
            "messages": [],
            "intent": "",
            "order_data": None,
            "context": "",
            "needs_escalation": False,
            "retry_count": 0,
            "customer_id": None,
        }
        assert state["retry_count"] == 0
        assert state["needs_escalation"] is False
        assert isinstance(state["messages"], list)


class TestShouldContinue:
    """Test the routing logic."""

    def test_ends_when_no_tool_calls(self):
        from src.agents.agent import _should_continue
        from langchain_core.messages import AIMessage
        state = {"messages": [AIMessage(content="Here is your answer.")], "retry_count": 0}
        assert _should_continue(state) == "end"

    def test_routes_to_tools_when_tool_calls(self):
        from src.agents.agent import _should_continue
        from langchain_core.messages import AIMessage
        msg = AIMessage(content="", tool_calls=[{"name": "lookup_order", "args": {"order_id": "ORD-123"}, "id": "1"}])
        state = {"messages": [msg], "retry_count": 0}
        assert _should_continue(state) == "tools"

    def test_stops_at_max_retries(self):
        from src.agents.agent import _should_continue, MAX_RETRIES
        from langchain_core.messages import AIMessage
        msg = AIMessage(content="", tool_calls=[{"name": "lookup_order", "args": {}, "id": "1"}])
        state = {"messages": [msg], "retry_count": MAX_RETRIES}
        assert _should_continue(state) == "end"


class TestUpdateState:
    """Test post-tool state updates."""

    def test_increments_retry_count(self):
        from src.agents.agent import _update_state
        from langchain_core.messages import AIMessage
        state = {"messages": [AIMessage(content="tool result")], "retry_count": 1}
        updates = _update_state(state)
        assert updates["retry_count"] == 2

    def test_detects_escalation(self):
        from src.agents.agent import _update_state
        from langchain_core.messages import AIMessage
        state = {"messages": [AIMessage(content="Escalation created for customer X")], "retry_count": 0}
        updates = _update_state(state)
        assert updates.get("needs_escalation") is True
