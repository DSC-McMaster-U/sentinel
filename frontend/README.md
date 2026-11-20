# frontend/

The Sentinel review dashboard: a Next.js, React, TypeScript and Tailwind CSS app where maintainers review findings, evidence and traces and then approve, dismiss or escalate them.

| Path | What goes here |
| --- | --- |
| `src/app/` | Next.js App Router routes, layouts and pages |
| `src/components/` | Reusable UI components (`findings/` holds finding-specific UI) |
| `src/lib/` | API client, formatting helpers and other non-UI utilities |
| `src/types/` | TypeScript types that mirror the backend Pydantic schemas |
| `public/` | Static assets (icons, images) served as-is |

**Primary owners:** Sarthak + Rohit (#6)

> **Sprint 1 (#6):** the findings dashboard design is in [docs/architecture/findings-dashboard.md](../docs/architecture/findings-dashboard.md). Types mirroring the #7 schemas are in `src/types/`. The expanded finding view and review action components are in `src/components/findings/`; the overview and findings list (Sarthak) are still to come.
>
> When the team starts building, initialize the Next.js project (`package.json`, `tsconfig.json`, Tailwind config) in this directory, keeping the default `@/*` → `./src/*` import alias the components use. `create-next-app` may report conflicts with these placeholder README files. If it does, scaffold in a temporary folder and move the files in.
