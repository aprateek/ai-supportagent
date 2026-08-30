"""Conversation memory — persists chat history across sessions as JSON lines."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path


class ConversationMemory:
    """File-backed conversation memory with per-thread JSON lines storage."""

    def __init__(self, storage_path: str = "data/memory"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def _thread_path(self, thread_id: str) -> Path:
        return self.storage_path / f"{thread_id}.jsonl"

    def save_turn(self, thread_id: str, human_msg: str, ai_msg: str, metadata: dict = None) -> None:
        """Append a conversation turn to the thread's history file."""
        turn = {
            "human": human_msg,
            "ai": ai_msg,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {},
        }
        with open(self._thread_path(thread_id), "a") as f:
            f.write(json.dumps(turn) + "\n")

    def get_history(self, thread_id: str, last_n: int = 10) -> list[dict]:
        """Return the last N turns for a thread."""
        path = self._thread_path(thread_id)
        if not path.exists():
            return []
        turns = []
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    turns.append(json.loads(line))
        return turns[-last_n:]

    def summarize_history(self, thread_id: str) -> str:
        """If history > 20 turns, summarize older turns into a context string."""
        path = self._thread_path(thread_id)
        if not path.exists():
            return ""
        turns = []
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    turns.append(json.loads(line))
        if len(turns) <= 20:
            return ""
        summary_parts = []
        for turn in turns[:10]:
            summary_parts.append(f"Customer: {turn['human']}")
            summary_parts.append(f"Agent: {turn['ai']}")
        return "Previous context: " + " | ".join(summary_parts)

    def get_all_threads(self) -> list[str]:
        return [p.stem for p in self.storage_path.glob("*.jsonl")]

    def delete_thread(self, thread_id: str) -> None:
        path = self._thread_path(thread_id)
        if path.exists():
            os.remove(path)

    def search_history(self, query: str, thread_id: str = None) -> list[dict]:
        """Simple keyword search across conversation history."""
        query_lower = query.lower()
        results = []
        threads = [thread_id] if thread_id else self.get_all_threads()
        for tid in threads:
            path = self._thread_path(tid)
            if not path.exists():
                continue
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    turn = json.loads(line)
                    if query_lower in turn["human"].lower() or query_lower in turn["ai"].lower():
                        turn["thread_id"] = tid
                        results.append(turn)
        return results
