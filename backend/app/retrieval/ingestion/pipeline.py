"""Local, read-only repository ingestion with source-preserving line chunks."""

from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class RepositoryChunk:
    """Search input; line ranges are inclusive and one-based, like Evidence."""

    file_path: str
    line_start: int
    line_end: int
    content: str
    kind: str


@dataclass(frozen=True)
class SkippedFile:
    file_path: str
    reason: str


@dataclass(frozen=True)
class IngestionResult:
    chunks: tuple[RepositoryChunk, ...]
    skipped_files: tuple[SkippedFile, ...]


_EXCLUDED_DIRS = frozenset({
    ".git", ".hg", ".svn", "node_modules", ".venv", "venv", "__pycache__",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", ".next", ".terraform",
    "dist", "build", "coverage", "vendor",
})
_MANIFESTS = frozenset({
    "package.json", "package-lock.json", "npm-shrinkwrap.json", "yarn.lock",
    "pnpm-lock.yaml", "pyproject.toml", "poetry.lock", "uv.lock", "pipfile",
    "pipfile.lock", "setup.py", "setup.cfg", "cargo.toml", "cargo.lock",
    "go.mod", "go.sum", "gemfile", "gemfile.lock", "pom.xml", "build.gradle",
    "build.gradle.kts", "composer.json", "composer.lock",
})


def classify_file(path: str) -> str | None:
    """Select documentation, dependency manifests, workflows and build config."""
    file = Path(path)
    name = file.name.lower()
    if name.startswith(".env") or file.suffix.lower() in {".pem", ".key", ".p12"}:
        return None
    if name in _MANIFESTS or (name.startswith("requirements") and name.endswith(".txt")):
        return "dependency"
    if file.suffix.lower() in {".md", ".rst"} or name in {"readme", "security", "contributing"}:
        return "documentation"
    if file.parts[:2] == (".github", "workflows") and file.suffix.lower() in {".yml", ".yaml"}:
        return "workflow"
    if (name in {"makefile", "justfile", "jenkinsfile", ".gitlab-ci.yml", ".npmrc", ".yarnrc", ".yarnrc.yml"}
            or name == "dockerfile" or name.startswith("dockerfile.")
            or name in {"docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"}
            or file.suffix.lower() in {".tf", ".toml", ".ini", ".cfg"}):
        return "configuration"
    return None


def ingest_repository(
    root: str | Path, *, chunk_lines: int = 80, max_file_bytes: int = 1_048_576,
) -> IngestionResult:
    """Read selected UTF-8 files in stable path order without following symlinks.

    Non-selected files and excluded directories are ignored. Selected files that
    cannot be read safely are reported in skipped_files. Nothing is executed.
    """
    if isinstance(chunk_lines, bool) or not isinstance(chunk_lines, int) or chunk_lines < 1:
        raise ValueError("chunk_lines must be a positive integer")
    if isinstance(max_file_bytes, bool) or not isinstance(max_file_bytes, int) or max_file_bytes < 1:
        raise ValueError("max_file_bytes must be a positive integer")
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise NotADirectoryError(root)
    chunks: list[RepositoryChunk] = []
    skipped: list[SkippedFile] = []

    def walk_error(error: OSError) -> None:
        path = Path(error.filename).relative_to(root).as_posix()
        skipped.append(SkippedFile(path, "unreadable directory"))

    candidates: list[Path] = []
    for directory, dirs, files in os.walk(root, followlinks=False, onerror=walk_error):
        base = Path(directory)
        dirs[:] = sorted(d for d in dirs if d not in _EXCLUDED_DIRS and not (base / d).is_symlink())
        candidates.extend(base / name for name in files)
    for file in sorted(candidates):
        relative = file.relative_to(root).as_posix()
        kind = classify_file(relative)
        if kind is None:
            continue
        if file.is_symlink():
            skipped.append(SkippedFile(relative, "symlink"))
            continue
        try:
            if not file.is_file():
                skipped.append(SkippedFile(relative, "not a regular file"))
                continue
            with file.open("rb") as stream:
                data = stream.read(max_file_bytes + 1)
            if len(data) > max_file_bytes:
                skipped.append(SkippedFile(relative, "file exceeds max_file_bytes"))
                continue
            if b"\x00" in data:
                skipped.append(SkippedFile(relative, "binary content"))
                continue
            content = data.decode("utf-8-sig")
        except UnicodeDecodeError:
            skipped.append(SkippedFile(relative, "not UTF-8"))
            continue
        except OSError:
            skipped.append(SkippedFile(relative, "unreadable file"))
            continue
        # Only actual newline characters split source lines (not Unicode separators).
        lines = content.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        if lines[-1] == "":
            lines.pop()
        for offset in range(0, len(lines), chunk_lines):
            section = lines[offset:offset + chunk_lines]
            if any(line.strip() for line in section):
                chunks.append(RepositoryChunk(relative, offset + 1, offset + len(section), "\n".join(section), kind))
    return IngestionResult(tuple(chunks), tuple(sorted(skipped, key=lambda item: item.file_path)))
