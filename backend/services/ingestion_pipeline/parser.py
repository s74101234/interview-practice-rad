import pymupdf4llm
from pathlib import Path


def parse(file_path: str) -> list[dict]:
    pages = pymupdf4llm.to_markdown(file_path, page_chunks=True)
    result = []
    for i, p in enumerate(pages):
        text = p.get("text", "")
        if not text.strip():
            continue
        meta = p.get("metadata", {})
        page_num = meta.get("page", meta.get("page_number", i))
        result.append({
            "source": Path(file_path).name,
            "page": str(page_num + 1),
            "content": text,
        })
    return result
