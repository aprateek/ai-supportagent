"""Phase 12: Pydantic schemas for API requests/responses."""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Any, Optional


class ChatRequest(BaseModel):
    """Incoming chat message."""
    session_id: str = Field(..., description="Unique session ID")
    message: str = Field(..., min_length=1, max_length=5000, description="User message")
    context: Optional[dict[str, Any]] = Field(default=None, description="Optional context")


class ChatResponse(BaseModel):
    """Outgoing chat response."""
    session_id: str
    agent_response: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    timestamp: datetime
    sources: list[str] = Field(default_factory=list)


class SessionInfo(BaseModel):
    """Session metadata."""
    session_id: str
    created_at: datetime
    last_message_at: datetime
    message_count: int
    user_id: Optional[str] = None
