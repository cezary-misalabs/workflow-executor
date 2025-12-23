# Unit Tests

Unit tests for individual components in isolation.

## Structure

- `domain/` - Tests for domain entities, value objects, and interfaces
- `application/` - Tests for use cases, templates, and tasks
- `infrastructure/` - Tests for concrete implementations (with mocked external dependencies)

## Guidelines

- Test one unit (class/function) at a time
- Mock all external dependencies
- Fast execution (< 100ms per test)
- No I/O operations (network, file system, database)

## Running

```bash
# All unit tests
uv run pytest tests/unit/ -v

# Specific domain tests
uv run pytest tests/unit/domain/ -v

# With coverage
uv run pytest tests/unit/ --cov=src/workflow_executor
```
