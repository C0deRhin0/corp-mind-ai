from pathlib import Path

# Paths
DOCS_DIR = Path("../data/docs")         # default; overridden by CLI --dir

# Qdrant
QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "corp_docs"
VECTOR_SIZE = 384                        # BAAI/bge-small-en-v1.5 output dim

# Chunking
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

# Embedding model — MUST match backend/config.py
# Options: 
#   - all-MiniLM-L6-v2 (384-dim) - original, works
#   - BAAI/bge-small-en-v1.5 (384-dim) - better quality, still works
#   - BAAI/bge-base-en-v1.5 (768-dim) - best quality but larger
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

# Batch size for upsert (avoids memory spikes on large corpora)
UPSERT_BATCH_SIZE = 64
