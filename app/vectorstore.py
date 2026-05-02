import json
from dataclasses import dataclass

import faiss
import numpy as np

from app.config import CHUNKS_PATH, EMBED_DIM, FAISS_INDEX_PATH


@dataclass
class Hit:
    chunk_id: str
    article_id: str
    source: str
    title: str
    url: str
    published: str
    text: str
    score: float


class VectorStore:
    def __init__(self) -> None:
        self.index: faiss.Index | None = None
        self.chunks: list[dict] = []

    def build(self, chunks: list[dict], vectors: np.ndarray) -> None:
        index = faiss.IndexFlatIP(EMBED_DIM)
        index.add(vectors)
        self.index = index
        self.chunks = chunks

    def save(self) -> None:
        assert self.index is not None
        faiss.write_index(self.index, str(FAISS_INDEX_PATH))
        with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
            json.dump(self.chunks, f, ensure_ascii=False, indent=2)

    def load(self) -> None:
        self.index = faiss.read_index(str(FAISS_INDEX_PATH))
        with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
            self.chunks = json.load(f)

    def search(self, query_vec: np.ndarray, top_k: int) -> list[Hit]:
        assert self.index is not None
        scores, indices = self.index.search(query_vec, top_k)
        hits: list[Hit] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            c = self.chunks[idx]
            hits.append(
                Hit(
                    chunk_id=c["id"],
                    article_id=c["article_id"],
                    source=c["source"],
                    title=c["title"],
                    url=c.get("url", ""),
                    published=c.get("published", ""),
                    text=c["text"],
                    score=float(score),
                )
            )
        return hits
