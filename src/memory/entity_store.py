"""EntityStore — simple knowledge graph for entity relationships."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


class EntityStore:
    """Graph-like store mapping entities to their relationships and attributes."""

    def __init__(self, storage_path: str = "data/memory/entities"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.graph_file = self.storage_path / "graph.json"
        if not self.graph_file.exists():
            self.graph_file.write_text(json.dumps({"entities": {}, "relations": []}, indent=2))

    def _load(self) -> dict:
        return json.loads(self.graph_file.read_text())

    def _save(self, data: dict) -> None:
        self.graph_file.write_text(json.dumps(data, indent=2))

    def add_entity(self, entity_id: str, entity_type: str, attributes: dict = None) -> None:
        data = self._load()
        data["entities"][entity_id] = {
            "type": entity_type, "attributes": attributes or {},
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        self._save(data)

    def add_relation(self, subject: str, predicate: str, obj: str) -> None:
        data = self._load()
        relation = {"subject": subject, "predicate": predicate, "object": obj,
                     "timestamp": datetime.now(timezone.utc).isoformat()}
        for r in data["relations"]:
            if r["subject"] == subject and r["predicate"] == predicate and r["object"] == obj:
                return
        data["relations"].append(relation)
        self._save(data)

    def get_entity(self, entity_id: str) -> Optional[dict]:
        return self._load()["entities"].get(entity_id)

    def get_relations(self, entity_id: str) -> list[dict]:
        data = self._load()
        return [r for r in data["relations"] if r["subject"] == entity_id or r["object"] == entity_id]

    def query(self, subject=None, predicate=None, obj=None) -> list[dict]:
        results = self._load()["relations"]
        if subject: results = [r for r in results if r["subject"] == subject]
        if predicate: results = [r for r in results if r["predicate"] == predicate]
        if obj: results = [r for r in results if r["object"] == obj]
        return results

    def get_all_entities(self) -> dict:
        return self._load()["entities"]

    def delete_entity(self, entity_id: str) -> bool:
        data = self._load()
        if entity_id not in data["entities"]: return False
        del data["entities"][entity_id]
        data["relations"] = [r for r in data["relations"] if r["subject"] != entity_id and r["object"] != entity_id]
        self._save(data)
        return True

    def clear(self) -> None:
        self._save({"entities": {}, "relations": []})
