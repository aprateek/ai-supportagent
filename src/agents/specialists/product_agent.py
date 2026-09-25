"""ProductAgent — specialist for product information and recommendations."""

from langchain_aws import ChatBedrock
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from src.agents.state import AgentState
from src.tools.knowledge_tools import search_knowledge_base

PRODUCT_AGENT_PROMPT = """\
You specialize in product information. You help customers with product details, \
specifications, pricing, availability, comparisons, and recommendations.

Rules:
- Use search_knowledge_base for product details, specs, pricing, and availability.
- Provide accurate information only — never invent product details.
- When comparing products, highlight key differences clearly.
- If a product is not found, suggest similar alternatives or ask for clarification."""

TOOLS = [search_knowledge_base]


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
        messages = [SystemMessage(content=PRODUCT_AGENT_PROMPT)] + list(messages)
    return {"messages": [llm.invoke(messages)]}


def should_continue(state: AgentState) -> str:
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"
    return END


def build_product_agent():
    tool_node = ToolNode(TOOLS)
    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")
    return graph.compile()


class ProductAgent:
    def __init__(self):
        self.graph = build_product_agent()

    def chat(self, message: str, thread_id: str = "default") -> str:
        result = self.graph.invoke({"messages": [HumanMessage(content=message)]})
        for msg in reversed(result["messages"]):
            if isinstance(msg, AIMessage) and not msg.tool_calls:
                return msg.content
        return ""
