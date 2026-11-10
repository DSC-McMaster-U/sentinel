# backend/app/schemas/

Shared Pydantic models: the contracts between the API, the LangGraph workflow, the agents and the frontend. Examples include the pull request input, changed files, findings (severity, confidence, evidence) and the review report.

**Primary owners:** Megh + Behzad. Contracts are coordinated by **Megh + Sarthak**.

Many teams depend on these models. Tag both coordinators on any PR that changes an existing schema.

> **TODO (Sprint 1, Megh + Sarthak: "Finalize Shared API Schemas and Agent Communication Contracts" (due Nov 11)):** define the initial review request, finding and report schemas.
