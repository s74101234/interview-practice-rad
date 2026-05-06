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


async def _log(msg: str) -> None:
    await broadcast("log", {"message": msg})


async def _run_pipeline(file_path: str, filename: str) -> None:
    try:
        await broadcast("pipeline_start", {"filename": filename})
        await _log(f"開始處理：{filename}")

        await _log("解析 PDF 文件結構...")
        pages = await asyncio.to_thread(parser.parse, file_path)
        await _log(f"解析完成，共 {len(pages)} 頁")
        await broadcast("pipeline_progress", {"stage": "parse"})

        await _log("清洗文字內容...")
        pages = await asyncio.to_thread(cleaner.clean_pages, pages)
        await _log(f"清洗完成，保留 {len(pages)} 頁")
        await broadcast("pipeline_progress", {"stage": "clean"})

        await _log("切分段落...")
        chunks = await asyncio.to_thread(chunker.chunk_pages, pages)
        await _log(f"切分完成，共 {len(chunks)} 個段落")
        await broadcast("pipeline_progress", {"stage": "chunk"})

        await _log("建立向量索引...")
        texts = [c["text"] for c in chunks]
        vectors = await asyncio.to_thread(embed_texts, texts)
        await _log(f"向量嵌入完成，共 {len(vectors)} 筆")
        await broadcast("pipeline_progress", {"stage": "embed"})

        await _log("寫入向量資料庫...")
        await asyncio.to_thread(upsert, chunks, vectors)
        await _log("完成！知識庫就緒")

        state.uploaded_file_path = file_path
        await broadcast("pipeline_done", {"chunk_count": len(chunks), "filename": filename})

    except Exception as e:
        await _log(f"錯誤：{e}")
        await broadcast("pipeline_error", {"message": str(e)})


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext != ".pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    job_id = str(uuid.uuid4())
    dest = UPLOAD_DIR / f"{job_id}{ext}"

    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    asyncio.create_task(_run_pipeline(str(dest), file.filename))

    return UploadResponse(job_id=job_id, filename=file.filename)
