.PHONY: install dev-install clean test build run run-local-popup run-local-silent run-local-immediate run-local-headless test-local-popup test-local-silent test-local-immediate test-local-headless test-all-local check-deps test-minimal test-structure run-minimal

# Default Python interpreter
PYTHON ?= python3
VENV_DIR ?= .venv

# Check for system dependencies
check-deps:
	@echo "Checking for required system dependencies..."
	@if ! pkg-config --exists gobject-introspection-1.0; then \
		echo "Error: gobject-introspection-1.0 development libraries not found"; \
		echo "Install using: sudo apt-get install libgirepository1.0-dev"; \
		exit 1; \
	fi
	@if ! pkg-config --exists girepository-2.0; then \
		echo "Error: girepository-2.0 not found (required for PyGObject)"; \
		echo "Install using: sudo apt-get install libgirepository1.0-dev"; \
		exit 1; \
	fi
	@if ! pkg-config --exists gtk4; then \
		echo "Warning: GTK4 development libraries not found (needed for popup mode)"; \
		echo "Install using: sudo apt-get install libgtk-4-dev"; \
	fi
	@if ! which wtype >/dev/null 2>&1; then \
		echo "Warning: wtype not found (needed for automatic typing)"; \
		echo "Install using: sudo apt-get install wtype"; \
	fi
	@echo "System dependencies check completed."

# Installation targets
install: check-deps
	uv pip install .

dev-install: check-deps
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

# Local UV run targets (without installation)
run-local-popup: check-deps
	uvx --from . s2t-popup $(ARGS)

run-local-silent: check-deps
	uvx --from . s2t-silent $(ARGS)

run-local-immediate: check-deps
	uvx --from . s2t-immediate $(ARGS)

run-local-headless: check-deps
	uvx --from . s2t-headless $(ARGS)

# Test local run targets
test-local-popup: check-deps
	uvx --from . s2t-popup --help

test-local-silent: check-deps
	uvx --from . s2t-silent --help

test-local-immediate: check-deps
	uvx --from . s2t-immediate --help

test-local-headless: check-deps
	uvx --from . s2t-headless --help

# Test minimal dependency version (silent mode)
test-minimal: check-deps
	@echo "Testing minimal functionality (silent mode)..."
	@if ! uvx --from . s2t-silent --help >/dev/null 2>&1; then \
		echo "Error: Silent mode test failed!"; \
		exit 1; \
	fi
	@echo "Silent mode test passed."

# Test structure only (no dependencies required)
test-structure:
	@echo "Testing package structure (no dependencies required)..."
	@$(PYTHON) -c "from importlib import import_module; modules = ['s2t', 's2t.config', 's2t.utils']; all_good = True; [print(f'✓ {m} importable') if __import__(m) else print(f'✗ {m} not importable') or (all_good := False) for m in modules]; exit(0 if all_good else 1)"
	@echo "Package structure test completed."

# Run silent mode without checking dependencies (for testing in minimal environments)
run-minimal:
	@echo "Running silent mode without dependency checks (minimal environment)..."
	@echo "Note: This may fail if you don't have the required Python packages installed."
	@$(PYTHON) -m s2t.truly_silent --help || { echo "Error: Failed to run silent mode."; exit 1; }
	@echo "✓ Minimal test passed!"

test-all-local: test-local-popup test-local-silent test-local-immediate test-local-headless
	@echo "All local run tests passed!"

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
	@echo "  run-local-popup      Run popup recorder locally using UV without installation"
	@echo "  run-local-silent     Run silent recorder locally using UV without installation"
	@echo "  run-local-immediate  Run immediate popup recorder locally using UV without installation"
	@echo "  run-local-headless   Run headless recorder locally using UV without installation"
	@echo "  test-local-popup     Test local popup recorder without installation"
	@echo "  test-local-silent    Test local silent recorder without installation"
	@echo "  test-local-immediate Test local immediate popup recorder without installation"
	@echo "  test-local-headless  Test local headless recorder without installation"
	@echo "  test-all-local       Test all local run options without installation"
	@echo "  test-minimal         Test minimal functionality (silent mode only)"
	@echo "  test-structure       Test package structure without requiring dependencies"
	@echo "  check-deps           Check for required system dependencies"
	@echo "  run-minimal          Run silent mode without dependency checks (minimal environment)"
	@echo "  help            Show this help message"
	@echo ""
	@echo "Variables:"
	@echo "  PYTHON          Python interpreter to use (default: python3)"
	@echo "  VENV_DIR        Virtual environment directory (default: .venv)"
	@echo "  ARGS            Additional arguments to pass to the script (e.g., ARGS='--silent')"
