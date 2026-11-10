# backend/app/schemas/

Shared Pydantic models: the contracts between the API, the LangGraph workflow, the agents and the frontend. Examples include the pull request input, changed files, findings (severity, confidence, evidence) and the review report.

**Primary owners:** **Ronn + Neel (#7)**, who also coordinate the contracts.

Many teams depend on these models. Tag both owners on any PR that changes an existing schema.

> **TODO (Sprint 1, Ronn + Neel, #7: "Finalize Shared API Schemas and Agent Communication Contracts" (due Nov 11)):** define the initial review request, finding and report schemas.
