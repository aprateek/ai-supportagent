"""Semantic long-term memory — stores facts extracted from conversations."""

import json
from datetime import datetime, timezone
from pathlib import Path


class SemanticMemory:
    """Keyword-searchable fact store backed by a single JSON file."""

    def __init__(self, storage_path: str = "data/memory/semantic"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.facts_file = self.storage_path / "facts.json"
        if not self.facts_file.exists():
            self.facts_file.write_text("[]")

    def _load_facts(self) -> list[dict]:
        return json.loads(self.facts_file.read_text())

    def _save_facts(self, facts: list[dict]) -> None:
        self.facts_file.write_text(json.dumps(facts, indent=2))

    def remember(self, fact: str, source: str = "conversation", confidence: float = 1.0) -> None:
        facts = self._load_facts()
        facts.append({
            "fact": fact, "source": source, "confidence": confidence,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        self._save_facts(facts)

    def recall(self, query: str, k: int = 5) -> list[dict]:
        query_words = set(query.lower().split())
        facts = self._load_facts()
        scored = []
        for fact_entry in facts:
            score = sum(1 for w in query_words if w in fact_entry["fact"].lower())
            if score > 0:
                scored.append((score, fact_entry))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in scored[:k]]

    def forget(self, fact: str) -> bool:
        facts = self._load_facts()
        original_len = len(facts)
        facts = [f for f in facts if f["fact"] != fact]
        if len(facts) < original_len:
            self._save_facts(facts)
            return True
        return False

    def get_all_facts(self) -> list[dict]:
        return self._load_facts()

    def clear(self) -> None:
        self._save_facts([])
