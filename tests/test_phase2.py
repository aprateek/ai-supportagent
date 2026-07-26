"""Phase 2 tests: verify prompt engineering pipeline — templates, parsing, fallback."""

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.phase2_prompts import (
    SYSTEM_PROMPT,
    FEW_SHOT_EXAMPLES,
    VALID_INTENTS,
    OutputParser,
    SupportResponse,
    PromptTemplate,
    classify_and_respond,
)


class TestPromptTemplate:
    """Test that prompt templates inject variables correctly."""

    def test_format_injects_variables(self):
        template = PromptTemplate("Hello {name}, your order is {status}.", ["name", "status"])
        result = template.format(name="Alice", status="shipped")
        assert "Alice" in result
        assert "shipped" in result

    def test_missing_variable_raises(self):
        template = PromptTemplate("Hello {name}.", ["name"])
        with pytest.raises(ValueError, match="Missing"):
            template.format()


class TestOutputParser:
    """Test JSON extraction and SupportResponse parsing."""

    def test_parse_json_code_fence(self):
        raw = '```json\n{"intent": "order_status", "confidence": 0.9}\n```'
        result = OutputParser.parse_json(raw)
        assert result["intent"] == "order_status"

    def test_parse_json_raw_object(self):
        raw = 'Here is the response: {"intent": "general", "confidence": 0.5}'
        result = OutputParser.parse_json(raw)
        assert result["intent"] == "general"

    def test_parse_support_response_valid(self):
        raw = json.dumps({
            "intent": "return_request",
            "confidence": 0.93,
            "response": "I can help with your return.",
            "needs_escalation": False,
            "escalation_reason": None,
        })
        result = OutputParser.parse_support_response(raw)
        assert isinstance(result, SupportResponse)
        assert result.intent == "return_request"
        assert result.confidence == 0.93

    def test_parse_support_response_fallback(self):
        raw = "This is not valid JSON at all!"
        result = OutputParser.parse_support_response(raw)
        assert result.intent == "general"
        assert result.confidence == 0.0
        assert "not valid JSON" in result.response

    def test_escalation_detected(self):
        raw = json.dumps({
            "intent": "billing_issue",
            "confidence": 0.88,
            "response": "Escalating to billing team.",
            "needs_escalation": True,
            "escalation_reason": "Duplicate charge with legal threat",
        })
        result = OutputParser.parse_support_response(raw)
        assert result.needs_escalation is True
        assert "legal" in result.escalation_reason.lower()


class TestIntentValidation:
    """Test intent taxonomy enforcement."""

    def test_valid_intents_accepted(self):
        for intent in VALID_INTENTS:
            assert OutputParser.validate_intent(intent) is True

    def test_validate_intent_invalid(self):
        assert OutputParser.validate_intent("refund_request") is False
        assert OutputParser.validate_intent("") is False
        assert OutputParser.validate_intent("ORDER_STATUS") is False


class TestSystemPrompt:
    """Test system prompt content."""

    def test_system_prompt_contains_intents(self):
        for intent in VALID_INTENTS:
            assert intent in SYSTEM_PROMPT

    def test_system_prompt_includes_few_shot(self):
        assert "order_status" in FEW_SHOT_EXAMPLES
        assert "return_request" in FEW_SHOT_EXAMPLES
        assert "billing_issue" in FEW_SHOT_EXAMPLES


class TestClassifyAndRespond:
    """Test end-to-end classification flow."""

    def test_returns_support_response(self, mock_bedrock_client, mock_bedrock_response):
        mock_bedrock_client.invoke_model.return_value = mock_bedrock_response(json.dumps({
            "intent": "product_question",
            "confidence": 0.91,
            "response": "Yes, we carry laptop stands!",
            "needs_escalation": False,
            "escalation_reason": None,
        }))
        result = classify_and_respond("Do you sell laptop stands?")
        assert isinstance(result, SupportResponse)
        assert result.intent == "product_question"

    def test_handles_malformed_llm_output(self, mock_bedrock_client, mock_bedrock_response):
        mock_bedrock_client.invoke_model.return_value = mock_bedrock_response(
            "Sorry, I encountered an error processing your request."
        )
        result = classify_and_respond("Help me!")
        assert isinstance(result, SupportResponse)
        assert result.intent == "general"
        assert result.confidence == 0.0
