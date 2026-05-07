from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from pathlib import Path

COLLECTION = "knowledge_base"
VECTOR_SIZE = 3072

_DB_PATH = str(Path(__file__).resolve().parent.parent.parent / "data" / "qdrant")
_client: QdrantClient | None = None


def _get_client() -> QdrantClient:
    global _client
    if _client is None:
        Path(_DB_PATH).mkdir(parents=True, exist_ok=True)
        _client = QdrantClient(path=_DB_PATH)
    return _client


def _ensure_collection() -> None:
    client = _get_client()
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION not in existing:
        client.create_collection(
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
    _get_client().upsert(collection_name=COLLECTION, points=points)


def search(query_vector: list[float], top_k: int = 5) -> list[dict]:
    _ensure_collection()
    results = _get_client().query_points(
        collection_name=COLLECTION,
        query=query_vector,
        limit=top_k,
        with_payload=True,
    ).points
    return [
        {
            "text": r.payload["text"],
            "source": r.payload["source"],
            "page": r.payload["page"],
            "score": round(r.score, 4),
        }
        for r in results
    ]


def scroll_all() -> list[dict]:
    _ensure_collection()
    results, _ = _get_client().scroll(
        collection_name=COLLECTION,
        with_payload=True,
        limit=1000,
    )
    return [
        {
            "text": r.payload["text"],
            "source": r.payload["source"],
            "page": r.payload["page"],
        }
        for r in results
    ]


def count() -> int:
    try:
        _ensure_collection()
        return _get_client().count(collection_name=COLLECTION).count
    except Exception:
        return 0
