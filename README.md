# corp-mind-ai

A secure, internal AI assistant that answers questions using company documents with high accuracy and traceability.

## Features

- **Hybrid Search**: Combines semantic (vector) and keyword (BM25) search for accurate results
- **Source Citations**: Every answer shows which documents were used
- **Local LLM**: Runs entirely on your machine - no data leaves your network
- **Easy Ingestion**: Drop documents in a folder, run one command to index them

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  SYSTEM A: INGESTION PIPELINE (admin only, runs offline)  │
│                                                             │
│  /data/docs/  ──► loader.py ──► chunker.py ──► embedder.py │
│                                                    │        │
│                                            Qdrant HTTP API  │
│                                            (upsert vectors) │
└────────────────────────────────────────────────┬────────────┘
                                                 │  shared Qdrant
┌────────────────────────────────────────────────▼────────────┐
│  SYSTEM B: QUERY APP (company-facing, always running)       │
│                                                             │
│  Browser ──► React UI ──► FastAPI ──► Qdrant (query only)  │
│                                  └──► Ollama (generate)     │
└─────────────────────────────────────────────────────────────┘
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React + Vite + TailwindCSS |
| Backend | FastAPI (Python) |
| Vector DB | Qdrant |
| LLM | Ollama (llama3.2:3b) |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |

## Quick Start

```bash
# 1. Start the application
./start.sh

# 2. Ingest your documents
./ingest.sh --dir /path/to/your/docs

# 3. Open browser
# http://localhost:5173
```

See [USAGE.md](USAGE.md) for detailed instructions.

## Project Structure

```
corp-mind-ai/
├── codebase/
│   ├── ingestion/          # Document ingestion pipeline
│   │   ├── main.py         # CLI entrypoint
│   │   ├── loader.py       # PDF/DOCX/TXT/MD parsing
│   │   ├── chunker.py      # Text chunking
│   │   ├── embedder.py     # Generate embeddings
│   │   └── qdrant_writer.py # Upload to Qdrant
│   │
│   └── backend/            # FastAPI server
│       ├── main.py         # App entrypoint
│       ├── api/routes_ask.py # API endpoints
│       ├── retrieval/      # Qdrant query logic
│       └── generation/     # Ollama LLM integration
│
├── frontend/               # React UI
│   ├── src/
│   │   ├── App.jsx         # Main layout
│   │   ├── components/     # UI components
│   │   └── api/            # API client
│   └── package.json
│
├── start.sh                # Start all services (one command!)
├── stop.sh                 # Stop all services
├── ingest.sh               # Ingest documents (--dir or --file)
└── USAGE.md                # Detailed usage guide
```

## Requirements

- Python 3.10+
- Node.js 18+
- Docker (for Qdrant)
- Ollama with llama3.2:3b model

## License

MIT