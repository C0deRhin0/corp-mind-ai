import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
INGESTION_DIR = ROOT_DIR / "ingestion"
sys.path.insert(0, str(INGESTION_DIR))

from loader import load_document
from chunker import chunk_pages
from embedder import embed
from qdrant_writer import ensure_collection, upsert_chunks
from ingestion_config import DOCS_DIR, QDRANT_URL, COLLECTION_NAME

def ingest_documents(reset: bool = False):
    """Ingest documents from the documents directory."""
    docs_dir = Path(os.getenv("DOCS_DIR", DOCS_DIR))

    if reset:
        from qdrant_client import QdrantClient
        client = QdrantClient(url=QDRANT_URL)
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass

    ensure_collection()

    files = [
        f for f in docs_dir.rglob("*")
        if f.suffix.lower() in {".pdf", ".docx", ".txt", ".md", ".markdown"}
    ]

    for f in files:
        pages = load_document(f)
        if not pages:
            continue
        chunks = chunk_pages(pages)
        texts = [c["text"] for c in chunks]
        embeddings = embed(texts)
        upsert_chunks(chunks, embeddings)
