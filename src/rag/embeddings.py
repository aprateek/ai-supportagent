"""Embedding generation via Amazon Bedrock Titan Embed v2."""

import json
import sys
from pathlib import Path

import boto3

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from config.settings import AWS_REGION, EMBEDDING_MODEL_ID


class EmbeddingModel:
    DIMENSION = 1024  # Titan Embed Text v2

    def __init__(self, model_id: str = EMBEDDING_MODEL_ID, region: str = AWS_REGION):
        self.model_id = model_id
        self.client = boto3.client("bedrock-runtime", region_name=region)

    @property
    def dimension(self) -> int:
        return self.DIMENSION

    def embed(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        response = self.client.invoke_model(
            modelId=self.model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps({"inputText": text}),
        )
        return json.loads(response["body"].read())["embedding"]

    def embed_batch(self, texts: list[str], batch_size: int = 10) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        results = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            for text in batch:
                results.append(self.embed(text))
        return results
