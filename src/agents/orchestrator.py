"""Orchestrator — routes customer messages to specialist agents."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_aws import ChatBedrock
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

from src.agents.state import AgentState
from src.agents.specialists.order_agent import OrderAgent
from src.agents.specialists.returns_agent import ReturnsAgent
from src.agents.specialists.product_agent import ProductAgent
from src.agents.specialists.general_agent import GeneralAgent

ROUTER_PROMPT = """\
You are a routing agent. Classify the customer's message into exactly one category and respond with ONLY the category name:

- order: order status, tracking, delivery, shipping questions, order history
- returns: returns, refunds, exchanges, return policy
- product: product info, specs, pricing, availability, recommendations, comparisons
- general: greetings, account questions, complaints, escalation requests, anything else

Respond with a single word: order, returns, product, or general."""

VALID_ROUTES = {"order", "returns", "product", "general"}


def _get_llm():
    
    return ChatBedrock(
        model_id="us.anthropic.claude-sonnet-4-6",
        region_name="us-east-1",
        model_kwargs={"max_tokens": 10, "temperature": 0.0},
    )


def classify_intent(message: str) -> str:
    """Use LLM to classify the message into a route."""
    llm = _get_llm()
    response = llm.invoke([
        SystemMessage(content=ROUTER_PROMPT),
        HumanMessage(content=message),
    ])
    route = response.content.strip().lower().rstrip(".")
    if route in VALID_ROUTES:
        return route
    # Keyword fallback
    msg_lower = message.lower()
    if any(w in msg_lower for w in ["order", "track", "ship", "deliver", "ORD-"]):
        return "order"
    if any(w in msg_lower for w in ["return", "refund", "exchange"]):
        return "returns"
    if any(w in msg_lower for w in ["product", "price", "stock", "recommend"]):
        return "product"
    return "general"


def route_node(state: AgentState) -> dict:
    """Classify and route to the appropriate specialist."""
    last_human = ""
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage):
            last_human = msg.content
            break
    intent = classify_intent(last_human)
    return {"intent": intent}


def specialist_node(state: AgentState) -> dict:
    """Invoke the appropriate specialist agent."""
    intent = state.get("intent", "general")
    last_human = ""
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage):
            last_human = msg.content
            break

    agents = {
        "order": OrderAgent,
        "returns": ReturnsAgent,
        "product": ProductAgent,
        "general": GeneralAgent,
    }
    agent_cls = agents.get(intent, GeneralAgent)
    agent = agent_cls()
    response = agent.chat(last_human)
    return {"messages": [AIMessage(content=response)]}


def build_orchestrator():
    """Build the multi-agent orchestrator graph."""
    graph = StateGraph(AgentState)
    graph.add_node("route", route_node)
    graph.add_node("specialist", specialist_node)
    graph.add_edge(START, "route")
    graph.add_edge("route", "specialist")
    graph.add_edge("specialist", END)
    return graph.compile()


class Orchestrator:
    """Multi-agent orchestrator that routes to specialist agents."""

    def __init__(self):
        self.graph = build_orchestrator()

    def chat(self, message: str, thread_id: str = "default") -> str:
        result = self.graph.invoke({"messages": [HumanMessage(content=message)]})
        for msg in reversed(result["messages"]):
            if isinstance(msg, AIMessage) and not msg.tool_calls:
                return msg.content
        return ""

    def route(self, message: str) -> str:
        """Classify a message without invoking a specialist (for testing)."""
        return classify_intent(message)


# ── Demo ─────────────────────────────────────────
if __name__ == "__main__":
    from rich.console import Console
    from rich.panel import Panel

    console = Console()
    console.print(Panel("[bold cyan]Multi-Agent Orchestrator Demo[/]"))

    orchestrator = Orchestrator()

    test_messages = [
        "Where is my order #12345?",
        "I want to return the headphones I bought last week.",
        "What's the best laptop under $1000?",
        "Hi, I just have a general question about my account.",
    ]

    for msg in test_messages:
        console.print(f"\n[bold]Customer:[/] {msg}")
        route = orchestrator.route(msg)
        console.print(f"[dim]Routed to:[/] [yellow]{route}[/]")
        response = orchestrator.chat(msg)
        console.print(Panel(response, title="Response", border_style="green"))
