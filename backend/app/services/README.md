# backend/app/services/

Application logic that sits between the API routes and the workflow, GitHub and persistence layers. For example, a review service might start a workflow run and assemble the report.

Keep services independent of FastAPI (no `Request` objects) so they are easy to unit test.

**Primary owners:** Megh + Behzad
