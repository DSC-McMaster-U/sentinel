"""Build mock review reports for submitted pull requests."""

from app.schemas import (
    AgentOutput,
    Evidence,
    FindingSubject,
    PullRequestInput,
    SecurityFinding,
)
from app.schemas.review_report import ReviewReport, combine_findings


def build_mock_review_report(pull_request: PullRequestInput) -> ReviewReport:
    """Build a mock review report for the submitted PR's head commit.

    For issue #3, a change to the root package.json produces a sample finding.
    The mock uses the submitted file path and does not inspect the diff.

    In issue #9, the service will pass the validated PR to LangGraph instead.
    The workflow will select agents based on the changed files, and their
    outputs will supply the findings in the same ReviewReport response.
    """

    outputs: list[AgentOutput] = []
    manifest = None

    for file in pull_request.files_changed:
        if file.path == "package.json":
            manifest = file
            break

    if manifest is not None:
        finding = SecurityFinding(
            agent="dependency",
            check_id="mock.manifest-changed",
            subject=FindingSubject(file_path=manifest.path, key="manifest"),
            title="Mock finding: dependency manifest changed",
            description="This sample finding shows how Sentinel reports a dependency change.",
            severity="low",
            recommendation="Review the dependency changes before merging.",
            evidence=[
                Evidence(
                    file_path=manifest.path,
                    line_start=1,  # Placeholder required by the Evidence schema.
                    observation="The submitted PR lists package.json as a changed file.",
                )
            ],
            confidence=0.0,
            uncertainty=["This mock review does not inspect the file contents."],
            requires_human_review=False,
        )
        outputs.append(
            AgentOutput(
                agent_name="dependency",
                findings=[finding],
                status="success",
            )
        )

    return combine_findings(
        outputs,
        pr_number=pull_request.pr_number,
        repo_url=str(pull_request.repository.url),
        commit_sha=pull_request.head_sha,
    )
