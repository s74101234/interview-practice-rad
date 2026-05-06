import asyncio
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException

from core.app_state import broadcast
import core.app_state as state
from core.schemas import UploadResponse
from services.ingestion_pipeline import parser, cleaner, chunker
from services.models.embedder import embed_texts
from services.data.store import upsert

router = APIRouter()
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


async def _run_pipeline(file_path: str, filename: str) -> None:
    try:
        await broadcast("pipeline_start", {"filename": filename})

        pages = await asyncio.to_thread(parser.parse, file_path)
        await broadcast("pipeline_progress", {"stage": "parse", "message": "解析文件結構"})

        pages = await asyncio.to_thread(cleaner.clean_pages, pages)
        await broadcast("pipeline_progress", {"stage": "clean", "message": "清洗文字內容"})

        chunks = await asyncio.to_thread(chunker.chunk_pages, pages)
        await broadcast("pipeline_progress", {"stage": "chunk", "message": "切分段落"})

        texts = [c["text"] for c in chunks]
        vectors = await asyncio.to_thread(embed_texts, texts)
        await broadcast("pipeline_progress", {"stage": "embed", "message": "建立向量索引"})

        await asyncio.to_thread(upsert, chunks, vectors)

        state.uploaded_file_path = file_path
        await broadcast("pipeline_done", {"chunk_count": len(chunks), "filename": filename})

    except Exception as e:
        await broadcast("pipeline_error", {"message": str(e)})


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in (".pdf", ".pptx", ".ppt"):
        raise HTTPException(status_code=400, detail="Only PDF and PPTX files are supported")

    job_id = str(uuid.uuid4())
    dest = UPLOAD_DIR / f"{job_id}{ext}"

    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    asyncio.create_task(_run_pipeline(str(dest), file.filename))

    return UploadResponse(job_id=job_id, filename=file.filename)
