import json
import re
from pathlib import Path

from app.config import ARTICLES_PATH, CHUNK_OVERLAP, CHUNK_SIZE


def _split_sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    sentences = _split_sentences(text)
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for sentence in sentences:
        words = sentence.split()
        if current_len + len(words) > chunk_size and current:
            chunks.append(" ".join(current))
            tail = " ".join(current).split()[-overlap:] if overlap > 0 else []
            current = tail.copy()
            current_len = len(current)
        current.extend(words)
        current_len += len(words)

    if current:
        chunks.append(" ".join(current))
    return chunks


def load_articles(path: Path = ARTICLES_PATH) -> list[dict]:
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_chunks() -> list[dict]:
    articles = load_articles()
    out: list[dict] = []
    for art in articles:
        body = f"{art['title']}. {art['text']}"
        for chunk_id, chunk in enumerate(chunk_text(body)):
            out.append(
                {
                    "id": f"{art['id']}-{chunk_id}",
                    "article_id": art["id"],
                    "source": art["source"],
                    "title": art["title"],
                    "url": art.get("url", ""),
                    "published": art.get("published", ""),
                    "text": chunk,
                }
            )
    return out
