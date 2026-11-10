# Repository Structure

Sentinel is a monorepo. This document describes the **current** layout. The tree in [PROJECT.md](../../PROJECT.md#project-structure) was the original proposal.

Owners have **primary responsibility** for a directory: they review changes and keep it coherent. Anyone may contribute anywhere. Tag the owners when you change their area.

| Directory | Purpose | Primary owners |
| --- | --- | --- |
| `backend/app/api/` | FastAPI routes (HTTP layer) | Megh + Behzad |
| `backend/app/schemas/` | Shared Pydantic models and agent contracts | Megh + Behzad (contracts: Megh + Sarthak) |
| `backend/app/github/` | GitHub webhook and API integration | Megh + Behzad |
| `backend/app/services/` | Application logic between API and workflows | Megh + Behzad |
| `backend/app/core/` | Config, logging and shared errors | Megh + Behzad |
| `backend/app/workflows/` | LangGraph state, routing and orchestration | Sarthak + Alex |
| `backend/app/agents/` | Dependency, CI/CD, release and synthesis agents | Rohit + Ronn |
| `backend/app/retrieval/` | Repository context ingestion and search | Yug + Toheeb |
| `backend/tests/` | Backend unit and integration tests | Everyone (integration: Sarthak + Behzad) |
| `mcp-server/` | Sentinel MCP server: tools and adapters | Megh + Behzad |
| `frontend/` | Next.js findings dashboard | Saqib + Nana |
| `evaluation/` | Labelled PR fixtures, expected findings and harness | Saqib + Nana |
| `infrastructure/` | Docker, Cloud Run and Terraform | Neel + Parmeet |
| `.github/workflows/` | GitHub Actions CI | Neel + Parmeet |
| `docs/security-checks/` | Security check specifications | Rohit + Ronn |
| `docs/` (other) | Architecture, ADRs, onboarding, sprints | Project lead and everyone |
| `scripts/` | Developer helper scripts | Shared |

## Coordination Roles

- **Shared schemas:** Megh + Sarthak. Any change to `backend/app/schemas/` affects the workflow, the agents and the frontend types.
- **End-to-end integration:** Sarthak + Behzad. They own the Sprint 1 demo path: sample PR → FastAPI → LangGraph intake → mock agents → risk synthesis → structured findings.

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
