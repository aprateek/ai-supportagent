"""Text chunking strategies for RAG pipeline."""

import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Chunk:
    text: str
    metadata: dict = field(default_factory=dict)
    embedding: Optional[list[float]] = None


class ChunkingStrategy:
    """Multiple text chunking strategies."""

    @staticmethod
    def fixed_size(text: str, chunk_size: int = 500, overlap: int = 100, source: str = "unknown") -> list[Chunk]:
        """Overlapping fixed-size window chunking."""
        chunks = []
        start = 0
        idx = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(Chunk(text=text[start:end], metadata={"source": source, "start": start, "end": end, "chunk_index": idx}))
            idx += 1
            start += chunk_size - overlap
        return chunks

    @staticmethod
    def recursive_split(text: str, chunk_size: int = 500, overlap: int = 100, separators: Optional[List[str]] = None, source: str = "unknown") -> list[Chunk]:
        """Split on natural boundaries — paragraphs, then sentences, then words."""
        if separators is None:
            separators = ["\n\n", "\n", ". ", " "]

        def _split(text: str, seps: list[str]) -> list[str]:
            if not seps or len(text) <= chunk_size:
                return [text] if text.strip() else []
            sep = seps[0]
            parts = text.split(sep)
            result = []
            current = ""
            for part in parts:
                candidate = current + sep + part if current else part
                if len(candidate) <= chunk_size:
                    current = candidate
                else:
                    if current:
                        result.append(current)
                    if len(part) > chunk_size:
                        result.extend(_split(part, seps[1:]))
                    else:
                        current = part
                        continue
                    current = ""
            if current:
                result.append(current)
            return result

        pieces = _split(text, separators)
        chunks = []
        for idx, piece in enumerate(pieces):
            if idx > 0 and overlap > 0:
                prev_tail = pieces[idx - 1][-overlap:]
                piece = prev_tail + piece
            chunks.append(Chunk(text=piece, metadata={"source": source, "start": 0, "end": len(piece), "chunk_index": idx}))
        return chunks

    @staticmethod
    def semantic_sections(text: str, source: str = "unknown") -> list[Chunk]:
        """Split on markdown headers, keeping each section together."""
        sections = re.split(r"(?=^#{1,3}\s)", text, flags=re.MULTILINE)
        chunks = []
        idx = 0
        for section in sections:
            section = section.strip()
            if not section:
                continue
            chunks.append(Chunk(text=section, metadata={"source": source, "start": 0, "end": len(section), "chunk_index": idx}))
            idx += 1
        return chunks
