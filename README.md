# 📰 News Intelligence Platform · LLM-Powered (RAG)

> ✅ **Status:** Working MVP — ingests live RSS feeds, builds a semantic index, and answers questions with grounded, cited responses.

An end-to-end **Retrieval-Augmented Generation** platform that ingests news from multiple RSS feeds, builds a FAISS-backed semantic index, and serves four capabilities through a FastAPI app:

1. **Ingestion** — fetch & deduplicate articles from configured feeds
2. **Semantic search** — vector similarity over the corpus
3. **Contextual QA** — RAG-grounded answers with inline citations
4. **Trends** — top entities + sentiment distribution across the corpus

![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![FAISS](https://img.shields.io/badge/FAISS-0084FF?logo=meta&logoColor=white)
![Sentence-Transformers](https://img.shields.io/badge/Sentence--Transformers-FFD21E?logoColor=black)
![Groq](https://img.shields.io/badge/Groq-F55036?logoColor=white)
![Status](https://img.shields.io/badge/status-MVP_working-brightgreen)

---

## 🎯 What it does

```
You: POST /ingest        → fetches latest from BBC, NPR, Guardian, HN, TechCrunch, Ars Technica
You: POST /reindex       → chunks + embeds + builds FAISS index
You: GET  /search?q=iran → top semantic matches across the corpus
You: POST /ask           → RAG-grounded answer with citations
You: GET  /trends        → trending entities + sentiment distribution
```

Sample real-world output (corpus of 60 articles ingested):

```json
// GET /trends
{
  "article_count": 60,
  "top_entities": [
    {"name": "Trump",  "mentions": 10},
    {"name": "AI",     "mentions": 7},
    {"name": "Iran",   "mentions": 5},
    {"name": "China",  "mentions": 3},
    {"name": "AWS",    "mentions": 3}
  ],
  "sentiment_distribution": {"positive": 7, "neutral": 45, "negative": 8}
}
```

```json
// POST /ask {"question":"AI being used in defense or government"}
{
  "answer": "The Pentagon has inked deals with Nvidia, Microsoft, and AWS to
             deploy AI on classified networks ... [Source: TechCrunch — Pentagon
             inks deals with Nvidia, Microsoft, and AWS...]",
  "sources": [...]
}
```

## 🏗️ Architecture

```
┌──────────────┐    ┌──────────────┐    ┌────────────────┐    ┌──────────┐
│  RSS Feeds   │ ─► │  httpx +     │ ─► │  HTML cleaning │ ─► │  Articles│
│  (BBC, NPR,  │    │  feedparser  │    │  + dedup (sha) │    │  JSON    │
│   TC, ...)   │    └──────────────┘    └────────────────┘    └────┬─────┘
└──────────────┘                                                    │
                                                                    │
   ┌────────────────────────────────────────────────────────────────┘
   ▼
┌──────────────┐    ┌─────────────────────┐    ┌──────────┐
│  Chunking    │ ─► │  Sentence-BERT      │ ─► │  FAISS   │
│  (overlap)   │    │  Embeddings (384d)  │    │  Index   │
└──────────────┘    └─────────────────────┘    └────┬─────┘
                                                    │
   User Query                                       │
       │                                            │
       ▼                                            │
┌──────────────┐    ┌──────────────────┐    ┌──────────────┐
│  Embed       │ ─► │  Top-K Search    │ ◄──┤  Retrieve    │ ◄──┘
└──────────────┘    └────────┬─────────┘    └──────────────┘
                             │
        ┌────────────────────┼─────────────────────┐
        ▼                    ▼                     ▼
┌───────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  /search      │  │  /ask (RAG)      │  │  /trends         │
│  → top hits   │  │  → LLM answer    │  │  → entities +    │
│               │  │  + citations     │  │    sentiment     │
└───────────────┘  └──────────────────┘  └──────────────────┘
```

## 📂 Project Structure

```
news-intelligence-rag/
├── app/
│   ├── config.py         # Paths, model names, RSS sources, hyperparameters
│   ├── ingest.py         # httpx + feedparser RSS ingestion + dedup
│   ├── chunking.py       # Sentence-aware chunking with overlap
│   ├── embeddings.py     # Sentence-BERT encoder (cached)
│   ├── vectorstore.py    # FAISS wrapper (build/save/load/search)
│   ├── enrich.py         # Entity extraction + sentiment scoring
│   ├── llm.py            # Groq client with grounded prompt + citation
│   ├── rag.py            # Orchestrator: embed → retrieve → generate
│   └── main.py           # FastAPI: /ingest /reindex /ask /search /trends
├── scripts/
│   └── run_pipeline.py   # CLI: ingest + chunk + embed + index in one shot
├── data/
│   ├── articles/         # Persisted article corpus (JSON)
│   └── index/            # FAISS index + chunks
├── requirements.txt
└── .env.example
```

## ⚙️ Tech Stack

| Layer            | Choice                              | Why |
|------------------|-------------------------------------|------|
| Ingestion        | `httpx` + `feedparser` + `bs4`      | httpx uses certifi → bypasses macOS SSL issues |
| Deduplication    | SHA-1 hash of canonical URL/title   | Cheap, deterministic |
| Embeddings       | `all-MiniLM-L6-v2` (384-dim)        | Fast, small, strong baseline |
| Vector Store     | FAISS `IndexFlatIP`                 | Cosine via inner product on normalized vectors |
| Enrichment       | Regex + curated lexicons            | No heavy deps; easy to swap for spaCy/HF later |
| LLM              | Groq (LLaMA 3.3 70B)                | Free tier, blazing fast inference |
| API              | FastAPI + Uvicorn                   | Async, auto-docs, production-ready |

## 🚀 Quick Start

### 1. Setup
```bash
git clone https://github.com/TJA23/news-intelligence-rag.git
cd news-intelligence-rag
python3.13 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. (Optional) Add Groq API key for LLM-synthesized answers
Get a free key at https://console.groq.com → copy `.env.example` to `.env`:
```bash
cp .env.example .env
# edit .env: GROQ_API_KEY=gsk_...
```
Without a key, `/ask` still returns the top retrieved articles (graceful degradation).

### 3. One-shot pipeline (ingest → chunk → embed → index)
```bash
python -m scripts.run_pipeline
```
Sample output:
```
[1/4] Ingesting from RSS feeds...
  → corpus size: 60 (new: 60)
[2/4] Chunking articles... → 62 chunks
[3/4] Generating embeddings... → vectors shape: (62, 384)
[4/4] Building & saving FAISS index... done.
```

### 4. Run the API
```bash
uvicorn app.main:app --reload --port 8000
```
Open http://localhost:8000/docs for the interactive Swagger UI.

### 5. Try it out
```bash
# fetch fresh articles
curl -X POST http://localhost:8000/ingest

# rebuild index after ingestion
curl -X POST http://localhost:8000/reindex

# semantic search
curl "http://localhost:8000/search?q=artificial+intelligence&top_k=3"

# RAG QA
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What are the latest tech industry developments?","top_k":4}'

# trends
curl http://localhost:8000/trends
```

## 🧠 Key Design Decisions

- **httpx for fetching, feedparser for parsing** — splits the network IO from the parsing layer; sidesteps macOS Python SSL cert issues by relying on certifi.
- **SHA-1 dedup at the URL level** — repeated pulls don't bloat the corpus or the index.
- **Normalized embeddings + Inner Product** — equivalent to cosine similarity, faster on FAISS.
- **`/reindex` separate from `/ingest`** — lets you re-embed after model swaps without re-fetching.
- **LLM-optional retrieval** — system works without an LLM key; useful for CI tests and offline demos.
- **Heuristic enrichment by default** — keeps install fast; production version would swap to spaCy NER / Hugging Face sentiment.

## 📊 Sample Retrieval Quality

| Query                              | Top match (score) | Source |
|------------------------------------|-------------------|--------|
| "artificial intelligence"          | 0.39 ✅            | Ars Technica — AI models considering user feelings |
| "iran"                             | 0.31 ✅            | BBC — Billions of meals at risk due to Iran war |
| "AI in defense or government"      | 0.50 ✅            | TechCrunch — Pentagon AI deals with Nvidia/MSFT/AWS |

## 🔮 Roadmap

- [ ] Swap heuristic NER for **spaCy / HF transformer pipeline**
- [ ] Cross-encoder **re-ranking** of top-K results
- [ ] **Topic modeling** (BERTopic / LDA) for theme detection
- [ ] **Multi-turn** conversational memory in `/ask`
- [ ] **Streamlit UI** for interactive analyst use
- [ ] **Airflow DAG** for scheduled incremental ingestion (matches resume bullet)
- [ ] **AWS S3** sink for raw articles (matches resume bullet)
- [ ] **Hybrid retrieval** (BM25 + dense)
- [ ] **Dockerize** for deployment

## 👤 Author

**Teeja S** — Data Scientist & AI/ML Engineer
📧 teejasenthilkumar@gmail.com · 💼 [LinkedIn](https://www.linkedin.com/in/teeja-senthilkumar/) · 🌐 [Portfolio](https://datascienceportfol.io/teeja)
