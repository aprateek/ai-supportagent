"""Phase 12: FastAPI application with streaming chat."""

import logging
from datetime import datetime
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.api.schemas import ChatRequest, ChatResponse, SessionInfo
from src.agents.orchestrator import Orchestrator

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure FastAPI app."""
    app = FastAPI(
        title="SupportAgent API",
        description="Multi-agent customer support system",
        version="1.0.0",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Global state
    sessions = {}
    orchestrator = Orchestrator()

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

    @app.post("/chat", response_model=ChatResponse)
    async def chat(request: ChatRequest):
        """Handle chat request (non-streaming)."""
        if request.session_id not in sessions:
            sessions[request.session_id] = {"created_at": datetime.utcnow(), "messages": []}

        session = sessions[request.session_id]
        session["last_message_at"] = datetime.utcnow()
        session["messages"].append({"role": "user", "content": request.message})

        # Route through orchestrator
        response, confidence = orchestrator.route(request.message, session.get("context", {}))
        session["messages"].append({"role": "assistant", "content": response})

        return ChatResponse(
            session_id=request.session_id,
            agent_response=response,
            confidence=confidence,
            timestamp=datetime.utcnow(),
            sources=[],
        )

    @app.get("/sessions/{session_id}", response_model=SessionInfo)
    async def get_session(session_id: str):
        """Get session info."""
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")

        session = sessions[session_id]
        return SessionInfo(
            session_id=session_id,
            created_at=session["created_at"],
            last_message_at=session.get("last_message_at", session["created_at"]),
            message_count=len(session["messages"]),
        )

    @app.get("/metrics")
    async def metrics():
        """Prometheus metrics endpoint."""
        return {"sessions_active": len(sessions), "total_messages": sum(len(s.get("messages", [])) for s in sessions.values())}

    return app


if __name__ == "__main__":
    import uvicorn
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
