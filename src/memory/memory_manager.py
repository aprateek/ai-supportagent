"""MemoryManager — unified orchestrator for all memory systems."""

import re

from src.memory.conversation import ConversationMemory
from src.memory.semantic import SemanticMemory
from src.memory.entity_store import EntityStore


class MemoryManager:
    def __init__(self, base_path: str = "data/memory"):
        self.conversation = ConversationMemory(storage_path=base_path)
        self.semantic = SemanticMemory(storage_path=f"{base_path}/semantic")
        self.entities = EntityStore(storage_path=f"{base_path}/entities")

    def on_conversation_turn(self, thread_id: str, human_msg: str, ai_msg: str, intent: str = None) -> None:
        """Called AFTER each agent turn."""
        self.conversation.save_turn(thread_id, human_msg, ai_msg, metadata={"intent": intent})
        facts = self._extract_facts(human_msg, ai_msg)
        for fact in facts:
            self.semantic.remember(fact, source=f"thread:{thread_id}")
        self._update_entities(human_msg, thread_id)

    def get_context_for_query(self, thread_id: str, query: str) -> str:
        """Called BEFORE agent thinks."""
        parts = []
        history = self.conversation.get_history(thread_id, last_n=5)
        if history:
            lines = []
            for turn in history:
                lines.append(f"Customer: {turn['human']}")
                lines.append(f"Agent: {turn['ai']}")
            parts.append("Recent conversation:\n" + "\n".join(lines))
        facts = self.semantic.recall(query, k=3)
        if facts:
            parts.append("Relevant facts:\n" + "\n".join(f"- {f['fact']}" for f in facts))
        entities = self._find_entities_in_text(query)
        if entities:
            elines = []
            for eid in entities:
                entity = self.entities.get_entity(eid)
                if entity:
                    elines.append(f"- {eid} ({entity['type']}): {entity['attributes']}")
            if elines:
                parts.append("Entity context:\n" + "\n".join(elines))
        summary = self.conversation.summarize_history(thread_id)
        if summary:
            parts.append(summary)
        return "\n\n".join(parts)

    def _extract_facts(self, human_msg: str, ai_msg: str) -> list[str]:
        facts = []
        patterns = [
            r"(?:my|our)\s+(\w+)\s+(?:is|are)\s+(.+?)(?:\.|$)",
            r"(?:order|account|ticket)\s*(?:number|#|id)?\s*(?:is)?\s*[:#]?\s*([A-Z0-9-]+)",
        ]
        for pattern in patterns:
            matches = re.findall(pattern, human_msg, re.IGNORECASE)
            for match in matches:
                fact = " ".join(match).strip() if isinstance(match, tuple) else match.strip()
                if len(fact) > 3:
                    facts.append(fact)
        return facts

    def _update_entities(self, text: str, thread_id: str) -> None:
        for oid in re.findall(r"(ORD-\d+)", text, re.IGNORECASE):
            self.entities.add_entity(oid, "order", {"mentioned_in": thread_id})
            self.entities.add_relation(thread_id, "mentions", oid)
        for email in re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", text):
            self.entities.add_entity(email, "customer_email", {"mentioned_in": thread_id})
            self.entities.add_relation(thread_id, "involves", email)

    def _find_entities_in_text(self, text: str) -> list[str]:
        found = []
        for pattern in [r"(ORD-\d+)", r"((?:ACC|TKT|CUST)-\d+)", r"([\w.+-]+@[\w-]+\.[\w.-]+)"]:
            found.extend(re.findall(pattern, text, re.IGNORECASE))
        return found

    def clear_all(self) -> None:
        self.semantic.clear()
        self.entities.clear()
