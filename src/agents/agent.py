"""SupportAgent — ReAct agent built with LangGraph."""

import sys
from pathlib import Path

from langchain_aws import ChatBedrock
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from config.settings import AWS_REGION, MAX_TOKENS, MODEL_ID, TEMPERATURE
from src.agents.state import AgentState
from src.prompts import SYSTEM_PROMPT
from src.tools import ALL_TOOLS

MAX_RETRIES = 3

AGENT_SYSTEM_PROMPT = f"""{SYSTEM_PROMPT}

You have access to tools. Use them to look up order information, search the knowledge base, or escalate to a human agent.

Think step by step:
1. Classify the customer's intent.
2. Decide which tool(s) to call, if any.
3. Use the tool results to formulate a helpful response.
4. If you cannot resolve the issue after 3 attempts, escalate to a human agent.

Always be helpful, empathetic, and concise."""


def _get_llm() -> ChatBedrock:
    return ChatBedrock(
        model_id=MODEL_ID,
        region_name=AWS_REGION,
        model_kwargs={
            "max_tokens": MAX_TOKENS,
            "temperature": TEMPERATURE,
        },
    )


def _reason(state: AgentState) -> dict:
    """Think node — invoke the LLM with tools bound."""
    llm = _get_llm().bind_tools(ALL_TOOLS)
    messages = state["messages"]

    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=AGENT_SYSTEM_PROMPT)] + list(messages)

    response = llm.invoke(messages)
    return {"messages": [response]}


def _should_continue(state: AgentState) -> str:
    """Route after reasoning: call tools or finish."""
    last_message = state["messages"][-1]

    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        retry_count = state.get("retry_count", 0)
        if retry_count >= MAX_RETRIES:
            return "end"
        return "tools"

    return "end"


def _update_state(state: AgentState) -> dict:
    """Post-tool state update — increment retry count, detect escalation."""
    updates: dict = {"retry_count": state.get("retry_count", 0) + 1}

    for msg in reversed(state["messages"]):
        if hasattr(msg, "content") and "Escalation created" in str(msg.content):
            updates["needs_escalation"] = True
            break

    return updates


def build_support_agent() -> StateGraph:
    """Build and compile the LangGraph support agent."""
    tool_node = ToolNode(ALL_TOOLS)

    graph = StateGraph(AgentState)

    graph.add_node("reason", _reason)
    graph.add_node("tools", tool_node)
    graph.add_node("update_state", _update_state)

    graph.set_entry_point("reason")

    graph.add_conditional_edges("reason", _should_continue, {"tools": "tools", "end": END})
    graph.add_edge("tools", "update_state")
    graph.add_edge("update_state", "reason")

    return graph.compile()


class SupportAgent:
    """High-level wrapper around the LangGraph support agent."""

    def __init__(self):
        self.graph = build_support_agent()

    def chat(self, message: str, **initial_state) -> dict:
        """Send a message and get the final agent state."""
        state: AgentState = {
            "messages": [HumanMessage(content=message)],
            "intent": initial_state.get("intent", ""),
            "order_data": initial_state.get("order_data"),
            "context": initial_state.get("context", ""),
            "needs_escalation": initial_state.get("needs_escalation", False),
            "retry_count": initial_state.get("retry_count", 0),
            "customer_id": initial_state.get("customer_id"),
        }
        return self.graph.invoke(state)

    def get_response(self, message: str, **kwargs) -> str:
        """Convenience: send a message and return just the final AI response text."""
        result = self.chat(message, **kwargs)
        for msg in reversed(result["messages"]):
            if isinstance(msg, AIMessage) and not msg.tool_calls:
                return msg.content
        return ""
