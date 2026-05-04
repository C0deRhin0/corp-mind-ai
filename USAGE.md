# corp-mind-ai Usage Guide

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Starting/Stopping Services](#startingstopping-services)
4. [Ingesting Documents](#ingesting-documents)
5. [Using the Application](#using-the-application)
6. [Troubleshooting](#troubleshooting)

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
- Start Qdrant (if not running)
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
| **Qdrant Dashboard** | http://localhost:6333/dashboard | Vector database UI |

---

## Ingesting Documents

### Supported Formats

| Format | Extensions | Notes |
|--------|-----------|-------|
| PDF | `.pdf` | Full page-by-page extraction |
| Word | `.docx` | Single page treated as one chunk |
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
2. You'll see the two-panel layout:

```
┌─────────────────────────────────────────────────────────────┐
│  corp-mind ● Connected                                     │
├─────────────────────────────────┬───────────────────────────┤
│                                 │                           │
│         CHAT (60%)              │    SOURCES (40%)          │
│                                 │                           │
│  ┌─────────────────────────┐    │  ┌─────────────────────┐ │
│  │ 🧑 How do I submit a   │    │  │ Source 1 of 3       │ │
│  │    travel claim?       │    │  │ ──────────────────── │ │
│  └─────────────────────────┘    │  │ 📄 policy.pdf p.4   │ │
│                                 │  │ Confidence: 91%      │ │
│  ┌─────────────────────────┐    │  │ "Employees must..." │ │
│  │ 🤖 To submit a travel  │    │  └─────────────────────┘ │
│  │    claim, log in to    │    │                           │
│  │    the HR portal...    │    │                           │
│  └─────────────────────────┘    │                           │
│                                 │                           │
│  ┌──────────────────────┐ [Ask] │                           │
│  │ Type your question...│       │                           │
│  └──────────────────────┘       │                           │
└─────────────────────────────────┴───────────────────────────┘
```

### Asking Questions

1. Type your question in the input box
2. Press Enter or click "Ask"
3. The answer streams in real-time
4. Sources appear in the right panel

### Example Questions

- "What is our remote work policy?"
- "How do I submit a travel reimbursement?"
- "What are the IT security requirements?"
- "What is the vacation policy?"

### Understanding Source Cards

Each source card shows:
- **Filename**: The document name
- **Page**: Which page the info came from
- **Confidence**: How relevant the match is (green = high, amber = medium)
- **Excerpt**: The actual text used to answer

---

## Troubleshooting

### Qdrant Won't Start

```bash
# Check if Docker is running
docker ps

# Start Qdrant manually
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant:latest
```

### Ollama Not Running

```bash
# Start Ollama
ollama serve

# Pull the model if needed
ollama pull llama3.2:3b
```

### Backend Errors

```bash
# Check backend logs
cat /tmp/backend.log

# Restart with
./start.sh
```

### No Documents Found

Make sure your documents are in a supported format:
- `.pdf`
- `.docx`
- `.txt`
- `.md`

### Empty Answers

1. Check that documents were ingested:
   - Go to http://localhost:6333/dashboard
   - Look at the `corp_docs` collection - should show vectors > 0

2. Try re-phrasing your question

3. Check that the LLM is working:
   - Go to http://localhost:8000/docs
   - Try the `/api/ask` endpoint directly

### Port Already in Use

```bash
# Find what's using the port
lsof -i :8000  # for backend
lsof -i :5173  # for frontend

# Kill the process
kill <PID>
```

---

## Configuration

### Change Ollama Model

Edit `codebase/backend/config.py`:

```python
OLLAMA_MODEL = "llama3.2:3b"  # Change to another model
```

### Change Embedding Model

Edit both:
- `codebase/ingestion/config.py`
- `codebase/backend/config.py`

```python
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Must match in both files
```

### Change Chunk Size

Edit `codebase/ingestion/config.py`:

```python
CHUNK_SIZE = 800        # Characters per chunk
CHUNK_OVERLAP = 150     # Overlap between chunks
```

---

## Development

### Backend Development

```bash
cd codebase/backend
source venv/bin/activate
python -m uvicorn main:app --reload --port 8000
```

### Frontend Development

```bash
cd frontend
npm run dev
```

### View API Docs

Go to http://localhost:8000/docs to see and test all API endpoints.

---

## Next Steps (Post-PoC)

- Add authentication
- Add document-level access control
- Switch to better embedding model (nomic-embed-text)
- Add scheduled re-indexing
- Add answer caching with Redis