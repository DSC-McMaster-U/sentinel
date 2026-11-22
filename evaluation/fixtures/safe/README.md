# evaluation/fixtures/safe/

Sample pull request changes that Sentinel should **not** flag, such as a routine dependency patch bump. Each fixture is a `PullRequestInput` JSON file and needs a matching file in `../../expected-findings/` with `"label": "safe"` and `"findings": []`.

Good safe fixtures are close to a risky one (same files, same agent) so they measure false positives. See [evaluation/README.md](../../README.md#dataset) for the current list and format.
