# BharatSetu (भारतसेतु) — Complete Project Handoff & Architecture Context

> **Note for AI Models / Engineers reading this document:**
> This document is a complete, self-contained snapshot of the **BharatSetu** codebase. It outlines all architecture decisions, constraints, completed files, and system workflows. Use this to continue development, debugging, or optimization seamlessly.

---

## 1. Executive Summary

- **Project Name**: BharatSetu (भारतसेतु)
- **Primary Function**: A generalized, multilingual Retrieval-Augmented Generation (RAG) assistant designed for **20 authorized PDFs (~100 pages each = ~2,000 pages total)**.
- **Scope**: Supports both **educational textbooks** (Physics, Chemistry, Math, Biology) and **enterprise/corporate documents** (HR policies, IT security protocols, compliance guidelines, legal contracts).
- **Supported Languages (8 Indic + English)**:
  - English (`en`), Hindi (`hi`), Odia (`od`), Tamil (`ta`), Kannada (`kn`), Marathi (`mr`), Punjabi (`pa`), Gujarati (`gu`).
- **Core Triplet Rule**: The PDF language, the student/user question language, and the generated answer language **can all be different** (e.g., Gujarati PDF chunk → Tamil question → Tamil answer).

---

## 2. Non-Negotiable Architectural Principles

1. **Zero Upfront Document Translation**:
   - Chunks remain in their original script (e.g. Gujarati, Tamil).
   - They are directly projected into a multilingual vector space.
   - We **never** translate PDFs to English before embedding.
2. **100% Free Stack (₹0 Cost)**:
   - No paid OpenAI, Anthropic, or Cohere APIs.
   - LLM: **Google Gemini Free API** (`gemini-2.0-flash` on AI Studio free tier).
   - Embeddings: **`BAAI/bge-m3`** running locally on CPU.
   - Reranker: **`BAAI/bge-reranker-v2-m3`** running locally on CPU.
   - Vector Store: **ChromaDB** (with built-in high-performance in-memory fallback).
   - Database: **SQLite** via `aiosqlite`.
   - Single User Auth: Hardcoded `user_1` (no login barriers).
3. **No IndicTrans2 in v1**:
   - Gemini handles all cross-lingual understanding and answer generation directly.
   - Explicit passage translation uses a dedicated Gemini translation endpoint.
4. **Dynamic Jev Domain Router**:
   - Jev is a domain classifier running on Gemini Flash.
   - It queries active domains dynamically from the database (e.g., `["HR Policies", "IT Security", "Physics"]`) and routes user queries to the relevant domain(s) to narrow the vector search space safely without discarding documents blindly.
5. **ChatGPT-Style Multi-Turn Memory**:
   - Every chat gets a persistent `conversation_id`.
   - Multi-turn pronoun references (e.g., *"What is its SI unit?"* or *"How many days are allowed?"*) are resolved by an LLM-powered **Query Rewriter** before vector search.

---

## 3. Hardware Profile & Performance Expectations

- **User Machine**: Lenovo Laptop with **Intel Core i5-1250H** (12 cores / 16 threads: 4 P-cores + 8 E-cores).
- **GPU**: None (CPU-only execution).
- **Ingestion Speed**: ~1 to 1.5 minutes per 100-page PDF on 12 CPU cores. All 20 books (~2,000 pages) take ~25–30 minutes total (performed **once** offline).
- **Query Latency**: ~2.0 to 3.5 seconds end-to-end (query rewrite: ~300ms, Jev: ~200ms, embedding on CPU: ~150ms, search: ~10ms, reranker: ~300ms, Gemini streaming: ~1.5s).

---

## 4. End-to-End System Workflows

### A. One-Time Document Ingestion Workflow
```
PDF Upload (e.g., Employee_Leave_Policy.pdf in English or Physics in Gujarati)
    │
    ▼
PDF Parser (`pdfplumber` with `pypdf` fallback)
    │
    ▼
Semantic Chunker (~400 words, 50-word overlap, section & clause boundary detection)
    │
    ▼
Multilingual Embedding (`bge-m3` on multi-core CPU)
    │
    ▼
ChromaDB Persistent Store (Vectors + {document_id, domain, section, page, language})
    │
    ▼
SQLite DB (Document status set to "completed")
```

