"""Tracer — lightweight span-based tracing for agent execution."""

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Span:
    name: str
    trace_id: str
    span_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    parent_id: Optional[str] = None
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    attributes: dict = field(default_factory=dict)
    events: list = field(default_factory=list)
    status: str = "ok"

    @property
    def duration_ms(self) -> float:
        if self.end_time is None:
            return (time.time() - self.start_time) * 1000
        return (self.end_time - self.start_time) * 1000

    def end(self, status: str = "ok") -> None:
        self.end_time = time.time()
        self.status = status

    def add_event(self, name: str, attributes: Optional[dict] = None) -> None:
        self.events.append({"name": name, "time": time.time(), "attributes": attributes or {}})

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_id": self.parent_id,
            "duration_ms": round(self.duration_ms, 2),
            "status": self.status,
            "attributes": self.attributes,
            "events": self.events,
        }


class Tracer:
    """Collects spans for a single request trace."""

    def __init__(self):
        self._traces: dict[str, list[Span]] = {}

    def start_trace(self, name: str) -> Span:
        """Start a new trace with a root span."""
        trace_id = str(uuid.uuid4())[:12]
        span = Span(name=name, trace_id=trace_id)
        self._traces[trace_id] = [span]
        return span

    def start_span(self, name: str, parent: Span) -> Span:
        """Start a child span under a parent."""
        span = Span(name=name, trace_id=parent.trace_id, parent_id=parent.span_id)
        self._traces.setdefault(parent.trace_id, []).append(span)
        return span

    def end_span(self, span: Span, status: str = "ok") -> None:
        span.end(status)

    def get_trace(self, trace_id: str) -> list[dict]:
        """Get all spans for a trace."""
        return [s.to_dict() for s in self._traces.get(trace_id, [])]

    def get_all_traces(self) -> dict[str, list[dict]]:
        """Get all traces."""
        return {tid: [s.to_dict() for s in spans] for tid, spans in self._traces.items()}
