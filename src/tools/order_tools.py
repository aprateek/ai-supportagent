"""Simulated order management tools."""

from langchain_core.tools import tool

ORDERS_DB = {
    "ORD-12345": {"order_id": "ORD-12345", "status": "shipped", "carrier": "FedEx",
                  "tracking_number": "FX-789456123", "eta": "2026-05-04",
                  "items": [{"name": "Wireless Noise-Cancelling Headphones", "qty": 1, "price": 149.99}]},
    "ORD-67890": {"order_id": "ORD-67890", "status": "processing", "carrier": "N/A",
                  "tracking_number": "N/A", "eta": "2026-05-08",
                  "items": [{"name": "USB-C Laptop Docking Station", "qty": 1, "price": 89.99},
                            {"name": "Smart LED Desk Lamp", "qty": 2, "price": 59.99}]},
    "ORD-11111": {"order_id": "ORD-11111", "status": "delivered", "carrier": "UPS",
                  "tracking_number": "UPS-111222333", "eta": "2026-04-28",
                  "items": [{"name": "Men\'s Classic Fit Cotton T-Shirt", "qty": 3, "price": 24.99}]},
    "ORD-22222": {"order_id": "ORD-22222", "status": "cancelled", "carrier": "N/A",
                  "tracking_number": "N/A", "eta": "N/A",
                  "items": [{"name": "Bamboo Desk Organizer Set", "qty": 1, "price": 29.99}]},
    "ORD-33333": {"order_id": "ORD-33333", "status": "returning", "carrier": "USPS",
                  "tracking_number": "USPS-333444555", "eta": "2026-05-06",
                  "items": [{"name": "Women\'s Waterproof Hiking Jacket", "qty": 1, "price": 119.99},
                            {"name": "Stainless Steel French Press", "qty": 1, "price": 34.99}]},
}

CUSTOMER_ORDERS = {
    "alice@example.com": ["ORD-12345", "ORD-11111", "ORD-22222"],
    "bob@example.com": ["ORD-67890", "ORD-33333"],
}


def _format_order(order: dict) -> str:
    items_str = "\n".join(
        f"  - {item['name']} (x{item['qty']}) ${item['price']:.2f}"
        for item in order["items"]
    )
    return (f"Order: {order['order_id']}\nStatus: {order['status']}\n"
            f"Carrier: {order['carrier']}\nTracking: {order['tracking_number']}\n"
            f"ETA: {order['eta']}\nItems:\n{items_str}")


@tool
def lookup_order(order_id: str) -> str:
    """Look up an order by its order ID. Returns order status, carrier, tracking number, ETA, and items."""
    order = ORDERS_DB.get(order_id)
    if not order:
        return f"Order not found: {order_id}"
    return _format_order(order)


@tool
def get_order_history(customer_email: str) -> str:
    """Get the last 3 orders for a customer by their email address."""
    order_ids = CUSTOMER_ORDERS.get(customer_email)
    if not order_ids:
        return f"No orders found for {customer_email}"
    results = []
    for oid in order_ids[:3]:
        order = ORDERS_DB.get(oid)
        if order:
            results.append(_format_order(order))
    return "\n\n---\n\n".join(results)
