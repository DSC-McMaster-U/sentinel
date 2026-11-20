"""Keyword retrieval over ingested chunks using BM25 (standard library only)."""

from collections import Counter
from collections.abc import Iterable
import math
import re

from app.retrieval.ingestion import RepositoryChunk, ingest_repository

from .models import SearchResult

_TOKEN = re.compile(r"[a-z0-9]+")
_STOPWORDS = frozenset({
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "how", "in",
    "is", "it", "of", "on", "or", "that", "the", "to", "was", "what", "when",
    "where", "which", "who", "with",
})


def tokenize(text: str) -> list[str]:
    """Lowercase, split on non-alphanumerics and drop stopwords."""
    return [t for t in _TOKEN.findall(text.lower()) if t not in _STOPWORDS]


class KeywordIndex:
    """In-memory BM25 index. Build once, then call search() repeatedly."""

    def __init__(self, chunks: Iterable[RepositoryChunk], *, k1: float = 1.5, b: float = 0.75):
        self._chunks = tuple(chunks)
        self._k1, self._b = k1, b
        self._terms = [Counter(tokenize(c.content)) for c in self._chunks]
        self._lengths = [sum(t.values()) for t in self._terms]
        self._avg_length = (sum(self._lengths) / len(self._lengths)) if self._lengths else 0.0
        doc_freq: Counter[str] = Counter()
        for terms in self._terms:
            doc_freq.update(terms.keys())
        n = len(self._chunks)
        self._idf = {t: math.log(1 + (n - df + 0.5) / (df + 0.5)) for t, df in doc_freq.items()}

    def search(
        self, query: str, limit: int = 5, *, kinds: Iterable[str] | None = None,
    ) -> list[SearchResult]:
        """Return up to `limit` best chunks; [] for empty or unmatched queries.

        Ties break by path then line so results are repeatable. `kinds`
        restricts results, e.g. {"workflow"} or {"documentation"}.
        """
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
            raise ValueError("limit must be a positive integer")
        query_terms = set(tokenize(query))
        allowed = None if kinds is None else frozenset(kinds)
        scored: list[tuple[float, RepositoryChunk]] = []
        for chunk, terms, length in zip(self._chunks, self._terms, self._lengths):
            if allowed is not None and chunk.kind not in allowed:
                continue
            score = 0.0
            for term in query_terms:
                freq = terms.get(term, 0)
                if freq:
                    norm = 1 - self._b + self._b * length / self._avg_length
                    score += self._idf[term] * freq * (self._k1 + 1) / (freq + self._k1 * norm)
            if score > 0:
                scored.append((score, chunk))
        scored.sort(key=lambda s: (-s[0], s[1].file_path, s[1].line_start))
        return [
            SearchResult(c.file_path, c.line_start, c.line_end, c.content, c.kind, round(s, 6))
            for s, c in scored[:limit]
        ]


def search_repository(
    root, query: str, limit: int = 5, *, kinds: Iterable[str] | None = None,
) -> list[SearchResult]:
    """Ingest a local repository and search it: the one-call entry point."""
    return KeywordIndex(ingest_repository(root).chunks).search(query, limit, kinds=kinds)
