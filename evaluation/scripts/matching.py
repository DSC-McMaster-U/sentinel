"""Deterministic Sprint 1 finding comparison; see evaluation/README.md."""

from dataclasses import dataclass, field
from app.schemas import SecurityFinding


@dataclass
class MatchResult:
    """Pairs are (expected, actual); other lists contain original finding objects."""

    matched: list[tuple[SecurityFinding, SecurityFinding]] = field(default_factory=list)
    missed: list[SecurityFinding] = field(default_factory=list)
    unexpected: list[SecurityFinding] = field(default_factory=list)
    duplicates: list[SecurityFinding] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not (self.missed or self.unexpected or self.duplicates)


def _key(finding: SecurityFinding) -> tuple:
    # Exact regression matching, separate from stable finding IDs. Evidence order is irrelevant.
    locations = frozenset(
        (e.file_path, e.line_start, e.line_end) for e in finding.evidence
    )
    return finding.agent, finding.title, locations


def compare_findings(
    expected: list[SecurityFinding], actual: list[SecurityFinding]
) -> MatchResult:
    """Compare validated findings for ONE fixture, without changing either input.

    Exact agent/title/location identity only; no semantic or fuzzy matching.
    Duplicate expected identities are annotation errors. Repeated actual
    identities fail the case but are excluded from unique-finding precision.
    """
    expected_by_key = {}
    for finding in expected:
        key = _key(finding)
        if key in expected_by_key:
            raise ValueError("Expected findings contain a duplicate identity")
        expected_by_key[key] = finding

    result = MatchResult()
    seen = set()
    for finding in actual:
        key = _key(finding)
        if key in seen:
            result.duplicates.append(finding)
            continue
        seen.add(key)
        if key in expected_by_key:
            result.matched.append((expected_by_key[key], finding))
        else:
            result.unexpected.append(finding)
    result.missed = [f for key, f in expected_by_key.items() if key not in seen]
    return result
