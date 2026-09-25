# 🤖 SupportAgent — Agentic Customer Support Platform

> A progressive AI learning project: build a production-grade multi-agent customer support system, one phase at a time.

## 📚 Article Series

This repo accompanies the **"Building an AI Agent System from Zero to Production"** series:

- [Part 1 — The 12-Phase Blueprint](https://medium.com/@ag.prateek/02c5c6277ce5)
- [Part 2 — From Blank IDE to AI That Answers From Evidence](https://medium.com/@ag.prateek/PART2_LINK) (Phases 1–3)
- [Part 3 — The AI Forgot My Order Number. So I Gave It a Brain.](https://medium.com/@ag.prateek/PART3_LINK) (Phases 4–6)
- [Part 4 — One Agent Was Doing Four Jobs. So We Gave It a Team.](https://medium.com/@ag.prateek/PART4_LINK) (Phases 7–9)
- [Part 5 — From Laptop to Production](https://medium.com/@ag.prateek/PART5_LINK) (Phase 10)
- [Part 6 — Closing the Loop](https://medium.com/@ag.prateek/PART6_LINK) (Phases 11–12) ← **this code**

## 🗺️ Phases (Current: 1–12 — Complete System)

| Phase | Pillar | Status |
|-------|--------|--------|
| 1 | Foundation Models — Basic LLM call | ✅ |
| 2 | Prompt Engineering — Structured output | ✅ |
| 3 | RAG Pipeline — Knowledge retrieval | ✅ |
| 4 | Agent Core — LangGraph ReAct loop | ✅ |
| 5 | Memory — Conversation + semantic + entity | ✅ |
| 6 | Tools & Actions — 9 tool functions | ✅ |
| 7 | Multi-Agent — Orchestrator + 4 specialists | ✅ |
| 8 | Guardrails — PII, injection, toxicity, HITL | ✅ |
| 9 | Eval & Observability — LLM-judge, tracing, metrics | ✅ |
| 10 | Data Pipeline — ETL, ingestion, embeddings, quality checks | ✅ |
| 11 | Infrastructure — Docker, ECS/K8s, CDK, health checks, metrics | ✅ |
| 12 | Chat UI & Human-AI Loop — FastAPI, chat interface, feedback | ✅ |
|  | **System complete, ready for production** | 🚀 |

## 🛠️ Tech Stack

- **Python 3.11+**
- **Amazon Bedrock** (Claude Sonnet + Titan Embeddings)
- **LangGraph / LangChain** (agent orchestration)
- **FAISS** (vector search)
- **boto3** (AWS SDK)
- **FastAPI / Uvicorn** (API server)
- **Docker & AWS CDK** (infrastructure)

## 🚀 Quick Start

```bash
git clone https://github.com/ag-prateek/ai-supportagent.git
cd ai-supportagent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # edit with your AWS config
```

### Run the demos

```bash
python src/llm_client.py             # Phase 1: LLM calling patterns
python src/prompts.py                # Phase 2: Structured JSON output
python src/rag/pipeline.py           # Phase 3: RAG pipeline
python src/agents/agent.py           # Phase 4: Single agent ReAct loop
python src/agents/orchestrator.py    # Phase 7: Multi-agent routing
```

### Run the tests

```bash
pytest tests/ -v                       # All phases
pytest tests/test_orchestrator.py -v   # Phase 7 (multi-agent routing)
pytest tests/test_guardrails.py -v     # Phase 8 (guardrails + HITL)
pytest tests/test_eval.py -v           # Phase 9 (eval + tracing + metrics)
pytest tests/test_api.py -v            # Phase 12 (API schemas)
pytest tests/test_infra.py -v          # Phase 11 (infrastructure)
```

All tests mock Bedrock calls — **no AWS credentials needed**.

### Run the production stack (Phases 11–12)

```bash
python src/api/app.py                  # Phase 12: FastAPI chat server
# Then open http://localhost:8000 in your browser to use the chat UI
```

## 📁 Project Structure

```
ai-supportagent/
├── README.md
├── requirements.txt
├── .env.example
├── config/
│   └── settings.py                 ← env-driven config
├── src/
│   ├── llm_client.py               ← Phase 1: 3 LLM calling patterns
│   ├── prompts.py                  ← Phase 2: system prompt + parser
│   ├── rag/                        ← Phase 3: RAG pipeline
│   │   ├── chunking.py
│   │   ├── embeddings.py
│   │   ├── pipeline.py
│   │   └── vector_store.py
│   ├── agents/                     ← Phase 4 & 7: agents
│   │   ├── state.py                ← shared AgentState
│   │   ├── agent.py                ← Phase 4: single ReAct agent
│   │   ├── orchestrator.py         ← Phase 7: router + delegation
│   │   └── specialists/            ← Phase 7: 4 specialist agents
│   │       ├── order_agent.py
│   │       ├── returns_agent.py
│   │       ├── product_agent.py
│   │       └── general_agent.py
│   ├── memory/                     ← Phase 5: three-layer memory
│   │   ├── conversation.py
│   │   ├── semantic.py
│   │   ├── entity_store.py
│   │   └── memory_manager.py
│   ├── tools/                      ← Phase 6: 9 tool functions
│   │   ├── order_tools.py
│   │   ├── action_tools.py
│   │   ├── email_tools.py
│   │   ├── knowledge_tools.py
│   │   └── memory_tools.py
│   ├── guardrails/                 ← Phase 8: input/output guards + HITL
│   │   ├── input_guard.py          ← PII, injection, toxicity
│   │   ├── output_guard.py         ← redaction, hallucination, forbidden
│   │   └── manager.py              ← orchestration + human review queue
│   ├── eval/                       ← Phase 9: evaluation framework
│   │   ├── llm_judge.py            ← LLM-as-Judge scoring
│   │   ├── evaluator.py            ← test-case runner
│   │   ├── reporter.py             ← summary reports
│   │   └── test_cases.json         ← eval dataset
│   ├── observability/              ← Phase 9: tracing + metrics
│   │   ├── tracer.py               ← span-based tracing
│   │   └── metrics.py              ← counters + p50/p95/p99
│   ├── pipeline/                   ← Phase 10: data ETL pipeline
│   │   ├── loader.py               ← multi-source ingestion
│   │   ├── transformers.py         ← normalize, enrich, validate
│   │   ├── embedder.py             ← Bedrock embeddings
│   │   ├── quality_checker.py       ← rule-based QA
│   │   └── __init__.py
│   ├── infra/                      ← Phase 11: infrastructure & deployment
│   │   ├── docker_builder.py       ← DockerBuilder (build, push image)
│   │   ├── cdk_stack.py            ← SupportAgentStack (ECS Fargate)
│   │   ├── health_checker.py       ← liveness, readiness, Bedrock connectivity
│   │   ├── monitoring.py           ← MetricsCollector, p95 tracking
│   │   └── __init__.py
│   └── api/                        ← Phase 12: FastAPI chat server + UI
│       ├── schemas.py              ← Pydantic models (ChatRequest/Response)
│       ├── app.py                  ← FastAPI factory + endpoints
│       ├── __init__.py
│       └── ui/                     ← Chat interface (HTML/CSS/JS)
│           ├── index.html
│           ├── app.js
│           └── styles.css
├── data/
│   ├── policies/                   ← return & shipping policies
│   └── products/                   ← product catalog (JSON)
└── tests/
    ├── conftest.py                 ← shared mock fixtures
    ├── test_llm_calls.py           ← Phase 1
    ├── test_prompt_engineering.py  ← Phase 2
    ├── test_rag_pipeline.py        ← Phase 3
    ├── test_agent_core.py          ← Phase 4
    ├── test_memory.py              ← Phase 5
    ├── test_tools.py               ← Phase 6
    ├── test_orchestrator.py        ← Phase 7
    ├── test_guardrails.py          ← Phase 8
    ├── test_eval.py                ← Phase 9
    ├── test_pipeline.py            ← Phase 10
    ├── test_infra.py               ← Phase 11
    └── test_api.py                 ← Phase 12
```

## ⭐ Star This Repo

Star the repo to get notified when new phases drop.

---

**Authors:** [Prateek Agrawal](https://www.linkedin.com/in/prateekag/) & [Rishi Arora](https://www.linkedin.com/in/rishiarora/)

**Series:** *Building an AI Agent System from Zero to Production: The 12-Phase Blueprint*  
**Status:** Complete (all 12 phases implemented)  
**Last Updated:** September 2026
