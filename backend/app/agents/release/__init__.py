"""Release and packaging checks (later sprint). Sprint 1 placeholder: Neel + Alex (#1); checks from Jin + Behzad (#2)."""

from app.agents.placeholder import build_placeholder_output
from app.schemas import AgentInput, AgentOutput

AGENT_NAME = "release"


def run(agent_input: AgentInput) -> AgentOutput:
    return build_placeholder_output(AGENT_NAME, "release/build config", agent_input)
