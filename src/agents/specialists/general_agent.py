"""GeneralAgent — handles greetings, general questions, and fallback."""

from langchain_aws import ChatBedrock
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from src.agents.state import AgentState
from src.tools.knowledge_tools import search_knowledge_base
from src.tools.action_tools import escalate_to_human

GENERAL_AGENT_PROMPT = """\
You are a friendly general support assistant for ShopSmart. You handle greetings, \
general questions, account inquiries, and anything that doesn't fit order/return/product categories.

Rules:
- Be warm and helpful for greetings and general questions.
- Use search_knowledge_base for policy or FAQ questions.
- Use escalate_to_human when the customer is frustrated, mentions legal action, or explicitly asks for a human.
- Keep responses concise and offer to help with specific needs."""

TOOLS = [search_knowledge_base, escalate_to_human]


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
        messages = [SystemMessage(content=GENERAL_AGENT_PROMPT)] + list(messages)
    return {"messages": [llm.invoke(messages)]}


def should_continue(state: AgentState) -> str:
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"
    return END


def build_general_agent():
    tool_node = ToolNode(TOOLS)
    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")
    return graph.compile()


class GeneralAgent:
    def __init__(self):
        self.graph = build_general_agent()

    def chat(self, message: str, thread_id: str = "default") -> str:
        result = self.graph.invoke({"messages": [HumanMessage(content=message)]})
        for msg in reversed(result["messages"]):
            if isinstance(msg, AIMessage) and not msg.tool_calls:
                return msg.content
        return ""
