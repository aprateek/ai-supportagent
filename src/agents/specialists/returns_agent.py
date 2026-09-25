"""ReturnsAgent — specialist for returns, refunds, and exchanges."""

import uuid
from datetime import datetime, timedelta, timezone

from langchain_aws import ChatBedrock
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from src.agents.state import AgentState
from src.tools.knowledge_tools import search_knowledge_base
from src.tools.email_tools import send_return_label


@tool
def create_return(order_id: str, reason: str) -> str:
    """Initiate a return for an order. Provide the order ID and reason for return."""
    return_id = f"RET-{str(uuid.uuid4())[:8].upper()}"
    deadline = (datetime.now(timezone.utc) + timedelta(days=14)).strftime("%Y-%m-%d")
    return (
        f"Return initiated: {return_id}\n"
        f"Status: pending\n"
        f"Order: {order_id}\n"
        f"Reason: {reason}\n"
        f"Deadline: {deadline}"
    )


RETURNS_AGENT_PROMPT = """\
You specialize in returns and refunds. You help customers initiate returns, understand \
return policies, check refund status, and process exchanges.

Rules:
- Use search_knowledge_base to find return policies before answering policy questions.
- Use create_return to initiate a return when the customer confirms they want to return an item.
- Always cite the specific policy when explaining return rules.
- Confirm the order ID and reason before initiating a return.
- After creating a return, provide the return label and deadline."""

TOOLS = [search_knowledge_base, create_return, send_return_label]


def _get_llm():
    return ChatBedrock(
        model_id="us.anthropic.claude-sonnet-4-6",
        region_name="us-east-1",
        model_kwargs={"max_tokens": 1024, "temperature": 0.2},
    )


def agent_node(state: AgentState) -> dict:
    llm = _get_llm().bind_tools(TOOLS)
    messages = state["messages"]
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=RETURNS_AGENT_PROMPT)] + list(messages)
    return {"messages": [llm.invoke(messages)]}


def should_continue(state: AgentState) -> str:
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"
    return END


def build_returns_agent():
    tool_node = ToolNode(TOOLS)
    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")
    return graph.compile()


class ReturnsAgent:
    def __init__(self):
        self.graph = build_returns_agent()

    def chat(self, message: str, thread_id: str = "default") -> str:
        result = self.graph.invoke({"messages": [HumanMessage(content=message)]})
        for msg in reversed(result["messages"]):
            if isinstance(msg, AIMessage) and not msg.tool_calls:
                return msg.content
        return ""
