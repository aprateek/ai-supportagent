"""Eval module — evaluation framework for the SupportAgent."""

import json
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.eval.evaluator import Evaluator, EvalResult
from src.eval.llm_judge import LLMJudge
from src.eval.reporter import Reporter


def load_test_cases(path: Optional[str] = None) -> list[dict]:
    """Load test cases from JSON file."""
    if path is None:
        path = str(Path(__file__).parent / "test_cases.json")
    with open(path) as f:
        return json.load(f)


__all__ = ["Evaluator", "EvalResult", "LLMJudge", "Reporter", "load_test_cases"]
