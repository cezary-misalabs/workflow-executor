# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

workflow-executor is a Python project, potentially using the Abstra framework for AI-powered process automation.

## Development Setup

This project uses **uv** for dependency management and virtual environment handling.

Python version: 3.12 (specified in .python-version)

Common commands:
```bash
uv sync                  # Install dependencies and sync environment
uv add <package>         # Add a new dependency
uv add --dev <package>   # Add a development dependency
uv remove <package>      # Remove a dependency
uv run <command>         # Run a command in the project environment
uv run python main.py    # Run the main script
uv lock                  # Update lock file
uv python install 3.12   # Install Python 3.12 if needed
```

## Testing

Use pytest for running tests (run via uv):
```bash
uv run pytest                    # Run all tests
uv run pytest path/to/test.py   # Run specific test file
uv run pytest -k test_name      # Run specific test by name
uv run pytest -v                # Verbose output
```

## Code Quality

This project uses ruff (linting + formatting) and mypy (type checking).

Commands:
```bash
uv run ruff format .        # Format code
uv run ruff check .         # Lint code
uv run ruff check --fix .   # Lint and auto-fix issues
uv run mypy .               # Type check code
```

Configuration is in pyproject.toml:
- ruff: Line length 100, Python 3.12 target
- mypy: Strict mode enabled (disallow_untyped_defs=true)

## Abstra Framework

This project includes Abstra-specific configuration (.abstra/ directory is gitignored). Abstra is an AI-powered process automation framework. See https://abstra.io/docs for framework-specific documentation.
