"""Deterministic intake and graph wiring for externally supplied review nodes."""

from collections.abc import Callable, Mapping
from pathlib import PurePosixPath
from typing import Literal, Protocol

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.schemas import AgentInput, AgentOutput, ChangedFile, FileChangeStatus
from app.workflows.state import (
    AGENT_ORDER,
    AgentName,
    AgentUpdate,
    IntakeUpdate,
    ReviewState,
    SynthesisUpdate,
)

AgentNode = Callable[[AgentInput], AgentOutput]


class AgentStateNode(Protocol):
    """Graph adapter signature, preserving LangGraph's named state parameter."""

    def __call__(self, state: ReviewState) -> AgentUpdate: ...


class SynthesisNode(Protocol):
    """Signature expected from the externally supplied synthesis node."""

    def __call__(self, state: ReviewState) -> SynthesisUpdate: ...


Route = Literal["dependency", "cicd", "release", "synthesis"]

_DEPENDENCY_FILES = {"package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml"}
_RELEASE_FILES = {"Dockerfile", ".dockerignore"}


def _classify_path(path: str) -> set[AgentName]:
    """Match repository-relative Git paths, including nested manifests."""
    selected: set[AgentName] = set()
    filename = PurePosixPath(path).name
    if filename in _DEPENDENCY_FILES:
        selected.add("dependency")
    if path.startswith(".github/workflows/") and len(path.split("/")) > 2:
        selected.add("cicd")
    if filename in _RELEASE_FILES:
        selected.add("release")
    return selected


def _classify_file(file: ChangedFile) -> set[AgentName]:
    if file.status == FileChangeStatus.unchanged:
        return set()
    selected = _classify_path(file.path)
    # Moving a sensitive file out of its old location still needs review.
    if file.status == FileChangeStatus.renamed and file.previous_path:
        selected.update(_classify_path(file.previous_path))
    return selected


def classify_files(state: ReviewState) -> IntakeUpdate:
    """Intake: select agents and build their independent, filtered PR inputs."""
    pull_request = state["pull_request"]
    files_by_agent: dict[AgentName, list[ChangedFile]] = {
        name: [] for name in AGENT_ORDER
    }
    for file in pull_request.files_changed:
        for name in _classify_file(file):
            # An overlapping match must not expose another branch's mutable data.
            files_by_agent[name].append(file.model_copy(deep=True))

    inputs: dict[AgentName, AgentInput] = {
        name: AgentInput(
            pr_number=pull_request.pr_number,
            commit_sha=pull_request.head_sha,
            repo_url=str(pull_request.repository.url),
            changed_files=files,
        )
        for name, files in files_by_agent.items()
        if files
    }
    return {"agent_inputs": inputs}


def choose_agents(state: ReviewState) -> list[Route]:
    """Route to agents with prepared inputs, in stable order."""
    if "agent_inputs" not in state:
        raise ValueError("Intake must prepare agent inputs before routing")
    destinations: list[Route] = [
        name for name in AGENT_ORDER if name in state["agent_inputs"]
    ]
    return destinations or ["synthesis"]


def _adapt_agent(name: AgentName, node: AgentNode) -> AgentStateNode:
    """Bridge the shared AgentInput/AgentOutput contract to graph state updates."""
    def execute(state: ReviewState) -> AgentUpdate:
        if "agent_inputs" not in state:
            raise ValueError("Intake must prepare agent inputs before execution")
        output = node(state["agent_inputs"][name])
        if output.agent_name != name:
            raise ValueError(f"Expected output from {name}, got {output.agent_name}")
        return {"agent_outputs": [output]}

    return execute


def build_review_graph(
    *, agent_nodes: Mapping[AgentName, AgentNode], synthesis_node: SynthesisNode
) -> CompiledStateGraph:
    """Assemble a fresh graph; callers supply all agent and synthesis behavior.

    Agent callables take AgentInput and return AgentOutput. The synthesis callable
    takes ReviewState and returns {"report": ReviewReport}; its owner should use
    combine_findings(). No production agent or synthesis implementation lives here.
    Invoke with {"pull_request": PullRequestInput}; other state is populated by intake
    and LangGraph's output reducer. Raised node exceptions propagate to the caller.
    """
    if set(agent_nodes) != set(AGENT_ORDER):
        raise ValueError("Provide exactly the dependency, cicd, and release agent nodes")

    builder = StateGraph(ReviewState)
    builder.add_node("intake", classify_files)
    for name in AGENT_ORDER:
        builder.add_node(name, _adapt_agent(name, agent_nodes[name]))
        builder.add_edge(name, "synthesis")
    builder.add_node("synthesis", synthesis_node, defer=True)
    builder.add_edge(START, "intake")
    builder.add_conditional_edges(
        "intake", choose_agents, [*AGENT_ORDER, "synthesis"]
    )
    builder.add_edge("synthesis", END)
    return builder.compile()
