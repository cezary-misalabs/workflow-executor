# Integration Tests

Tests for interactions between multiple components.

## Purpose

- Test integration between layers (domain + application, application + infrastructure)
- Verify component communication protocols work correctly
- Test workflow templates with real Prefect execution
- Validate repository implementations with real storage backends

## Examples

- HTTP communicator actually making requests (to test server)
- Prefect executor running real flows
- Workflow repository storing/retrieving from local filesystem
- Templates orchestrating multiple tasks

## Guidelines

- Test interaction between 2-3 components
- May use real external services (local test servers, local files)
- Slower than unit tests (< 5s per test)
- Should be runnable without production credentials

## Running

```bash
# All integration tests
uv run pytest tests/integration/ -v

# With coverage
uv run pytest tests/integration/ --cov=src/workflow_executor --cov-append
```
