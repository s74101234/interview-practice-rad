import re


_PAGE_PATTERNS = [
    re.compile(r"-\s*\d+\s*-"),
    re.compile(r"Page\s+\d+\s+of\s+\d+", re.IGNORECASE),
    re.compile(r"^\s*\d+\s*$", re.MULTILINE),
]


def clean(text: str) -> str:
    for pattern in _PAGE_PATTERNS:
        text = pattern.sub("", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def clean_pages(pages: list[dict]) -> list[dict]:
    cleaned = []
    for page in pages:
        content = clean(page["content"])
        if len(content) >= 20:
            cleaned.append({**page, "content": content})
    return cleaned
