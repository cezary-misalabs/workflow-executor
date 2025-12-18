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

**Clean Architecture - The 10 Principles:**
1. **Single Responsibility (SRP)** - Each module has one reason to change
2. **Open-Closed (OCP)** - Open for extension, closed for modification
3. **Interface Segregation (ISP)** - Minimal necessary interfaces only
4. **Dependency Inversion (DIP)** - Depend on abstractions, not concretions
5. **Release-Reuse Equivalence (REP)** - Reusable components are properly versioned
6. **Common Closure (CCP)** - Group things that change together
7. **Common Reuse (CRP)** - Don't depend on unused functionality
8. **Acyclic Dependencies (ADP)** - No circular dependencies
9. **Stable Dependencies (SDP)** - Depend on stable modules
10. **Stable Abstractions (SAP)** - Abstract = stable

**Dependency Rule**: Domain ← Application ← Infrastructure (inward only)
- Domain: zero external dependencies
- Application: depends only on domain
- Infrastructure: implements domain interfaces
- **Never import from outer layers in inner layers**

**Protocol Abstraction**: All communication via `IComponentCommunicator` interface
- Supports HTTP, gRPC, Ray, message queues
- No hardcoded protocols in application layer

**External Storage**: Workflows stored via `IWorkflowRepository`
- Framework only; client workflows in separate repos
- Backends: PostgreSQL, S3, MongoDB, Git (infrastructure layer)

## Design Best Practices

**Core Patterns:**
- **Dependency Injection**: Infrastructure provides dependencies via constructors, never self-instantiate
- **Law of Demeter**: Talk only to direct dependencies, avoid `obj.getDep().getOther().call()`
- **Polymorphism > Conditionals**: Use interfaces/inheritance instead of switch/if-else chains
- **Encapsulation**: Hide internals, expose minimal public interfaces
- **Separation of Concerns**: Isolate threading (Prefect) from business logic

**Code Organization:**
- **Single Responsibility**: One class = one concern. If multiple reasons to change, split it
- **No Hybrid Structures**: Don't mix data + behavior (Pydantic = data, Services = behavior)
- **Minimal State**: Fewer instance variables = less complexity
- **Downward Flow**: High-level functions first, helpers below (read top-to-bottom like narrative)
- **Function Proximity**: Related functions stay close together

**SOLID Examples:**
```python
# ✅ SRP: Separate concerns
class WorkflowExecutor:
    def execute(self): ...
class WorkflowRepository:
    def save(self): ...

# ✅ OCP: Extend via new implementations
class GRPCCommunicator(IComponentCommunicator):
    async def invoke(self): ...

# ✅ DIP: Depend on abstractions
class ExecuteWorkflow:
    def __init__(self, communicator: IComponentCommunicator): ...
```

**Anti-Patterns (Avoid):**
- Over-engineering (YAGNI), premature optimization (KISS)
- Tight coupling, hardcoded dependencies
- God objects (classes doing too much)
- Circular dependencies
- Scattered configuration (centralize in infrastructure layer)

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

## Testing & TDD

**MANDATORY: Test-Driven Development (TDD)**
- **Always write tests BEFORE implementation code**
- Follow Red-Green-Refactor cycle:
  1. **Red**: Write failing test first
  2. **Green**: Write minimal code to pass
  3. **Refactor**: Clean up while keeping tests green
- Never write production code without a failing test first
- Tests define the contract and expected behavior
- Write tests that make sense and bring value

```bash
uv run pytest tests/unit/ -v              # Unit (isolated, layer-specific)
uv run pytest tests/integration/ -v       # Integration (component interactions)
uv run pytest tests/system/ -v            # System (end-to-end)
uv run pytest --cov=src/workflow_executor # All tests with coverage
uv run pytest -m unit|integration|system  # By marker
```

## Code Quality

```bash
uv run ruff format .        # Format
uv run ruff check .         # Lint
uv run ruff check --fix .   # Auto-fix
uv run mypy src/            # Type check (strict mode)
```

Config (pyproject.toml): ruff (line 100, Py3.12), mypy (strict), pytest (async, markers)

## CI/CD

Runs on push/PR: ruff format/lint, mypy, tests (Py3.12), coverage (Codecov), build

## Examples

Trading bot demo: `uv run python examples/trading_bot/run_trading_bot.py --symbol AAPL`

## Workflow Patterns

**Sequential**: `result1 = step1() → result2 = step2(result1) → result3 = step3(result2)`

**Parallel**: `future1/2 = task.submit() → merge(future1.result(), future2.result())`

**Event-Driven**: State machine with event transitions driving state changes

**State-Machine**: Explicit state management (<7 states) with handler mapping

## Prefect Best Practices

**Tasks** (`@task`): Pure, idempotent functions. Auto-retry, parallel via `.submit()`, no shared state
**Flows** (`@flow`): Orchestration only (no business logic). Never use `flow.submit()`
**Parallel**: `task.submit()` | **Sequential**: Direct calls

## PyPI Distribution

Package: `workflow-executor` (framework only, client workflows in separate repos)

## Code Completion Checklist

**CRITICAL: ALL checks must pass before considering work complete:**

```bash
uv run ruff format --check .                            # Format ✅
uv run ruff check .                                     # Lint ✅
uv run mypy src/                                        # Type check (strict) ✅
uv run pytest tests/unit/ tests/integration/ tests/system/ -v  # All tests ✅
```

**Never skip checks or consider work done with failing tests/linting/type errors.**

## Important Notes

- **TDD is mandatory**: Write tests first, then implementation (Red-Green-Refactor)
- This is a **framework**, not an application. Client workflows live in separate repos.
- Follow Clean Architecture strictly: respect layer boundaries and dependency rule.
- Use dependency injection for all interfaces (IComponentCommunicator, IWorkflowRepository).
- All external communication must go through protocol abstractions.
- Workflow definitions should be stored externally via IWorkflowRepository.
- The `examples/` directory contains demonstrations, not production code.
