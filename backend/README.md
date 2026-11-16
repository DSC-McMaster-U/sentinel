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
| `app/core/` | Config, logging and shared errors | Toheeb + Parmeet (#3) (env config with Saqib + Ronn (#5)) |
| `tests/unit/`, `tests/integration/` | Tests | Everyone (unit tests with each issue); integration by Parmeet (#9) |

## Run tests

From the repository root, activate your virtual environment and run pytest
from `backend/`:

```bash
source .venv/bin/activate
cd backend
python -m pytest -q
```

The tests use `TestClient` and run without a server. If you're setting up from
scratch, run `uv venv` from the repository root and install dependencies in
the activated environment with `uv pip install fastapi pydantic uvicorn pytest httpx2`.
Issue #5 tracks the shared dependency setup.

## Try the API manually (optional)

From `backend/` with the same environment active:

```bash
python -m uvicorn app.main:app --reload
```

In the [interactive API docs](http://127.0.0.1:8000/docs), use **Try it out**
on either endpoint:

- `GET /health` returns `200` with `{"status":"ok"}`.
- For `POST /reviews`, paste the
  [sample PR JSON](../docs/architecture/CONTRACTS.md#pullrequestinput).
  Expect `200` with one mock dependency finding for `package.json`.

**Or use `curl`.** Leave the server running and open a second terminal.
Save the sample PR JSON linked above as `sample_pr.json` in that terminal's
current directory, then run:

```bash
curl -i http://127.0.0.1:8000/health
curl -i -X POST http://127.0.0.1:8000/reviews \
  -H 'Content-Type: application/json' \
  --data-binary @sample_pr.json
```

## Imports

Run Python commands from inside `backend/` so the `app` package is importable:

```python
from app.schemas import ...
```
> **TODO (Sprint 1, Saqib + Megh, #5: "Configure Local Development Environment, Docker, and GitHub Actions CI"):** add dependency management (`requirements.txt` or `pyproject.toml`) and run instructions here.

