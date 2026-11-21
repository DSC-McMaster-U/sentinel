# backend/app/workflows/

LangGraph orchestration: the shared review state, deterministic intake and file classification, conditional routing to agent nodes, and the risk synthesis step.

Routing must be **deterministic first**. For example, a changed dependency manifest triggers the Dependency agent, without asking an LLM to decide.

**Primary owners:** Neel + Alex (#1)

## Orchestration and node ownership

`graph.py` implements intake, deterministic routing, and graph assembly.
Production Dependency, CI/CD, Release, and Risk Synthesis implementations are
provided separately by their owners. This module does not supply placeholder
agents or a synthesis implementation, and does not change `POST /reviews`.

```
START → intake → selected agents in parallel → synthesis → END
             └─ no matches ──────────────────↗
```

Intake receives a normalized `PullRequestInput` and preserves it in shared state.
It builds an `AgentInput` for each selected agent using PR number, repository URL,
head SHA, and only relevant `ChangedFile` objects, including patches and rename
metadata. Each branch gets independent copies of its selected files.
Routing uses the keys of `agent_inputs` in `AGENT_ORDER`; an empty mapping routes
directly to synthesis.

| File rule | Agent |
| --- | --- |
| `package.json`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml` at any depth | Dependency |
| Files under repository-root `.github/workflows/` | CI/CD |
| `Dockerfile`, `.dockerignore` at any depth | Release |

Rules are case-sensitive and expect repository-relative Git paths. Renames match
both current and previous paths. Deleted files still trigger review; entries with
status `unchanged` do not. A file can match multiple agents. These are Sprint 1
selection rules, not a complete inventory of security-sensitive files.

## Plug in the owned nodes

`build_review_graph` requires all three synchronous agent callables and a
synchronous synthesis callable:

- Each agent takes `AgentInput` and returns `AgentOutput` with the corresponding
  `agent_name`: `dependency`, `cicd`, or `release`.
- Synthesis takes `ReviewState` and returns `SynthesisUpdate`, a dictionary shaped
  as `{"report": ReviewReport}`. Its owner should call `combine_findings()` from
  `app.schemas.review_report` using `state["agent_outputs"]` and PR metadata.
- Agents return outputs only; the graph adapter appends each to `agent_outputs`
  through an additive reducer. Synthesis runs once after all selected agents
  finish. It receives an empty output list if no agents are selected.
- Output collection order is not a completion-order contract. If stable report
  ordering is needed, the synthesis owner can order outputs using `AGENT_ORDER`.
- Return `failure` or `partial` through the shared `AgentOutput` contract when
  analysis is incomplete. Unhandled exceptions propagate and stop the invocation.

Once the node owners provide their functions, integration can wire them this way
(the four node variables below are supplied by those owners):

```python
from app.workflows.graph import build_review_graph

graph = build_review_graph(
    agent_nodes={
        "dependency": dependency_node,
        "cicd": cicd_node,
        "release": release_node,
    },
    synthesis_node=synthesis_node,
)
result = graph.invoke({"pull_request": pull_request})  # PullRequestInput
report = result["report"]  # ReviewReport
```

Pass only the new PR on each invocation. The compiled graph has no checkpointer;
reusing it does not retain previous reviews. API-to-workflow wiring belongs to #9.

## Local verification

The orchestration was verified with LangGraph `1.2.22`. Install it in the project
virtual environment if needed with `python -m pip install 'langgraph==1.2.22'`.
From `backend/`, with that environment active:

```bash
python -m pytest -q tests/unit/test_routing.py
python -m pytest -q tests/unit
```

Tests supply local doubles without adding production nodes. They cover routing,
file filtering and isolation, all eight combinations of selected agents,
concurrent execution, exactly one synthesis, finding transport through shared
schemas, and fresh state when reusing a compiled graph. Concurrency is verified
using a barrier rather than elapsed-time assertions.
