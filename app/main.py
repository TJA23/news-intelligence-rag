from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.chunking import build_chunks, load_articles
from app.config import TOP_K
from app.embeddings import embed
from app.enrich import sentiment_score, trending_topics
from app.ingest import ingest_all
from app.rag import answer, reset_store, search
from app.vectorstore import VectorStore

app = FastAPI(
    title="News Intelligence · RAG",
    description="Retrieval-Augmented Generation platform over a live news corpus. Ingestion · semantic search · contextual QA · trends.",
    version="0.1.0",
)


class IngestResponse(BaseModel):
    total_in_corpus: int
    new_articles: int
    per_source: dict


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, examples=["What's happening with the latest AI announcements?"])
    top_k: int = Field(TOP_K, ge=1, le=10)


class Source(BaseModel):
    title: str
    source: str
    url: str
    published: str
    score: float
    text: str


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[Source]


class SearchResponse(BaseModel):
    query: str
    results: list[Source]


class TrendsResponse(BaseModel):
    article_count: int
    top_entities: list[dict]
    sentiment_distribution: dict


def _hits_to_sources(hits) -> list[Source]:
    return [
        Source(
            title=h.title,
            source=h.source,
            url=h.url,
            published=h.published,
            score=h.score,
            text=h.text,
        )
        for h in hits
    ]


@app.get("/")
def root():
    return {
        "name": "News Intelligence · RAG",
        "endpoints": ["/ingest (POST)", "/reindex (POST)", "/ask (POST)", "/search (GET)", "/trends (GET)", "/docs"],
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ingest", response_model=IngestResponse)
def ingest():
    result = ingest_all()
    return IngestResponse(**result)


@app.post("/reindex")
def reindex():
    chunks = build_chunks()
    if not chunks:
        raise HTTPException(status_code=400, detail="No articles to index. Run /ingest first.")
    vectors = embed([c["text"] for c in chunks])
    store = VectorStore()
    store.build(chunks, vectors)
    store.save()
    reset_store()
    return {"chunks": len(chunks), "embedding_dim": int(vectors.shape[1])}


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    result = answer(req.question, req.top_k)
    return AskResponse(
        question=result.question,
        answer=result.answer,
        sources=_hits_to_sources(result.sources),
    )


@app.get("/search", response_model=SearchResponse)
def search_endpoint(q: str, top_k: int = TOP_K):
    hits = search(q, top_k)
    return SearchResponse(query=q, results=_hits_to_sources(hits))


@app.get("/trends", response_model=TrendsResponse)
def trends():
    articles = load_articles()
    if not articles:
        raise HTTPException(status_code=400, detail="No articles in corpus. Run /ingest first.")
    entities = trending_topics(articles, top_k=15)
    distribution = {"positive": 0, "neutral": 0, "negative": 0}
    for art in articles:
        label = sentiment_score(f"{art['title']} {art['text']}")["label"]
        distribution[label] += 1
    return TrendsResponse(
        article_count=len(articles),
        top_entities=[{"name": n, "mentions": c} for n, c in entities],
        sentiment_distribution=distribution,
    )
