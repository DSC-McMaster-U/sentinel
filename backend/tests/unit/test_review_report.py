"""Tests for backend/app/schemas/review_report.py (#7)."""

from datetime import datetime, timezone

from backend.app.schemas.agent import AgentOutput
from backend.app.schemas.finding import Evidence, SecurityFinding
from backend.app.schemas.review_report import combine_findings


def _finding(
    agent: str,
    title: str,
    severity: str = "high",
    file_path: str = "src/app.py",
    line_start: int = 10,
    requires_human_review: bool = False,
) -> SecurityFinding:
    return SecurityFinding(
        agent=agent,
        title=title,
        description="A representative description of the issue.",
        severity=severity,
        recommendation="Do the safe thing instead.",
        evidence=[
            Evidence(
                file_path=file_path,
                line_start=line_start,
                line_end=None,
                observation="Something suspicious was observed here.",
            )
        ],
        confidence=0.8,
        uncertainty=[],
        requires_human_review=requires_human_review,
    )


def test_combines_findings_from_multiple_successful_agents():
    outputs = [
        AgentOutput(
            agent_name="dependency",
            findings=[_finding("dependency", "Unpinned version", severity="high")],
            status="success",
        ),
        AgentOutput(
            agent_name="cicd",
            findings=[_finding("cicd", "Unpinned GitHub Action", severity="critical")],
            status="success",
        ),
    ]

    report = combine_findings(
        outputs,
        pr_number=42,
        repo_url="https://github.com/DSC-McMaster-U/sentinel",
        commit_sha="abc123",
    )

    assert report.agents_run == ["dependency", "cicd"]
    assert report.agents_failed == []
    assert report.agents_partial == []
    assert len(report.findings) == 2
    assert report.findings[0].severity == "critical"
    assert report.findings[1].severity == "high"
    assert report.severity_counts == {"critical": 1, "high": 1, "medium": 0, "low": 0}


def test_failed_agent_contributes_no_findings_but_is_recorded():
    outputs = [
        AgentOutput(
            agent_name="release",
            findings=[],
            status="failure",
            error_message="Timed out talking to the registry.",
        ),
    ]

    report = combine_findings(
        outputs,
        pr_number=1,
        repo_url="https://github.com/DSC-McMaster-U/sentinel",
        commit_sha="abc123",
    )

    assert report.agents_run == ["release"]
    assert report.agents_failed == ["release"]
    assert report.findings == []
    assert report.requires_human_review is True


def test_partial_agent_keeps_its_findings_and_flags_human_review():
    outputs = [
        AgentOutput(
            agent_name="cicd",
            findings=[_finding("cicd", "Unsafe trigger")],
            status="partial",
            error_message="Only checked half the workflow files before timing out.",
        ),
    ]

    report = combine_findings(
        outputs,
        pr_number=1,
        repo_url="https://github.com/DSC-McMaster-U/sentinel",
        commit_sha="abc123",
    )

    assert report.agents_partial == ["cicd"]
    assert len(report.findings) == 1
    assert report.requires_human_review is True


def test_duplicate_findings_from_the_same_agent_are_deduplicated():
    duplicate = _finding("dependency", "Unpinned version")
    outputs = [
        AgentOutput(agent_name="dependency", findings=[duplicate, duplicate], status="success"),
    ]

    report = combine_findings(
        outputs,
        pr_number=1,
        repo_url="https://github.com/DSC-McMaster-U/sentinel",
        commit_sha="abc123",
    )

    assert len(report.findings) == 1


def test_same_title_different_evidence_is_not_deduplicated():
    outputs = [
        AgentOutput(
            agent_name="dependency",
            findings=[
                _finding("dependency", "Unpinned version", file_path="package.json"),
                _finding("dependency", "Unpinned version", file_path="requirements.txt"),
            ],
            status="success",
        ),
    ]

    report = combine_findings(
        outputs,
        pr_number=1,
        repo_url="https://github.com/DSC-McMaster-U/sentinel",
        commit_sha="abc123",
    )

    assert len(report.findings) == 2


def test_no_review_required_when_everything_succeeds_cleanly():
    outputs = [
        AgentOutput(
            agent_name="dependency",
            findings=[_finding("dependency", "Minor note", severity="low")],
            status="success",
        ),
    ]

    report = combine_findings(
        outputs,
        pr_number=1,
        repo_url="https://github.com/DSC-McMaster-U/sentinel",
        commit_sha="abc123",
        generated_at=datetime(2026, 11, 11, tzinfo=timezone.utc),
    )

    assert report.requires_human_review is False
    assert report.generated_at == datetime(2026, 11, 11, tzinfo=timezone.utc)
