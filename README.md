# 🤖 SupportAgent — Agentic Customer Support Platform

> A progressive AI learning project: build a production-grade multi-agent customer support system, one phase at a time.

## 📚 Article Series

This repo accompanies the **"Building an AI Agent System from Zero to Production"** series:

- [Part 1 — The 12-Phase Blueprint](https://medium.com/@ag.prateek/02c5c6277ce5)
- [Part 2 — From Blank IDE to AI That Answers From Evidence](https://medium.com/@ag.prateek/PART2_LINK) (Phases 1–3)
- [Part 3 — The AI Forgot My Order Number. So I Gave It a Brain.](https://medium.com/@ag.prateek/PART3_LINK) (Phases 4–6) ← **this code**
- Parts 4–6 — Coming soon

## 🗺️ Phases (Current: 1–6)

| Phase | Pillar | Status |
|-------|--------|--------|
| 1 | Foundation Models — Basic LLM call | ✅ |
| 2 | Prompt Engineering — Structured output | ✅ |
| 3 | RAG Pipeline — Knowledge retrieval | ✅ |
| 4 | Agent Core — LangGraph ReAct loop | ✅ |
| 5 | Memory — Conversation + semantic + entity | ✅ |
| 6 | Tools & Actions — 9 tool functions | ✅ |
| 7–12 | Multi-Agent, Guardrails, Eval, Pipeline, Infra, UI | 🔜 |

## 🛠️ Tech Stack

- **Python 3.11+**
- **Amazon Bedrock** (Claude Sonnet + Titan Embeddings)
- **LangGraph / LangChain** (agent orchestration)
- **FAISS** (vector search)
- **boto3** (AWS SDK)

## 🚀 Quick Start

```bash
git clone https://github.com/ag-prateek/supportagent.git
cd supportagent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # edit with your AWS config
```

### Run the demos

```bash
python src/llm_client.py          # Phase 1: LLM calling patterns
python src/prompts.py             # Phase 2: Structured JSON output
python src/rag/pipeline.py        # Phase 3: RAG pipeline
python src/agents/agent.py        # Phase 4: Agent ReAct loop (requires tools)
```

### Run the tests

```bash
pytest tests/ -v                  # All phases
pytest tests/test_agent_core.py -v  # Phase 4 only
pytest tests/test_memory.py -v      # Phase 5 only
pytest tests/test_tools.py -v       # Phase 6 only
```

All tests mock Bedrock calls — **no AWS credentials needed**.

## 📁 Project Structure

```
ai-supportagent/
├── README.md
├── requirements.txt
├── .env.example
├── config/
│   └── settings.py              ← env-driven config
├── src/
│   ├── llm_client.py            ← Phase 1: 3 LLM calling patterns
│   ├── prompts.py               ← Phase 2: system prompt + parser
│   ├── rag/                     ← Phase 3: RAG pipeline
│   │   ├── chunking.py
│   │   ├── embeddings.py
│   │   ├── vector_store.py
│   │   └── pipeline.py
│   ├── agents/                  ← Phase 4: LangGraph ReAct agent
│   │   ├── state.py
│   │   └── agent.py
│   ├── memory/                  ← Phase 5: three-layer memory
│   │   ├── conversation.py
│   │   ├── semantic.py
│   │   ├── entity_store.py
│   │   └── memory_manager.py
│   └── tools/                   ← Phase 6: 9 tool functions
│       ├── order_tools.py
│       ├── knowledge_tools.py
│       ├── action_tools.py
│       ├── memory_tools.py
│       └── email_tools.py
├── data/
│   ├── policies/                ← return & shipping policies
│   └── products/                ← product catalog (JSON)
└── tests/
    ├── conftest.py              ← shared mock fixtures
    ├── test_llm_calls.py        ← Phase 1 tests
    ├── test_prompt_engineering.py ← Phase 2 tests
    ├── test_rag_pipeline.py     ← Phase 3 tests
    ├── test_agent_core.py       ← Phase 4 tests
    ├── test_memory.py           ← Phase 5 tests
    └── test_tools.py            ← Phase 6 tests
```

## ⭐ Star This Repo

Star the repo to get notified when new phases drop.

---

**Authors:** [Prateek Agrawal](https://www.linkedin.com/in/prateekag/) & [Rishi Arora](https://www.linkedin.com/in/rishiarora/)
