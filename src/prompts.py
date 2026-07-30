"""Phase 2: Prompt Engineering — Structured prompting with JSON output."""

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.llm_client import call_llm_with_system

# ── Valid intents ────────────────────────────────
VALID_INTENTS = [
    "order_status",
    "return_request",
    "product_question",
    "billing_issue",
    "general",
]

# ── System Prompt ────────────────────────────────
SYSTEM_PROMPT = """\
You are SupportBot, the customer support assistant for ShopSmart, an online e-commerce store.

Rules:
- Be helpful, empathetic, and concise.
- Never make up order information — if you don\'t have details, ask the customer or suggest they check their account.
- Classify the customer\'s intent before responding.
- Your output MUST be valid JSON and nothing else.

Intent categories: order_status, return_request, product_question, billing_issue, general

Output format (strict JSON):
{
  "intent": "<one of the intent categories>",
  "confidence": <float 0.0-1.0>,
  "response": "<your helpful response to the customer>",
  "needs_escalation": <true|false>,
  "escalation_reason": "<reason string or null>"
}"""

# ── Few-Shot Examples ────────────────────────────
FEW_SHOT_EXAMPLES = """\
Here are examples of how to respond:

Customer: "Where is my order #12345? It was supposed to arrive yesterday."
```json
{
  "intent": "order_status",
  "confidence": 0.95,
  "response": "I understand your concern about order #12345. Let me look into that for you. Could you please verify the email address associated with your account so I can pull up the tracking details?",
  "needs_escalation": false,
  "escalation_reason": null
}
```

Customer: "I want to return the shoes I bought last week. They don\'t fit."
```json
{
  "intent": "return_request",
  "confidence": 0.95,
  "response": "I\'m sorry the shoes didn\'t fit! ShopSmart offers free returns within 30 days of delivery. You can start your return by going to My Orders in your account and selecting \'Request Return\'. You\'ll receive a prepaid shipping label.",
  "needs_escalation": false,
  "escalation_reason": null
}
```

Customer: "I was charged twice for my last order and if this isn\'t fixed immediately I\'m calling my lawyer."
```json
{
  "intent": "billing_issue",
  "confidence": 0.92,
  "response": "I sincerely apologize for the duplicate charge. I\'m escalating this to our billing team right now so they can investigate and process a refund for the extra charge.",
  "needs_escalation": true,
  "escalation_reason": "Duplicate charge with legal threat — requires immediate billing team review"
}
```"""


# ── Dataclass ────────────────────────────────────
@dataclass
class SupportResponse:
    intent: str
    confidence: float
    response: str
    needs_escalation: bool
    escalation_reason: Optional[str] = None


# ── PromptTemplate ───────────────────────────────
class PromptTemplate:
    def __init__(self, template: str, variables: list[str]):
        self.template = template
        self.variables = variables

    def format(self, **kwargs) -> str:
        missing = [v for v in self.variables if v not in kwargs]
        if missing:
            raise ValueError(f"Missing template variables: {missing}")
        return self.template.format(**kwargs)


# ── OutputParser ─────────────────────────────────
class OutputParser:
    @staticmethod
    def parse_json(raw: str) -> dict:
        """Extract JSON from LLM output, handling code fences and surrounding text."""
        match = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", raw, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise ValueError(f"No JSON found in output: {raw[:200]}")

    @staticmethod
    def parse_support_response(raw: str) -> SupportResponse:
        """Parse LLM output into SupportResponse with fallback for malformed output."""
        try:
            data = OutputParser.parse_json(raw)
            return SupportResponse(
                intent=data.get("intent", "general"),
                confidence=float(data.get("confidence", 0.0)),
                response=data.get("response", ""),
                needs_escalation=bool(data.get("needs_escalation", False)),
                escalation_reason=data.get("escalation_reason"),
            )
        except (ValueError, json.JSONDecodeError):
            return SupportResponse(
                intent="general",
                confidence=0.0,
                response=raw.strip(),
                needs_escalation=False,
                escalation_reason=None,
            )

    @staticmethod
    def validate_intent(intent: str) -> bool:
        return intent in VALID_INTENTS


# ── Main function ────────────────────────────────
def classify_and_respond(customer_message: str) -> SupportResponse:
    """Compose system prompt + few-shot + customer message, call LLM, parse response."""
    full_system = f"{SYSTEM_PROMPT}\n\n{FEW_SHOT_EXAMPLES}"
    raw = call_llm_with_system(full_system, customer_message)
    return OutputParser.parse_support_response(raw)
