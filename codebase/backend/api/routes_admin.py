import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from qdrant_client import QdrantClient
from config import QDRANT_URL, COLLECTION_NAME
from services.document_ingestion import ingest_documents

admin_router = APIRouter(prefix="/api/admin")

def _get_admin_code() -> str:
    return os.getenv("ADMIN_CODE", "")

def _get_max_file_size() -> int:
    return int(os.getenv("MAX_FILE_SIZE_MB", "50"))

def verify_code(code: str):
    admin_code = _get_admin_code()
    if not admin_code:
        raise HTTPException(status_code=500, detail="Admin code not configured")
    if code != admin_code:
        raise HTTPException(status_code=401, detail="Invalid admin code")

@admin_router.post("/login")
async def login(payload: dict):
    verify_code(payload.get("code", ""))
    return {"status": "ok"}

@admin_router.get("/documents")
async def list_documents():
    client = QdrantClient(url=QDRANT_URL)
    # List unique filenames
    points = client.scroll(COLLECTION_NAME, limit=1000)[0]
    filenames = sorted({p.payload.get("filename") for p in points if p.payload})
    return {"documents": [{"filename": f} for f in filenames]}

@admin_router.delete("/documents/{filename}")
async def delete_document(filename: str):
    client = QdrantClient(url=QDRANT_URL)
    client.delete(collection_name=COLLECTION_NAME, points_selector={"filter": {"must": [{"key": "filename", "match": {"value": filename}}]}})
    return {"deleted": filename}

@admin_router.post("/documents/reset")
async def reset_documents():
    client = QdrantClient(url=QDRANT_URL)
    client.delete_collection(COLLECTION_NAME)
    return {"status": "reset"}

@admin_router.post("/documents/reingest")
async def reingest_documents():
    # Re-ingest from server documents directory
    ingest_documents(reset=True)
    return {"status": "reingested"}

@admin_router.post("/documents/upload")
async def upload_documents(files: list[UploadFile] = File(...)):
    # Save files to documents folder, then ingest
    documents_dir = os.path.join(os.getcwd(), "documents")
    os.makedirs(documents_dir, exist_ok=True)

    for file in files:
        # Validate file size
        file.file.seek(0, os.SEEK_END)
        size = file.file.tell() / (1024 * 1024)
        file.file.seek(0)
        max_size = _get_max_file_size()
        if size > max_size:
            raise HTTPException(status_code=400, detail=f"File {file.filename} exceeds {max_size}MB")

        # Save file
        file_path = os.path.join(documents_dir, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())

    # Ingest new files
    ingest_documents(reset=False)
    return JSONResponse({"status": "uploaded"})
