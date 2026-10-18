# Contributing to Flote

Thanks for your interest in contributing. This guide explains how to set up your
environment, run checks, and open a pull request.

## Development Setup

First, you need to have UV and Rust toolchain (for building the native internal
package).

1. Install project dependencies

    ```bash
    uv sync
    ```

2. Install git hooks

    ```bash
    pre-commit install
    ```

3. Install package in editable mode for development

    ```bash
    maturin develop
    ```

## Build Notes

Flote uses Maturin with pyo3 for packaging and native bindings.

To build a local wheel:

```bash
maturin build
```

## Pull Requests

Before opening your PR, confirm:

- Code is formatted and linted
- New behavior has tests
- Tests pass locally
- Docs were updated when needed
- CHANGELOG.md was updated for user-facing changes

### Branch Naming for PRs

Use branch names with a prefix and a short slug.

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
- hotfix/ for urgent fixes

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

## Reporting Bugs and Proposing Features

When opening an issue, include:

- A clear description of the problem
- Minimal reproduction steps
- Expected behavior and actual behavior
- Environment details (Python version, OS)
- Logs, traceback, or sample input when relevant
