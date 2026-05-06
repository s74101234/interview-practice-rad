from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
from core.config import settings

COLLECTION = "knowledge_base"
VECTOR_SIZE = 768

_client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)


def _ensure_collection() -> None:
    existing = [c.name for c in _client.get_collections().collections]
    if COLLECTION not in existing:
        _client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )


def upsert(chunks: list[dict], vectors: list[list[float]]) -> None:
    _ensure_collection()
    points = [
        PointStruct(
            id=abs(hash(chunk["id"])) % (2**63),
            vector=vector,
            payload={
                "id": chunk["id"],
                "source": chunk["source"],
                "page": chunk["page"],
                "text": chunk["text"],
                "char_count": chunk["char_count"],
            },
        )
        for chunk, vector in zip(chunks, vectors)
    ]
    _client.upsert(collection_name=COLLECTION, points=points)


def search(query_vector: list[float], top_k: int = 5) -> list[dict]:
    _ensure_collection()
    results = _client.search(
        collection_name=COLLECTION,
        query_vector=query_vector,
        limit=top_k,
        with_payload=True,
    )
    return [
        {
            "text": r.payload["text"],
            "source": r.payload["source"],
            "page": r.payload["page"],
            "score": round(r.score, 4),
        }
        for r in results
    ]


def count() -> int:
    try:
        _ensure_collection()
        return _client.count(collection_name=COLLECTION).count
    except Exception:
        return 0
