MAX_CHARS = 600


def _split_sentences(text: str) -> list[str]:
    import re
    parts = re.split(r"(?<=[。！？.!?])\s*", text)
    return [p.strip() for p in parts if p.strip()]


def chunk_page(page: dict) -> list[dict]:
    text = page["content"]
    if len(text) <= MAX_CHARS:
        return [{
            "id": f"{page['source']}_p{page['page']}_c0",
            "source": page["source"],
            "page": page["page"],
            "text": text,
            "char_count": len(text),
        }]

    sentences = _split_sentences(text)
    chunks = []
    current = []
    current_len = 0
    last_sentence = None

    for sent in sentences:
        if current_len + len(sent) > MAX_CHARS and current:
            chunk_text = " ".join(current)
            chunks.append(chunk_text)
            current = [last_sentence] if last_sentence else []
            current_len = len(last_sentence) if last_sentence else 0
        current.append(sent)
        current_len += len(sent)
        last_sentence = sent

    if current:
        chunks.append(" ".join(current))

    return [
        {
            "id": f"{page['source']}_p{page['page']}_c{i}",
            "source": page["source"],
            "page": page["page"],
            "text": chunk,
            "char_count": len(chunk),
        }
        for i, chunk in enumerate(chunks)
    ]


def chunk_pages(pages: list[dict]) -> list[dict]:
    result = []
    for page in pages:
        result.extend(chunk_page(page))
    return result
