"""Email tools — simulated email sending."""

from langchain_core.tools import tool


@tool
def send_order_confirmation(order_id: str, customer_email: str) -> str:
    """Send an order confirmation email to the customer."""
    return f"Order confirmation email sent to {customer_email} for order {order_id}."


@tool
def send_return_label(order_id: str, customer_email: str) -> str:
    """Send a prepaid return shipping label to the customer."""
    return f"Prepaid return label sent to {customer_email} for order {order_id}."


@tool
def send_escalation_notice(reason: str, customer_id: str = "unknown") -> str:
    """Send an escalation notice to the support team."""
    return f"Escalation notice sent to support team. Customer: {customer_id}, Reason: {reason}."
