.PHONY: test install dev

test:
	uv run pytest

install:
	uv pip install -e .

dev:
	uv pip install -e ".[dev]"
