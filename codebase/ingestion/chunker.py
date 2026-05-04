from langchain.text_splitter import RecursiveCharacterTextSplitter
from config import CHUNK_SIZE, CHUNK_OVERLAP
import hashlib

_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", ". ", " ", ""],
)

def chunk_pages(pages: list[dict]) -> list[dict]:
    """
    Input:  [{"text", "page", "filename", "filepath"}]
    Output: same fields + "chunk_id" (stable hash), "chunk_index"
    chunk_id is deterministic so re-ingesting the same file upserts, not duplicates.
    """
    chunks = []
    for page in pages:
        splits = _splitter.split_text(page["text"])
        for i, text in enumerate(splits):
            chunk_id = hashlib.md5(
                f"{page['filename']}::p{page['page']}::c{i}".encode()
            ).hexdigest()
            chunks.append({
                **page,
                "text": text,
                "chunk_index": i,
                "chunk_id": chunk_id,
            })
    return chunks
