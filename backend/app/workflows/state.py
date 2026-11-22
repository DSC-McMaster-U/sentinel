"""Shared PR context, selected inputs, agent results, and final review report."""

import operator
from typing import Annotated, Literal, NotRequired, TypedDict

from app.schemas import AgentInput, AgentOutput, PullRequestInput
from app.schemas.review_report import ReviewReport

AgentName = Literal["dependency", "cicd", "release"]
AGENT_ORDER: tuple[AgentName, ...] = ("dependency", "cicd", "release")


class ReviewState(TypedDict):
    pull_request: PullRequestInput
    agent_inputs: NotRequired[dict[AgentName, AgentInput]]
    agent_outputs: NotRequired[Annotated[list[AgentOutput], operator.add]]
    report: NotRequired[ReviewReport | None]


class IntakeUpdate(TypedDict):
    agent_inputs: dict[AgentName, AgentInput]


class AgentUpdate(TypedDict):
    agent_outputs: list[AgentOutput]


class SynthesisUpdate(TypedDict):
    report: ReviewReport
