"""Tests for the mock pull request review endpoint (#3)."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.review_report import ReviewReport

client = TestClient(app)


@pytest.fixture
def sample_pr() -> dict:
    return {
        "repository": {
            "owner": "example",
            "name": "demo",
            "full_name": "example/demo",
            "url": "https://github.com/example/demo",
            "default_branch": "main",
        },
        "pr_number": 42,
        "title": "Update dependencies",
        "author": "contributor",
        "base_branch": "main",
        "head_branch": "update-dependencies",
        "base_sha": "abc123",
        "head_sha": "def456",
        "url": "https://github.com/example/demo/pull/42",
        "created_at": "2026-11-10T12:00:00Z",
        "updated_at": "2026-11-10T12:05:00Z",
        "files_changed": [
            {"path": "package.json", "status": "modified", "additions": 1, "deletions": 1}
        ],
    }


def test_review_returns_mock_dependency_finding(sample_pr: dict) -> None:
    response = client.post("/reviews", json=sample_pr)

    assert response.status_code == 200
    report = ReviewReport.model_validate(response.json()) #response should be same a
    assert report.pr_number == sample_pr["pr_number"]
    assert report.repo_url == sample_pr["repository"]["url"]
    assert report.commit_sha == sample_pr["head_sha"]
    assert report.agents_run == ["dependency"]
    assert len(report.findings) == 1
    assert report.findings[0].agent == "dependency"
    assert report.findings[0].evidence[0].file_path == "package.json"
    assert response.json()["findings"][0]["id"] == report.findings[0].id


def test_review_keeps_finding_id_across_requests_and_commits(sample_pr: dict) -> None:
    first = client.post("/reviews", json=sample_pr)
    sample_pr["head_sha"] = "new-commit"
    later = client.post("/reviews", json=sample_pr)

    assert first.status_code == later.status_code == 200
    assert first.json()["findings"][0]["id"] == later.json()["findings"][0]["id"]
    assert first.json()["commit_sha"] != later.json()["commit_sha"]


def test_review_returns_no_findings_for_unrelated_file(sample_pr: dict) -> None:
    sample_pr["files_changed"][0]["path"] = "README.md"

    response = client.post("/reviews", json=sample_pr)

    assert response.status_code == 200
    report = ReviewReport.model_validate(response.json())
    assert report.findings == []
    assert report.agents_run == []


def test_review_rejects_missing_pr_number(sample_pr: dict) -> None:
    del sample_pr["pr_number"]

    response = client.post("/reviews", json=sample_pr)

    assert response.status_code == 422
    assert any(
        error["loc"] == ["body", "pr_number"] and error["type"] == "missing"
        for error in response.json()["detail"]
    )
