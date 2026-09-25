"""GuardrailsManager — orchestrates input/output guards with human-in-the-loop gates."""

from src.guardrails.input_guard import InputGuard
from src.guardrails.output_guard import OutputGuard


class GuardrailsManager:
    """Coordinates all guardrails and human-in-the-loop escalation."""

    def __init__(self, human_review_callback=None):
        self.input_guard = InputGuard()
        self.output_guard = OutputGuard()
        self._human_review_callback = human_review_callback
        self._pending_reviews: list[dict] = []

    def screen_input(self, text: str) -> dict:
        """Screen incoming customer message. Returns action dict."""
        result = self.input_guard.check(text)

        if result["blocked"]:
            return {
                "action": "block",
                "reason": result["reason"],
                "response": "I'm sorry, but I'm unable to process that message. "
                "Please rephrase your request and I'll be happy to help.",
                "details": result,
            }

        if result["checks"]["pii"]["has_pii"]:
            return {
                "action": "warn",
                "reason": "PII detected in message",
                "warning": "It looks like you've shared sensitive personal information. "
                "For your security, please avoid sharing credit card numbers, "
                "SSNs, or other sensitive data in chat.",
                "details": result,
            }

        if result["checks"]["injection"]["is_injection"]:
            return {
                "action": "flag",
                "reason": "Possible injection attempt",
                "details": result,
            }

        return {"action": "allow", "details": result}

    def screen_output(self, text: str) -> dict:
        """Screen outgoing agent response. Returns action dict."""
        result = self.output_guard.check(text)

        if result["flagged"] and "forbidden_content" in result["reasons"]:
            self._request_human_review(text, "forbidden_content", result)
            return {
                "action": "hold",
                "reason": "Response contains forbidden content — held for review",
                "filtered": result["filtered"],
                "details": result,
            }

        if result["filtered"] != result["original"]:
            return {
                "action": "redact",
                "reason": "PII redacted from response",
                "filtered": result["filtered"],
                "details": result,
            }

        if result["flagged"]:
            return {
                "action": "flag",
                "reason": "Response flagged for quality concerns",
                "filtered": result["filtered"],
                "details": result,
            }

        return {"action": "allow", "filtered": result["filtered"], "details": result}

    def _request_human_review(self, text: str, reason: str, details: dict) -> None:
        """Queue a response for human review."""
        review_item = {"text": text, "reason": reason, "details": details, "status": "pending"}
        self._pending_reviews.append(review_item)
        if self._human_review_callback:
            self._human_review_callback(review_item)

    def get_pending_reviews(self) -> list[dict]:
        """Return all pending human review items."""
        return [r for r in self._pending_reviews if r["status"] == "pending"]

    def approve_review(self, index: int) -> dict:
        """Approve a pending review item."""
        pending = self.get_pending_reviews()
        if 0 <= index < len(pending):
            pending[index]["status"] = "approved"
            return {"action": "allow", "filtered": pending[index]["text"]}
        return {"action": "error", "reason": "Invalid review index"}

    def reject_review(self, index: int) -> dict:
        """Reject a pending review item."""
        pending = self.get_pending_reviews()
        if 0 <= index < len(pending):
            pending[index]["status"] = "rejected"
            return {"action": "block", "reason": "Rejected by human reviewer"}
        return {"action": "error", "reason": "Invalid review index"}

    def process_message(self, text: str) -> dict:
        """Full pipeline: screen input, return action for the agent layer."""
        return self.screen_input(text)

    def process_response(self, text: str) -> dict:
        """Full pipeline: screen output, return filtered response."""
        return self.screen_output(text)
