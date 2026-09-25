"""Phase 10: Unit tests — Data Pipeline (loader, transformers, embedder, quality checks).

Trust, but Verify: test_pipeline.py
"""

import pytest
import sys
from pathlib import Path

# Add parent dir to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.pipeline import DataLoader, DataQualityChecker, DataTransformer, EmbeddingService


class TestDataLoader:
    def test_load_mock_api(self):
        loader = DataLoader()
        records = list(loader.load_mock_api(num_records=10))
        assert len(records) == 10
        assert records[0].source == "api"
        assert records[0].record_id.startswith("api-")

    def test_deduplication(self):
        loader = DataLoader()
        records1 = list(loader.load_mock_api(num_records=5))
        records2 = list(loader.load_mock_api(num_records=5))
        assert len(records2) == 0  # All deduplicated


class TestDataTransformer:
    def test_normalize(self):
        text = "  HELLO  World  "
        result = DataTransformer.normalize(text)
        assert result == "hello world"

    def test_enrich(self):
        content = "Test content"
        meta = {"source": "test"}
        result = DataTransformer.enrich(content, meta)
        assert result["length"] == len(content)
        assert result["metadata"] == meta

    def test_validate_short_content(self):
        assert not DataTransformer.validate("hi", min_length=10)

    def test_chunk_long_content(self):
        long_text = " ".join(["word"] * 1000)
        chunks = DataTransformer.chunk_long_content(long_text, chunk_size=100)
        assert len(chunks) > 1


class TestDataQualityChecker:
    def test_check_valid(self):
        checker = DataQualityChecker()
        result = checker.check("This is valid content for testing.", "rec-1")
        assert result.passed
        assert result.score == 1.0

    def test_check_short(self):
        checker = DataQualityChecker()
        result = checker.check("short", "rec-1")
        assert not result.passed
        assert len(result.issues) > 0

    def test_health_score(self):
        checker = DataQualityChecker()
        records = [
            ("This is valid content", "rec-1", {}),
            ("Valid text here", "rec-2", {}),
        ]
        health = checker.health_score(records)
        assert health["total"] == 2
        assert health["avg_score"] > 0.5


class TestEmbeddingService:
    def test_embed_text_shape(self):
        """Mock test without Bedrock (no AWS creds needed)."""
        service = EmbeddingService()
        # This will return zeros (Bedrock call fails gracefully in unit test)
        embedding = service.embed_text("test text")
        assert embedding.shape == (1024,)
        assert embedding.dtype == "float32"

    def test_embed_empty_text(self):
        service = EmbeddingService()
        embedding = service.embed_text("")
        assert (embedding == 0).all()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--tb=short"])
