"""Incoming pull request data: the normalized shape the Intake agent reads
from and every downstream agent (Dependency, CI/CD, Release) inspects.

Owners: Ronn + Neel (#7).
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, HttpUrl, model_validator


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
    path: str = Field(min_length=1)
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

    @model_validator(mode="after")
    def validate_rename_has_previous_path(self) -> ChangedFile:
        if self.status is FileChangeStatus.renamed and not self.previous_path:
            raise ValueError("A renamed file requires previous_path")
        return self


class PullRequestInput(BaseModel):
    """The normalized pull request the review workflow operates on.

    This is what a GitHub webhook payload, or a seeded fixture in
    evaluation/fixtures/, gets mapped into before anything touches the
    LangGraph workflow or an agent.
    """

    repository: Repository
    number: int = Field(ge=1)
    title: str = Field(min_length=1)
    description: str | None = None
    author: str = Field(min_length=1)
    base_branch: str = Field(min_length=1)
    head_branch: str = Field(min_length=1)
    base_sha: str = Field(min_length=1)
    head_sha: str = Field(min_length=1)
    url: HttpUrl
    created_at: datetime
    updated_at: datetime
    files_changed: list[ChangedFile] = Field(default_factory=list)
