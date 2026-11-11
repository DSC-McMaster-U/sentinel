# Shared Contracts (#7)

The schemas behind `backend/app/schemas/`. Every example below was generated
directly from the Pydantic models and validated against them, so these
payloads are guaranteed to pass validation as written.

**Owners:** Ronn + Neel. Tag both on any PR that changes a schema here.

## Flow

```
PullRequestInput --> (per agent) AgentInput --> AgentOutput --> combine_findings() --> ReviewReport
```

A `PullRequestInput` is the whole normalized PR. The workflow slices it into
a smaller `AgentInput` per agent (only the files that agent cares about).
Each agent returns an `AgentOutput` containing zero or more `SecurityFinding`
objects. `combine_findings()` merges every agent's output into one
deduplicated `ReviewReport`.

## `PullRequestInput`

Defined in `backend/app/schemas/pull_request.py`. The normalized pull
request the review workflow operates on.

```json
{
  "repository": {
    "owner": "DSC-McMaster-U",
    "name": "sentinel",
    "full_name": "DSC-McMaster-U/sentinel",
    "url": "https://github.com/DSC-McMaster-U/sentinel",
    "default_branch": "main"
  },
  "number": 42,
  "title": "Bump lodash to 4.17.21",
  "description": "Routine dependency bump",
  "author": "ronnphil",
  "base_branch": "main",
  "head_branch": "deps/bump-lodash",
  "base_sha": "abc123",
  "head_sha": "def456",
  "url": "https://github.com/DSC-McMaster-U/sentinel/pull/42",
  "created_at": "2026-11-10T12:00:00Z",
  "updated_at": "2026-11-10T12:05:00Z",
  "files_changed": [
    {
      "path": "package.json",
      "status": "modified",
      "additions": 1,
      "deletions": 1,
      "patch": "-  \"lodash\": \"4.17.20\"\n+  \"lodash\": \"4.17.21\"",
      "previous_path": null
    }
  ]
}
```

## `AgentInput`

Defined in `backend/app/schemas/agent.py`. The slice of a PR that one agent
sees: just the files relevant to that agent's check.

> Note: `AgentInput.changed_files` uses `AgentChangedFile` (`file_path`,
> `patch`), a deliberately smaller shape than `PullRequestInput`'s
> `ChangedFile` (`path`, `status`, `additions`, `deletions`, `patch`,
> `previous_path`). The workflow is responsible for narrowing the full PR's
> file list down to this shape per agent.

```json
{
  "pr_number": 42,
  "commit_sha": "def456",
  "repo_url": "https://github.com/DSC-McMaster-U/sentinel",
  "changed_files": [
    {
      "file_path": "package.json",
      "patch": "-  \"lodash\": \"4.17.20\"\n+  \"lodash\": \"4.17.21\""
    }
  ]
}
```

## `AgentOutput` (containing a `SecurityFinding`)

Defined in `backend/app/schemas/agent.py` and `finding.py`. `severity` is
one of `critical`, `high`, `medium`, `low` (case-insensitive on input,
normalized to lowercase). `status` is one of `success`, `failure`,
`partial`; `error_message` must be set whenever `status` isn't `success`,
and every finding's `agent` must match `agent_name`.

```json
{
  "agent_name": "dependency",
  "findings": [
    {
      "agent": "dependency",
      "title": "Dependency version bump has no changelog review",
      "description": "package.json bumps lodash from 4.17.20 to 4.17.21 with no changelog or release notes link in the PR.",
      "severity": "low",
      "recommendation": "Link the upstream release notes in the PR description before merging.",
      "evidence": [
        {
          "file_path": "package.json",
          "line_start": 12,
          "line_end": 12,
          "observation": "lodash version changed with no accompanying justification."
        }
      ],
      "confidence": 0.6,
      "uncertainty": [
        "Did not check whether CI already pins a lockfile hash for this package."
      ],
      "requires_human_review": false
    }
  ],
  "status": "success",
  "error_message": null
}
```

## `ReviewReport` (combined findings)

Defined in `backend/app/schemas/review_report.py`. Built by
`combine_findings(outputs, pr_number=..., repo_url=..., commit_sha=...)`,
which takes the `AgentOutput` from every agent that ran, merges their
findings, drops exact duplicates (same agent, title, and evidence
locations), sorts by severity, and flags `requires_human_review` whenever
any individual finding needs it, or any agent failed or only partially
completed.

```json
{
  "pr_number": 42,
  "repo_url": "https://github.com/DSC-McMaster-U/sentinel",
  "commit_sha": "def456",
  "generated_at": "2026-11-11T09:00:00Z",
  "findings": [
    {
      "agent": "dependency",
      "title": "Dependency version bump has no changelog review",
      "description": "package.json bumps lodash from 4.17.20 to 4.17.21 with no changelog or release notes link in the PR.",
      "severity": "low",
      "recommendation": "Link the upstream release notes in the PR description before merging.",
      "evidence": [
        {
          "file_path": "package.json",
          "line_start": 12,
          "line_end": 12,
          "observation": "lodash version changed with no accompanying justification."
        }
      ],
      "confidence": 0.6,
      "uncertainty": [
        "Did not check whether CI already pins a lockfile hash for this package."
      ],
      "requires_human_review": false
    }
  ],
  "agents_run": ["dependency"],
  "agents_failed": [],
  "agents_partial": [],
  "requires_human_review": false
}
```

## Dependency note

`review_report.py` imports `SecurityFinding` from `finding.py` and
`AgentOutput` from `agent.py` (#10, Neel). Until #10 merges, this file and
its tests only run locally against that branch's copies of those files.
