# frontend/src/types/

TypeScript types for API requests and responses (reviews, findings, evidence).

These must mirror the Pydantic models in `backend/app/schemas/`. When a schema changes, update the matching type in the same PR or open a linked issue. Contracts are owned by Ronn + Neel (#7).

| File | Mirrors |
| --- | --- |
| `findings.ts` | `Evidence`, `SecurityFinding`, `AgentOutput`, `ReviewReport` |
| `review.ts` | **Proposed** review-decision types (no backend schema yet), see [findings-dashboard.md](../../../docs/architecture/findings-dashboard.md#decision-record-proposed) |
