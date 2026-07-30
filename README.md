# 🤖 SupportAgent — Agentic Customer Support Platform

> A progressive AI learning project: build a production-grade multi-agent customer support system, one phase at a time.

## 📚 Article Series

This repo accompanies the **"Building an AI Agent System from Zero to Production"** series:

- [Part 1 — The 12-Phase Blueprint](https://medium.com/@ag.prateek/02c5c6277ce5)
- Part 2 — The Foundation Layer (Phases 1–3) ← **this code**
- Part 3–6 — Coming soon

## 🗺️ Phases (Current: 1–3)

| Phase | Pillar | Status |
|-------|--------|--------|
| 1 | Foundation Models — Basic LLM call | ✅ |
| 2 | Prompt Engineering — Structured output | ✅ |
| 3 | RAG Pipeline — Product knowledge retrieval | ✅ |
| 4 | Agent Core — ReAct with LangGraph | 🔜 |
| 5–12 | Memory, Tools, Multi-Agent, Guardrails, Eval, Pipeline, Infra, UI | 🔜 |

## 🛠️ Tech Stack

- **Python 3.11+**
- **Amazon Bedrock** (Claude Sonnet + Titan Embeddings)
- **FAISS** (vector search)
- **boto3** (AWS SDK)

## 🚀 Quick Start

```bash
# 1. Clone & setup
git clone https://github.com/ag-prateek/supportagent.git
cd supportagent
python -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure AWS credentials
cp .env.example .env
# Edit .env with your AWS profile/region

# 4. Run Phase 1
python src/llm_client.py

# 5. Run Phase 2
python src/prompts.py

# 6. Run Phase 3
python src/rag/pipeline.py
```

## 📁 Project Structure

```
supportagent/
├── README.md
├── requirements.txt
├── .env.example
├── config/
│   └── settings.py              ← Centralized config (env-driven)
├── src/
│   ├── llm_client.py      ← Phase 1: 3 LLM calling patterns
│   ├── prompts.py        ← Phase 2: Structured JSON + parser
│   └── rag/
│       ├── chunking.py          ← 3 chunking strategies
│       ├── embeddings.py        ← Titan Embed v2 wrapper
│       ├── vector_store.py      ← FAISS index with persistence
│       └── pipeline.py          ← End-to-end RAG pipeline
├── data/
│   ├── policies/                ← Return & shipping policies
│   └── products/                ← Product catalog (JSON)
└── tests/                       ← Test suite (coming soon)
```

## ⭐ Star This Repo

If you're following along with the series, star the repo to get notified when new phases drop.

---

**Author:** [Prateek Agrawal](https://medium.com/@ag.prateek)

#GenerativeAI #AIAgents #AmazonBedrock #BuildInPublic
