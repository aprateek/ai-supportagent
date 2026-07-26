"""FAISS-based vector store for RAG retrieval."""

import pickle
from pathlib import Path

import faiss
import numpy as np

from src.rag.chunking import Chunk


class VectorStore:
    def __init__(self, dimension: int = 1024):
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)
        self.chunks: list[Chunk] = []

    def add(self, chunks: list[Chunk], embeddings: np.ndarray) -> None:
        """Normalize embeddings and add to the FAISS index."""
        embeddings = np.array(embeddings, dtype=np.float32)
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings)
        self.chunks.extend(chunks)

    def search(self, query_embedding: np.ndarray, k: int = 5) -> list[tuple[Chunk, float]]:
        """Return top-k most similar chunks with scores."""
        query = np.array([query_embedding], dtype=np.float32)
        faiss.normalize_L2(query)
        k = min(k, self.index.ntotal)
        if k == 0:
            return []
        scores, indices = self.index.search(query, k)
        return [(self.chunks[i], float(scores[0][j])) for j, i in enumerate(indices[0]) if i >= 0]

    def save(self, path: str) -> None:
        """Persist index and chunks to disk."""
        p = Path(path)
        p.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(p / "index.faiss"))
        with open(p / "chunks.pkl", "wb") as f:
            pickle.dump(self.chunks, f)

    @classmethod
    def load(cls, path: str) -> "VectorStore":
        """Load index and chunks from disk."""
        p = Path(path)
        index = faiss.read_index(str(p / "index.faiss"))
        with open(p / "chunks.pkl", "rb") as f:
            chunks = pickle.load(f)
        store = cls(dimension=index.d)
        store.index = index
        store.chunks = chunks
        return store

    @property
    def size(self) -> int:
        return self.index.ntotal
