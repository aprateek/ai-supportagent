"""Phase 10: Generate embeddings via Amazon Bedrock Titan Embeddings."""

import json
import logging
from typing import Any

import boto3
import numpy as np
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Synchronous embedding via Bedrock Titan Embed v2."""

    MODEL_ID = "amazon.titan-embed-text-v2:0"
    DIMENSION = 1024

    def __init__(self, region: str = "us-east-1"):
        self.client = boto3.client("bedrock-runtime", region_name=region)

    def embed_text(self, text: str) -> np.ndarray:
        """Generate 1024-dim embedding for text."""
        if not text or len(text.strip()) < 2:
            logger.warning("Text too short for embedding; returning zero vector.")
            return np.zeros(self.DIMENSION, dtype=np.float32)

        try:
            response = self.client.invoke_model(
                modelId=self.MODEL_ID,
                contentType="application/json",
                accept="application/json",
                body=json.dumps({"inputText": text}),
            )
            body = json.loads(response["body"].read())
            embedding = body.get("embedding", [])
            return np.array(embedding, dtype=np.float32)
        except ClientError as e:
            logger.error(f"Bedrock embedding failed: {e}")
            return np.zeros(self.DIMENSION, dtype=np.float32)

    def embed_batch(self, texts: list[str], batch_size: int = 10) -> list[np.ndarray]:
        """Embed multiple texts with rate-limit handling."""
        embeddings = []
        for i, text in enumerate(texts):
            if i > 0 and i % batch_size == 0:
                logger.info(f"Embedded {i}/{len(texts)} texts...")
            embeddings.append(self.embed_text(text))
        return embeddings
