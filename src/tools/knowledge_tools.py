"""Knowledge search tool — wraps the RAG pipeline."""

from langchain_core.tools import tool


@tool
def search_knowledge_base(query: str) -> str:
    """Search ShopSmart's knowledge base for product info, policies, and FAQs. Use for any factual question about the store."""
    # In mock mode, return canned responses
    q = query.lower()
    if "return" in q:
        return "ShopSmart Return Policy: All items may be returned within 30 days of delivery. Items must be unused and in original packaging."
    if "ship" in q:
        return "Shipping: Standard (5-7 days, free over $35), Expedited (2-3 days, $12.99), Next-Day (1 day, $24.99)."
    if "headphone" in q or "laptop" in q or "product" in q:
        return "We carry electronics, clothing, and home products. Check our catalog for current availability and pricing."
    return "I found some general information in our knowledge base. Could you be more specific about what you're looking for?"
