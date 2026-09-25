"""Input guardrails — screens customer messages before agent processing."""

import re


class InputGuard:
    """Screens customer messages for PII, prompt injection, and toxicity."""

    # PII patterns
    _CREDIT_CARD = re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b")
    _SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
    _EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
    _PHONE = re.compile(r"\b[\d][\d\s\-]{8,}[\d]\b")

    # Injection patterns
    _INJECTION_HIGH = [
        r"ignore previous instructions",
        r"ignore your instructions",
        r"forget everything",
        r"new instructions:",
        r"system prompt:",
    ]
    _INJECTION_MEDIUM = [
        r"you are now",
        r"pretend you are",
        r"act as",
        r"developer mode",
        r"\bDAN\b",
    ]
    _INJECTION_LOW = [
        r"jailbreak",
        r"bypass",
    ]

    # Toxicity
    _PROFANITY = [
        "fuck", "shit", "ass", "bitch", "damn", "crap", "bastard",
        "dick", "piss", "slut", "whore", "douche", "moron", "idiot",
    ]
    _THREATS = ["kill", "hurt", "destroy", "bomb", "attack", "murder", "stab", "shoot"]
    _HARASSMENT = ["stupid", "worthless", "pathetic", "useless", "incompetent"]

    def detect_pii(self, text: str) -> dict:
        """Detect PII patterns in text."""
        types_found = []
        locations = []

        for name, pattern in [
            ("credit_card", self._CREDIT_CARD),
            ("ssn", self._SSN),
            ("email", self._EMAIL),
            ("phone", self._PHONE),
        ]:
            for match in pattern.finditer(text):
                types_found.append(name)
                locations.append({"type": name, "start": match.start(), "end": match.end()})

        return {"has_pii": bool(types_found), "types_found": list(set(types_found)), "locations": locations}

    def detect_injection(self, text: str) -> dict:
        """Detect prompt injection attempts."""
        lower = text.lower()
        patterns_matched = []
        severity = "low"

        for pattern in self._INJECTION_HIGH:
            if re.search(pattern, lower):
                patterns_matched.append(pattern)
                severity = "high"

        for pattern in self._INJECTION_MEDIUM:
            if re.search(pattern, lower):
                patterns_matched.append(pattern)
                if severity != "high":
                    severity = "medium"

        for pattern in self._INJECTION_LOW:
            if re.search(pattern, lower):
                patterns_matched.append(pattern)

        return {
            "is_injection": bool(patterns_matched),
            "patterns_matched": patterns_matched,
            "severity": severity if patterns_matched else "low",
        }

    def detect_toxicity(self, text: str) -> dict:
        """Detect toxic content."""
        lower = text.lower()
        categories = []
        word_hits = 0
        total_checks = len(self._PROFANITY) + len(self._THREATS) + len(self._HARASSMENT)

        for word in self._PROFANITY:
            if re.search(rf"\b{word}\b", lower):
                if "profanity" not in categories:
                    categories.append("profanity")
                word_hits += 1

        for word in self._THREATS:
            if re.search(rf"\b{word}\b", lower):
                if "threats" not in categories:
                    categories.append("threats")
                word_hits += 1

        for word in self._HARASSMENT:
            if re.search(rf"\b{word}\b", lower):
                if "harassment" not in categories:
                    categories.append("harassment")
                word_hits += 1

        confidence = min(word_hits / 3, 1.0) if word_hits else 0.0

        return {"is_toxic": bool(categories), "categories": categories, "confidence": round(confidence, 2)}

    def check(self, text: str) -> dict:
        """Run all checks and return combined result."""
        pii = self.detect_pii(text)
        injection = self.detect_injection(text)
        toxicity = self.detect_toxicity(text)

        blocked = False
        reason = None

        if injection["is_injection"] and injection["severity"] == "high":
            blocked = True
            reason = "Prompt injection detected (high severity)"
        elif toxicity["is_toxic"] and "threats" in toxicity["categories"]:
            blocked = True
            reason = "Threatening content detected"

        return {
            "blocked": blocked,
            "reason": reason,
            "checks": {"pii": pii, "injection": injection, "toxicity": toxicity},
        }
