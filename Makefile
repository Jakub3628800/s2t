.PHONY: install dev-install clean test run-popup run-silent run-popup-immediate run-headless build run-s2t

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

test-coverage:
	$(PYTHON) -m pytest --cov=s2t tests/

# Build targets
build:
	uv pip build

# Run targets
run-popup:
	$(PYTHON) -m s2t.popup_recorder

run-popup-silent:
	PYTHONWARNINGS=ignore $(PYTHON) -m s2t.popup_recorder --silent --silence-duration 3.0 2>/dev/null

run-popup-immediate:
	$(PYTHON) -m s2t.immediate_popup

run-headless:
	$(PYTHON) -m s2t.headless_recorder

run-silent:
	$(PYTHON) -m s2t.truly_silent

# Script targets - using the new unified script
run-script:
	OPENAI_API_KEY=$$(grep OPENAI_API_KEY .env | cut -d= -f2) ./s2t.py

run-script-popup:
	OPENAI_API_KEY=$$(grep OPENAI_API_KEY .env | cut -d= -f2) ./s2t.py

run-script-silent:
	OPENAI_API_KEY=$$(grep OPENAI_API_KEY .env | cut -d= -f2) ./s2t.py --silent

run-script-newline:
	OPENAI_API_KEY=$$(grep OPENAI_API_KEY .env | cut -d= -f2) ./s2t.py --newline

run-script-silent-newline:
	OPENAI_API_KEY=$$(grep OPENAI_API_KEY .env | cut -d= -f2) ./s2t.py --silent --newline

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
	@echo "  test-coverage   Run tests with coverage report"
	@echo "  build           Build the package using UV"
	@echo "  run-popup       Run with a pop-up recording window (with VAD)"
	@echo "  run-popup-silent Run with a pop-up recording window in silent mode"
	@echo "  run-popup-immediate Run with a pop-up that starts recording immediately"
	@echo "  run-headless    Run the headless recorder with notifications"
	@echo "  run-silent      Run the truly silent recorder"
	@echo "  run-script      Run the unified script (popup mode by default)"
	@echo "  run-script-popup Run the unified script in popup mode"
	@echo "  run-script-silent Run the unified script in silent mode"
	@echo "  run-script-newline Run the unified script with newline after transcription"
	@echo "  run-script-silent-newline Run the unified script in silent mode with newline"
	@echo "  help            Show this help message"
	@echo ""
	@echo "Variables:"
	@echo "  PYTHON          Python interpreter to use (default: python3)"
	@echo "  VENV_DIR        Virtual environment directory (default: .venv)"
