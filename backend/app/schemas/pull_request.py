"""Incoming pull request data: the normalized shape the Intake agent reads
from and every downstream agent (Dependency, CI/CD, Release) inspects.

Owners: Ronn + Neel (#7).
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, HttpUrl


class FileChangeStatus(str, Enum):
    added = "added"
    modified = "modified"
    removed = "removed"
    renamed = "renamed"


class Repository(BaseModel):
    owner: str
    name: str
    full_name: str
    url: HttpUrl
    default_branch: str


class ChangedFile(BaseModel):
    path: str
    status: FileChangeStatus
    additions: int = Field(ge=0)
    deletions: int = Field(ge=0)
    patch: str | None = Field(
        default=None,
        description="Unified diff for this file, when GitHub provides one.",
    )
    previous_path: str | None = Field(
        default=None,
        description="Set when status is 'renamed'.",
    )


class PullRequestInput(BaseModel):
    """The normalized pull request the review workflow operates on.

    This is what a GitHub webhook payload, or a seeded fixture in
    evaluation/fixtures/, gets mapped into before anything touches the
    LangGraph workflow or an agent.
    """

    repository: Repository
    number: int
    title: str
    description: str | None = None
    author: str
    base_branch: str
    head_branch: str
    base_sha: str
    head_sha: str
    url: HttpUrl
    created_at: datetime
    updated_at: datetime
    files_changed: list[ChangedFile] = Field(default_factory=list)
