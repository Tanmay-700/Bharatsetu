# BharatSetu (भारतसेतु) — Multilingual AI Knowledge & Study Companion

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-FF6F61?style=for-the-badge)](https://www.trychroma.com)
[![Embeddings](https://img.shields.io/badge/Embeddings-BAAI%2Fbge--m3-blueviolet?style=for-the-badge)](https://huggingface.co/BAAI/bge-m3)
[![Cost](https://img.shields.io/badge/Operating_Cost-₹0%20(Free%20Tier)-brightgreen?style=for-the-badge)](#-100-free-stack-0-cost)

**A ₹0-cost, offline-first multilingual Retrieval-Augmented Generation (RAG) platform for educational textbooks and enterprise policy documents across 8+ Indian languages.**

[Features](#-key-features) • [Architecture](#-system-architecture) • [Supported Languages](#-supported-languages) • [API Endpoints](#-api-endpoints) • [Quickstart](#-quickstart-guide) • [Evaluation](#-running-the-evaluation-benchmark)

</div>

---

## 🌟 The Core Triplet Rule

```
Document Language (e.g., English / Gujarati)
                     │
                     ▼
         Cross-Lingual Retrieval
                     │
                     ▼
Student Question Language (e.g., Tamil)
                     │
                     ▼
Synthesized Answer Language (e.g., Tamil / Hindi)
```

- **Zero Upfront Document Translation**: PDFs remain in their native scripts. Documents are directly projected into a shared cross-lingual vector space.
- **Cross-Lingual Dense Retrieval**: A question asked in **Tamil** or **Hindi** seamlessly matches and retrieves relevant paragraphs originally written in **English** or **Gujarati**.
- **100% Free Stack (₹0 Cost)**: Vector calculations run **100% locally on CPU** using `BAAI/bge-m3` without requiring paid embedding APIs. LLM generation and query routing leverage the Google Gemini free tier.

---

## ⚡ Key Features

- **🧠 Dynamic Jev Domain Router**: An intelligent domain classifier that dynamically inspects active collections (e.g. `HR Policies`, `IT Security`, `Academic/Physics`) and routes queries to relevant domains rather than blindly searching everything.
- **🔄 Conversational Query Rewriter**: Resolves multi-turn pronoun references (e.g., *"What is its SI unit?"* → *"What is the SI unit of electric current?"*) before vector search, enabling natural multi-turn chat.
- **🛡️ Strict Anti-Hallucination Grounding**: Low-temperature reasoning (`temperature=0.2`) with rigorous grounding rules. The system evaluates mathematical conditions (e.g. prorated leave calculations) and flags document ambiguity instead of hallucinating false certainty.
- **🛑 Real-Time SSE Token Streaming with Stop/Cancel**: Smooth Server-Sent Events (SSE) token generation with full client-side abort support (`AbortController`), allowing users to cancel generation at any time with a single click or by pressing `Escape`.
- **⚡ Pre-Warmed Local Vector Engine**: `BAAI/bge-m3` is loaded directly from local disk (`local_files_only=True`) with multi-threaded CPU parallelization, ensuring instant zero-latency embedding without remote rate limits.
- **🌐 Dedicated Passage Translator**: Instantly translate any cited passage or policy clause into any of the 8 supported Indian languages on demand.

---

## 🏛️ System Architecture

```
                           ┌─────────────────────────┐
                           │      User / Student     │
                           └────────────┬────────────┘
                                        │
                                        ▼
                           React + TypeScript Frontend
                                        │
                         ┌──────────────┴──────────────┐
                         ▼                             ▼
                 PDF Upload Pipeline          Conversational RAG
                         │                             │
                         ▼                             ▼
                 Layout Parser (PyPDF)        Chat Memory (SQLite)
                         │                             │
                         ▼                             ▼
                 Semantic Chunker             Query Rewriter (LLM)
                         │                             │
                         ▼                             ▼
                Local BGE-M3 (CPU)            Jev Domain Router
                         │                             │
                         ▼                             ▼
                  ChromaDB Store ◄────────── Dense Query Vector
                         │
                         ▼
                    Top-K Chunks (Cosine Similarity)
                         │
                         ▼
                Prompt Factory (Grounding Rules)
                         │
                         ▼
              Gemini Free LLM (Streaming SSE)
                         │
                         ▼
           Grounded Answer + Page & Clause Citations
```

---

## 🌐 Supported Languages

| Code | Language | Native Script |
|:---:|:---:|:---:|
| `en` | **English** | English |
| `hi` | **Hindi** | हिन्दी |
| `ta` | **Tamil** | தமிழ் |
| `gu` | **Gujarati** | ગુજરાતી |
| `kn` | **Kannada** | ಕನ್ನಡ |
| `mr` | **Marathi** | मराठी |
| `pa` | **Punjabi** | ਪੰਜਾਬੀ |
| `od` | **Odia** | ଓଡ଼ିଆ |

---

## 🔌 API Endpoints

The backend provides a clean RESTful and SSE API under `/api/v1`:

| Method | Endpoint | Description |
|:---|:---|:---|
| `POST` | `/api/v1/chat` | Main SSE streaming Q&A endpoint with multi-turn memory & Jev routing. |
| `POST` | `/api/v1/documents/upload` | Multipart PDF upload with background chunking and vector indexing. |
| `GET` | `/api/v1/documents` | Lists all indexed documents, chunk counts, and processing statuses. |
| `GET` | `/api/v1/documents/domains`| Returns all unique active domains currently in the vector store. |
| `DELETE`| `/api/v1/documents/{id}` | Cascades deletion of document from disk, SQLite, and ChromaDB. |
| `GET` | `/api/v1/conversations` | Lists conversation history threads for the active user. |
| `POST` | `/api/v1/conversations` | Creates a new chat conversation thread. |
| `DELETE`| `/api/v1/conversations/{id}` | Deletes a conversation thread and its messages. |
| `POST` | `/api/v1/translate` | Dedicated passage translation endpoint across all 8 languages. |
| `GET` | `/health` | Service health status, embedding dimensions, and active models. |

---

## 📂 Project Structure

```
Bharatsetu/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/       # Chat (SSE), Conversations, Documents, Translate
│   │   ├── core/                   # Config, Database (aiosqlite), Logger
│   │   ├── models/                 # SQLAlchemy ORM models (Conversation, Message, Document, Chunk)
│   │   ├── schemas/                # Pydantic schemas for request/response validation
│   │   ├── services/
│   │   │   ├── chat/               # Conversation history, query rewriter, context assembler
│   │   │   ├── generation/         # Grounded prompts & Gemini streaming
│   │   │   ├── ingestion/          # PDF parser, semantic boundary chunker, pipeline
│   │   │   ├── retrieval/          # BGE-M3 embeddings, ChromaDB vector store, reranker
│   │   │   ├── routing/            # Jev dynamic domain classifier
│   │   │   └── translation/        # Dedicated passage translator
│   │   └── main.py                 # FastAPI application with lifecycle pre-warming
│   ├── data/
│   │   ├── uploads/                # Local PDF storage
│   │   ├── vectordb/               # ChromaDB persistent vector storage
│   │   └── bharatsetu.db           # SQLite database for threads and metadata
│   ├── requirements.txt            # Python dependencies
│   └── .env.example                # Environment variable template
├── frontend/
│   ├── src/
│   │   ├── api/                    # Axios REST client & native ReadableStream SSE client
│   │   ├── components/             # Sidebar, Header, ChatThread, Input (with Stop button), Citations
│   │   ├── types/                  # TypeScript domain models
│   │   └── App.tsx                 # Main application state and tab controller
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts              # Vite dev server with proxy to :8000
├── evaluation/
│   ├── benchmark_dataset.json      # Multilingual test dataset
│   └── evaluate_jev.py             # A/B evaluation runner (Direct vs Jev-Routed)
├── run.py                          # Unified launcher for backend and frontend
└── README.md
```

---

## 🚀 Quickstart Guide

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** & `npm`
- Free Google Gemini API Key from [Google AI Studio](https://aistudio.google.com/)

---

### Option A: Quick Launch with `run.py`

```powershell
# 1. Clone repository
git clone https://github.com/Tanmay-700/Bharatsetu.git
cd Bharatsetu

# 2. Configure environment
copy backend\.env.example backend\.env
# Open backend\.env and insert your free GEMINI_API_KEY

# 3. Install dependencies
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..

# 4. Start both servers
python run.py
```

---

### Option B: Manual Step-by-Step Setup

#### 1. Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate       # On Linux/macOS: source venv/bin/activate

pip install -r requirements.txt
copy .env.example .env      # Add your GEMINI_API_KEY in .env

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
* Interactive Swagger API documentation: `http://localhost:8000/docs`

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
* Web Application: `http://localhost:3000`

---

## 🧪 Running the Evaluation Benchmark

To verify retrieval precision across languages:

```bash
python evaluation/evaluate_jev.py
```
This runs an A/B benchmark comparing **System A (Direct Search)** against **System B (Jev-Routed Search)** across educational and enterprise policy test queries.

---

## 💻 Hardware Requirements

- **CPU**: Intel Core i5 / AMD Ryzen 5 or higher (Multi-core recommended for CPU embeddings).
- **RAM**: Minimum 8 GB (16 GB recommended).
- **GPU**: **None required** — fully optimized for CPU inference.

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
