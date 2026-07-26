"""Central configuration for SupportAgent."""

import os
from dotenv import load_dotenv

load_dotenv()

# ── AWS ──────────────────────────────────────────
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# ── Model ────────────────────────────────────────
MODEL_ID = os.getenv("MODEL_ID", "us.anthropic.claude-sonnet-4-6")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1024"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.3"))

# ── Embedding ────────────────────────────────────
EMBEDDING_MODEL_ID = os.getenv("EMBEDDING_MODEL_ID", "amazon.titan-embed-text-v2:0")
