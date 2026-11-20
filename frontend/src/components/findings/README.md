# frontend/src/components/findings/

UI components for displaying security findings: finding cards, severity and confidence badges, evidence panels, and confirm/dismiss/investigate controls.

Components should receive data through props typed with `src/types/`. Do not fetch data directly here.

| Component | Owner (#6) | Purpose |
| --- | --- | --- |
| `FindingDetails` | Rohit | Expanded finding view: description, evidence, uncertainty, recommendation, review actions, history |
| `EvidenceList` | Rohit | Evidence locations linked to the reviewed commit, with observations |
| `UncertaintyList` | Rohit | What the agent could not verify, with an explicit empty state |
| `ReviewActions` | Rohit | Confirm, dismiss and request investigation, with validation |
| Findings list, card header, severity/confidence badges, report states | Sarthak | See the overview sections of the design doc |

The design is in [docs/architecture/findings-dashboard.md](../../../../docs/architecture/findings-dashboard.md). These are a Sprint 1 prototype: typechecked and rendered against the evaluation fixtures, but not yet wired into a Next.js page. They use Tailwind classes and the `@/*` → `src/*` import alias.
