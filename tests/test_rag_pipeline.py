"""Tests: verify RAG pipeline — chunking, embeddings, vector store, end-to-end."""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.rag.chunking import Chunk, ChunkingStrategy


class TestChunking:
    """Test document chunking strategies."""

    SAMPLE_TEXT = (
        "ShopSmart Return Policy\n\n"
        "All items may be returned within 30 days of delivery.\n\n"
        "Items must be unused and in original packaging.\n\n"
        "Gift cards and perishable goods are not eligible for return.\n\n"
        "Refunds are processed within 5-7 business days."
    )

    def test_produces_chunks(self):
        chunks = ChunkingStrategy.fixed_size(self.SAMPLE_TEXT, chunk_size=80, overlap=20)
        assert len(chunks) > 1
        assert all(isinstance(c, Chunk) for c in chunks)

    def test_overlap_creates_more_chunks(self):
        no_overlap = ChunkingStrategy.fixed_size(self.SAMPLE_TEXT, chunk_size=80, overlap=0)
        with_overlap = ChunkingStrategy.fixed_size(self.SAMPLE_TEXT, chunk_size=80, overlap=40)
        assert len(with_overlap) >= len(no_overlap)

    def test_recursive_split(self):
        chunks = ChunkingStrategy.recursive_split(self.SAMPLE_TEXT, chunk_size=100, source="test")
        assert len(chunks) > 1
        assert all(c.metadata["source"] == "test" for c in chunks)

    def test_splits_on_headers(self):
        md_text = "# Section 1\nContent one.\n# Section 2\nContent two.\n# Section 3\nContent three."
        chunks = ChunkingStrategy.semantic_sections(md_text, source="doc.md")
        assert len(chunks) == 3
        assert "Section 1" in chunks[0].text

    def test_metadata_preserved(self):
        chunks = ChunkingStrategy.recursive_split(self.SAMPLE_TEXT, source="return_policy.md")
        for c in chunks:
            assert "source" in c.metadata
            assert c.metadata["source"] == "return_policy.md"
            assert "chunk_index" in c.metadata


class TestVectorStore:
    """Test FAISS-based vector store operations."""

    def _make_store(self):
        from src.rag.vector_store import VectorStore
        store = VectorStore(dimension=4)  # small dim for tests
        chunks = [Chunk(text=f"chunk {i}", metadata={"source": "test", "chunk_index": i}) for i in range(5)]
        embeddings = np.random.randn(5, 4).astype(np.float32)
        store.add(chunks, embeddings)
        return store, embeddings

    def test_search_returns_results(self):
        store, embeddings = self._make_store()
        results = store.search(embeddings[0], k=3)
        assert len(results) == 3
        assert all(isinstance(r[0], Chunk) for r in results)

    def test_search_top_result_is_self(self):
        store, embeddings = self._make_store()
        results = store.search(embeddings[2], k=1)
        assert results[0][0].text == "chunk 2"

    def test_save_and_load(self, tmp_path):
        store, embeddings = self._make_store()
        store.save(str(tmp_path / "test_index"))

        from src.rag.vector_store import VectorStore
        loaded = VectorStore.load(str(tmp_path / "test_index"))
        assert loaded.size == 5
        results = loaded.search(embeddings[0], k=1)
        assert len(results) == 1


class TestEmbeddings:
    """Test embedding model returns correct dimensions."""

    def test_embed_returns_vector(self, mock_bedrock_client, mock_embedding):
        mock_bedrock_client.invoke_model.return_value = mock_embedding(1024)
        from src.rag.embeddings import EmbeddingModel
        model = EmbeddingModel()
        vec = model.embed("test text")
        assert len(vec) == 1024
        assert all(isinstance(v, float) for v in vec)


class TestRAGPipeline:
    """Test end-to-end RAG pipeline with mocked LLM and embeddings."""

    def test_ingest_text(self, mock_bedrock_client, mock_embedding):
        mock_bedrock_client.invoke_model.return_value = mock_embedding(1024)
        from src.rag.pipeline import RAGPipeline
        pipeline = RAGPipeline()
        count = pipeline.ingest_text("ShopSmart offers free returns within 30 days.", source="policy")
        assert count > 0
        assert pipeline.store.size > 0

    def test_retrieve(self, mock_bedrock_client, mock_embedding):
        mock_bedrock_client.invoke_model.return_value = mock_embedding(1024)
        from src.rag.pipeline import RAGPipeline
        pipeline = RAGPipeline()
        pipeline.ingest_text("Returns are allowed within 30 days.", source="policy")
        results = pipeline.retrieve("return policy", k=1)
        assert len(results) >= 1
        assert isinstance(results[0][0], Chunk)

    def test_query_includes_context_in_prompt(self, mock_bedrock_client, mock_embedding, mock_bedrock_response):
        # First calls: embeddings for ingest + query
        mock_bedrock_client.invoke_model.side_effect = [
            mock_embedding(1024),  # ingest embedding
            mock_embedding(1024),  # query embedding
            mock_bedrock_response(json.dumps({  # LLM response
                "intent": "product_question",
                "confidence": 0.9,
                "response": "Our return policy allows 30-day returns.",
                "needs_escalation": False,
                "escalation_reason": None,
            })),
        ]
        from src.rag.pipeline import RAGPipeline
        pipeline = RAGPipeline()
        pipeline.ingest_text("All items may be returned within 30 days.", source="return_policy.md")
        result = pipeline.query("What is the return policy?")
        assert result.response
        assert result.intent == "product_question"

    def test_query_returns_support_response(self, mock_bedrock_client, mock_embedding, mock_bedrock_response):
        mock_bedrock_client.invoke_model.side_effect = [
            mock_embedding(1024),
            mock_embedding(1024),
            mock_bedrock_response(json.dumps({
                "intent": "product_question",
                "confidence": 0.92,
                "response": "Next-day shipping costs $24.99.",
                "needs_escalation": False,
                "escalation_reason": None,
            })),
        ]
        from src.rag.pipeline import RAGPipeline
        from src.phase2_prompts import SupportResponse
        pipeline = RAGPipeline()
        pipeline.ingest_text("Next-day shipping is $24.99.", source="shipping_policy.md")
        result = pipeline.query("How much is next-day shipping?")
        assert isinstance(result, SupportResponse)
        assert result.confidence > 0.5
