.PHONY: install dev-install clean test run-popup run-silent run-popup-immediate run-headless build

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
	@echo "DesktopSTT installed in development mode in virtual environment"

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
	$(PYTHON) -m pytest --cov=desktopstt tests/

# Build targets
build:
	uv pip build

# Run targets
run-popup:
	$(PYTHON) -m desktopstt.popup_recorder

run-popup-silent:
	PYTHONWARNINGS=ignore $(PYTHON) -m desktopstt.popup_recorder --silent --silence-duration 3.0 2>/dev/null

run-popup-immediate:
	$(PYTHON) -m desktopstt.immediate_popup --wtype

run-headless:
	$(PYTHON) -m desktopstt.headless_recorder --wtype

run-silent:
	$(PYTHON) -m desktopstt.truly_silent

# Script targets
run-script-popup:
	./desktopstt-popup-silent.sh

run-script-silent:
	./desktopstt-silent.sh

# Help target
help:
	@echo "DesktopSTT Makefile"
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
	@echo "  run-script-popup Run the optimized popup script"
	@echo "  run-script-silent Run the silent script"
	@echo "  help            Show this help message"
	@echo ""
	@echo "Variables:"
	@echo "  PYTHON          Python interpreter to use (default: python3)"
	@echo "  VENV_DIR        Virtual environment directory (default: .venv)"
