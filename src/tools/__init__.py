"""Tools for the SupportAgent."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.tools.order_tools import lookup_order, get_order_history
from src.tools.knowledge_tools import search_knowledge_base
from src.tools.action_tools import escalate_to_human
from src.tools.memory_tools import recall_customer_info, remember_preference
from src.tools.email_tools import send_order_confirmation, send_return_label, send_escalation_notice

ALL_TOOLS = [
    lookup_order,
    get_order_history,
    search_knowledge_base,
    escalate_to_human,
    recall_customer_info,
    remember_preference,
    send_order_confirmation,
    send_return_label,
    send_escalation_notice,
]
