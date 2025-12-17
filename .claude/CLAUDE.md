# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

workflow-executor is a Python project, potentially using the Abstra framework for AI-powered process automation.

## Development Setup

This project uses standard Python tooling. Common dependency managers supported:
- pip with requirements.txt
- poetry with pyproject.toml
- uv
- pdm
- pipenv

Create a virtual environment before installing dependencies:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate  # Windows
```

## Testing

Use pytest for running tests:
```bash
pytest                    # Run all tests
pytest path/to/test.py   # Run specific test file
pytest -k test_name      # Run specific test by name
pytest -v                # Verbose output
```

## Code Quality

- Type hints: Use type annotations for function signatures
- Linting: ruff is configured (see .ruff_cache/ in .gitignore)
- Formatting: Use ruff format or black for code formatting

## Abstra Framework

This project includes Abstra-specific configuration (.abstra/ directory is gitignored). Abstra is an AI-powered process automation framework. See https://abstra.io/docs for framework-specific documentation.
