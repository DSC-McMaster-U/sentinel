"""Risk synthesis: combine, deduplicate and score findings. Owners: Neel + Alex (#1)."""

from app.schemas.review_report import combine_findings
from app.workflows.state import ReviewState, SynthesisUpdate


def synthesize(state: ReviewState) -> SynthesisUpdate:
    """Combine every agent's output into the final ReviewReport.

    Agents that were not routed contribute no outputs, so an empty list yields
    an empty report.
    """
    pull_request = state["pull_request"]
    report = combine_findings(
        state.get("agent_outputs", []),
        pr_number=pull_request.pr_number,
        repo_url=str(pull_request.repository.url),
        commit_sha=pull_request.head_sha,
    )
    return {"report": report}
