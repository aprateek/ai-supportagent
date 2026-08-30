"""Phase 5 tests: verify three-layer memory — conversation, semantic, entity store."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


class TestConversationMemory:
    """Test per-thread conversation persistence."""

    def test_save_and_get_history(self, tmp_path):
        from src.memory.conversation import ConversationMemory
        mem = ConversationMemory(storage_path=str(tmp_path))
        mem.save_turn("t1", "Where is my order?", "Let me look that up.")
        mem.save_turn("t1", "Order ORD-123", "Found it — shipped via FedEx.")
        history = mem.get_history("t1")
        assert len(history) == 2
        assert history[0]["human"] == "Where is my order?"

    def test_last_n_limits(self, tmp_path):
        from src.memory.conversation import ConversationMemory
        mem = ConversationMemory(storage_path=str(tmp_path))
        for i in range(10):
            mem.save_turn("t1", f"msg {i}", f"reply {i}")
        assert len(mem.get_history("t1", last_n=3)) == 3

    def test_empty_thread(self, tmp_path):
        from src.memory.conversation import ConversationMemory
        mem = ConversationMemory(storage_path=str(tmp_path))
        assert mem.get_history("nonexistent") == []


class TestSemanticMemory:
    """Test fact storage and keyword recall."""

    def test_remember_and_recall(self, tmp_path):
        from src.memory.semantic import SemanticMemory
        mem = SemanticMemory(storage_path=str(tmp_path))
        mem.remember("Customer prefers email communication")
        mem.remember("Order ORD-123 was delayed")
        results = mem.recall("email communication")
        assert len(results) >= 1
        assert "email" in results[0]["fact"].lower()

    def test_forget(self, tmp_path):
        from src.memory.semantic import SemanticMemory
        mem = SemanticMemory(storage_path=str(tmp_path))
        mem.remember("test fact")
        assert mem.forget("test fact") is True
        assert mem.forget("nonexistent") is False

    def test_clear(self, tmp_path):
        from src.memory.semantic import SemanticMemory
        mem = SemanticMemory(storage_path=str(tmp_path))
        mem.remember("fact 1")
        mem.remember("fact 2")
        mem.clear()
        assert mem.get_all_facts() == []


class TestEntityStore:
    """Test entity graph operations."""

    def test_add_and_get_entity(self, tmp_path):
        from src.memory.entity_store import EntityStore
        store = EntityStore(storage_path=str(tmp_path))
        store.add_entity("ORD-123", "order", {"status": "shipped"})
        entity = store.get_entity("ORD-123")
        assert entity is not None
        assert entity["type"] == "order"

    def test_add_and_get_relation(self, tmp_path):
        from src.memory.entity_store import EntityStore
        store = EntityStore(storage_path=str(tmp_path))
        store.add_relation("thread:1", "mentions", "ORD-123")
        rels = store.get_relations("ORD-123")
        assert len(rels) == 1
        assert rels[0]["predicate"] == "mentions"

    def test_no_duplicate_relations(self, tmp_path):
        from src.memory.entity_store import EntityStore
        store = EntityStore(storage_path=str(tmp_path))
        store.add_relation("a", "knows", "b")
        store.add_relation("a", "knows", "b")
        assert len(store.query(subject="a")) == 1

    def test_delete_entity_removes_relations(self, tmp_path):
        from src.memory.entity_store import EntityStore
        store = EntityStore(storage_path=str(tmp_path))
        store.add_entity("X", "test")
        store.add_relation("X", "rel", "Y")
        store.delete_entity("X")
        assert store.get_entity("X") is None
        assert store.get_relations("X") == []


class TestMemoryManager:
    """Test the orchestrator across all three layers."""

    def test_on_conversation_turn_persists(self, tmp_path):
        from src.memory.memory_manager import MemoryManager
        mgr = MemoryManager(base_path=str(tmp_path))
        mgr.on_conversation_turn("t1", "My order ORD-555 is late", "Let me check.", intent="order_status")
        history = mgr.conversation.get_history("t1")
        assert len(history) == 1
        # Entity should be extracted
        entity = mgr.entities.get_entity("ORD-555")
        assert entity is not None

    def test_get_context_includes_history(self, tmp_path):
        from src.memory.memory_manager import MemoryManager
        mgr = MemoryManager(base_path=str(tmp_path))
        mgr.on_conversation_turn("t1", "Hello", "Hi there!")
        context = mgr.get_context_for_query("t1", "order status")
        assert "Hello" in context
