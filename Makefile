.PHONY: install dev-install clean test build run

# Default Python interpreter
PYTHON ?= python3
VENV_DIR ?= .venv

# Installation targets
install:
	uv pip install .

dev-install:
	uv pip install -e ".[dev]"

venv:
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "Virtual environment created at $(VENV_DIR)"
	@echo "Activate with: source $(VENV_DIR)/bin/activate"

install-venv: venv
	$(VENV_DIR)/bin/uv pip install -e .
	@echo "S2T installed in development mode in virtual environment"

# Clean targets
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

# Test targets
test:
	$(PYTHON) -m pytest tests/

# Build targets
build:
	uv pip build

# Run targets
run:
	OPENAI_API_KEY=$$(grep OPENAI_API_KEY .env | cut -d= -f2) ./s2t.py $(ARGS)

# Help target
help:
	@echo "S2T Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  install         Install the package using UV"
	@echo "  dev-install     Install the package in development mode using UV"
	@echo "  venv            Create a virtual environment"
	@echo "  install-venv    Create a virtual environment and install in development mode using UV"
	@echo "  clean           Clean build artifacts"
	@echo "  test            Run tests"
	@echo "  build           Build the package using UV"
	@echo "  run             Run the unified script (use ARGS='--silent' for silent mode)"
	@echo "  help            Show this help message"
	@echo ""
	@echo "Variables:"
	@echo "  PYTHON          Python interpreter to use (default: python3)"
	@echo "  VENV_DIR        Virtual environment directory (default: .venv)"
	@echo "  ARGS            Additional arguments to pass to the script (e.g., ARGS='--silent')"
