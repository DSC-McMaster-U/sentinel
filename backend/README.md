# backend/

The Sentinel backend: a Python FastAPI service that accepts pull request data, runs the LangGraph review workflow, and returns structured security findings.

| Path | What goes here | Primary owners |
| --- | --- | --- |
| `app/api/routes/` | FastAPI routers (HTTP layer only) | Toheeb + Parmeet (#3); demo wiring by Parmeet (#9) |
| `app/schemas/` | Shared Pydantic models and contracts | Ronn + Neel (#7) |
| `app/github/` | GitHub webhook and API integration | Not assigned in Sprint 1 (GitHub intake starts in Sprint 2) |
| `app/workflows/` | LangGraph state, routing and graphs | Neel + Alex (#1) |
| `app/agents/` | Security agents and checks | Neel + Alex (#1) (Sprint 1 placeholder nodes); check definitions by Jin + Behzad (#2) |
| `app/retrieval/` | Repository context ingestion and search | Yug + Nana (#4) |
| `app/services/` | Business logic between API and workflows | Toheeb + Parmeet (#3); API-to-workflow wiring by Parmeet (#9) |
| `app/core/` | Config, logging and shared errors | Toheeb + Parmeet (#3) (env config with Saqib + Megh (#5)) |
| `tests/unit/`, `tests/integration/` | Tests | Everyone (unit tests with each issue); integration by Parmeet (#9) |

## Imports

Run Python commands from inside `backend/` so the `app` package is importable:

```python
from app.schemas import ...
```

> **TODO (Sprint 1, Toheeb + Parmeet, #3: "Set Up FastAPI Backend and Initial MCP Tool Integration"):** create the FastAPI application entry point (e.g. `app/main.py`) with health and mock review endpoints.
>
> **TODO (Sprint 1, Saqib + Megh, #5: "Configure Local Development Environment, Docker, and GitHub Actions CI"):** add dependency management (`requirements.txt` or `pyproject.toml`) and run instructions here.
