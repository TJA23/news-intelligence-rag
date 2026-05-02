from typing import Iterable

from groq import Groq

from app.config import GROQ_API_KEY, GROQ_MODEL
from app.vectorstore import Hit


SYSTEM_PROMPT = (
    "You are a careful news analyst. Answer the user's question using ONLY the "
    "context articles provided. If the context does not contain the answer, say "
    "so plainly — do not speculate. Cite sources by their [Source: outlet — title] "
    "tag inline. Keep answers concise, factual, and time-aware (the context is "
    "from real news articles)."
)


def _format_context(hits: Iterable[Hit]) -> str:
    blocks = []
    for hit in hits:
        blocks.append(f"[Source: {hit.source} — {hit.title}]\n{hit.text}")
    return "\n\n".join(blocks)


def generate_answer(question: str, hits: list[Hit]) -> str:
    if not hits:
        return "No relevant articles found in the corpus. Try /ingest to fetch the latest news."

    context = _format_context(hits)
    user_msg = (
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        "Answer using only the context above. Cite sources inline."
    )

    if not GROQ_API_KEY:
        snippet = "\n\n".join(f"• [{h.source}] {h.title}: {h.text[:280]}..." for h in hits)
        return (
            "[Groq API key not set — returning retrieved articles without LLM synthesis.]\n\n"
            f"Top retrieved articles:\n\n{snippet}"
        )

    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.2,
        max_tokens=600,
    )
    return response.choices[0].message.content.strip()
