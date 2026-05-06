from google import genai
from core.config import settings

_client = genai.Client(api_key=settings.gemini_api_key)
_MODEL = "text-embedding-004"
_BATCH = 16


def embed_texts(texts: list[str]) -> list[list[float]]:
    vectors = []
    for i in range(0, len(texts), _BATCH):
        batch = texts[i : i + _BATCH]
        response = _client.models.embed_content(model=_MODEL, contents=batch)
        vectors.extend([e.values for e in response.embeddings])
    return vectors


def embed_query(query: str) -> list[float]:
    response = _client.models.embed_content(model=_MODEL, contents=query)
    return response.embeddings[0].values
