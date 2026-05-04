# Identical to ingestion/embedder.py — shared model, no internet after first load
from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL

_model = None

def embed_query(query: str) -> list[float]:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model.encode([query])[0].tolist()