### B. Multi-Turn Query Workflow (Online)
```
User asks: "What is its SI unit?" in Tamil
    │
    ▼
1. SQLite: Fetches recent conversation messages using `conversation_id`
    │
    ▼
2. Query Rewriter (Gemini Flash): Rewrites to "What is the SI unit of electric current?"
    │
    ▼
3. Jev Domain Router (Gemini Flash): Dynamically inspects active domains → routes to ["Physics"]
    │
    ▼
4. bge-m3: Embeds rewritten query into 1024-dim vector (~150ms on CPU)
    │
    ▼
5. ChromaDB: Scans vectors filtered by `domain == "Physics"`
    │
    ▼
6. bge-reranker: Rescores candidate chunks using cross-attention (top 25 → top 5)
    │
    ▼
7. Gemini LLM: Receives {Rewritten Question, Gujarati/English Evidence Chunks, Target Language: Tamil}
    │
    ▼
8. SSE Stream: Real-time tokens streamed to frontend + verified citations attached
    │
    ▼
9. SQLite: Saves assistant response, rewritten question, and source citations
```

---

## 5. Complete Inventory of Created Files

### Backend (`c:\Bharatsetu\backend`)
| File Path | Description |
| :--- | :--- |
| `app/main.py` | FastAPI application entry point with CORS, `/health`, and DB lifespan. |
| `app/core/config.py` | Settings class supporting 8 Indic languages, paths, and environment vars. |
| `app/core/database.py` | SQLAlchemy async SQLite engine (`aiosqlite`) with `init_db`. |
| `app/core/logger.py` | Zero-dependency logging using Python's standard `logging` library. |
| `app/models/models.py` | ORM models: `Conversation`, `Message`, `Document`, `Chunk`. |
| `app/schemas/schemas.py` | Pydantic validation schemas for all requests and responses. |
| `app/services/ingestion/parser.py` | PDF text extraction using `pdfplumber` with `pypdf` fallback. |
| `app/services/ingestion/chunker.py` | Semantic chunker with section/clause detection and overlap. |
| `app/services/ingestion/metadata.py` | SHA256 file hashing (idempotency) and script-based language detection. |
| `app/services/ingestion/pipeline.py` | Background ingestion orchestrator connecting parser, chunker, and vector store. |
| `app/services/retrieval/embeddings.py` | `bge-m3` embedding service with CPU thread allocation and fallback. |
| `app/services/retrieval/vector_store.py` | ChromaDB vector store with dynamic domain filtering & in-memory fallback. |
| `app/services/retrieval/reranker.py` | `bge-reranker-v2-m3` cross-encoder reranker service. |
| `app/services/routing/jev_router.py` | Dynamic Jev domain router using Gemini Flash JSON mode. |
| `app/services/chat/conversation_service.py`| SQLite CRUD operations for conversations, messages, and titles. |
| `app/services/chat/query_rewriter.py` | Pronoun and coreference resolution service. |
| `app/services/chat/context_manager.py` | Assembles sliding window chat turns and formatted citations. |
| `app/services/generation/prompts.py` | Domain-adaptive multilingual prompts for educational vs corporate policies. |
| `app/services/generation/llm.py` | Gemini client for real-time Server-Sent Events (SSE) streaming. |
| `app/services/translation/__init__.py`| Dedicated passage translation service. |
| `app/api/v1/router.py` | Combines chat, conversations, documents, and translate endpoints. |
| `app/api/v1/endpoints/chat.py` | SSE streaming Q&A endpoint. |
| `app/api/v1/endpoints/conversations.py`| Chat thread management endpoints. |
| `app/api/v1/endpoints/documents.py` | PDF upload, background processing, and status endpoints. |
| `app/api/v1/endpoints/translate.py` | Explicit passage translation endpoint. |
| `scripts/create_sample_docs.py` | Generates sample PDFs for testing (HR, IT, Physics). |
| `requirements.txt` | Python dependency specification. |
| `.env.example` | Environment variable template. |

