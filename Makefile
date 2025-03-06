.PHONY: install dev-install clean test run-popup run-silent

# Default Python interpreter
PYTHON ?= python3
VENV_DIR ?= .venv

# Installation targets
install:
	$(PYTHON) -m pip install .

dev-install:
	$(PYTHON) -m pip install -e ".[dev]"

venv:
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "Virtual environment created at $(VENV_DIR)"
	@echo "Activate with: source $(VENV_DIR)/bin/activate"

install-venv: venv
	$(VENV_DIR)/bin/pip install -e .
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

# Run targets
run-popup:
	$(PYTHON) -m desktopstt.popup_recorder

run-popup-silent:
	PYTHONWARNINGS=ignore $(PYTHON) -m desktopstt.popup_recorder --silent --silence-duration 3.0 2>/dev/null

run-silent:
	$(PYTHON) -m desktopstt.truly_silent

# Help target
help:
	@echo "DesktopSTT Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  install         Install the package"
	@echo "  dev-install     Install the package in development mode"
	@echo "  venv            Create a virtual environment"
	@echo "  install-venv    Create a virtual environment and install in development mode"
	@echo "  clean           Clean build artifacts"
	@echo "  test            Run tests"
	@echo "  run-popup       Run with a pop-up recording window (with VAD)"
	@echo "  run-popup-silent Run with a pop-up recording window in silent mode"
	@echo "  run-silent      Run the headless terminal-based version"
	@echo "  help            Show this help message"
	@echo ""
	@echo "Variables:"
	@echo "  PYTHON          Python interpreter to use (default: python3)"
	@echo "  VENV_DIR        Virtual environment directory (default: .venv)"
