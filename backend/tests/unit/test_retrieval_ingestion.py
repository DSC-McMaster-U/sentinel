from pathlib import Path

import pytest

from app.retrieval.ingestion import ingest_repository
from app.retrieval.ingestion.pipeline import classify_file


FIXTURE = Path(__file__).parents[1] / "fixtures" / "sample-repo"


def test_sample_repository():
    result = ingest_repository(FIXTURE)
    assert not result.skipped_files
    assert [c.file_path for c in result.chunks] == [
        ".github/workflows/release.yml", "SECURITY.md", "package.json",
    ]
    assert [c.kind for c in result.chunks] == ["workflow", "documentation", "dependency"]
    security = result.chunks[1]
    assert (security.line_start, security.line_end) == (1, 4)
    assert "Release artifacts must be signed" in security.content
    assert result == ingest_repository(FIXTURE)


@pytest.mark.parametrize("name,kind", [
    ("docs/design.md", "documentation"), ("requirements-dev.txt", "dependency"),
    ("uv.lock", "dependency"), ("infra/main.tf", "configuration"),
    ("Dockerfile", "configuration"), ("compose.yaml", "configuration"),
    ("src/main.py", None), (".env", None), (".env.example", None),
    ("private.key", None),
])
def test_selection(name, kind):
    assert classify_file(name) == kind


def test_chunk_references_match_source(tmp_path):
    source = "# Policy\r\n\r\nSign releases\r\nAudit\u2028trail\r\nLast line"
    (tmp_path / "SECURITY.md").write_bytes(b"\xef\xbb\xbf" + source.encode())
    chunks = ingest_repository(tmp_path, chunk_lines=2).chunks
    assert [(c.line_start, c.line_end) for c in chunks] == [(1, 2), (3, 4), (5, 5)]
    assert chunks[1].content == "Sign releases\nAudit\u2028trail"
    assert chunks[2].content == "Last line"


def test_unsafe_and_generated_files_are_excluded(tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "README.md").write_text("outside")
    root = tmp_path / "repo"
    root.mkdir()
    (root / "SECURITY.md").symlink_to(outside / "README.md")
    (root / "linked").symlink_to(outside, target_is_directory=True)
    for directory in [".git", "node_modules", ".venv", "dist"]:
        (root / directory).mkdir()
        (root / directory / "README.md").write_text("excluded")
    (root / ".env").write_text("TOKEN=example")
    result = ingest_repository(root)
    assert result.chunks == ()
    assert [(s.file_path, s.reason) for s in result.skipped_files] == [("SECURITY.md", "symlink")]


def test_invalid_binary_oversize_and_empty_files(tmp_path):
    for name, data in {"binary.md": b"a\x00b", "invalid.md": b"\xff", "large.md": b"x" * 11,
                       "empty.md": b"", "blank.md": b"\n \n", "valid.md": b"x" * 10}.items():
        (tmp_path / name).write_bytes(data)
    result = ingest_repository(tmp_path, max_file_bytes=10)
    assert [c.file_path for c in result.chunks] == ["valid.md"]
    assert {s.reason for s in result.skipped_files} == {"binary content", "not UTF-8", "file exceeds max_file_bytes"}


@pytest.mark.parametrize("option,value", [("chunk_lines", 0), ("chunk_lines", -1),
    ("chunk_lines", True), ("chunk_lines", 1.5), ("max_file_bytes", 0), ("max_file_bytes", False)])
def test_invalid_limits(tmp_path, option, value):
    with pytest.raises(ValueError):
        ingest_repository(tmp_path, **{option: value})


def test_invalid_roots(tmp_path):
    with pytest.raises(FileNotFoundError):
        ingest_repository(tmp_path / "missing")
    file = tmp_path / "file"
    file.touch()
    with pytest.raises(NotADirectoryError):
        ingest_repository(file)


def test_unreadable_file_is_reported(tmp_path, monkeypatch):
    (tmp_path / "README.md").write_text("hello")
    def denied(*args, **kwargs):
        raise PermissionError("denied")
    monkeypatch.setattr(Path, "open", denied)
    result = ingest_repository(tmp_path)
    assert not result.chunks
    assert result.skipped_files[0].reason == "unreadable file"
