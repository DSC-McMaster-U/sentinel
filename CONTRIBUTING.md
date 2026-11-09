# Contributing to Sentinel

Thanks for your interest in contributing to **Sentinel**! 🛡️ This project is built by student contributors at GDG McMaster, and contributors at every experience level are welcome. If something in this guide is unclear, ask on Discord or open an issue. Improving the docs counts as a contribution too.

All contributors must follow our [Code of Conduct](CODE_OF_CONDUCT.md). Please be respectful, patient, and kind.

## Table of Contents

- [Getting Started](#getting-started)
- [Finding Work](#finding-work)
- [Branching](#branching)
- [Commit Conventions](#commit-conventions)
- [Pull Request Workflow](#pull-request-workflow)
- [Linking Issues to Pull Requests](#linking-issues-to-pull-requests)
- [Running Tests Locally](#running-tests-locally)
- [Code Review Expectations](#code-review-expectations)
- [Reporting Bugs and Suggesting Features](#reporting-bugs-and-suggesting-features)
- [Security Issues](#security-issues)

## Getting Started

1. **Fork or clone the repository.** Team members with write access can clone directly. Everyone else should [fork](https://docs.github.com/en/get-started/quickstart/fork-a-repo) the repo first.

   ```bash
   git clone https://github.com/DSC-McMaster-U/sentinel.git
   cd sentinel
   ```

2. **Create a Python virtual environment and install dependencies.** See the [README](README.md) for project context.

   ```bash
   python -m venv .venv

   # macOS / Linux
   source .venv/bin/activate
   # Windows (PowerShell)
   .venv\Scripts\Activate.ps1

   pip install -r requirements.txt
   ```

   > **Note:** The project is still being set up. `requirements.txt`, environment variables (`.env`), and Docker instructions will be added as the backend and MCP server take shape. <!-- TODO: update once setup is final -->

3. **Keep your local `main` up to date** before starting new work:

   ```bash
   git checkout main
   git pull origin main
   ```

## Finding Work

- Browse the [open issues](https://github.com/DSC-McMaster-U/sentinel/issues) and the GitHub Project board.
- Issues labelled `good first issue` are a great place to start.
- **Claim an issue before you start:** comment on it (e.g. "I'd like to work on this") and wait to be assigned. This prevents two people from doing the same work.
- If you want to work on something without an issue, open one first so it can be discussed.

## Branching

- `main` is **protected**. Never push directly to it. All changes go through a pull request.
- Create a new branch for each issue using this format:

  ```
  <type>/<issue-number>-short-description
  ```

| Type       | Use for                                      |
| ---------- | -------------------------------------------- |
| `feat`     | A new feature                                |
| `fix`      | A bug fix                                    |
| `docs`     | Documentation only                           |
| `chore`    | Maintenance (deps, config, tooling)          |
| `refactor` | Code changes that don't change behaviour     |
| `test`     | Adding or updating tests                     |
| `ci`       | CI/CD and GitHub Actions changes             |

**Examples:** `feat/12-webhook-receiver`, `fix/27-npm-lockfile-parsing`, `docs/8-contribution-guidelines`

```bash
git checkout -b feat/12-webhook-receiver
```

## Commit Conventions

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>: <short description> (#<issue-number>)
```

- Use the same types as branch names (`feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `ci`).
- Write in the **imperative mood**: "add parser", not "added parser" or "adds parser".
- Keep the subject line short (about 72 characters or fewer) and don't end it with a period.
- Reference the issue number.

**Examples:**

```
feat: add GitHub webhook receiver endpoint (#12)
fix: handle missing version in package-lock.json (#27)
docs: add CONTRIBUTING guide (#8)
test: add unit tests for file classifier (#31)
```

## Pull Request Workflow

1. **Keep PRs small and focused.** Aim for one issue per PR. Smaller PRs get reviewed faster.
2. **Open a Draft PR** if your work is still in progress and you want early feedback.
3. **Link the issue** in the PR description (e.g. `Closes #12`). See below.
4. **Fill out the PR template** completely. It loads automatically when you open a PR.
5. **Self-review your diff** before requesting review. Look for leftover debug code, typos, and unrelated changes.
6. **Make sure tests and CI pass.**
7. **Request a review.** A code owner is requested automatically. Mark the PR "Ready for review" when it's done.

## Linking Issues to Pull Requests

Use these keywords in your PR description so GitHub links the issue:

| Keyword                        | Effect                                                    |
| ------------------------------ | --------------------------------------------------------- |
| `Closes #12` / `Fixes #12`     | Links the issue and **closes it automatically** on merge  |
| `Relates to #12`               | Links for reference only. The issue stays open.           |

Use `Fixes` for bugs, `Closes` for features and tasks, and `Relates to` for partial work.

## Running Tests Locally

Run the test suite before pushing:

```bash
pytest
```

- Add or update tests for any behaviour you change.
- **Linting and formatting:** <!-- TODO: add commands (e.g. `ruff check .` / `ruff format .`) once tooling is configured --> Not configured yet. This section will be updated when lint and format tools are added.
- **Your PR must pass CI** (GitHub Actions) before it can be merged, once CI is set up.

## Code Review Expectations

- Every PR needs **at least 1 approval** before merging.
- Reviewers aim to respond within **about 2 days**. If your PR has been waiting longer, ping the reviewer on Discord.
- Authors should **address every comment**, either by making the change or by replying with an explanation. Resolve conversations once they're handled.
- **Be kind and constructive.** Review the code, not the person. Explain *why* you suggest a change and say what's done well.
- PRs are merged using **Squash and merge** to keep `main` history clean.
- **Delete your branch** after it's merged.

## Reporting Bugs and Suggesting Features

Use our [issue templates](https://github.com/DSC-McMaster-U/sentinel/issues/new/choose):

- 🐛 **Bug report**: something isn't working as expected.
- ✨ **Feature request**: an idea or improvement.

Search existing issues first to avoid duplicates.

## Security Issues

**Do not open a public issue for security vulnerabilities.** Report them privately as described in [SECURITY.md](SECURITY.md).

---

Thank you for helping build Sentinel! 💙
