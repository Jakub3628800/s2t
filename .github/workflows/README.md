# GitHub Actions Workflows

This directory contains GitHub Actions workflows for automating various tasks in the repository.

## Tests

![Tests](https://github.com/username/s2t/actions/workflows/tests.yml/badge.svg)

This workflow runs the test suite on every push and pull request to the main branch.

## Pre-commit

![Pre-commit](https://github.com/username/s2t/actions/workflows/pre-commit.yml/badge.svg)

This workflow runs pre-commit hooks on every push and pull request to the main branch.

## Release

![Release](https://github.com/username/s2t/actions/workflows/release.yml/badge.svg)

This workflow creates a new release when a new tag is pushed to the repository.

## Badge Markdown

You can use the following markdown to add badges to your README.md file:

```markdown
[![Tests](https://github.com/username/s2t/actions/workflows/tests.yml/badge.svg)](https://github.com/username/s2t/actions/workflows/tests.yml)
[![Pre-commit](https://github.com/username/s2t/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/username/s2t/actions/workflows/pre-commit.yml)
[![Release](https://github.com/username/s2t/actions/workflows/release.yml/badge.svg)](https://github.com/username/s2t/actions/workflows/release.yml)
```

Replace `username` with your GitHub username or organization name.

## Setting up PyPI Releases

To enable automatic PyPI releases, you need to:

1. Create a PyPI API token at https://pypi.org/manage/account/token/
2. Add the token as a secret in your GitHub repository settings with the name `PYPI_API_TOKEN`
