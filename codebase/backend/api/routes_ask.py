from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from retrieval.qdrant_retriever import retrieve
from generation.llm import stream_response
import json
import logging
import httpx
import hashlib
import time
from typing import Optional

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")

# Simple in-memory cache for answers
# Format: {question_hash: {"answer": str, "sources": list, "timestamp": float}}
answer_cache = {}
CACHE_TTL_SECONDS = 7200  # 2 hours

def _get_cache_key(question: str) -> str:
    """Generate a cache key from the question."""
    return hashlib.sha256(question.lower().strip().encode()).hexdigest()

def _get_cached_answer(question: str) -> Optional[dict]:
    """Get cached answer if available and not expired."""
    key = _get_cache_key(question)
    if key in answer_cache:
        entry = answer_cache[key]
        if time.time() - entry["timestamp"] < CACHE_TTL_SECONDS:
            logger.info(f"Cache hit for question: {question[:50]}...")
            return entry
        else:
            # Remove expired entry
            del answer_cache[key]
    return None

def _set_cached_answer(question: str, answer: str, sources: list):
    """Cache the answer."""
    key = _get_cache_key(question)
    answer_cache[key] = {
        "answer": answer,
        "sources": sources,
        "timestamp": time.time()
    }
    logger.info(f"Cached answer for question: {question[:50]}...")

class AskRequest(BaseModel):
    question: str

def _check_service(name: str, url: str, check_fn) -> dict:
    """Helper to check a service and return its status."""
    try:
        result = check_fn()
        return {"name": name, "url": url, "status": "ok", "details": result}
    except Exception as e:
        return {"name": name, "url": url, "status": "error", "error": str(e)}

def _check_qdrant():
    from qdrant_client import QdrantClient
    from config import QDRANT_URL, COLLECTION_NAME
    client = QdrantClient(url=QDRANT_URL, timeout=5)
    info = client.get_collection(COLLECTION_NAME)
    return {"collection": COLLECTION_NAME, "points": info.points_count, "status": str(info.status)}

def _check_ollama():
    from config import OLLAMA_URL, OLLAMA_MODEL
    response = httpx.get(f"{OLLAMA_URL}/api/tags", timeout=5)
    data = response.json()
    models = [m["name"] for m in data.get("models", [])]
    has_model = OLLAMA_MODEL in models
    return {"model": OLLAMA_MODEL, "available": has_model, "models": models}

@router.get("/diagnostics")
async def diagnostics():
    """
    Check status of all services: Qdrant, Ollama, and collection.
    Use this to diagnose why the app might not be working.
    """
    results = {
        "qdrant": _check_service("Qdrant", "http://localhost:6333", _check_qdrant),
        "ollama": _check_service("Ollama", "http://localhost:11434", _check_ollama),
    }
    
    # Overall status
    all_ok = all(r["status"] == "ok" for r in results.values())
    results["overall"] = "ok" if all_ok else "error"
    
    return results

@router.post("/ask")
async def ask_sync(req: AskRequest):
    """Non-streaming fallback with caching."""
    # Check cache first
    cached = _get_cached_answer(req.question)
    if cached:
        return {
            "answer": cached["answer"],
            "sources": cached["sources"],
            "cached": True
        }
    
    try:
        chunks = retrieve(req.question)
        full = ""
        async for token in stream_response(req.question, chunks):
            full += token
        
        # Cache the answer
        _set_cached_answer(req.question, full, _format_sources(chunks))
        
        return {
            "answer": full,
            "sources": _format_sources(chunks),
        }
    except Exception as e:
        logger.error(f"Error in ask_sync: {e}")
        error_msg = str(e)
        
        # Provide more specific error messages
        if "Connection" in error_msg:
            if "11434" in error_msg:
                user_msg = "I couldn't connect to the LLM (Ollama). Please ensure Ollama is running: 'ollama serve'"
            elif "6333" in error_msg:
                user_msg = "I couldn't connect to the database (Qdrant). Please ensure Qdrant is running."
            else:
                user_msg = f"I encountered a connection error: {error_msg}"
        elif "Collection" in error_msg and "doesn't exist" in error_msg:
            user_msg = "No documents have been ingested yet. Run ./ingest.sh --dir /path/to/documents first."
        else:
            user_msg = f"I encountered an error: {error_msg[:100]}"
        
        return {
            "answer": user_msg,
            "sources": [],
            "error": error_msg
        }

