"""Phase 10: Transform raw records into vectors-ready format."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class DataTransformer:
    """Clean, normalize, and enrich records."""

    @staticmethod
    def normalize(record_content: str) -> str:
        """Normalize text: strip, lowercase, remove extra whitespace."""
        return " ".join(record_content.lower().split())

    @staticmethod
    def enrich(content: str, metadata: dict[str, Any]) -> dict[str, Any]:
        """Enrich with computed fields (e.g., length, token estimate)."""
        return {
            "content": content,
            "length": len(content),
            "token_estimate": len(content) // 4,
            "metadata": metadata,
        }

    @staticmethod
    def validate(content: str, min_length: int = 10) -> bool:
        """Check record meets quality thresholds."""
        if not content or len(content) < min_length:
            logger.warning(f"Content too short ({len(content)} chars); skipping.")
            return False
        return True

    @staticmethod
    def chunk_long_content(content: str, chunk_size: int = 512, overlap: int = 50) -> list[str]:
        """Split long text into overlapping chunks for embedding."""
        chunks = []
        words = content.split()
        word_chunks = []
        current_chunk = []
        current_length = 0

        for word in words:
            current_chunk.append(word)
            current_length += len(word) + 1
            if current_length >= chunk_size:
                word_chunks.append(" ".join(current_chunk))
                # Overlap: keep last N words
                overlap_count = overlap // 5  # rough word estimate
                current_chunk = current_chunk[-overlap_count:] if overlap_count > 0 else []
                current_length = sum(len(w) + 1 for w in current_chunk)

        if current_chunk:
            word_chunks.append(" ".join(current_chunk))

        return word_chunks
