# corp-mind-ai Usage Guide

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Starting/Stopping Services](#startingstopping-services)
4. [Ingesting Documents](#ingesting-documents)
5. [Using the Application](#using-the-application)
6. [Admin Panel](#admin-panel)
7. [Search & Conversation History](#search--conversation-history)
8. [Answer Caching](#answer-caching)
9. [Diagnostics](#diagnostics)
10. [Configuration](#configuration)
11. [Troubleshooting](#troubleshooting)
12. [Development](#development)

---

## Prerequisites

Before running the application, ensure you have:

| Requirement | Check Command | Installation |
|-------------|---------------|--------------|
| Python 3.10+ | `python3 --version` | [python.org](https://www.python.org/) |
| Node.js 18+ | `node --version` | [nodejs.org](https://nodejs.org/) |
| Docker | `docker --version` | [docker.com](https://www.docker.com/) |
| Ollama | `ollama --version` | [ollama.ai](https://ollama.ai/) |

### Install Ollama Model

```bash
# Pull the required LLM model
ollama pull llama3.2:3b
```

### Python Virtual Environment

The backend uses a virtual environment at `codebase/backend/venv/`. If it doesn't exist:

```bash
cd codebase/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Quick Start

```bash
# 1. Start everything (Ollama, Qdrant, Backend, Frontend)
./start.sh

# 2. Ingest your documents
./ingest.sh --dir /path/to/your/documents

# 3. Open http://localhost:5173 in your browser
```

---

## Starting/Stopping Services

### Start All Services

```bash
./start.sh
```

This one command will:
- Start Ollama (if not running)
- Start Qdrant in Docker (if not running)
- Start the FastAPI backend on port 8000
- Start the Vite frontend on port 5173

### Stop Services

```bash
./stop.sh
```

This stops the Backend and Frontend. Ollama and Qdrant keep running (so they're ready next time).

### Service URLs

| Service | URL | Description |
|---------|-----|-------------|
| **App** | http://localhost:5173 | Main UI |
| **API Docs** | http://localhost:8000/docs | FastAPI Swagger docs |
| **Admin Panel** | http://localhost:5173/#/admin | Document management UI |
| **Qdrant Dashboard** | http://localhost:6333/dashboard | Vector database UI |

---

## Ingesting Documents

### Supported Formats

| Format | Extensions | Notes |
|--------|-----------|-------|
| PDF | `.pdf` | Full page-by-page extraction |
| Word | `.docx` | Entire document treated as single page |
| Text | `.txt` | Plain text |
| Markdown | `.md`, `.markdown` | Treated as plain text |

### Ingest a Folder

```bash
./ingest.sh --dir /path/to/your/documents
```

### Ingest a Single File

```bash
./ingest.sh --file /path/to/document.pdf
```

### Reset and Re-ingest

To delete all indexed data and start fresh:

```bash
./ingest.sh --dir /path/to/documents --reset
```

### Example

```bash
# Create a sample documents folder
mkdir -p ~/company-docs
cp ~/Documents/policy.pdf ~/company-docs/
cp ~/Documents/handbook.md ~/company-docs/

# Ingest them
./ingest.sh --dir ~/company-docs
```

Expected output:

```
🔍 Found 2 document(s) in /Users/.../company-docs

📄 Processing: policy.pdf
  → 5 pages, 12 chunks
  Loading embedding model: BAAI/bge-small-en-v1.5
  Upserted batch 1: 12 points
  ✅ Done: policy.pdf

📄 Processing: handbook.md
  → 1 pages, 3 chunks
  Upserted batch 1: 3 points
  ✅ Done: handbook.md

========================================
INGESTION COMPLETE
  Files:  2 ingested, 0 skipped
  Chunks: 15 total
  Qdrant: 15 vectors in collection
========================================
```

---

## Using the Application

### Opening the App

1. Open http://localhost:5173 in your browser
2. You'll see the two-panel layout with a NuecAI header

```
┌─────────────────────────────────────────────────────────────┐
│  🧠 NuecAI                                                 │
│  Corporate Mind                                             │
├─────────────────────────────────┬───────────────────────────┤
│                                 │                           │
│         CHAT (60%)              │    SOURCES (40%)          │
│                                 │                           │
│  ┌─────────────────────────┐    │  ┌─────────────────────┐ │
│  │ 🧑 What is the paid    │    │  │ Source 1 of 3       │ │
│  │    leave policy?        │    │  │ ─────────────────── │ │
│  └─────────────────────────┘    │  │ 📄 policy.pdf      │ │
│                                 │  │    Page 4           │ │
│  ┌─────────────────────────┐    │  │ Confidence: ████░░ │ │
│  │ 🤖 The paid leave      │    │  │                     │ │
│  │    policy provides...   │    │  │ "Employees are      │ │
│  │                         │    │  │  entitled to..."    │ │
│  │  [View Sources ▾]       │    │  │ [Expand ▾]          │ │
│  └─────────────────────────┘    │  └─────────────────────┘ │
│                                 │                           │
│  ┌──────────────────────┐ [Ask] │                           │
│  │ Type your question...│       │                           │
│  └──────────────────────┘       │                           │
└─────────────────────────────────┴───────────────────────────┘
```

### Asking Questions

1. Type your question in the input box
2. Press Enter or click "Ask"
3. The answer streams in real-time as tokens arrive
4. Sources appear in the right panel after the answer completes

### Example Questions

- "What is our paid leave policy?"
- "How do I submit a travel reimbursement?"
- "What are the data privacy requirements?"
- "What is the summer dress code?"
- "When is the next holiday?"

### Understanding Source Cards

Each source card shows:
- **Filename**: The document name (without extension)
- **Page**: Which page the info came from
- **Confidence**: How relevant the match is (color-coded bar)
- **Excerpt**: The actual text used — click "Expand" to see the full chunk

Confidence color coding:
- **≥75%**: Green (highly relevant)
- **50–74%**: Amber (moderately relevant)
- **25–49%**: Orange (somewhat relevant)
- **<25%**: Red (filtered server-side, should rarely appear)

### Search History

- The app remembers your recent queries (last 10)
- Click the search history icon in the input area to see past questions
- Click any past question to re-ask it instantly

### Conversation History

- The app groups messages into conversations
- Each conversation has a unique ID
- Conversations persist in your browser's localStorage
- Refreshing the page restores the last conversation
- Click "Clear Chat" to start a new conversation

---

## Admin Panel

Access at: `http://localhost:5173/#/admin`

### Login

1. Navigate to http://localhost:5173/#/admin
2. Enter the admin code from your `.env` file
3. Click "Login"

The default admin code is `NuecAI-ADMIN-2026` (set in `.env` as `ADMIN_CODE`).

### Features

#### Upload Documents

1. Click the upload area or drag & drop files
2. Supported formats: PDF, DOCX, TXT, MD
3. Maximum file size: 50MB (configurable in `.env`)
4. Uploaded files are automatically ingested into the vector store

#### List Documents

View all currently ingested documents with their filenames.

#### Delete Documents

Remove a specific document from the vector store. This deletes all chunks associated with that filename.

#### Reset & Re-ingest

- **Reset**: Wipes the entire vector collection
- **Re-ingest**: After a reset (or to refresh all documents), re-processes all files from the documents directory

---

## Search & Conversation History

### How History Works

- **Search History**: Your last 10 questions are saved in `localStorage`. Click any past question to re-ask it. The popup appears when you focus on the input field.

- **Conversation History**: Each browser session maintains a "conversation" with a unique ID. This ID is sent with every question so the backend can associate messages. On page refresh, your last conversation is restored.

### Persistence

| Data | Storage | Persists After |
|------|---------|----------------|
| Search history | localStorage | Page refresh, browser close |
| Conversation messages | localStorage | Page refresh, browser close |
| Answer cache | Backend memory (RAM) | Backend restart (cleared) |
| Documents | Qdrant (disk) | Everything |

---

## Answer Caching

To reduce latency and Ollama load, the backend caches answers for **2 hours**.

### How It Works

- Questions are normalized (lowercased, trimmed) and hashed with SHA-256
- If the same question is asked again within 2 hours, the cached answer is returned instantly
- Cached responses show up immediately in the UI (no streaming delay)

### Manage Cache

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/cache/stats` | GET | View number of cached answers and TTL |
| `/api/cache/clear` | POST | Clear all cached answers |

### When to Clear Cache

- After re-ingesting documents with new information
- If an answer seems stale or incorrect
- During development and testing

---

## Diagnostics

The `/api/diagnostics` endpoint provides a health check for all services:

```bash
curl http://localhost:8000/api/diagnostics
```

Example response:

```json
{
  "qdrant": {
    "name": "Qdrant",
    "url": "http://localhost:6333",
    "status": "ok",
    "details": {
      "collection": "corp_docs",
      "points": 99,
      "status": "green"
    }
  },
  "ollama": {
    "name": "Ollama",
    "url": "http://localhost:11434",
    "status": "ok",
    "details": {
      "model": "llama3.2:3b",
      "available": true,
      "models": [
        "llama3.2:3b",
        "llama3.1:8b",
        "qwen2.5:7b"
      ]
    }
  },
  "overall": "ok"
}
```

Use this to verify all services are healthy before troubleshooting chat issues.

---

## Configuration

### `.env` File

Create a `.env` file in the project root (if not present):

```env
ADMIN_CODE=NuecAI-ADMIN-2026
MAX_FILE_SIZE_MB=50
DOCS_DIR=./documents
```

| Variable | Default | Description |
|----------|---------|-------------|
| `ADMIN_CODE` | *(empty)* | Secret code for admin panel access |
| `MAX_FILE_SIZE_MB` | `50` | Maximum upload file size |
| `DOCS_DIR` | `./documents` | Default documents directory |

> **Note**: The `.env` file must exist AND `load_dotenv()` must run before any module-level `os.getenv()` calls. The backend handles this correctly by loading `.env` at app startup.

### Change Ollama Model

Edit `codebase/backend/config.py`:

```python
OLLAMA_MODEL = "llama3.2:3b"  # Change to another installed Ollama model
```

### Change Embedding Model

Edit **both** files — they MUST match:

1. `codebase/ingestion/ingestion_config.py`:
```python
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
VECTOR_SIZE = 384  # Must match the model's output dimension
```

2. `codebase/backend/config.py`:
```python
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"  # Must match ingestion
```

After changing the embedding model, you **must** re-ingest all documents:
```bash
./ingest.sh --dir /path/to/docs --reset
```

### Change Chunk Size

Edit `codebase/ingestion/ingestion_config.py`:

```python
CHUNK_SIZE = 800        # Characters per chunk
CHUNK_OVERLAP = 150     # Overlap between consecutive chunks
```

### Change Retrieval Parameters

Edit `codebase/backend/config.py`:

```python
TOP_K = 10              # Number of chunks sent to the LLM
SCORE_THRESHOLD = 0.2   # Minimum relevance score (0.0 to 1.0)
```

### Change Cache TTL

Edit `codebase/backend/api/routes_ask.py`:

```python
CACHE_TTL_SECONDS = 7200  # 2 hours (change to any value in seconds)
```

---

## Troubleshooting

### Backend Won't Start

```bash
# Check the log
cat /tmp/backend.log

# Common errors:

# "ImportError: cannot import name 'CHUNK_SIZE' from 'config'"
#   → This means ingestions modules are importing from the wrong config.py.
#     The ingestion config was renamed to `ingestion_config.py` to avoid this
#     collision. Make sure imports in chunker.py, embedder.py, qdrant_writer.py
#     use `from ingestion_config import ...`

# "Address already in use"
#   → Kill the existing process: kill <PID> or lsof -ti :8000 | xargs kill -9

# "command not found: python"
#   → Use python3 instead. Ensure start.sh and ingest.sh use python3.
```

### Admin Login Fails ("Admin code not configured")

1. Check that `.env` exists in the project root with `ADMIN_CODE` set
2. Restart the backend: `./stop.sh && ./start.sh`
3. If it still fails, the `.env` file may not be loading — check that `load_dotenv()` runs before any config reads. The backend handles this, but module-level `os.getenv()` calls in `routes_admin.py` were moved into lazy functions to fix this exact issue.

### Qdrant Won't Start

```bash
# Check if Docker is running
docker ps

# Start Qdrant manually
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant:latest

# Check if container exists but is stopped
docker start qdrant
```

### Ollama Not Running

```bash
# Start Ollama
ollama serve

# Pull the model if needed
ollama pull llama3.2:3b
```

### Chat Returns "I apologize, but I encountered an error"

1. Check diagnostics: `curl http://localhost:8000/api/diagnostics`
2. Verify all services show `"status": "ok"`
3. Check the backend log: `cat /tmp/backend.log`
4. Try the `/api/ask` endpoint directly via Swagger at http://localhost:8000/docs
5. Ensure documents have been ingested (Qdrant points > 0)

### No Documents Found

Check that Qdrant has data:
```bash
# Via API
curl http://localhost:8000/api/diagnostics
# Check the "points" field — should be > 0

# Via Qdrant dashboard
# Open http://localhost:6333/dashboard and check the corp_docs collection
```

### Empty or Wrong Answers

1. Try re-phrasing your question
2. Check if the embedding model matches between ingestion and backend:
   - `codebase/ingestion/ingestion_config.py` — `EMBEDDING_MODEL`
   - `codebase/backend/config.py` — `EMBEDDING_MODEL`
3. Re-ingest documents after any config change: `./ingest.sh --dir /path/to/docs --reset`
4. Clear the answer cache: `curl -X POST http://localhost:8000/api/cache/clear`

### Port Already in Use

```bash
# Find what's using the port
lsof -i :8000  # for backend
lsof -i :5173  # for frontend
lsof -i :6333  # for Qdrant

# Kill the process
kill <PID>

# Force kill if needed
kill -9 <PID>
```

### First Request is Slow

The first question after starting the backend will be slow because:
1. The embedding model (BAAI/bge-small-en-v1.5) must load into memory (~3-5 seconds)
2. The LLM model (llama3.2:3b) may need to load if Ollama unloaded it

Subsequent requests will be much faster. The answer cache also helps with repeated questions.

---

## Development

### Backend Development

```bash
cd codebase/backend
source venv/bin/activate
python3 -m uvicorn main:app --reload --port 8000
```

### Frontend Development

```bash
cd frontend
npm run dev
```

### View API Docs

Go to http://localhost:8000/docs to see and test all API endpoints, including:
- `/api/ask` — Chat
- `/api/ask/stream` — Streaming chat (SSE)
- `/api/diagnostics` — Health check
- `/api/cache/stats` — Cache statistics
- `/api/cache/clear` — Clear cache
- `/api/admin/login` — Admin authentication
- `/api/admin/documents` — Document management
- `/api/health` — Simple health check

### Run Ingestion Independently

```bash
cd codebase/ingestion
source venv/bin/activate
python3 main.py --dir /path/to/docs
```

---

## API Reference

### Streaming Chat (SSE)

The frontend connects to `GET /api/ask/stream?question=...` using an `EventSource`.

Events:

| Type | Payload | Description |
|------|---------|-------------|
| `token` | `{"type":"token","text":"..."}` | A single token from the LLM stream |
| `sources` | `{"type":"sources","sources":[...]}` | Source documents with scores, confidence, excerpts |
| `cached` | `{"type":"cached","value":true}` | Indicates the response was served from cache |
| `error` | `{"type":"error","message":"..."}` | An error occurred with a user-friendly message |
| `[DONE]` | `data: [DONE]` | End of stream signal |

### Confidence Score Calculation

The confidence score shown in source cards is calculated as:

```
confidence = min(100, max(0, (score / 0.8) * 100))
```

- A score of 0.8 → 100% (perfect match)
- A score of 0.4 → 50% (moderate match)
- A score of 0.2 → 25% (weak match, threshold floor)

---

## Post-PoC Upgrade Ideas

- Add user authentication and session management
- Server-side conversation history for multi-device persistence
- Replace in-memory cache with Redis
- Add document-level access control (RBAC)
- Improve sparse vectors with SPLADE or FastEmbed
- Scheduled re-indexing via cron
- Rate limiting for production deployment
