"""RAG Pipeline — end-to-end retrieval-augmented generation."""

import json
import sys
from pathlib import Path
from typing import Optional

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.llm_client import call_llm_with_system
from src.prompts import SYSTEM_PROMPT, FEW_SHOT_EXAMPLES, OutputParser, SupportResponse
from src.rag.chunking import Chunk, ChunkingStrategy
from src.rag.embeddings import EmbeddingModel
from src.rag.vector_store import VectorStore

RAG_SYSTEM_PROMPT = f"""{SYSTEM_PROMPT}

You also have access to retrieved knowledge from ShopSmart\'s knowledge base.
Use ONLY the provided context to answer product and policy questions.
If the context doesn\'t contain the answer, say so honestly.
"""


class RAGPipeline:
    def __init__(self, embedding_model: Optional[EmbeddingModel] = None, vector_store: Optional[VectorStore] = None):
        self.embeddings = embedding_model or EmbeddingModel()
        self.store = vector_store or VectorStore(dimension=self.embeddings.dimension)

    def ingest_text(self, text: str, source: str = "unknown", chunk_size: int = 500) -> int:
        """Chunk text, embed, and add to vector store."""
        chunks = ChunkingStrategy.recursive_split(text, chunk_size=chunk_size, source=source)
        vectors = self.embeddings.embed_batch([c.text for c in chunks])
        self.store.add(chunks, np.array(vectors, dtype=np.float32))
        return len(chunks)

    def ingest_directory(self, directory: str, glob: str = "*.md") -> int:
        """Ingest all matching files from a directory."""
        total = 0
        for path in sorted(Path(directory).glob(glob)):
            total += self.ingest_text(path.read_text(), source=path.name)
        return total

    def retrieve(self, query: str, k: int = 5) -> list[tuple[Chunk, float]]:
        """Retrieve top-k relevant chunks for a query."""
        query_vec = self.embeddings.embed(query)
        return self.store.search(np.array(query_vec, dtype=np.float32), k=k)

    def query(self, customer_message: str, k: int = 5) -> SupportResponse:
        """Full RAG: retrieve context, build prompt, call LLM, parse response."""
        results = self.retrieve(customer_message, k=k)
        context = "\n\n---\n\n".join(
            f"[Source: {chunk.metadata.get('source', '?')}]\n{chunk.text}"
            for chunk, _score in results
        )
        system = f"{RAG_SYSTEM_PROMPT}\n\n{FEW_SHOT_EXAMPLES}"
        user_prompt = f"""Retrieved context:\n{context}\n\nCustomer message: {customer_message}"""
        raw = call_llm_with_system(system, user_prompt)
        return OutputParser.parse_support_response(raw)

    def save(self, path: str) -> None:
        self.store.save(path)

    @classmethod
    def load(cls, path: str, embedding_model: Optional[EmbeddingModel] = None) -> "RAGPipeline":
        store = VectorStore.load(path)
        return cls(embedding_model=embedding_model, vector_store=store)
