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
git clone https://github.com/ag-prateek/ai-supportagent.git
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
└── tests/
│   ├── conftest.py              ← Shared fixtures (mock Bedrock client)
│   ├── test_llm_calls.py        ← Phase 1: LLM calling pattern tests
│   ├── test_prompt_engineering.py ← Phase 2: Prompt template & parser tests
│   └── test_rag_pipeline.py     ← Phase 3: Chunking, embeddings & RAG tests
```

## 🧪 Running Tests

Tests use `pytest` with mocked AWS Bedrock calls — no real AWS credentials needed.

> **Important:** Always run with the `-v` flag to see per-test outcomes.

Run all tests:

```bash
pytest tests/ -v
```

Or run a specific test file:

```bash
pytest tests/test_llm_calls.py -v
pytest tests/test_prompt_engineering.py -v
pytest tests/test_rag_pipeline.py -v
```

---

### Phase 1 — LLM Calls (`test_llm_calls.py`)

#### `TestBasicResponse` — Basic LLM response validation
| Test | Description |
|------|-------------|
| `test_basic_response_non_empty` | Verifies `call_llm()` returns a non-empty string for a basic customer query |
| `test_customer_query_keywords` | Verifies the response contains relevant keywords (e.g. "order") matching the query context |

#### `TestStreaming` — Streaming response assembly
| Test | Description |
|------|-------------|
| `test_streaming_returns_complete` | Verifies `call_llm_streaming()` correctly assembles chunked stream tokens into a complete response |

#### `TestSystemPrompt` — System prompt handling
| Test | Description |
|------|-------------|
| `test_system_prompt_respected` | Verifies `call_llm_with_system()` correctly passes the system prompt as a separate field in the Bedrock request body |

---

### Phase 2 — Prompt Engineering (`test_prompt_engineering.py`)

#### `TestPromptTemplate` — Template variable injection
| Test | Description |
|------|-------------|
| `test_format_injects_variables` | Verifies that named variables are correctly substituted into the prompt template |
| `test_missing_variable_raises` | Verifies a `ValueError` is raised when required template variables are missing |

#### `TestOutputParser` — JSON extraction and response parsing
| Test | Description |
|------|-------------|
| `test_parse_json_code_fence` | Verifies JSON is correctly extracted from a markdown code fence block |
| `test_parse_json_raw_object` | Verifies JSON is correctly extracted from a raw inline object in text |
| `test_parse_support_response_valid` | Verifies a valid JSON string is parsed into a `SupportResponse` object |
| `test_parse_support_response_fallback` | Verifies malformed/non-JSON output falls back to a `general` intent with 0.0 confidence |
| `test_escalation_detected` | Verifies escalation flag and reason are correctly parsed from the LLM response |

#### `TestIntentValidation` — Intent taxonomy enforcement
| Test | Description |
|------|-------------|
| `test_valid_intents_accepted` | Verifies all defined valid intents pass validation |
| `test_validate_intent_invalid` | Verifies unrecognised, empty, or wrong-case intents fail validation |

#### `TestSystemPrompt` — System prompt content
| Test | Description |
|------|-------------|
| `test_system_prompt_contains_intents` | Verifies the system prompt includes every valid intent in its text |
| `test_system_prompt_includes_few_shot` | Verifies the few-shot examples cover key intents (`order_status`, `return_request`, `billing_issue`) |

#### `TestClassifyAndRespond` — End-to-end classification flow
| Test | Description |
|------|-------------|
| `test_returns_support_response` | Verifies `classify_and_respond()` returns a `SupportResponse` with correct intent on valid LLM output |
| `test_handles_malformed_llm_output` | Verifies the pipeline gracefully handles non-JSON LLM output with a fallback response |

---

### Phase 3 — RAG Pipeline (`test_rag_pipeline.py`)

#### `TestChunking` — Document chunking strategies
| Test | Description |
|------|-------------|
| `test_produces_chunks` | Verifies `fixed_size` chunking produces multiple `Chunk` objects from a document |
| `test_overlap_creates_more_chunks` | Verifies that increasing overlap produces an equal or greater number of chunks |
| `test_recursive_split` | Verifies `recursive_split` chunking produces multiple chunks with correct source metadata |
| `test_splits_on_headers` | Verifies `semantic_sections` splits a markdown document on `#` headers |
| `test_metadata_preserved` | Verifies each chunk retains `source` and `chunk_index` in its metadata |

#### `TestVectorStore` — FAISS vector store operations
| Test | Description |
|------|-------------|
| `test_search_returns_results` | Verifies similarity search returns the requested number of results |
| `test_search_top_result_is_self` | Verifies the nearest neighbour of an embedding is the chunk it was indexed from |
| `test_save_and_load` | Verifies the FAISS index can be persisted to disk and reloaded with all chunks intact |

#### `TestEmbeddings` — Embedding model output
| Test | Description |
|------|-------------|
| `test_embed_returns_vector` | Verifies `EmbeddingModel.embed()` returns a 1024-dimensional float vector |

#### `TestRAGPipeline` — End-to-end RAG pipeline
| Test | Description |
|------|-------------|
| `test_ingest_text` | Verifies text ingestion creates chunks and populates the vector store |
| `test_retrieve` | Verifies retrieval returns relevant chunks for a given query |
| `test_query_includes_context_in_prompt` | Verifies the full query pipeline returns a `SupportResponse` with the correct intent |
| `test_query_returns_support_response` | Verifies the pipeline returns a typed `SupportResponse` with confidence > 0.5 |

---

## ⭐ Star This Repo

If you're following along with the series, star the repo to get notified when new phases drop.

---

**Author:** [Prateek Agrawal](https://medium.com/@ag.prateek)

#GenerativeAI #AIAgents #AmazonBedrock #BuildInPublic
