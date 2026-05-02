"""Lightweight, dependency-free enrichment: entities, sentiment, topics.

Avoids heavy NLP installs (spaCy models, transformer pipelines) so the
project stays fast to install and run. Uses simple but effective heuristics
suitable for portfolio/demo purposes — easy to swap for spaCy/HF later.
"""

import re
from collections import Counter
from typing import Iterable

POSITIVE_WORDS = {
    "good", "great", "win", "wins", "gain", "growth", "boost", "rise", "soar",
    "soared", "agreement", "deal", "success", "successful", "approved", "record",
    "high", "strong", "rally", "surge", "improve", "improved", "improves",
    "celebrate", "praise", "milestone", "breakthrough",
}

NEGATIVE_WORDS = {
    "bad", "loss", "lose", "lost", "fall", "fell", "drop", "decline", "crisis",
    "death", "killed", "war", "attack", "fail", "failed", "warn", "warning",
    "fear", "fears", "fired", "layoff", "layoffs", "shutdown", "ban", "banned",
    "scandal", "fraud", "collapse", "outage", "breach", "hack", "hacked",
    "violence", "deadly",
}

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "of", "to", "in", "on", "at", "by",
    "for", "with", "as", "is", "are", "was", "were", "be", "been", "being",
    "this", "that", "these", "those", "it", "its", "his", "her", "their", "our",
    "from", "into", "over", "after", "before", "than", "then", "have", "has",
    "had", "will", "would", "could", "should", "can", "may", "also", "more",
    "new", "said", "says", "say", "told",
}

# RSS boilerplate / non-entity tokens to skip
BOILERPLATE = {
    "Continue", "Comments URL", "Points", "Show HN", "Ask HN", "Comments",
    "Article URL", "Tell HN", "Read", "Read More", "More", "View", "Source",
    "BBC", "BBC News", "Reuters", "NPR", "Guardian", "Hacker News", "TechCrunch",
    "Ars Technica", "The Guardian", "URL", "Posted", "Hours Ago", "Minutes Ago",
}

ENTITY_PATTERN = re.compile(r"\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){0,3})\b")
WORD_PATTERN = re.compile(r"\b[a-zA-Z]{4,}\b")


def extract_entities(text: str, top_k: int = 5) -> list[str]:
    candidates = ENTITY_PATTERN.findall(text)
    filtered = [
        c for c in candidates
        if c.lower() not in STOPWORDS and c not in BOILERPLATE
    ]
    counts = Counter(filtered)
    return [name for name, _ in counts.most_common(top_k)]


def trending_topics(articles, top_k: int = 10) -> list[tuple[str, int]]:
    counter: Counter = Counter()
    for art in articles:
        counter.update(extract_entities(f"{art['title']} {art['text']}", top_k=20))
    return [(n, c) for n, c in counter.most_common(top_k * 3) if c >= 2][:top_k]


def sentiment_score(text: str) -> dict:
    words = [w.lower() for w in WORD_PATTERN.findall(text)]
    pos = sum(1 for w in words if w in POSITIVE_WORDS)
    neg = sum(1 for w in words if w in NEGATIVE_WORDS)
    total = pos + neg
    if total == 0:
        label = "neutral"
        score = 0.0
    else:
        score = (pos - neg) / total
        label = "positive" if score > 0.2 else "negative" if score < -0.2 else "neutral"
    return {"label": label, "score": round(score, 3), "pos_hits": pos, "neg_hits": neg}


