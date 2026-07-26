"""Shared test fixtures — mocks for Bedrock calls so tests run without AWS credentials."""

import json
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_bedrock_response():
    """Return a factory that builds mock Bedrock invoke_model responses."""
    def _make_response(text: str):
        body_bytes = json.dumps({"content": [{"text": text}]}).encode()
        mock_body = MagicMock()
        mock_body.read.return_value = body_bytes
        return {"body": mock_body}
    return _make_response


@pytest.fixture
def mock_bedrock_client(mock_bedrock_response):
    """Patch boto3 Bedrock client globally."""
    with patch("boto3.client") as mock_client_factory:
        client = MagicMock()
        mock_client_factory.return_value = client
        client._mock_response_factory = mock_bedrock_response
        yield client


@pytest.fixture
def mock_streaming_response():
    """Build a mock streaming response from Bedrock."""
    def _make_stream(chunks: list[str]):
        events = []
        for chunk_text in chunks:
            event = {
                "chunk": {
                    "bytes": json.dumps({
                        "type": "content_block_delta",
                        "delta": {"text": chunk_text}
                    }).encode()
                }
            }
            events.append(event)
        return {"body": events}
    return _make_stream


@pytest.fixture
def mock_embedding():
    """Return a factory that builds mock embedding responses."""
    import numpy as np

    def _make_embedding(dimension: int = 1024):
        vec = np.random.randn(dimension).tolist()
        body_bytes = json.dumps({"embedding": vec}).encode()
        mock_body = MagicMock()
        mock_body.read.return_value = body_bytes
        return {"body": mock_body}
    return _make_embedding
