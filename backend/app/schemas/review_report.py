"""Combining multiple agents' findings into one review report (#7).

Builds on the SecurityFinding and AgentOutput schemas in `finding.py` and
`agent.py`.
"""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field

from .agent import AgentOutput
from .finding import SecurityFinding

_SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


class ReviewReport(BaseModel):
    """The final, combined output of a review: every agent's findings in one
    deduplicated, severity-ordered list, plus which agents actually ran.
    """

    pr_number: int = Field(ge=1)
    repo_url: str = Field(min_length=1)
    commit_sha: str = Field(min_length=1)
    generated_at: datetime
    findings: list[SecurityFinding]
    agents_run: list[str] = Field(default_factory=list)
    agents_failed: list[str] = Field(
        default_factory=list, description="Agents whose status was 'failure'."
    )
    agents_partial: list[str] = Field(
        default_factory=list, description="Agents whose status was 'partial'."
    )
    requires_human_review: bool

    @property
    def severity_counts(self) -> dict[str, int]:
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for finding in self.findings:
            counts[finding.severity] += 1
        return counts


def _same_finding(a: SecurityFinding, b: SecurityFinding) -> bool:
    """Two findings are the same claim if they're from the same agent, have
    the same title, and point at the same evidence locations.
    """
    if a.agent != b.agent or a.title != b.title:
        return False

    a_locations = {(e.file_path, e.line_start, e.line_end) for e in a.evidence}
    b_locations = {(e.file_path, e.line_start, e.line_end) for e in b.evidence}
    return a_locations == b_locations


def combine_findings(
    outputs: list[AgentOutput],
    *,
    pr_number: int,
    repo_url: str,
    commit_sha: str,
    generated_at: datetime | None = None,
) -> ReviewReport:
    """Merge every agent's output into a single deduplicated review report.

    An agent that failed entirely contributes no findings; one that reported
    "partial" still contributes whatever findings it managed to produce.
    Duplicate findings (same agent, title and evidence locations) are kept
    once. The report requires human review if any individual finding asks
    for it, or if any agent didn't fully succeed.
    """
    merged: list[SecurityFinding] = []
    agents_run: list[str] = []
    agents_failed: list[str] = []
    agents_partial: list[str] = []

    for output in outputs:
        agents_run.append(output.agent_name)

        if output.status == "failure":
            agents_failed.append(output.agent_name)
            continue

        if output.status == "partial":
            agents_partial.append(output.agent_name)

        for finding in output.findings:
            if not any(_same_finding(finding, existing) for existing in merged):
                merged.append(finding)

    merged.sort(key=lambda f: _SEVERITY_ORDER.get(f.severity, len(_SEVERITY_ORDER)))

    return ReviewReport(
        pr_number=pr_number,
        repo_url=repo_url,
        commit_sha=commit_sha,
        generated_at=generated_at or datetime.now(timezone.utc),
        findings=merged,
        agents_run=agents_run,
        agents_failed=agents_failed,
        agents_partial=agents_partial,
        requires_human_review=bool(agents_failed)
        or bool(agents_partial)
        or any(f.requires_human_review for f in merged),
    )
