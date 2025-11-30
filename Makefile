.PHONY: test install dev

test:
	uv run --extra dev pytest

install:
	uv pip install -e .

dev:
	uv pip install -e ".[dev]"
