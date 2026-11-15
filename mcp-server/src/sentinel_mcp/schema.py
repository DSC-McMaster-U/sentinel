"""Incoming pull request data: the normalized shape the Intake agent reads
from and every downstream agent (Dependency, CI/CD, Release) inspects.

Owners: Ronn + Neel (#7).
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, model_validator


class FileChangeStatus(str, Enum):
    added = "added"
    modified = "modified"
    removed = "removed"
    renamed = "renamed"


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
