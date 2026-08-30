"""Memory tools — recall and remember customer information."""

from langchain_core.tools import tool


@tool
def recall_customer_info(customer_id: str) -> str:
    """Recall known information about a customer from previous interactions."""
    # Mock — return canned profile
    profiles = {
        "alice@example.com": "Known customer. Prefers email communication. Has 3 orders on file.",
        "bob@example.com": "Known customer. Previously had a return issue resolved successfully.",
    }
    return profiles.get(customer_id, f"No previous information found for {customer_id}.")


@tool
def remember_preference(customer_id: str, preference: str) -> str:
    """Save a customer preference for future interactions."""
    return f"Preference saved for {customer_id}: {preference}"
