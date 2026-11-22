"""End-to-end graph tests using the real placeholder agents and synthesis node."""

import pytest

from app.agents import cicd, dependency, release
from app.agents.synthesis import synthesize
from app.schemas import ChangedFile, PullRequestInput
from app.workflows.graph import build_review_graph


@pytest.fixture
def graph():
    return build_review_graph(
        agent_nodes={
            "dependency": dependency.run,
            "cicd": cicd.run,
            "release": release.run,
        },
        synthesis_node=synthesize,
    )


def make_pr(*paths):
    return PullRequestInput.model_validate({
        "repository": {
            "owner": "example", "name": "sentinel", "full_name": "example/sentinel",
            "url": "https://github.com/example/sentinel", "default_branch": "main",
        },
        "pr_number": 42, "title": "Update", "author": "contributor",
        "base_branch": "main", "head_branch": "update", "base_sha": "base123",
        "head_sha": "head456", "url": "https://github.com/example/sentinel/pull/42",
        "created_at": "2026-11-17T12:00:00Z", "updated_at": "2026-11-17T12:00:00Z",
        "files_changed": [
            ChangedFile(path=p, status="modified", additions=1, deletions=1).model_dump()
            for p in paths
        ],
    })


@pytest.mark.parametrize(("paths", "agents"), [
    (["package.json"], {"dependency"}),
    ([".github/workflows/ci.yml"], {"cicd"}),
    (["Dockerfile"], {"release"}),
    (["package.json", ".github/workflows/ci.yml"], {"dependency", "cicd"}),
])
def test_relevant_changes_trigger_matching_agents(graph, paths, agents):
    report = graph.invoke({"pull_request": make_pr(*paths)})["report"]

    assert set(report.agents_run) == agents
    assert {finding.agent for finding in report.findings} == agents
    assert report.pr_number == 42
    assert report.commit_sha == "head456"
    assert not report.agents_failed


def test_findings_reference_changed_files(graph):
    report = graph.invoke({"pull_request": make_pr("web/package.json")})["report"]

    assert [e.file_path for f in report.findings for e in f.evidence] == ["web/package.json"]


def test_unrelated_changes_produce_empty_report(graph):
    report = graph.invoke({"pull_request": make_pr("README.md")})["report"]

    assert report.findings == []
    assert report.agents_run == []
    assert not report.requires_human_review
