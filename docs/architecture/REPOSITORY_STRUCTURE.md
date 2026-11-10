# Repository Structure

Sentinel is a monorepo. This document describes the **current** layout. The tree in [PROJECT.md](../../PROJECT.md#project-structure) was the original proposal.

Owners have **primary responsibility** for a directory: they review changes and keep it coherent. Anyone may contribute anywhere. Tag the owners when you change their area.

| Directory | Purpose | Primary owners |
| --- | --- | --- |
| `backend/app/api/` | FastAPI routes (HTTP layer) | Toheeb + Parmeet (#3); demo wiring by Parmeet (#9) |
| `backend/app/schemas/` | Shared Pydantic models and agent contracts | Ronn + Neel (#7) |
| `backend/app/github/` | GitHub webhook and API integration | Not assigned in Sprint 1 |
| `backend/app/services/` | Application logic between API and workflows | Toheeb + Parmeet (#3); API-to-workflow wiring by Parmeet (#9) |
| `backend/app/core/` | Config, logging and shared errors | Toheeb + Parmeet (#3) |
| `backend/app/workflows/` | LangGraph state, routing and orchestration | Neel + Alex (#1) |
| `backend/app/agents/` | Dependency, CI/CD, release and synthesis agents | Neel + Alex (#1) (Sprint 1 placeholders); checks by Jin + Behzad (#2) |
| `backend/app/retrieval/` | Repository context ingestion and search | Yug + Nana (#4) |
| `backend/tests/` | Backend unit and integration tests | Everyone (integration: Parmeet (#9)) |
| `mcp-server/` | Sentinel MCP server: tools and adapters | Toheeb + Parmeet (#3) |
| `frontend/` | Next.js findings dashboard | Sarthak + Rohit (#6) |
| `evaluation/` | Labelled PR fixtures, expected findings and harness | Sarthak + Rohit (#6); check fixtures by Jin + Behzad (#2) |
| `infrastructure/` | Docker, Cloud Run and Terraform | Saqib + Megh (#5) |
| `.github/workflows/` | GitHub Actions CI | Saqib + Megh (#5) |
| `docs/security-checks/` | Security check specifications | Jin + Behzad (#2) |
| `docs/` (other) | Architecture, ADRs, onboarding, sprints | Project lead and everyone |
| `scripts/` | Developer helper scripts | Shared |

## Coordination Roles

- **Shared schemas:** Ronn + Neel (#7). Any change to `backend/app/schemas/` affects the workflow, the agents and the frontend types.
- **End-to-end integration:** Parmeet (#9), who owns the Sprint 1 demo path: sample PR → FastAPI → LangGraph intake → mock agents → risk synthesis → structured findings.

## How the Pieces Connect

```text
frontend  --HTTP-->  backend/app/api  -->  services  -->  workflows (LangGraph)
                                                            |
                                    +-----------------------+--------------------+
                                    v                       v                    v
                              agents/*              retrieval/*          mcp-server tools
                                    |                                            |
                                    +--------> schemas (shared contracts) <------+
```

Each README in these directories explains what belongs there and lists its Sprint 1 TODOs.
