from qdrant_client import QdrantClient
from qdrant_client.models import (
    NamedVector, NamedSparseVector, SparseVector,
    SearchRequest, FusionQuery, Fusion, Prefetch,
)
from config import QDRANT_URL, COLLECTION_NAME, TOP_K, SCORE_THRESHOLD
from retrieval.embedder import embed_query
import hashlib
from collections import Counter

_client: QdrantClient | None = None

def get_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(url=QDRANT_URL, timeout=20)
    return _client

def _sparse_from_query(query: str) -> SparseVector:
    tokens = query.lower().split()
    counts = Counter(tokens)
    total = sum(counts.values())
    indices, values = [], []
    for token, count in counts.items():
        idx = int(hashlib.md5(token.encode()).hexdigest(), 16) % (2**20)
        indices.append(idx)
        values.append(count / total)
    return SparseVector(indices=indices, values=values)

def retrieve(question: str) -> list[dict]:
    """
    Hybrid search via Qdrant's native RRF fusion.
    Runs dense + sparse searches in parallel server-side, fuses with RRF.
    Returns list of dicts with: text, filename, page, score, source_type
    """
    client = get_client()
    dense_vec = embed_query(question)
    sparse_vec = _sparse_from_query(question)

    # Qdrant native hybrid search (v1.10+)
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        prefetch=[
            Prefetch(
                query=dense_vec,
                using="dense",
                limit=TOP_K * 2,
            ),
            Prefetch(
                query=sparse_vec,
                using="sparse",
                limit=TOP_K * 2,
            ),
        ],
        query=FusionQuery(fusion=Fusion.RRF),
        limit=TOP_K,
        with_payload=True,
    )

    chunks = []
    for point in results.points:
        score = round(point.score, 4)
        if score < SCORE_THRESHOLD:
            continue
        payload = point.payload
        
        # Confidence: normalize RRF score to 0-100%
        # RRF scores typically range from 0 to ~1.0 (higher = more relevant)
        # Use a sigmoid-like scaling for better distribution
        # score of 0.3 = ~50%, score of 0.5 = ~75%, score of 0.8+ = ~95%+
        confidence = min(100, round((score / 0.8) * 100))
        confidence = max(0, confidence)  # Ensure not negative
        
        chunks.append({
            "text": payload["text"],
            "filename": payload["filename"],
            "page": payload["page"],
            "score": score,
            "confidence": confidence,
        })

    return chunks
