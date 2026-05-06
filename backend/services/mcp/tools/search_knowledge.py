from services.models.embedder import embed_query
from services.data.store import search


def run(query: str, top_k: int = 5) -> list[dict]:
    vector = embed_query(query)
    return search(vector, top_k)
