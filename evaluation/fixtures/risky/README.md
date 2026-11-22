# evaluation/fixtures/risky/

Sample pull request changes with known issues, such as an unpinned GitHub Action, excessive workflow permissions or a new dependency with an install script. Each fixture is a `PullRequestInput` JSON file and needs a matching file in `../../expected-findings/` with `"label": "risky"` and at least one expected `SecurityFinding`.

See [evaluation/README.md](../../README.md#dataset) for the current list and format.
