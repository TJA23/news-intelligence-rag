from dataclasses import dataclass
from functools import lru_cache

from app.config import TOP_K
from app.embeddings import embed
from app.llm import generate_answer
from app.vectorstore import Hit, VectorStore


@dataclass
class RagResponse:
    question: str
    answer: str
    sources: list[Hit]


_store_cache: dict[str, VectorStore] = {}


def get_store(force_reload: bool = False) -> VectorStore:
    if force_reload or "store" not in _store_cache:
        store = VectorStore()
        store.load()
        _store_cache["store"] = store
    return _store_cache["store"]


def reset_store() -> None:
    _store_cache.pop("store", None)


def answer(question: str, top_k: int = TOP_K) -> RagResponse:
    store = get_store()
    query_vec = embed([question])
    hits = store.search(query_vec, top_k)
    text = generate_answer(question, hits)
    return RagResponse(question=question, answer=text, sources=hits)


def search(query: str, top_k: int = TOP_K) -> list[Hit]:
    store = get_store()
    query_vec = embed([query])
    return store.search(query_vec, top_k)
