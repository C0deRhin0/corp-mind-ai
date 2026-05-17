import httpx
import json
from config import OLLAMA_URL, OLLAMA_MODEL

SYSTEM = """You are NuecAI, a precise internal knowledge assistant for Corporate Mind.
Your role is to answer questions ONLY using the provided company documents.

ANSWER STRUCTURE:
- Start with a direct, concise answer to the question
- Use bullet points for lists or multiple items
- If providing specific numbers, dates, or policies, cite them exactly as in the documents
- If the answer is uncertain about a detail, say so

IMPORTANT RULES:
1. If the question is NOT related to company documents, policies, or internal information, respond with: "I'm designed to answer questions about company documents and policies. Please ask me something related to your company's internal documents."
2. If NO relevant sources are found (empty context), respond with: "I couldn't find any relevant information in the indexed documents to answer your question. You may need to ingest the relevant documents first, or try a different question."
3. If you cannot find specific information in the provided context, say so clearly: "Based on the documents provided, I don't have specific information about [topic]."
4. Never invent or hallucinate information not in the documents.
5. Be concise but comprehensive - include all relevant details from the documents.
6. Use formatting: **bold** for key terms, bullet points for lists.

Always prioritize accuracy over completeness. It's okay to say you don't know."""

def build_prompt(question: str, chunks: list[dict]) -> str:
    if not chunks:
        # No relevant documents found - inform the user
        return f"""You are NuecAI, a precise internal knowledge assistant for Corporate Mind.

The user is asking: "{question}"

However, there are NO relevant documents indexed in the system to answer this question.

Respond with: "I couldn't find any relevant information in the indexed documents to answer your question. You may need to ingest the relevant documents first, or try a different question."

Do not make up any information."""

    # Build context with source attribution
    parts = []
    for i, c in enumerate(chunks):
        # Extract clean filename without extension
        filename = c['filename'].replace('.pdf', '').replace('.docx', '').replace('.txt', '').replace('.md', '')
        parts.append(f"[Source {i+1}: {filename}]\n{c['text']}")
    context = "\n\n---\n\n".join(parts)
    
    return f"""Based on the following company documents, please answer the question thoroughly and accurately.

---
CONTEXT:
{context}

---
QUESTION: {question}

---
ANSWER: (Provide a clear, well-structured answer based ONLY on the context above. Use bullet points where appropriate. If the context doesn't contain enough information to fully answer, state what you can determine and what is unclear.)"""

async def stream_response(question: str, chunks: list[dict]):
    """Async generator yielding text tokens from Ollama."""
    prompt = build_prompt(question, chunks)
    async with httpx.AsyncClient(timeout=120) as client:
        async with client.stream(
            "POST",
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "system": SYSTEM,
                "stream": True,
                "options": {
                    "temperature": 0.1,     # Low temp for factual accuracy
                    "num_ctx": 4096,
                }
            },
        ) as resp:
            async for line in resp.aiter_lines():
                if line:
                    data = json.loads(line)
                    if not data.get("done"):
                        yield data.get("response", "")
