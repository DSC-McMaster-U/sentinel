from typing import Literal

from pydantic import BaseModel, Field


class Evidence(BaseModel):
    """An observation tied to a location in the reviewed code."""

    file_path: str = Field(min_length=1)
    line_start: int = Field(ge=1)
    line_end: int | None = Field(default=None, ge=1)
    observation: str = Field(min_length=1)


class SecurityFinding(BaseModel):
    """A security claim with supporting evidence and explicit review needs."""

    agent: str
    title: str
    description: str
    severity: Literal["Severe", "High", "Medium", "Low"] = Field(
        description="Potential impact if the finding is true."
    )
    risks: str
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
