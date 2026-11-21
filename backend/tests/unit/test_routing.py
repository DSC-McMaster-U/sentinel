"""Orchestration tested with doubles; production agent implementations are external."""

from itertools import combinations
from threading import Barrier

import pytest

from app.schemas import (
    AgentInput,
    AgentOutput,
    ChangedFile,
    Evidence,
    PullRequestInput,
    SecurityFinding,
)
from app.schemas.review_report import ReviewReport, combine_findings
from app.workflows.graph import build_review_graph, choose_agents, classify_files
from app.workflows.state import AGENT_ORDER, ReviewState, SynthesisUpdate


@pytest.fixture
def sample_pr():
    return PullRequestInput.model_validate({
        "repository": {
            "owner": "example", "name": "sentinel", "full_name": "example/sentinel",
            "url": "https://github.com/example/sentinel", "default_branch": "main",
        },
        "pr_number": 42, "title": "Update build", "author": "contributor",
        "base_branch": "main", "head_branch": "update", "base_sha": "base123",
        "head_sha": "head456", "url": "https://github.com/example/sentinel/pull/42",
        "created_at": "2026-11-17T12:00:00Z", "updated_at": "2026-11-17T12:00:00Z",
    })


def changed_file(path, **overrides):
    return ChangedFile(**{
        "path": path, "status": "modified", "additions": 1, "deletions": 1,
        "patch": "@@ -1 +1 @@\n-old\n+new", **overrides,
    })


@pytest.mark.parametrize(("path", "expected"), [
    ("package.json", ["dependency"]),
    ("frontend/package.json", ["dependency"]),
    ("package-lock.json", ["dependency"]),
    ("web/yarn.lock", ["dependency"]),
    ("pnpm-lock.yaml", ["dependency"]),
    (".github/workflows/ci.yml", ["cicd"]),
    (".github/workflows/release.yaml", ["cicd"]),
    ("Dockerfile", ["release"]),
    ("backend/Dockerfile", ["release"]),
    ("backend/.dockerignore", ["release"]),
    (".github/workflows/package.json", ["dependency", "cicd"]),
    ("README.md", ["synthesis"]),
    ("package.json.bak", ["synthesis"]),
    (".github/workflows-backup/ci.yml", ["synthesis"]),
    ("docs/.github/workflows/ci.yml", ["synthesis"]),
])
def test_intake_routing(sample_pr, path, expected):
    sample_pr.files_changed = [changed_file(path)]
    update = classify_files({"pull_request": sample_pr})
    state: ReviewState = {"pull_request": sample_pr, **update}
    assert choose_agents(state) == expected
    assert set(update["agent_inputs"]) == set(expected) - {"synthesis"}


@pytest.mark.parametrize("status", ["added", "modified", "removed", "copied", "changed"])
def test_change_status_and_missing_patch_preserved(sample_pr, status):
    sample_pr.files_changed = [changed_file("package.json", status=status, patch=None)]
    update = classify_files({"pull_request": sample_pr})
    state: ReviewState = {"pull_request": sample_pr, **update}
    assert choose_agents(state) == ["dependency"]
    assert update["agent_inputs"]["dependency"].changed_files == sample_pr.files_changed


def test_unchanged_file_does_not_select_agent(sample_pr):
    sample_pr.files_changed = [changed_file("package.json", status="unchanged")]
    update = classify_files({"pull_request": sample_pr})
    state: ReviewState = {"pull_request": sample_pr, **update}
    assert choose_agents(state) == ["synthesis"]


@pytest.mark.parametrize(("path", "previous_path", "expected"), [
    ("archive/manifest.txt", "package.json", ["dependency"]),
    ("package.json", "archive/manifest.txt", ["dependency"]),
    ("Dockerfile", ".github/workflows/build.yml", ["cicd", "release"]),
])
def test_rename_classifies_both_paths(sample_pr, path, previous_path, expected):
    sample_pr.files_changed = [changed_file(path, status="renamed", previous_path=previous_path)]
    update = classify_files({"pull_request": sample_pr})
    state: ReviewState = {"pull_request": sample_pr, **update}
    assert choose_agents(state) == expected
    for agent_input in update["agent_inputs"].values():
        assert agent_input.changed_files == sample_pr.files_changed


