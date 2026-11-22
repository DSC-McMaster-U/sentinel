"""Retrieval adapter tests: mock retriever for the contract, real index for the swap."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from app.retrieval.adapter import RetrievalAdapter, RetrievalRequest
from app.retrieval.search import SearchResult
from app.schemas import Evidence

SAMPLE_REPO = Path(__file__).resolve().parents[1] / "fixtures" / "sample-repo"


class MockRetriever:
    def __init__(self, results):
        self.results = results
        self.calls = []

    def search(self, query, limit=5, *, kinds=None):
        self.calls.append((query, limit, kinds))
        return self.results


def hit(path="SECURITY.md", start=1, end=4, kind="documentation", score=1.5):
    return SearchResult(path, start, end, "Release artifacts must be signed.", kind, score)


def test_results_carry_source_references():
    adapter = RetrievalAdapter(MockRetriever([hit(), hit(".github/workflows/ci.yml", 3, 9, "workflow")]))

    response = adapter.retrieve(RetrievalRequest(query="signing"))

    assert response.query == "signing"
    assert [(r.file_path, r.line_start, r.line_end) for r in response.results] == [
        ("SECURITY.md", 1, 4),
        (".github/workflows/ci.yml", 3, 9),
    ]


def test_request_options_are_forwarded():
    retriever = MockRetriever([])
    RetrievalAdapter(retriever).retrieve(
        RetrievalRequest(query="permissions", limit=3, kinds=["workflow"])
    )

    assert retriever.calls == [("permissions", 3, ["workflow"])]


def test_no_matches_returns_empty_results():
    assert RetrievalAdapter(MockRetriever([])).retrieve(RetrievalRequest(query="x")).results == []


def test_results_can_become_evidence():
    result = RetrievalAdapter(MockRetriever([hit()])).retrieve(RetrievalRequest(query="x")).results[0]

    evidence = Evidence(
        file_path=result.file_path,
        line_start=result.line_start,
        line_end=result.line_end,
        observation=result.content,
    )
    assert evidence.file_path == "SECURITY.md"


@pytest.mark.parametrize("overrides", [{"query": ""}, {"limit": 0}, {"limit": 51}])
def test_invalid_requests_rejected(overrides):
    with pytest.raises(ValidationError):
        RetrievalRequest(**{"query": "x", **overrides})


def test_real_index_returns_security_policy():
    adapter = RetrievalAdapter.from_repository(SAMPLE_REPO)

    response = adapter.retrieve(RetrievalRequest(query="How must release artifacts be protected?"))

    assert response.results[0].file_path == "SECURITY.md"
