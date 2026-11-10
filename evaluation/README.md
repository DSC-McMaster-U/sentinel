# evaluation/

Datasets and scripts that measure how well Sentinel detects real risks without flagging safe changes.

| Path | What goes here |
| --- | --- |
| `fixtures/safe/` | Sample pull requests that should **not** be flagged |
| `fixtures/risky/` | Sample pull requests containing known issues |
| `expected-findings/` | Labelled expected output for each fixture (same base name) |
| `scripts/` | Evaluation harness that compares Sentinel output with expected findings |

**Primary owners:** Saqib + Nana. Rohit + Ronn contribute safe and unsafe fixtures for each documented security check.

> **TODO (Sprint 1, Saqib + Nana: "Design Security Findings Dashboard and Initial Evaluation Framework"):** at least six labelled PR fixtures and a basic evaluation harness.

**Never use real secrets in fixtures.** Use obviously fake values such as `ghp_FAKE_TOKEN_FOR_TESTING`.