def test_intake_filters_and_isolates_branch_inputs(sample_pr):
    sample_pr.files_changed = [changed_file(path) for path in (
        "README.md", ".github/workflows/package.json", "frontend/package-lock.json"
    )]
    original = sample_pr.model_dump()
    inputs = classify_files({"pull_request": sample_pr})["agent_inputs"]
    assert [f.path for f in inputs["dependency"].changed_files] == [
        ".github/workflows/package.json", "frontend/package-lock.json"
    ]
    assert [f.path for f in inputs["cicd"].changed_files] == [".github/workflows/package.json"]
    for agent_input in inputs.values():
        assert isinstance(agent_input, AgentInput)
        assert agent_input.pr_number == sample_pr.pr_number
        assert agent_input.commit_sha == sample_pr.head_sha
        assert agent_input.repo_url == str(sample_pr.repository.url)
        assert agent_input.changed_files[0].patch == sample_pr.files_changed[1].patch
    inputs["dependency"].changed_files[0].patch = "branch-local edit"
    assert inputs["cicd"].changed_files[0].patch != "branch-local edit"
    assert sample_pr.model_dump() == original


def finding_for(name, path):
    return SecurityFinding(
        agent=name, title=f"Test finding from {name}",
        description="Synthetic finding used only to verify graph transport.",
        severity="high", recommendation="Review the test observation.",
        evidence=[Evidence(file_path=path, line_start=1, observation="Test evidence")],
        confidence=0.8, uncertainty=[], requires_human_review=False,
    )


_AGENT_SUBSETS = [subset for size in range(4) for subset in combinations(AGENT_ORDER, size)]


@pytest.mark.parametrize("selected", _AGENT_SUBSETS)
def test_parallel_execution_then_single_synthesis(sample_pr, selected):
    paths = {"dependency": "package.json", "cicd": ".github/workflows/ci.yml", "release": "Dockerfile"}
    sample_pr.files_changed = [changed_file(paths[name]) for name in selected]
    # All branches must start before any finishes. Serial execution breaks this
    # barrier, so this verifies concurrency without measuring execution time.
    barrier = Barrier(len(selected)) if selected else None
    synthesis_calls = []

    def agent(name):
        def execute(agent_input):
            assert [f.path for f in agent_input.changed_files] == [paths[name]]
            assert barrier is not None
            barrier.wait(timeout=10)
            return AgentOutput(agent_name=name, status="success", findings=[finding_for(name, paths[name])])
        return execute

    def synthesize(state: ReviewState) -> SynthesisUpdate:
        # Receiving every output proves that every selected branch completed.
        assert "agent_outputs" in state
        assert {o.agent_name for o in state["agent_outputs"]} == set(selected)
        synthesis_calls.append(True)
        pr = state["pull_request"]
        return {"report": combine_findings(
            state["agent_outputs"], pr_number=pr.pr_number,
            repo_url=str(pr.repository.url), commit_sha=pr.head_sha,
        )}

    graph = build_review_graph(
        agent_nodes={name: agent(name) for name in AGENT_ORDER}, synthesis_node=synthesize,
    )
    result = graph.invoke({"pull_request": sample_pr})
    assert synthesis_calls == [True]
    assert len(result["agent_outputs"]) == len(selected)
    report = ReviewReport.model_validate_json(result["report"].model_dump_json())
    assert set(report.agents_run) == set(selected)
    assert {f.agent for f in report.findings} == set(selected)
    assert report.pr_number == sample_pr.pr_number
    assert report.commit_sha == sample_pr.head_sha

    # Reusing the compiled graph starts a fresh review without previous results.
    sample_pr.files_changed = [changed_file("README.md")]
    selected = ()
    second = graph.invoke({"pull_request": sample_pr})
    assert second["agent_outputs"] == []
    assert second["report"].agents_run == []
    assert second["report"].findings == []
    assert synthesis_calls == [True, True]


def test_missing_agent_registration_rejected():
    with pytest.raises(ValueError, match="exactly"):
        build_review_graph(
            agent_nodes={},
            synthesis_node=lambda state: pytest.fail("Invalid registration reached synthesis"),
        )


def test_output_from_wrong_agent_rejected(sample_pr):
    sample_pr.files_changed = [changed_file("package.json")]
    graph = build_review_graph(
        agent_nodes={name: lambda data: AgentOutput(
            agent_name="cicd", status="success", findings=[]
        ) for name in AGENT_ORDER},
        synthesis_node=lambda state: pytest.fail("Invalid output reached synthesis"),
    )
    with pytest.raises(ValueError, match="Expected output from dependency"):
        graph.invoke({"pull_request": sample_pr})