@router.get("/ask/stream")
async def ask_stream(question: str = Query(..., min_length=1)):
    """
    SSE stream. Frontend connects via EventSource.
    Events:
      {"type": "token",   "text": "..."}      — streamed tokens
      {"type": "sources", "sources": [...]}    — sent once after generation
      {"type": "cached",  "value": true}     — indicates cached response
      {"type": "error",   "message": "..."}  — error occurred with details
      data: [DONE]                             — end signal
    """
    # Check cache first - if cached, return immediately (no streaming needed)
    cached = _get_cached_answer(question)
    if cached:
        async def generate_cached():
            # Send the cached answer as a single token
            yield f"data: {json.dumps({'type': 'token', 'text': cached['answer']})}\n\n"
            yield f"data: {json.dumps({'type': 'sources', 'sources': cached['sources']})}\n\n"
            yield f"data: {json.dumps({'type': 'cached', 'value': True})}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate_cached(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )
    
    try:
        chunks = retrieve(question)

        async def generate():
            full_answer = ""
            try:
                async for token in stream_response(question, chunks):
                    full_answer += token
                    yield f"data: {json.dumps({'type': 'token', 'text': token})}\n\n"
                
                # Cache the answer after streaming completes
                _set_cached_answer(question, full_answer, _format_sources(chunks))
                
                yield f"data: {json.dumps({'type': 'sources', 'sources': _format_sources(chunks)})}\n\n"
                yield "data: [DONE]\n\n"
            except Exception as e:
                logger.error(f"Error during streaming: {e}")
                error_msg = str(e)
                
                # Provide specific error messages
                if "Connection" in error_msg:
                    if "11434" in error_msg:
                        user_msg = "I couldn't connect to the LLM (Ollama). Please ensure Ollama is running: 'ollama serve'"
                    else:
                        user_msg = f"Connection error: {error_msg[:80]}"
                else:
                    user_msg = f"Error generating response: {error_msg[:80]}"
                
                yield f"data: {json.dumps({'type': 'error', 'message': user_msg})}\n\n"
                yield "data: [DONE]\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )
    except Exception as e:
        logger.error(f"Error in ask_stream: {e}")
        error_msg = str(e)
        
        # Specific error messages for retrieval failures
        if "Collection" in error_msg and "doesn't exist" in error_msg:
            user_msg = "No documents indexed. Please run: ./ingest.sh --dir /path/to/documents"
        elif "Connection" in error_msg and "6333" in error_msg:
            user_msg = "Cannot connect to Qdrant. Please ensure Qdrant is running."
        else:
            user_msg = f"Failed to process request: {error_msg[:100]}"
        
        return StreamingResponse(
            iter([
                f"data: {json.dumps({'type': 'error', 'message': user_msg})}\n\n",
                "data: [DONE]\n\n"
            ]),
            media_type="text/event-stream",
        )

@router.get("/cache/stats")
async def cache_stats():
    """Get cache statistics."""
    # Clean up expired entries
    current_time = time.time()
    expired_keys = [
        key for key, entry in answer_cache.items()
        if current_time - entry["timestamp"] >= CACHE_TTL_SECONDS
    ]
    for key in expired_keys:
        del answer_cache[key]
    
    return {
        "cached_answers": len(answer_cache),
        "ttl_seconds": CACHE_TTL_SECONDS
    }

@router.post("/cache/clear")
async def cache_clear():
    """Clear the answer cache."""
    global answer_cache
    count = len(answer_cache)
    answer_cache = {}
    return {"cleared": count}

@router.get("/health")
async def health():
    return {"status": "ok"}

def _format_sources(chunks: list[dict]) -> list[dict]:
    if not chunks:
        return []
    return [
        {
            "filename": c["filename"],
            "page": c["page"],
            "score": c["score"],
            "confidence": c["confidence"],
            "text": c["text"],  # Full text for expansion
            "excerpt": c["text"][:350] + "…" if len(c["text"]) > 350 else c["text"],
            "isTruncated": len(c["text"]) > 350,
        }
        for c in chunks
    ]