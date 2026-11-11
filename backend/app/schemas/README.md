# backend/app/schemas/

Shared Pydantic models: the contracts between the API, the LangGraph workflow, the agents and the frontend. Examples include the pull request input, changed files, findings (severity, confidence, evidence) and the review report.

**Primary owners:** **Ronn + Neel (#7)**, who also coordinate the contracts.

Many teams depend on these models. Tag both owners on any PR that changes an existing schema.

## Finding text fields

`SecurityFinding` separates the issue from its potential consequences:

- `description` explains the security issue and how it occurs in the code. Example: "A workflow interpolates the PR title into a shell command."
- `risks` explains the potential security consequences if the finding is true, including affected assets or capabilities. Example: "An attacker could execute commands in the CI runner."

Both fields are required, nonempty strings. `severity` expresses the impact level, while `risks` explains that impact in words. Working example payloads are in `backend/tests/unit/test_schemas.py`.

> **TODO (Sprint 1, Ronn + Neel, #7: "Finalize Shared API Schemas and Agent Communication Contracts" (due Nov 11)):** define the initial review request, finding and report schemas.
