"""Phase 10: Data quality checks and health scoring."""

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class QualityScore:
    """Result of quality check."""
    passed: bool
    score: float  # 0.0 to 1.0
    issues: list[str]


class DataQualityChecker:
    """Rule-based quality checks."""

    def __init__(self, min_length: int = 10, max_length: int = 10000):
        self.min_length = min_length
        self.max_length = max_length
        self.rules = [
            self._check_length,
            self._check_encoding,
            self._check_duplicates,
        ]

    def check(self, content: str, record_id: str, seen_ids: set[str] | None = None) -> QualityScore:
        """Run all checks; return score and issues."""
        issues = []
        for rule in self.rules:
            result = rule(content, record_id, seen_ids or set())
            if not result[0]:
                issues.append(result[1])

        score = max(0.0, 1.0 - len(issues) * 0.3)
        return QualityScore(passed=len(issues) == 0, score=score, issues=issues)

    def _check_length(self, content: str, record_id: str, seen_ids: set[str]) -> tuple[bool, str]:
        """Check content length within bounds."""
        if len(content) < self.min_length:
            return False, f"Content too short ({len(content)} < {self.min_length})"
        if len(content) > self.max_length:
            return False, f"Content too long ({len(content)} > {self.max_length})"
        return True, ""

    def _check_encoding(self, content: str, record_id: str, seen_ids: set[str]) -> tuple[bool, str]:
        """Check for valid UTF-8 and problematic chars."""
        try:
            content.encode("utf-8")
            return True, ""
        except UnicodeEncodeError:
            return False, "Invalid UTF-8 encoding"

    def _check_duplicates(self, content: str, record_id: str, seen_ids: set[str]) -> tuple[bool, str]:
        """Check record_id not seen before."""
        if record_id in seen_ids:
            return False, f"Duplicate record_id: {record_id}"
        return True, ""

    def health_score(self, records: list[tuple[str, str, dict[str, Any]]]) -> dict[str, Any]:
        """Compute overall pipeline health."""
        if not records:
            return {"total": 0, "passed": 0, "failed": 0, "avg_score": 0.0}

        scores = [self.check(content, rid).score for content, rid, _ in records]
        passed = sum(1 for s in scores if s == 1.0)
        return {
            "total": len(records),
            "passed": passed,
            "failed": len(records) - passed,
            "avg_score": sum(scores) / len(scores),
        }
