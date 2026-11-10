"""Tests for backend/app/schemas/pull_request.py (#7)."""

import pytest
from pydantic import ValidationError

from backend.app.schemas.pull_request import (
    ChangedFile,
    FileChangeStatus,
    PullRequestInput,
    Repository,
)


def _sample_payload() -> dict:
    return {
        "repository": {
            "owner": "DSC-McMaster-U",
            "name": "sentinel",
            "full_name": "DSC-McMaster-U/sentinel",
            "url": "https://github.com/DSC-McMaster-U/sentinel",
            "default_branch": "main",
        },
        "number": 42,
        "title": "Bump lodash to 4.17.21",
        "description": "Routine dependency bump",
        "author": "ronnphil",
        "base_branch": "main",
        "head_branch": "deps/bump-lodash",
        "base_sha": "abc123",
        "head_sha": "def456",
        "url": "https://github.com/DSC-McMaster-U/sentinel/pull/42",
        "created_at": "2026-11-10T12:00:00Z",
        "updated_at": "2026-11-10T12:05:00Z",
        "files_changed": [
            {
                "path": "package.json",
                "status": "modified",
                "additions": 1,
                "deletions": 1,
                "patch": '-  "lodash": "4.17.20"\n+  "lodash": "4.17.21"',
            }
        ],
    }


def test_valid_payload_round_trips():
    pr = PullRequestInput.model_validate(_sample_payload())

    assert pr.number == 42
    assert pr.repository.full_name == "DSC-McMaster-U/sentinel"
    assert len(pr.files_changed) == 1
    assert pr.files_changed[0].status is FileChangeStatus.modified

    dumped = pr.model_dump(mode="json")
    assert dumped["files_changed"][0]["previous_path"] is None


def test_files_changed_defaults_to_empty_list():
    payload = _sample_payload()
    del payload["files_changed"]

    pr = PullRequestInput.model_validate(payload)

    assert pr.files_changed == []


def test_description_is_optional():
    payload = _sample_payload()
    del payload["description"]

    pr = PullRequestInput.model_validate(payload)

    assert pr.description is None


@pytest.mark.parametrize("field", ["additions", "deletions"])
def test_negative_line_counts_are_rejected(field):
    payload = _sample_payload()
    payload["files_changed"][0][field] = -1

    with pytest.raises(ValidationError):
        PullRequestInput.model_validate(payload)


def test_invalid_file_status_is_rejected():
    payload = _sample_payload()
    payload["files_changed"][0]["status"] = "yeeted"

    with pytest.raises(ValidationError):
        PullRequestInput.model_validate(payload)


def test_invalid_repository_url_is_rejected():
    payload = _sample_payload()
    payload["repository"]["url"] = "not-a-url"

    with pytest.raises(ValidationError):
        Repository.model_validate(payload["repository"])


def test_renamed_file_can_carry_previous_path():
    changed_file = ChangedFile.model_validate(
        {
            "path": "src/new_name.py",
            "status": "renamed",
            "additions": 0,
            "deletions": 0,
            "previous_path": "src/old_name.py",
        }
    )

    assert changed_file.previous_path == "src/old_name.py"
