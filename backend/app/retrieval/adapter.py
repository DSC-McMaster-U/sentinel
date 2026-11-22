"""LangGraph-facing adapter that lets agents request repository context.

Agents send a RetrievalRequest and get source-referenced results whose location
fields match the shared Evidence schema. The adapter depends only on the
Retriever protocol, so it works with the real KeywordIndex or a test double.
"""

from collections.abc import Iterable
from typing import Protocol

from pydantic import BaseModel, Field

from app.retrieval.ingestion import ingest_repository
from app.retrieval.search import KeywordIndex, SearchResult


class Retriever(Protocol):
    """Retrieval interface; KeywordIndex satisfies it."""

    def search(
        self, query: str, limit: int = 5, *, kinds: Iterable[str] | None = None
    ) -> list[SearchResult]: ...


class RetrievalRequest(BaseModel):
    query: str = Field(min_length=1, description="Natural-language or keyword question.")
    limit: int = Field(default=5, ge=1, le=50)
    kinds: list[str] | None = Field(
        default=None,
        description="Restrict to chunk kinds, e.g. ['workflow'] for the CI/CD agent.",
    )


class RetrievalResult(BaseModel):
    """A retrieved chunk. Location fields are usable as Evidence."""

    file_path: str
    line_start: int = Field(ge=1)
    line_end: int | None = Field(default=None, ge=1)
    content: str
    kind: str
    score: float


class RetrievalResponse(BaseModel):
    query: str
    results: list[RetrievalResult]


class RetrievalAdapter:
    def __init__(self, retriever: Retriever):
        self._retriever = retriever

    @classmethod
    def from_repository(cls, root) -> "RetrievalAdapter":
        """Ingest a local checkout and index it with BM25 keyword search."""
        return cls(KeywordIndex(ingest_repository(root).chunks))

    def retrieve(self, request: RetrievalRequest) -> RetrievalResponse:
        hits = self._retriever.search(request.query, request.limit, kinds=request.kinds)
        return RetrievalResponse(
            query=request.query,
            results=[
                RetrievalResult(
                    file_path=hit.file_path,
                    line_start=hit.line_start,
                    line_end=hit.line_end,
                    content=hit.content,
                    kind=hit.kind,
                    score=hit.score,
                )
                for hit in hits
            ],
        )
