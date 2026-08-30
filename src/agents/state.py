"""Agent state definition for the SupportAgent ReAct loop."""

from typing import Annotated, Optional, TypedDict

from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]  # chat history (append-only)
    intent: str  # classified customer intent
    order_data: Optional[dict]  # fetched order info
    context: str  # RAG-retrieved context
    needs_escalation: bool
    retry_count: int  # track retries (max 3)
    customer_id: Optional[str]
