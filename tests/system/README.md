# System Tests

End-to-end tests for complete workflow execution scenarios.

## Purpose

- Test entire workflow execution from definition to completion
- Verify all components work together in production-like scenarios
- Test example workflows (trading bot, etc.)
- Validate framework behavior under realistic conditions

## Examples

- Load workflow from YAML → Execute with real components → Verify results
- Multi-symbol trading bot workflow execution
- Sequential workflow with HTTP components
- Event-driven workflow with state transitions
- Error handling and retry behavior across full stack

## Guidelines

- Test complete user journeys
- May use docker containers for component services
- Slowest tests (< 30s per test)
- Should simulate production scenarios
- May require external test services

## Running

```bash
# All system tests
uv run pytest tests/system/ -v

# Specific scenario
uv run pytest tests/system/test_trading_bot_workflow.py -v

# With coverage
uv run pytest tests/system/ --cov=src/workflow_executor --cov-append
```

## Setup

Some system tests may require:
- Docker running (for containerized test components)
- Test API servers
- Mock external services

Check individual test files for specific requirements.
