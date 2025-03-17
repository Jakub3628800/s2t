.PHONY: test run help

# Run target
run:
	@echo "Running s2t directly with UV..."
	uv run -m s2t.main $(ARGS)

# Test target
test:
	@echo "Running tests with UV..."
	uv run -m pytest tests/ $(ARGS)

# Help target
help:
	@echo "S2T Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  run             Run s2t directly with UV (use ARGS for additional arguments)"
	@echo "  test            Run tests with UV (use ARGS for additional arguments)"
	@echo "  help            Show this help message"
	@echo ""
	@echo "Variables:"
	@echo "  PYTHON          Python interpreter to use (default: python3)"
	@echo "  ARGS            Additional arguments to pass to the script (e.g., ARGS='--silent')"
