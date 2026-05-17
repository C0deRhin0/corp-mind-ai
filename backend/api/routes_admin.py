import os
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Header, Depends
from fastapi.responses import JSONResponse
from qdrant_client import QdrantClient
from config import QDRANT_URL, COLLECTION_NAME
from services.document_ingestion import ingest_documents

admin_router = APIRouter(prefix="/api/admin")
ALLOWED_DOCUMENT_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".markdown"}

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

def require_admin(x_admin_code: str = Header(default="")):
    verify_code(x_admin_code)

@admin_router.post("/login")
async def login(payload: dict):
    verify_code(payload.get("code", ""))
    return {"status": "ok"}

@admin_router.get("/documents", dependencies=[Depends(require_admin)])
async def list_documents():
    client = QdrantClient(url=QDRANT_URL)
    # List unique filenames
    points = client.scroll(COLLECTION_NAME, limit=1000)[0]
    filenames = sorted({p.payload.get("filename") for p in points if p.payload})
    return {"documents": [{"filename": f} for f in filenames]}

@admin_router.delete("/documents/{filename}", dependencies=[Depends(require_admin)])
async def delete_document(filename: str):
    client = QdrantClient(url=QDRANT_URL)
    client.delete(collection_name=COLLECTION_NAME, points_selector={"filter": {"must": [{"key": "filename", "match": {"value": filename}}]}})
    return {"deleted": filename}

@admin_router.post("/documents/reset", dependencies=[Depends(require_admin)])
async def reset_documents():
    client = QdrantClient(url=QDRANT_URL)
    client.delete_collection(COLLECTION_NAME)
    return {"status": "reset"}

@admin_router.post("/documents/reingest", dependencies=[Depends(require_admin)])
async def reingest_documents():
    # Re-ingest from server documents directory
    ingest_documents(reset=True)
    return {"status": "reingested"}

@admin_router.post("/documents/upload", dependencies=[Depends(require_admin)])
async def upload_documents(files: list[UploadFile] = File(...)):
    # Save files to documents folder, then ingest
    documents_dir = Path(os.getenv("DOCS_DIR", os.path.join(os.getcwd(), "documents"))).resolve()
    documents_dir.mkdir(parents=True, exist_ok=True)

    for file in files:
        filename = Path(file.filename or "").name
        if not filename or filename != file.filename or "/" in filename or "\\" in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        if Path(filename).suffix.lower() not in ALLOWED_DOCUMENT_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {filename}")

        # Validate file size
        file.file.seek(0, os.SEEK_END)
        size = file.file.tell() / (1024 * 1024)
        file.file.seek(0)
        max_size = _get_max_file_size()
        if size > max_size:
            raise HTTPException(status_code=400, detail=f"File {file.filename} exceeds {max_size}MB")

        # Save file
        file_path = (documents_dir / filename).resolve()
        if documents_dir not in file_path.parents:
            raise HTTPException(status_code=400, detail="Invalid filename")
        with open(file_path, "wb") as f:
            f.write(await file.read())

    # Ingest new files
    ingest_documents(reset=False)
    return JSONResponse({"status": "uploaded"})
