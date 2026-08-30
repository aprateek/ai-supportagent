"""Action tools — escalation and final response delivery."""

from langchain_core.tools import tool


@tool
def escalate_to_human(reason: str, customer_id: str = "unknown") -> str:
    """Escalate the conversation to a human support agent. Use when the issue is too complex, the customer is upset, or you cannot resolve it."""
    return (f"Escalation created for customer {customer_id}. "
            f"Reason: {reason}. "
            "A human agent will follow up within 15 minutes.")
