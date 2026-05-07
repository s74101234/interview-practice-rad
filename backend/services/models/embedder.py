import json
import urllib.request
import urllib.error
from core.config import settings

_MODEL   = "gemini-embedding-001"
_API_KEY = settings.gemini_api_key
_BASE    = "https://generativelanguage.googleapis.com/v1beta/models"
_BATCH   = 100


def _post(url: str, body: dict) -> dict:
    data = json.dumps(body).encode()
    req  = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode(errors="replace")
        raise RuntimeError(f"HTTP {e.code} {e.reason}: {body_text}") from None


def embed_texts(texts: list[str]) -> list[list[float]]:
    url     = f"{_BASE}/{_MODEL}:batchEmbedContents?key={_API_KEY}"
    vectors = []
    for i in range(0, len(texts), _BATCH):
        batch = texts[i : i + _BATCH]
        body  = {
            "requests": [
                {
                    "model": f"models/{_MODEL}",
                    "content": {"parts": [{"text": t}]},
                    "taskType": "RETRIEVAL_DOCUMENT",
                }
                for t in batch
            ]
        }
        resp = _post(url, body)
        vectors.extend(e["values"] for e in resp["embeddings"])
    return vectors


def embed_query(query: str) -> list[float]:
    url  = f"{_BASE}/{_MODEL}:embedContent?key={_API_KEY}"
    body = {
        "model": f"models/{_MODEL}",
        "content": {"parts": [{"text": query}]},
        "taskType": "RETRIEVAL_QUERY",
    }
    resp = _post(url, body)
    return resp["embedding"]["values"]
