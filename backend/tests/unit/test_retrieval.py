from pathlib import Path

import pytest

from app.retrieval.ingestion import RepositoryChunk, ingest_repository
from app.retrieval.search import KeywordIndex, SearchResult, search_repository, tokenize

FIXTURE = Path(__file__).parents[1] / "fixtures" / "sample-repo"


def chunk(path, text, kind="documentation", start=1):
    return RepositoryChunk(path, start, start + text.count("\n"), text, kind)


def test_release_question_finds_security_policy_first():
    results = search_repository(FIXTURE, "How must release artifacts be protected?")
    top = results[0]
    assert isinstance(top, SearchResult)
    assert (top.file_path, top.line_start, top.line_end) == ("SECURITY.md", 1, 4)
    assert top.kind == "documentation"
    assert "signed" in top.content and top.score > 0


def test_workflow_query_finds_workflow_file():
    results = search_repository(FIXTURE, "workflow permissions contents read")
    assert results[0].file_path == ".github/workflows/release.yml"


def test_kinds_filter():
    results = search_repository(FIXTURE, "release", kinds={"workflow"})
    assert results and all(r.kind == "workflow" for r in results)
    assert search_repository(FIXTURE, "release", kinds=set()) == []


def test_no_match_and_empty_queries_return_nothing():
    assert search_repository(FIXTURE, "zzzxyz") == []
    assert search_repository(FIXTURE, "") == []
    assert search_repository(FIXTURE, "the of and") == []
    assert KeywordIndex([]).search("anything") == []


def test_limit_and_validation():
    index = KeywordIndex(ingest_repository(FIXTURE).chunks)
    assert len(index.search("release", limit=1)) == 1
    for bad in (0, -1, True, "3"):
        with pytest.raises(ValueError):
            index.search("release", limit=bad)


def test_rare_terms_and_repeated_terms_rank_higher():
    index = KeywordIndex([
        chunk("a.md", "signing signing signing policy"),
        chunk("b.md", "policy policy policy policy overview"),
        chunk("c.md", "policy overview"),
    ])
    assert [r.file_path for r in index.search("signing policy")][0] == "a.md"


def test_ties_are_ordered_by_path_and_line_and_repeatable():
    chunks = [chunk("z.md", "token"), chunk("a.md", "token", start=9), chunk("a.md", "token")]
    index = KeywordIndex(chunks)
    got = [(r.file_path, r.line_start) for r in index.search("token")]
    assert got == [("a.md", 1), ("a.md", 9), ("z.md", 1)]
    assert index.search("token") == index.search("token")


def test_results_keep_source_references():
    chunks = [chunk("docs/x.md", "alpha\nbeta\ngamma", start=40)]
    (result,) = KeywordIndex(chunks).search("beta")
    assert (result.file_path, result.line_start, result.line_end) == ("docs/x.md", 40, 42)


def test_tokenize():
    assert tokenize("How must Release-Artifacts be SIGNED?") == ["must", "release", "artifacts", "signed"]
