# 📰 LLM-Powered News Intelligence Platform (RAG-based)

> **Status:** 🚧 Codebase being rebuilt — original lost in laptop failure. Architecture, design, and results documented below.

An intelligent news analysis platform that ingests articles from multiple sources, builds a searchable knowledge base, and answers context-aware questions using **Retrieval-Augmented Generation (RAG)**.

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat&logo=openai&logoColor=white)
![FAISS](https://img.shields.io/badge/FAISS-0084FF?style=flat&logo=meta&logoColor=white)
![Transformers](https://img.shields.io/badge/🤗_Transformers-FFD21E?style=flat&logoColor=black)
![Airflow](https://img.shields.io/badge/Apache_Airflow-017CEE?style=flat&logo=apache-airflow&logoColor=white)
![AWS](https://img.shields.io/badge/AWS_S3-569A31?style=flat&logo=amazon-s3&logoColor=white)
![Status](https://img.shields.io/badge/status-rebuilding-yellow)

---

## 🎯 Problem

News content is fragmented across thousands of sources, with massive volume and noise. Analysts and decision-makers need:
- A unified pipeline to **ingest, deduplicate, and store** news articles
- **Contextual search & question-answering** that goes beyond keyword matching
- Insight extraction: entities, sentiment, topics
- Continuous, automated updates as new articles arrive

## 🏗️ Architecture

```
┌──────────────┐    ┌─────────────┐    ┌────────────────┐    ┌──────────┐
│  News APIs / │ ─► │  Ingestion  │ ─► │  Cleaning &    │ ─► │  AWS S3  │
│  RSS / Feeds │    │  (Python)   │    │  Deduplication │    │  (Raw)   │
└──────────────┘    └─────────────┘    └────────────────┘    └────┬─────┘
                                                                   │
                          ┌────────────────────────────────────────┘
                          ▼
              ┌───────────────────────┐    ┌─────────────────┐
              │  Embeddings           │ ─► │  FAISS Index    │
              │  (Sentence-BERT)      │    │  (Vector Store) │
              └───────────────────────┘    └────────┬────────┘
                                                    │
                          ┌─────────────────────────┘
                          ▼
              ┌───────────────────────┐    ┌────────────────────┐
              │  Retriever            │ ─► │  LLM (GPT)         │ ─► Answer
              │  (Top-K + Re-rank)    │    │  Context-aware QA  │
              └───────────────────────┘    └────────────────────┘

              ┌──────────────────────────┐
              │  Insight Layer           │
              │  • Entity Recognition    │
              │  • Sentiment Analysis    │
              │  • Topic Modeling        │
              └──────────────────────────┘

              Orchestrated by Apache Airflow (scheduled incremental ingestion)
```

## ⚙️ Tech Stack

| Layer            | Technology                                    |
|------------------|-----------------------------------------------|
| Language         | Python 3.10+                                  |
| LLM              | OpenAI GPT (configurable: GPT-4 / GPT-4o)     |
| Embeddings       | Hugging Face Transformers · Sentence-BERT     |
| Vector Store     | FAISS (Facebook AI Similarity Search)         |
| NLP utilities    | spaCy · NLTK · Hugging Face pipelines         |
| Storage          | AWS S3 (raw articles, embeddings, metadata)   |
| Orchestration    | Apache Airflow                                |

## 🔁 Pipeline Stages

1. **Ingestion** — Fetch articles from multiple news sources (APIs, RSS, scraping).
2. **Preprocessing** — Clean HTML, normalize text, deduplicate by hash + semantic similarity.
3. **Storage** — Raw articles + cleaned text written to AWS S3 with metadata (source, timestamp, URL).
4. **Embedding** — Generate dense vector embeddings using Sentence-BERT.
5. **Indexing** — Store embeddings in a FAISS index for fast semantic retrieval.
6. **RAG Query** — User question → embed → retrieve top-K articles → pass as context to GPT → generate grounded answer.
7. **Insight extraction** — Run NER, sentiment, and topic modeling on incoming articles.
8. **Automation** — Airflow DAG runs incremental ingestion + index refresh on schedule.

## 🧠 Key Engineering Decisions

- **RAG over fine-tuning** — keeps the system fresh as news changes daily; no retraining needed.
- **FAISS over hosted vector DB** — fast, free, runs locally; perfect for prototype-to-prod.
- **Deduplication at ingestion** — avoids cluttering the index with near-duplicate articles from wire services.
- **Airflow for incremental updates** — only embeds new articles, not the entire corpus, saving compute.

## 📊 Outcomes

- Built an **intelligent news analysis platform** unifying ingestion, search, and QA.
- Implemented **RAG with FAISS** for context-aware question answering grounded in real articles.
- Performed **NER, sentiment analysis, and topic modeling** for deeper insights.
- Automated the entire pipeline using **Airflow** for periodic, incremental updates.

## 🔮 Future Work

- Multi-modal: ingest video transcripts (YouTube, podcasts).
- Re-ranking with cross-encoders for better top-K precision.
- Streamlit / Next.js frontend for interactive analyst use.
- Hybrid search (BM25 + dense) for better keyword + semantic recall.

## 👤 Author

**Teeja S** — Data Scientist & AI/ML Engineer
📧 teejasenthilkumar@gmail.com · 💼 [LinkedIn](https://www.linkedin.com/in/teeja-senthilkumar/) · 🌐 [Portfolio](https://datascienceportfol.io/teeja)
