"""End-to-end pipeline: ingest articles → chunk → embed → build FAISS index.

Run from project root:
    python -m scripts.run_pipeline
"""

from app.chunking import build_chunks
from app.embeddings import embed
from app.ingest import ingest_all
from app.vectorstore import VectorStore


def main() -> None:
    print("[1/4] Ingesting from RSS feeds...")
    result = ingest_all()
    print(f"  → corpus size: {result['total_in_corpus']} (new: {result['new_articles']})")
    for source, count in result["per_source"].items():
        marker = "✗" if count == -1 else "+"
        print(f"     {marker} {source}: {count}")

    print("[2/4] Chunking articles...")
    chunks = build_chunks()
    print(f"  → {len(chunks)} chunks")

    if not chunks:
        print("  No chunks built — corpus may be empty. Aborting.")
        return

    print("[3/4] Generating embeddings...")
    vectors = embed([c["text"] for c in chunks])
    print(f"  → vectors shape: {vectors.shape}")

    print("[4/4] Building & saving FAISS index...")
    store = VectorStore()
    store.build(chunks, vectors)
    store.save()
    print("Pipeline complete.")


if __name__ == "__main__":
    main()
