"""Root conftest for all tests."""

import pytest


@pytest.fixture
def sample_component_config():
    """Sample component configuration for testing."""
    return {
        "name": "test-component",
        "protocol": "http",
        "endpoint": "http://localhost:8000/invoke",
        "timeout": 30,
        "retries": 3,
    }


@pytest.fixture
def sample_workflow_definition():
    """Sample workflow definition for testing."""
    return {
        "workflow_id": "test-workflow",
        "workflow_type": "sequential",
        "components": [
            {
                "name": "component-1",
                "protocol": "http",
                "endpoint": "http://localhost:8000/step1",
            },
            {
                "name": "component-2",
                "protocol": "http",
                "endpoint": "http://localhost:8000/step2",
            },
        ],
        "initial_data": {"input": "test_data"},
    }
