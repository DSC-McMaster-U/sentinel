# backend/tests/

- `unit/`: fast, isolated tests with no network or external services. Mirror the `app/` layout (e.g. `unit/workflows/test_routing.py`).
- `integration/`: tests that span components, e.g. sample PR → API → workflow → findings.

Run `pytest` from inside `backend/` once dependencies are set up. When you add a test subfolder, include an empty `__init__.py` so test files with the same name in different folders don't clash.

> **TODO (Sprint 1, Parmeet, #9: "Integrate Sprint 1 Components into an End-to-End Sentinel Demo"):** passing end-to-end integration test for the demo path.
