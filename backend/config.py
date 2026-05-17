import os

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = "corp_docs"

# CRITICAL: Must be the same model used during ingestion
# Options: 
#   - all-MiniLM-L6-v2 (384-dim) - original, works
#   - BAAI/bge-small-en-v1.5 (384-dim) - better quality, still works
#   - BAAI/bge-base-en-v1.5 (768-dim) - best quality but larger
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

# Retrieval config
TOP_K = 10           # chunks sent to LLM (increased for more context)
SCORE_THRESHOLD = 0.2   # drop chunks below this fused score
