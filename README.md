# BharatSetu (भारतसेतु) — Multilingual AI Knowledge & Study Companion

A generalized, multilingual RAG-based AI system supporting **20 authorized PDFs (~2,000 pages)** across **8 Indian languages + English**:
- English (`en`)
- Hindi (`hi`)
- Odia (`od`)
- Tamil (`ta`)
- Kannada (`kn`)
- Marathi (`mr`)
- Punjabi (`pa`)
- Gujarati (`gu`)

---

## 🌟 Core Philosophy

```
Original language in → multilingual semantic retrieval → relevant evidence → grounded LLM generation → student's chosen language out
```

- **Zero Upfront Translation**: Documents remain in their original languages (e.g. English, Gujarati).
- **Cross-Lingual Retrieval**: A question asked in **Tamil** retrieves relevant chunks in **English** or **Gujarati** using cross-lingual dense representations.
- **ChatGPT-Style Multi-Turn Memory**: `conversation_id` threads all turns together. The Query Rewriter resolves pronouns and coreferences (e.g. *"What is its SI unit?"* → *"What is the SI unit of electric current?"*).
- **Dynamic Jev Domain Router**: Routes questions to active domains (e.g. `HR Policies`, `IT Security`, `Physics`) instead of scanning all documents blindly.
- **100% Free Stack (₹0 Cost)**: Powered by local `bge-m3` on CPU and the Google Gemini Free API tier.

---

## 🏛️ System Architecture

```
                       ┌──────────────────────┐
                       │     USER / STUDENT   │
                       └──────────┬───────────┘
                                  │
                                  ▼
                         React + TypeScript UI
                                  │
                       ┌──────────┴──────────┐
                       │                     │
                  PDF Upload              Question
                       │                     │
                       ▼                     ▼
                FastAPI Backend        Query Understanding
                       │                     │
                       ▼                     ▼
                PDF Processing           Jev Router
                       │                     │
                       ▼               Domain Routing
                   Chunking                  │
                       │                     │
                       ▼                     │
             Multilingual bge-m3             │
                       │                     │
                       ▼                     ▼
                 ChromaDB DB  ◄──────── Query Vector
                       │
                       ▼
                 Top-K Chunks
                       │
                       ▼
              bge-reranker-v2-m3
                       │
                       ▼
                 Best Evidence
                       │
                       ▼
                 Gemini Free LLM
                       │
                       ▼
              Grounded Answer with Sources
```

---

## 📂 Project Structure

```
Bharatsetu/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/       # Chat, Conversations, Documents, Translate
│   │   ├── core/                   # Config, Database (SQLite), Logger
│   │   ├── models/                 # SQLAlchemy models (Conversation, Message, Document, Chunk)
│   │   ├── schemas/                # Pydantic schemas
│   │   ├── services/
│   │   │   ├── ingestion/          # PDF parser, semantic chunker, pipeline
│   │   │   ├── retrieval/          # bge-m3 embeddings, ChromaDB, bge-reranker
│   │   │   ├── routing/            # Jev dynamic domain router
│   │   │   ├── chat/               # Conversation service, query rewriter, context manager
│   │   │   ├── generation/         # Multilingual prompts & Gemini streaming
│   │   │   └── translation/        # Dedicated passage translator
│   │   └── main.py                 # FastAPI application
│   ├── data/
│   │   ├── uploads/                # Stored PDFs
│   │   ├── vectordb/               # ChromaDB index
│   │   └── bharatsetu.db           # SQLite database
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── api/                    # Axios & SSE streaming client
│   │   ├── components/             # Sidebar, Header, ChatThread, Input, Citations, Vault
│   │   ├── types/                  # TypeScript interfaces
│   │   └── App.tsx                 # Main UI
│   ├── package.json
│   └── vite.config.ts
├── evaluation/
│   ├── benchmark_dataset.json      # Multilingual QA test cases
│   └── evaluate_jev.py             # System A vs System B A/B evaluation
└── README.md
```

---

## 🚀 Quickstart Guide

### 1. Backend Setup

```bash
cd backend

# Create virtual environment (optional)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure .env
copy .env.example .env
# Edit .env and paste your GEMINI_API_KEY from https://aistudio.google.com/

# Generate sample documents
python scripts/create_sample_docs.py

# Start FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend Setup

```bash
cd frontend

# Install npm dependencies
npm install

# Start development server
npm run dev
```

Open `http://localhost:3000` in your browser.

---

## 🧪 Running the Jev A/B Evaluation Benchmark

```bash
python evaluation/evaluate_jev.py
```
This tests **System A (Direct Search)** vs **System B (Jev-Routed Search)** across multilingual queries.
