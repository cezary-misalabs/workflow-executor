"""Dummy integration test to pass CI."""

import pytest


@pytest.mark.integration
def test_dummy() -> None:
    """Dummy integration test that always passes."""
    assert True
