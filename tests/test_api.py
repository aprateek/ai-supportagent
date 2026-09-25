"""Phase 12: Unit tests — Chat API and schemas.

Trust, but Verify: test_api.py
"""

import pytest
from datetime import datetime
from src.api.schemas import ChatRequest, ChatResponse, SessionInfo


class TestChatRequest:
    def test_valid_chat_request(self):
        req = ChatRequest(
            session_id="sess-123",
            message="Hello, how can I help?",
        )
        assert req.session_id == "sess-123"
        assert req.message == "Hello, how can I help?"

    def test_message_too_short(self):
        with pytest.raises(ValueError):
            ChatRequest(session_id="sess-123", message="")

    def test_message_too_long(self):
        with pytest.raises(ValueError):
            ChatRequest(
                session_id="sess-123",
                message="x" * 5001,
            )


class TestChatResponse:
    def test_valid_chat_response(self):
        resp = ChatResponse(
            session_id="sess-123",
            agent_response="I'm here to help!",
            confidence=0.95,
            timestamp=datetime.utcnow(),
        )
        assert resp.session_id == "sess-123"
        assert resp.confidence == 0.95

    def test_confidence_out_of_range(self):
        with pytest.raises(ValueError):
            ChatResponse(
                session_id="sess-123",
                agent_response="Response",
                confidence=1.5,
                timestamp=datetime.utcnow(),
            )


class TestSessionInfo:
    def test_valid_session_info(self):
        now = datetime.utcnow()
        session = SessionInfo(
            session_id="sess-123",
            created_at=now,
            last_message_at=now,
            message_count=5,
        )
        assert session.session_id == "sess-123"
        assert session.message_count == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--tb=short"])
