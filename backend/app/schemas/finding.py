import json
from hashlib import sha256
from typing import Literal

from pydantic import BaseModel, Field, computed_field, field_validator, model_validator


class Evidence(BaseModel):
    """An observation tied to a location in the reviewed code."""

    file_path: str = Field(min_length=1)
    line_start: int = Field(ge=1)
    line_end: int | None = Field(default=None, ge=1)
    observation: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_line_range(self) -> "Evidence":
        if self.line_end is not None and self.line_end < self.line_start:
            raise ValueError("line_end must be greater than or equal to line_start")
        return self


class FindingSubject(BaseModel):
    """The logical object a check flags, independent of evidence line numbers."""

    file_path: str = Field(min_length=1, pattern=r"\S")
    key: str = Field(
        min_length=1,
        pattern=r"\S",
        description="Stable check-specific key, e.g. dependencies/lodash or jobs/build.",
    )


class SecurityFinding(BaseModel):
    """A security claim with supporting evidence and explicit review needs."""

    agent: str = Field(min_length=1)
    check_id: str = Field(
        min_length=1, pattern=r"\S", description="Fixed identifier of the check that ran."
    )
    subject: FindingSubject
    title: str = Field(min_length=1)
    description: str = Field(
        min_length=1, description="The security issue and how it occurs in the code."
    )
    severity: Literal["critical", "high", "medium", "low"] = Field(
        description="Potential impact if the finding is true."
    )
    recommendation: str = Field(
        min_length=1,
        description="Suggested action to fix or mitigate the security issue.",
    )
    evidence: list[Evidence] = Field(
        min_length=1, description="At least one observation supporting the finding."
    )
    confidence: float = Field(
        ge=0.0, le=1.0, description="Confidence that the evidence supports the claim."
    )
    uncertainty: list[str] = Field(
        description="Missing context or assumptions; use an empty list when none are known."
    )
    requires_human_review: bool = Field(
        description="Explicit review decision, independent of any confidence threshold."
    )

    @computed_field
    @property
    def id(self) -> str:
        """Stable within a repository and PR; changing the subject starts a new identity."""
        identity = json.dumps(
            [self.agent, self.check_id, self.subject.file_path, self.subject.key],
            separators=(",", ":"),
        )
        return f"fnd_v1_{sha256(identity.encode('utf-8')).hexdigest()}"

    @field_validator("severity", mode="before")
    @classmethod
    def normalize_severity(cls, value):
        if isinstance(value, str):
            return value.lower()
        return value
