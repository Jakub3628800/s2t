.PHONY: install dev-install clean test run uv-venv uv-sync

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

# uv targets
uv-venv:
	uv venv
	@echo "Virtual environment created with uv at .venv"
	@echo "Activate with: source .venv/bin/activate"

uv-sync:
	uv sync
	@echo "Dependencies installed with uv"

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
run:
	$(PYTHON) -m desktopstt.simple_cli

run-gui:
	$(PYTHON) -m desktopstt.main

# Transcription shortcuts
transcribe:
	$(PYTHON) -m desktopstt.simple_cli

transcribe-silent:
	PYTHONWARNINGS=ignore $(PYTHON) -m desktopstt.simple_cli --silent 2>/dev/null

transcribe-truly-silent:
	$(PYTHON) -m desktopstt.truly_silent

transcribe-time:
	$(PYTHON) -m desktopstt.simple_cli --time 5

# Pop-out UI targets
record-popup:
	$(PYTHON) -m desktopstt.popup_recorder

record-popup-time:
	$(PYTHON) -m desktopstt.popup_recorder --time 5 --no-vad

record-popup-vad:
	$(PYTHON) -m desktopstt.popup_recorder

record-popup-silent:
	PYTHONWARNINGS=ignore $(PYTHON) -m desktopstt.popup_recorder --silent --silence-duration 3.0 2>/dev/null

# Help target
help:
	@echo "DesktopSTT Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  install         Install the package"
	@echo "  dev-install     Install the package in development mode"
	@echo "  venv            Create a virtual environment"
	@echo "  install-venv    Create a virtual environment and install in development mode"
	@echo "  uv-venv         Create a virtual environment using uv"
	@echo "  uv-sync         Install dependencies using uv"
	@echo "  clean           Clean build artifacts"
	@echo "  test            Run tests"
	@echo "  run             Run the simple CLI"
	@echo "  run-gui         Run the GUI application"
	@echo "  transcribe      Run the simple CLI for transcription"
	@echo "  transcribe-silent Run the simple CLI with silent output (no warnings)"
	@echo "  transcribe-truly-silent Run the truly silent CLI (no warnings at all)"
	@echo "  transcribe-time Run the simple CLI with a 5-second recording time"
	@echo "  record-popup    Run with a pop-up recording window (with VAD)"
	@echo "  record-popup-time Run with a pop-up recording window for 5 seconds (no VAD)"
	@echo "  record-popup-vad Run with a pop-up recording window with voice activity detection"
	@echo "  record-popup-silent Run with a pop-up recording window in silent mode"
	@echo "  help            Show this help message"
	@echo ""
	@echo "Variables:"
	@echo "  PYTHON          Python interpreter to use (default: python3)"
	@echo "  VENV_DIR        Virtual environment directory (default: .venv)"
