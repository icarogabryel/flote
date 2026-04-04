# Contributing to Flote

Thanks for your interest in contributing.

This guide explains how to set up your environment, run checks, and open a pull request.

## Development Setup

First, you need to have Python 3.10, Poetry and Rust toolchain (for building the native internal package).

1. Install project dependencies and development dependencies

    ```bash
    poetry install --with dev
    ```

2. Install git hooks

    ```bash
    poetry run pre-commit install
    ```

3. Install package in editable mode for development

    ```bash
    poetry run maturin develop
    ```

## Build Notes

Flote uses Maturin with pyo3 for packaging and native bindings.

To build a local wheel:

```bash
poetry run maturin build
```

## Running Quality Checks

Make sure that pre-commit hooks are installed and run on each commit. You can also run them manually:

```bash
poetry run pre-commit run --all-files
```

## Pull Requests

Before opening your PR, confirm:

- Code is formatted and linted
- Tests pass locally
- New behavior has tests
- Docs were updated when needed
- CHANGELOG.md was updated for user-facing changes

### Code Style and Scope

- Keep changes focused and small
- Prefer clear names and straightforward logic
- Add tests for behavior changes and bug fixes
- Update docs when public behavior changes
- Avoid unrelated refactors in the same pull request

### Branch Naming for PRs

Use branch names with a prefix and a short slug.

All branches must derive from `dev` (except hot fixes which can derive from `main`).

Base flow:

```bash
git checkout dev
git pull
git checkout -b <prefix>/<short-description>
```

Pattern:

```text
<prefix>/<short-description>
```

Required prefixes:

- feature/ for new features
- rm-feature/ for feature removals
- docs/ for documentation changes
- bugfix/ for bug fixes
- refactor/ for internal refactoring without behavior change
- test/ for test-only changes
- chore/ for maintenance tasks
- ci/ for CI/CD workflow changes
- hotfix/ for urgent production fixes

### Commit Messages

Commit messages must follow Conventional Commits.

Format:

```text
type(scope): short description
```

Rules:

- Use lowercase `type`
- Keep description short and in imperative form

Common types:

- feat: new feature
- fix: bug fix
- docs: documentation
- refactor: code refactor without behavior change
- test: tests
- chore: maintenance tasks
- ci: CI/CD changes
- build: build or dependency changes

### Description Best Practices

A good PR description speeds up review and reduces back-and-forth.

Include these sections:

- Summary: what changed in 1-3 short sentences
- Motivation: why this change is needed
- Scope: what is included and what is intentionally out of scope
- Technical Notes: key implementation decisions and trade-offs
- Validation: commands run and results (tests, lint, formatting)
- Breaking Changes: migration notes, if applicable

Recommended checklist inside the PR description:

- Linked issue or task
- Screenshots or logs (when relevant)
- Test evidence added
- Docs updated

## Reporting Bugs and Proposing Features

When opening an issue, include:

- A clear description of the problem
- Minimal reproduction steps
- Expected behavior and actual behavior
- Environment details (Python version, OS)
- Logs, traceback, or sample input when relevant
