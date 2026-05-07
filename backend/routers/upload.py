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

        # 解析
        await _log("解析 PDF 文件結構（pymupdf4llm → Markdown）...")
        pages = await asyncio.to_thread(parser.parse, file_path)
        total_chars = sum(len(p["content"]) for p in pages)
        if len(pages) == 0:
            await _log("警告：未擷取到任何文字，PDF 可能為圖片型，請改用文字型 PDF")
        else:
            await _log(f"解析完成：{len(pages)} 頁，共 {total_chars:,} 字元")
        await broadcast("pipeline_progress", {"stage": "parse"})

        # 清洗
        await _log("清洗文字（移除頁碼、多餘空白）...")
        pages = await asyncio.to_thread(cleaner.clean_pages, pages)
        clean_chars = sum(len(p["content"]) for p in pages)
        await _log(f"清洗完成：保留 {len(pages)} 頁，{clean_chars:,} 字元")
        await broadcast("pipeline_progress", {"stage": "clean"})

        # 切分
        await _log(f"切分段落（每段上限 600 字元，重疊一句）...")
        chunks = await asyncio.to_thread(chunker.chunk_pages, pages)
        total_chunk_chars = sum(c["char_count"] for c in chunks)
        avg = round(total_chunk_chars / len(chunks)) if chunks else 0
        await _log(f"切分完成：{len(chunks)} 個段落，共 {total_chunk_chars:,} 字元，平均 {avg} 字元／段")
        await broadcast("pipeline_progress", {"stage": "chunk"})

        # 向量嵌入
        await _log(f"向量嵌入（gemini-embedding-001，3072 維，批次 100）...")
        texts = [c["text"] for c in chunks]
        vectors = await asyncio.to_thread(embed_texts, texts)
        await _log(f"嵌入完成：{len(vectors)} 筆向量")
        await broadcast("pipeline_progress", {"stage": "embed"})

        # 寫入
        await _log("寫入向量資料庫（Qdrant 本地，collection: knowledge_base）...")
        await asyncio.to_thread(upsert, chunks, vectors)
        await _log(f"完成！knowledge_base 已就緒，共 {len(chunks)} 個段落可供檢索")

        state.uploaded_file_path = file_path
        state.last_filename = filename
        state.last_chunk_count = len(chunks)
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
