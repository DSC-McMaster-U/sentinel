"""Search result record; location fields match the shared Evidence schema."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SearchResult:
    """A ranked chunk; line ranges are inclusive and one-based, like Evidence."""

    file_path: str
    line_start: int
    line_end: int
    content: str
    kind: str
    score: float
