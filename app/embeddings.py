from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import EMBED_MODEL


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    return SentenceTransformer(EMBED_MODEL)


def embed(texts: list[str]) -> np.ndarray:
    model = get_model()
    vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return np.asarray(vectors, dtype="float32")
