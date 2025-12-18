# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**workflow-executor** is a generic workflow orchestration framework for AI platforms, following Clean Architecture principles. It provides a protocol-agnostic foundation for building and executing complex workflows with containerized components.

**Key Features:**
- Clean Architecture with clear layer separation (domain → application → infrastructure)
- Protocol abstraction (HTTP, gRPC, Ray, message queues)
- Prefect-based runtime for reliable workflow execution
- Support for multiple workflow patterns (sequential, parallel, event-driven, state-machine)
- Designed for PyPI distribution

## Architecture

### Layer Structure

```
src/workflow_executor/
├── domain/                    # Core business logic (zero external dependencies)
│   ├── entities/             # Workflow, Component entities (Pydantic models)
│   ├── value_objects/        # WorkflowType, ProtocolType enums
│   └── interfaces/           # Abstract interfaces (IComponentCommunicator, IWorkflowRepository)
├── application/              # Use cases and templates (depends only on domain)
│   ├── tasks/               # Generic Prefect tasks for component invocation
│   ├── templates/           # Workflow pattern templates (sequential, parallel, etc.)
│   └── use_cases/           # Business use cases (ExecuteWorkflow, ValidateWorkflow)
└── infrastructure/           # External implementations (implements domain interfaces)
    ├── execution/           # Prefect runtime adapter
    ├── communication/       # Protocol implementations (HTTP, gRPC, etc.)
    ├── persistence/         # Workflow storage backends (S3, local, etc.)
    └── integrations/        # External system integrations
```

### Architectural Principles

**Dependency Rule**: Dependencies flow inward only (Domain ← Application ← Infrastructure)
- Domain layer has zero external dependencies
- Application layer depends only on domain
- Infrastructure implements domain interfaces

**Protocol Abstraction**: All component communication via `IComponentCommunicator` interface
- HTTP, gRPC, Ray, message queues supported
- No hardcoded protocol assumptions in application layer

**External Workflow Storage**: Client workflows stored externally via `IWorkflowRepository`
- This repo is the framework; client workflows live in separate repos
- Support for multiple backends (PostgreSQL, S3, MongoDB, Git)

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
uv lock                  # Update lock file
uv python install 3.12   # Install Python 3.12 if needed
```

## Testing

Test structure follows the architecture layers:

```bash
# Unit tests (isolated, fast)
uv run pytest tests/unit/ -v
uv run pytest tests/unit/domain/ -v       # Domain layer tests
uv run pytest tests/unit/application/ -v  # Application layer tests
uv run pytest tests/unit/infrastructure/ -v  # Infrastructure tests

# Integration tests (component interactions)
uv run pytest tests/integration/ -v

# System tests (end-to-end)
uv run pytest tests/system/ -v

# All tests with coverage
uv run pytest --cov=src/workflow_executor --cov-report=term --cov-report=xml

# Specific test markers
uv run pytest -m unit         # Run only unit tests
uv run pytest -m integration  # Run only integration tests
uv run pytest -m system       # Run only system tests
```

## Code Quality

This project uses ruff (linting + formatting) and mypy (type checking).

Commands:
```bash
uv run ruff format .        # Format code
uv run ruff check .         # Lint code
uv run ruff check --fix .   # Lint and auto-fix issues
uv run mypy src/            # Type check code
```

Configuration in pyproject.toml:
- **ruff**: Line length 100, Python 3.12 target
- **mypy**: Strict mode enabled (disallow_untyped_defs=true, Pydantic plugin enabled)
- **pytest**: Async support enabled, markers for unit/integration/system tests

## CI/CD

GitHub Actions workflow runs on push and PR:
- Linting and formatting checks (ruff)
- Type checking (mypy)
- Tests on Python 3.12 and 3.13 (unit, integration, system)
- Coverage reporting (Codecov)
- Package build verification

## Examples

Example workflows are in `examples/` directory (not part of framework package):

```bash
# Trading bot example (demonstrates sequential + parallel patterns)
uv run python examples/trading_bot/run_trading_bot.py --symbol AAPL
uv run python examples/trading_bot/run_trading_bot.py --multi
```

## Workflow Patterns

The framework supports multiple workflow patterns via templates:

**Sequential Workflow**: Tasks execute in strict order
```python
# Each step waits for previous to complete
result1 = step1()
result2 = step2(result1)
result3 = step3(result2)
```

**Parallel Workflow**: Independent tasks run simultaneously
```python
# Tasks run in parallel, then merge results
future1 = task1.submit()
future2 = task2.submit()
result = merge(future1.result(), future2.result())
```

**Event-Driven Workflow**: State machines with event transitions
```python
# Process moves between states based on events
current_state = State.INITIAL
while current_state != State.COMPLETE:
    result = process_state(current_state)
    current_state = determine_next_state(result)
```

**State-Machine Workflow**: Explicit state management with <7 states
```python
# Clear state transitions with defined logic
state_machine = {
    State.NEW: handle_new,
    State.PROCESSING: handle_processing,
    State.COMPLETE: handle_complete
}
```

## Prefect Best Practices

**Tasks** (`@task`): Pure functions with clear inputs/outputs
- Automatic retries on failure
- Parallel execution via `.submit()`
- No shared state modification
- Idempotent operations

**Flows** (`@flow`): Orchestration only, no business logic
- Define execution order
- Error handling and recovery
- Never use `flow.submit()` (use ThreadPoolExecutor instead)

**Parallel Execution**: Use `task.submit()` to run tasks concurrently
**Sequential Execution**: Call tasks directly to run them in order

## PyPI Distribution

This package will be published as `workflow-executor`:

```bash
# Install
pip install workflow-executor

# Usage
from workflow_executor.domain.entities import WorkflowDefinition
from workflow_executor.infrastructure.communication import HTTPCommunicator
from workflow_executor.infrastructure.execution import PrefectExecutor

# Define workflow
workflow = WorkflowDefinition(...)

# Execute
executor = PrefectExecutor(communicator=HTTPCommunicator())
result = await executor.execute(workflow)
```

## Code Completion Checklist

**CRITICAL: Before considering ANY code changes complete, you MUST run and pass ALL of the following checks:**

```bash
# 1. Format check
uv run ruff format --check .

# 2. Linting
uv run ruff check .

# 3. Type checking
uv run mypy src/

# 4. All tests
uv run pytest tests/unit/ tests/integration/ tests/system/ -v
```

**Required Standards:**
- ✅ All ruff format checks must pass (no formatting issues)
- ✅ All ruff linting checks must pass (zero violations)
- ✅ All mypy type checks must pass (strict mode, zero errors)
- ✅ All tests must pass (unit + integration + system)

**If any check fails:**
1. Fix the issues immediately
2. Re-run all checks
3. Only after ALL checks pass can you consider the work complete

**Never skip these checks or consider work done with failing tests/linting/type errors.**

## Important Notes

- This is a **framework**, not an application. Client workflows live in separate repos.
- Follow Clean Architecture strictly: respect layer boundaries and dependency rule.
- Use dependency injection for all interfaces (IComponentCommunicator, IWorkflowRepository).
- All external communication must go through protocol abstractions.
- Workflow definitions should be stored externally via IWorkflowRepository.
- The `examples/` directory contains demonstrations, not production code.
