"""OrderAgent — specialist for order tracking and delivery questions."""

from langchain_aws import ChatBedrock
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from src.agents.state import AgentState
from src.tools.order_tools import lookup_order, get_order_history
from src.tools.email_tools import send_order_confirmation

ORDER_AGENT_PROMPT = """\
You specialize in order tracking and delivery. You help customers check order status, \
tracking information, estimated delivery dates, and order history.

Rules:
- Use lookup_order when the customer provides an order ID.
- Use get_order_history when the customer asks about past orders or provides their email.
- NEVER guess order information — always use tools to look it up.
- Be concise and include all relevant details (status, carrier, tracking, ETA).
- If an order is not found, ask the customer to verify the order ID."""

TOOLS = [lookup_order, get_order_history, send_order_confirmation]


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
        messages = [SystemMessage(content=ORDER_AGENT_PROMPT)] + list(messages)
    return {"messages": [llm.invoke(messages)]}


def should_continue(state: AgentState) -> str:
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"
    return END


def build_order_agent():
    tool_node = ToolNode(TOOLS)
    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")
    return graph.compile()


class OrderAgent:
    def __init__(self):
        self.graph = build_order_agent()

    def chat(self, message: str, thread_id: str = "default") -> str:
        result = self.graph.invoke({"messages": [HumanMessage(content=message)]})
        for msg in reversed(result["messages"]):
            if isinstance(msg, AIMessage) and not msg.tool_calls:
                return msg.content
        return ""
