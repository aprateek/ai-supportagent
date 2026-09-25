"""Output guardrails — filters agent responses before sending to customer."""

import re


class OutputGuard:
    """Filters agent responses for PII leakage, hallucination markers, and unsafe content."""

    _CREDIT_CARD = re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b")
    _SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
    _EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
    _PHONE = re.compile(r"\b[\d][\d\s\-]{8,}[\d]\b")

    _HALLUCINATION_MARKERS = [
        "as an ai language model",
        "i don't have access to real",
        "i cannot actually",
        "i'm just an ai",
        "in my training data",
    ]

    _FORBIDDEN_TOPICS = [
        "competitor",
        "lawsuit",
        "internal policy",
        "employee name",
        "salary",
        "confidential",
    ]

    def redact_pii(self, text: str) -> str:
        """Replace detected PII with redaction markers."""
        text = self._CREDIT_CARD.sub("[REDACTED_CC]", text)
        text = self._SSN.sub("[REDACTED_SSN]", text)
        text = self._EMAIL.sub("[REDACTED_EMAIL]", text)
        text = self._PHONE.sub("[REDACTED_PHONE]", text)
        return text

    def check_hallucination(self, text: str) -> dict:
        """Check for hallucination markers in agent output."""
        lower = text.lower()
        markers_found = [m for m in self._HALLUCINATION_MARKERS if m in lower]
        return {"has_hallucination_markers": bool(markers_found), "markers": markers_found}

    def check_forbidden_content(self, text: str) -> dict:
        """Check for forbidden topics that shouldn't be in responses."""
        lower = text.lower()
        found = [topic for topic in self._FORBIDDEN_TOPICS if topic in lower]
        return {"has_forbidden_content": bool(found), "topics": found}

    def check(self, text: str) -> dict:
        """Run all output checks and return filtered text with metadata."""
        redacted = self.redact_pii(text)
        hallucination = self.check_hallucination(redacted)
        forbidden = self.check_forbidden_content(redacted)

        flagged = hallucination["has_hallucination_markers"] or forbidden["has_forbidden_content"]
        reasons = []
        if hallucination["has_hallucination_markers"]:
            reasons.append("hallucination_markers")
        if forbidden["has_forbidden_content"]:
            reasons.append("forbidden_content")

        return {
            "original": text,
            "filtered": redacted,
            "flagged": flagged,
            "reasons": reasons,
            "checks": {"hallucination": hallucination, "forbidden": forbidden},
        }
