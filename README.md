# workflow-executor

Generic workflow orchestration framework for AI platforms built on Clean Architecture principles.

## Features

- **Clean Architecture** - Clear separation: domain → application → infrastructure
- **Protocol-agnostic** - HTTP, gRPC, Ray, message queues via `IComponentCommunicator`
- **Prefect-based runtime** - Reliable execution with retry and parallel task support
- **Multiple workflow patterns** - Sequential, parallel, event-driven, state-machine
- **PyPI distribution ready** - Framework for building, not a monolithic application

## Installation

```bash
# Install Python 3.12
uv python install 3.12

# Sync dependencies
uv sync

# Run example
uv run python examples/trading_bot/run_trading_bot.py --symbol AAPL
```

## Architecture

```
domain/          # Core entities, zero external dependencies
application/     # Use cases, workflow templates (depends on domain only)
infrastructure/  # Protocol implementations, Prefect runtime
```

**Dependency Rule**: domain ← application ← infrastructure (never import outward)

## Development

```bash
uv run ruff format .                                        # Format
uv run ruff check .                                         # Lint
uv run mypy src/                                            # Type check
uv run pytest tests/unit/ tests/integration/ tests/system/ # Test
```

## Examples

- Trading bot: `examples/trading_bot/`
- LLM deployment: `examples/llm_deployment/`

## Documentation

See `.claude/CLAUDE.md` for detailed architecture, patterns, and best practices.
