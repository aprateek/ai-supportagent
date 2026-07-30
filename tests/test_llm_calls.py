"""Tests: Verify LLM calling patterns work correctly with mocked Bedrock."""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


class TestBasicResponse:
    """Test call_llm returns a non-empty parsed string."""

    def test_basic_response_non_empty(self, mock_bedrock_client, mock_bedrock_response):
        mock_bedrock_client.invoke_model.return_value = mock_bedrock_response(
            "I can help you with your order. Please provide your order number."
        )
        from src.llm_client import call_llm
        result = call_llm("Where is my order?")
        assert result
        assert isinstance(result, str)
        assert len(result) > 0

    def test_customer_query_keywords(self, mock_bedrock_client, mock_bedrock_response):
        mock_bedrock_client.invoke_model.return_value = mock_bedrock_response(
            "I understand you're concerned about your order status. Let me help you track it."
        )
        from src.llm_client import call_llm
        result = call_llm("My order hasn't arrived yet")
        assert "order" in result.lower()


class TestStreaming:
    """Test streaming response assembly."""

    def test_streaming_returns_complete(self, mock_bedrock_client, mock_streaming_response):
        mock_bedrock_client.invoke_model_with_response_stream.return_value = mock_streaming_response(
            ["Here are ", "3 tips: ", "1. Compare prices. ", "2. Read reviews. ", "3. Check return policy."]
        )
        from src.phase1_basic_llm import call_llm_streaming
        result = call_llm_streaming("List 3 shopping tips")
        assert "tips" in result.lower() or "Compare" in result
        assert len(result) > 20


class TestSystemPrompt:
    """Test system + user prompt separation."""

    def test_system_prompt_respected(self, mock_bedrock_client, mock_bedrock_response):
        mock_bedrock_client.invoke_model.return_value = mock_bedrock_response(
            "I'd be happy to help with your return! Our policy allows returns within 30 days."
        )
        from src.llm_client import call_llm_with_system
        result = call_llm_with_system(
            "You are ShopSmart's support agent.",
            "I want to return my shoes."
        )
        assert result
        # Verify the system prompt was actually sent in the request
        call_args = mock_bedrock_client.invoke_model.call_args
        body = json.loads(call_args[1]["body"])
        assert "system" in body
        assert "ShopSmart" in body["system"]
