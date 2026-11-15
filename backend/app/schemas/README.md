# backend/app/schemas/

Shared Pydantic models: the contracts between the API, the LangGraph workflow, the agents and the frontend. Examples include the pull request input, changed files, findings (severity, confidence, evidence) and the review report.

**Primary owners:** **Ronn + Neel (#7)**, who also coordinate the contracts.

Many teams depend on these models. Tag both owners on any PR that changes an existing schema.

## Finding text fields

`SecurityFinding` describes the issue and the recommended remediation:

- `description` explains the security issue and how it occurs in the code. Example: "A workflow interpolates the PR title into a shell command."
- `recommendation` suggests an action to fix or mitigate the issue. Example: "Pass the PR title through an environment variable and quote it in the shell command."

Both fields are required, nonempty strings. `recommendation` replaces the former `risks` field.

`severity` accepts `critical`, `high`, `medium`, and `low`, case-insensitively: `Critical`, `high`, and `High` all work. Values are serialized in lowercase. `Severe` is no longer accepted.

Working example payloads are in [test_schemas.py](../../tests/unit/test_schemas.py).

## Pull request file statuses

`pull_request.py` defines `PullRequestInput`, `ChangedFile`, and
`FileChangeStatus`. Accepted file statuses are `added`, `modified`, `removed`,
`renamed`, `copied`, `changed`, and `unchanged`. They are serialized as the
same lowercase strings; unknown statuses are rejected.

`ChangedFile` accepts zero additions and deletions. Its `patch` can be
omitted or explicitly `null`. A `renamed` file requires a nonempty
`previous_path`; the other statuses do not require it.

See [Shared Contracts](../../../docs/architecture/CONTRACTS.md#changedfile)
for an example and [test_pull_request_schema.py](../../tests/unit/test_pull_request_schema.py)
for status validation, mixed-status lists, and JSON round-trip coverage.

> **Remaining work for #7 (Ronn + Neel):** define the combined review report and finding aggregation rules, and document component communication and JSON examples in `docs/architecture/CONTRACTS.md`.