### Frontend (`c:\Bharatsetu\frontend`)
| File Path | Description |
| :--- | :--- |
| `src/App.tsx` | Main application shell with tab switching and SSE state management. |
| `src/main.tsx` | React 18 DOM mount. |
| `src/index.css` | Tailwind directives and custom scrollbar rules. |
| `src/types/index.ts` | TypeScript interfaces for conversations, messages, citations, languages. |
| `src/api/client.ts` | Axios instance configured for `/api/v1`. |
| `src/api/chat.ts` | Fetch `ReadableStream` SSE client for live streaming tokens. |
| `src/api/conversations.ts`| REST client for conversation threads. |
| `src/api/documents.ts` | Multipart upload and document status client. |
| `src/api/translate.ts` | Translation API client. |
| `src/components/Sidebar.tsx` | ChatGPT-style sidebar with conversation history and new chat trigger. |
| `src/components/Header.tsx` | Top bar with title, Jev routing badge, and language dropdown. |
| `src/components/Chat/ChatThread.tsx`| Message bubbles, markdown formatting, citations, and live typing cursor. |
| `src/components/Chat/ChatInput.tsx` | Auto-expanding textarea, language switcher, and follow-up suggestion pills. |
| `src/components/Chat/CitationCard.tsx`| Card showing document, domain, section, page, and "Translate Passage" button. |
| `src/components/Documents/DocumentManager.tsx`| Drag & drop PDF uploader, domain tagger, and indexed documents table. |
| `src/components/Translate/TranslationDrawer.tsx`| Dedicated passage translator across all 8 languages. |
| `package.json` | Vite, React, Tailwind, Lucide, and Markdown dependencies. |
| `vite.config.ts` | Vite config with port 3000 and proxy to port 8000. |
| `tailwind.config.js` | Tailwind custom colors and typography config. |

### Evaluation & Samples (`c:\Bharatsetu\evaluation` & `data/samples`)
| File Path | Description |
| :--- | :--- |
| `evaluation/benchmark_dataset.json` | Test questions across Hindi, Tamil, Gujarati, English. |
| `evaluation/evaluate_jev.py` | A/B evaluation runner (System A: Direct vs System B: Jev-Routed). |
| `backend/data/samples/Company_Leave_Policy.pdf` | Generated test PDF (HR Policies). |
| `backend/data/samples/IT_Security_Protocol.pdf` | Generated test PDF (IT Security). |
| `backend/data/samples/Physics_Class10_Electricity.pdf`| Generated test PDF (Physics). |

---

## 6. Verification & Automated Test Results

Automated test command:
```bash
python -m pytest backend/tests/ -v
```

**Results (4/4 Passed in 0.85s)**:
- `backend/tests/test_chat_memory.py::test_conversation_memory_lifecycle PASSED` [25%]
- `backend/tests/test_chunker.py::test_chunker_basic PASSED` [50%]
- `backend/tests/test_routing.py::test_jev_router_single_domain PASSED` [75%]
- `backend/tests/test_routing.py::test_jev_router_empty_domains PASSED` [100%]

---

## 7. How to Run the Application

### 1. Backend Server
```powershell
cd c:\Bharatsetu\backend
# Provide your free Gemini API key in backend/.env:
# GEMINI_API_KEY="AIzaSy..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Swagger UI will be accessible at: `http://localhost:8000/docs`

### 2. Frontend Development Server
```powershell
cd c:\Bharatsetu\frontend
npm install
npm run dev
```
Open: `http://localhost:3000`

---

## 8. Suggested Next Steps for the Next AI / Engineer
1. **Gemini API Key**: Add the user's free API key in `backend/.env` to enable live streaming answers.
2. **Frontend Run**: Run `npm install` and `npm run dev` in `frontend/` to test UI interactions.
3. **Ingest Sample Docs**: Upload the 3 sample PDFs from `backend/data/samples/` via the UI or a script.
4. **Evaluate Jev**: Run `python evaluation/evaluate_jev.py` to inspect A/B metrics once Gemini API key is configured.
