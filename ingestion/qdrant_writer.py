from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, SparseVectorParams, SparseIndexParams,
    PointStruct, SparseVector, Batch
)
from qdrant_client.models import models as qmodels
from ingestion_config import QDRANT_URL, COLLECTION_NAME, VECTOR_SIZE, UPSERT_BATCH_SIZE
import uuid

_client: QdrantClient | None = None

def get_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(url=QDRANT_URL, timeout=30)
    return _client

def ensure_collection():
    """
    Creates the collection if it doesn't exist.
    Uses named vectors:
      - "dense"  → HNSW cosine (semantic)
      - "sparse" → inverted index (keyword/BM25)
    This enables native hybrid search in one collection.
    """
    client = get_client()
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME in existing:
        print(f"  Collection '{COLLECTION_NAME}' already exists.")
        return

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config={
            "dense": VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            )
        },
        sparse_vectors_config={
            "sparse": SparseVectorParams(
                index=SparseIndexParams(on_disk=False)
            )
        },
    )
    print(f"  Created collection '{COLLECTION_NAME}'.")

def _build_sparse_vector(text: str) -> SparseVector:
    """
    Simple TF-IDF-like sparse vector from token hashes.
    In production, replace with SPLADE or FastEmbed sparse encoder.
    Qdrant v1.15+ handles IDF server-side, so client only sends TF indices.
    """
    from collections import Counter
    import hashlib

    tokens = text.lower().split()
    counts = Counter(tokens)
    total = sum(counts.values())
    indices = []
    values = []
    for token, count in counts.items():
        # Hash token to a stable integer index in [0, 2^20)
        idx = int(hashlib.md5(token.encode()).hexdigest(), 16) % (2**20)
        indices.append(idx)
        values.append(count / total)   # normalized TF

    return SparseVector(indices=indices, values=values)

def upsert_chunks(chunks: list[dict], embeddings: list[list[float]]):
    client = get_client()
    points = []
    for chunk, dense_vec in zip(chunks, embeddings):
        sparse_vec = _build_sparse_vector(chunk["text"])
        points.append(
            PointStruct(
                id=chunk["chunk_id"],   # deterministic MD5 hex string
                vector={
                    "dense": dense_vec,
                    "sparse": sparse_vec,
                },
                payload={
                    "text": chunk["text"],
                    "filename": chunk["filename"],
                    "filepath": chunk["filepath"],
                    "page": chunk["page"],
                    "chunk_index": chunk["chunk_index"],
                },
            )
        )

    # Upsert in batches
    for i in range(0, len(points), UPSERT_BATCH_SIZE):
        batch = points[i : i + UPSERT_BATCH_SIZE]
        client.upsert(collection_name=COLLECTION_NAME, points=batch)
        print(f"  Upserted batch {i // UPSERT_BATCH_SIZE + 1}: {len(batch)} points")

def collection_stats() -> dict:
    client = get_client()
    info = client.get_collection(COLLECTION_NAME)
    return {
        "total_vectors": info.points_count or 0,
        "status": info.status,
    }
