# frontend/src/components/findings/

UI components for displaying security findings: finding cards, severity and confidence badges, evidence panels, and confirm/dismiss/investigate controls.

Components should receive data through props typed with `src/types/`. Do not fetch data directly here.

The design these implement, including the wireframe and review-action rules, is in [docs/architecture/findings-dashboard.md](../../../../docs/architecture/findings-dashboard.md). `FindingsList` is the entry point for a review page; it takes a `ReviewReport`, the current status of each finding, and an `onDecision` callback.

These are a Sprint 1 prototype: typechecked and rendered against the evaluation fixtures, but not yet wired into a Next.js page. They use Tailwind classes and the `@/*` → `src/*` import alias.
