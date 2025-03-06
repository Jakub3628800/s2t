# GitHub Actions Workflows

This directory contains GitHub Actions workflows for automated testing, code quality checks, and releases.

## Workflows

### Tests

![Tests](https://github.com/username/desktopstt/actions/workflows/tests.yml/badge.svg)

Runs the test suite using pytest and uploads coverage reports to Codecov.

### Pre-commit Checks

![Pre-commit](https://github.com/username/desktopstt/actions/workflows/pre-commit.yml/badge.svg)

Runs pre-commit hooks to ensure code quality and consistency.

### Release

![Release](https://github.com/username/desktopstt/actions/workflows/release.yml/badge.svg)

Automatically creates a GitHub release and publishes to PyPI when a new tag is pushed.

## Adding Badges to Main README

Add these badges to your main README.md file:

```markdown
[![Tests](https://github.com/username/desktopstt/actions/workflows/tests.yml/badge.svg)](https://github.com/username/desktopstt/actions/workflows/tests.yml)
[![Pre-commit](https://github.com/username/desktopstt/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/username/desktopstt/actions/workflows/pre-commit.yml)
[![Release](https://github.com/username/desktopstt/actions/workflows/release.yml/badge.svg)](https://github.com/username/desktopstt/actions/workflows/release.yml)
```

Replace `username` with your GitHub username or organization name.

## Setting up PyPI Releases

To enable automatic PyPI releases, you need to:

1. Create a PyPI API token at https://pypi.org/manage/account/token/
2. Add the token as a secret in your GitHub repository settings with the name `PYPI_API_TOKEN` 