# evaluation/

Datasets and scripts that measure how well Sentinel detects real risks without flagging safe changes.

| Path | What goes here |
| --- | --- |
| `fixtures/safe/` | Sample pull requests that should **not** be flagged |
| `fixtures/risky/` | Sample pull requests containing known issues |
| `expected-findings/` | Labelled expected output for each fixture (same base name) |
| `scripts/` | Evaluation harness that compares Sentinel output with expected findings |

**Primary owners:** Sarthak + Rohit (#6). Jin + Behzad (#2) contribute safe and unsafe fixtures for each documented security check.

**Never use real secrets in fixtures.** Use obviously fake values such as `ghp_FAKE_TOKEN_FOR_TESTING`.

| Section | Owner (#6) |
| --- | --- |
| [Dependency fixtures](#dependency-fixtures) | Sarthak |
| [CI/CD fixtures](#cicd-fixtures) | Rohit |
| [Expected-findings format](#expected-findings-format) | Rohit |
| [Matching rules](#matching-rules) | Sarthak |
| [Metrics](#metrics): precision and recall | Sarthak |
| [Metrics](#metrics): false-positive rate and the other reported metrics | Rohit |
| [Running the harness](#running-the-harness) | Rohit |

## Dataset

### Dependency fixtures

> **TODO (Sarthak):** 3 dependency PR examples (1 safe + 2 risky) with
> expected findings, and their explanations.

### CI/CD fixtures

Three GitHub Actions workflow changes: 2 safe and 1 risky. The safe cases
are close to risky patterns: both touch workflows that hold secrets or
tokens. A check that flags workflow changes by file name alone will flag
them.

| Fixture | Label | Why | Expected findings |
| --- | --- | --- | --- |
| `safe/cicd-pinned-actions-read-only` | safe | New test workflow on `pull_request`. Its token is limited to `contents: read`. The first-party actions are pinned to full commit SHAs, and checkout doesn't persist credentials. | none |
| `safe/cicd-third-party-action-sha-bump` | safe | A third-party deploy action that receives the `DEPLOY_TOKEN` secret is bumped from v2.3.1 to v2.4.0 and stays pinned to a full commit SHA, with release notes linked. Bumping a pinned action is the safe way to update it. | none |
| `risky/cicd-pull-request-target-head-checkout` | risky | A `pull_request_target` workflow (which runs with the base repository's secrets, even for fork PRs) checks out the PR head and runs `npm ci` and a build script from it, with `PREVIEW_DEPLOY_KEY` in the environment and `permissions: write-all`. This is the classic "pwn request". | **critical**: untrusted PR code runs in a privileged job (evidence: trigger line 4, checkout ref line 15, run step lines 16-18). **medium**: `write-all` token permissions (line 7). |

Fixtures are synthetic. The repository `sentinel-fixtures/demo-app` and the
`example-org` action don't exist.

### Expected-findings format

A fixture is a `PullRequestInput` JSON file
([CONTRACTS.md](../docs/architecture/CONTRACTS.md#pullrequestinput)) with
unified diffs in each file's `patch`. It can be POSTed to `/reviews` as-is.

`expected-findings/<fixture-name>.json` holds the label and the findings
Sentinel should report, as `SecurityFinding` objects:

```json
{
  "fixture": "risky/cicd-pull-request-target-head-checkout.json",
  "label": "risky",
  "summary": "One sentence on why this PR is safe or risky.",
  "findings": [
    {
      "agent": "cicd",
      "title": "Workflow grants write-all token permissions",
      "description": "...",
      "severity": "medium",
      "recommendation": "...",
      "evidence": [
        {
          "file_path": ".github/workflows/preview.yml",
          "line_start": 7,
          "line_end": null,
          "observation": "Top-level permissions set to write-all."
        }
      ],
      "confidence": 0.9,
      "uncertainty": ["Did not check repository-level default token permissions."],
      "requires_human_review": false
    }
  ]
}
```

Evidence line numbers are on the **new** side of the diff (the head
commit), which is where reviewers and GitHub links point.

The harness checks these rules on load. They are also checked by
`--check-fixtures` and in CI:

- Every fixture is a valid `PullRequestInput` with a matching expected file,
  and every expected file has a fixture.
- Fixture base names are unique across `safe/` and `risky/`.
- `label` matches the fixture's directory. Safe fixtures expect `[]`, and
  risky fixtures expect at least one finding.
- Every expected finding is a valid `SecurityFinding`, and its evidence
  points at a file in the fixture and at a line visible in that file's diff.

All problems are reported in one pass, not one at a time.

To add a fixture:

1. Add `fixtures/<safe|risky>/<name>.json`. Prefix the name with the area
   (`dep-`, `cicd-`, `release-`) or the check ID (`DEP-001-...`).
2. Add `expected-findings/<name>.json` in the format above.
3. Run `python evaluation/scripts/run_evaluation.py --check-fixtures`.

## Matching rules

> **TODO (Sarthak):** how an actual finding is paired with an expected one.
> `match_findings()` in `scripts/run_evaluation.py` is currently a
> placeholder that only counts an exact match (same agent, same first
> evidence file and start line). Its signature and `MatchResult` return type
> are what the metrics and output rely on.

## Metrics

Matching turns each case into matched pairs, missed expected findings and
unexpected actual findings. Across all cases these are the **true
positives (TP)**, **false negatives (FN)** and **false positives (FP)**.

> **TODO (Sarthak):** precision and recall definitions.

| Metric | Definition | Question it answers |
| --- | --- | --- |
| **False-positive rate** | safe PRs with ≥ 1 finding / safe PRs | How often does Sentinel bother reviewers on a clean PR? |
| **False-negative rate** | risky PRs where no expected finding was matched / risky PRs | How often does a risky PR go completely unflagged? |
| **F1** | 2 · precision · recall / (precision + recall) | One number balancing both, for tracking over time |
| **Severity agreement** | matched pairs with equal severity / TP | Are real issues rated at the right severity? |
| **Human-review agreement** | matched pairs with equal `requires_human_review` / TP | Does the agent ask for review when it should? |
| **Mean confidence (TP vs FP)** | average `confidence` of matched vs unexpected findings | Is confidence informative? TP confidence should be clearly higher than FP confidence. |

### False-positive rate

The false-positive rate is measured **per pull request**:

```text
false-positive rate = (safe PRs where Sentinel reported at least one finding) / (safe PRs)
```

- **Why per PR, not per finding:** a per-finding rate needs a count of true
  negatives (findings that correctly weren't reported), and that set can't
  be counted. Per PR, the rate matches what a reviewer experiences: a clean
  PR that gets flagged.
- **Multiple findings on one safe PR count once.** The extra findings still
  show up in the FP count and lower precision.
- **Only safe fixtures count.** An unexpected finding on a risky PR is a
  false positive for precision, but it doesn't change this rate.
- **Thresholds apply.** With `--min-severity`, findings below the threshold
  are ignored first. That shows the rate at a given reporting threshold, for
  example "how often is a clean PR flagged at medium or above?"

### Undefined values

A ratio with a zero denominator is reported as `n/a`, never as 0 or 1. For
example, precision is undefined when Sentinel reports nothing, and the
false-negative rate is undefined when the run has no risky cases.

With this few fixtures, one case moves a rate by a large step. With 2 safe
cases, one flagged PR moves the false-positive rate by 50 points. Treat the
numbers as a regression signal until the dataset grows.

## Running the harness

From the repository root, with the backend dependencies installed (see
[GETTING_STARTED.md](../docs/onboarding/GETTING_STARTED.md)):

```bash
# Validate every fixture and expected-findings file, then exit
python evaluation/scripts/run_evaluation.py --check-fixtures

# Run the current backend review in-process against every fixture
python evaluation/scripts/run_evaluation.py

# Score saved outputs instead (one <fixture-name>.json per fixture)
python evaluation/scripts/run_evaluation.py --actual-dir path/to/outputs

# Only count findings at medium severity or above
python evaluation/scripts/run_evaluation.py --min-severity medium

# Also write full per-case results as JSON
python evaluation/scripts/run_evaluation.py --json-out evaluation-results.json
```

| Option | Default | Purpose |
| --- | --- | --- |
| `--runner module:function` | `app.services.review_service:build_mock_review_report` | Function that takes a `PullRequestInput` and returns a `ReviewReport` or a list of `SecurityFinding`. When #9 connects the API to the LangGraph workflow, point this at the new entry point. |
| `--actual-dir DIR` | none | Read actual output from `DIR/<fixture-name>.json` instead of running the backend. Each file can be a `ReviewReport`, any object with a `findings` list, or a bare list of findings. Use this for LLM runs: save each run, then score it. |
| `--evaluation-dir DIR` | `evaluation/` | Use a different dataset with the same layout. |
| `--min-severity LEVEL` | `low` | Ignore expected and actual findings below `LEVEL`. |
| `--json-out FILE` | none | Write metrics and per-case matched, missed and unexpected findings as JSON. |
| `--check-fixtures` | off | Only validate the dataset. |

### Output

The text report has three parts:

- a table with one row per case: label, expected and actual counts, TP, FP,
  FN, and `PASS`, `FAIL` or `ERROR`;
- details for every failing case, showing the missed and unexpected
  findings with their locations;
- the metrics.

```text
case                                     label  exp  act  TP  FP  FN  result
-----------------------------------------------------------------------------
cicd-pinned-actions-read-only            safe     0    0   0   0   0  PASS
cicd-third-party-action-sha-bump         safe     0    0   0   0   0  PASS
cicd-pull-request-target-head-checkout   risky    2    0   0   0   2  FAIL

Details:

cicd-pull-request-target-head-checkout (risky)
  missed:     [critical] cicd: Untrusted pull request code runs in a privileged pull_request_target job (...)
  missed:     [medium] cicd: Workflow grants write-all token permissions (.github/workflows/preview.yml:7)

Metrics:
  cases                   3 (2 safe, 1 risky), 2 passed, 0 errors
  findings                TP=0 FP=0 FN=2
  precision               n/a
  recall                  0.00
  ...
  false-positive rate     0.00  (safe PRs with any finding)
  false-negative rate     1.00  (risky PRs with no match)
```

That is the current baseline against the mock review from #3, which only
reacts to `package.json`. Replaying the expected findings
(`--actual-dir evaluation/expected-findings`) scores 1.00 on everything.

A runner that raises an exception on a case is recorded as `ERROR` for that
case. Its expected findings count as missed, and the other cases still run.

### Exit codes

| Code | Meaning |
| --- | --- |
| `0` | Every case ran. Low scores don't fail the run, because they are the expected state of a system in development. |
| `1` | The system under test raised an exception, or an actual-output file was missing. |
| `2` | The dataset is invalid, or the runner couldn't be loaded. |

Tests: `backend/tests/unit/test_evaluation_harness.py`, run by backend CI.
The backend Docker image only contains `backend/`, so the module skips
itself there.
