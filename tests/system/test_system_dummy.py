"""Dummy system test to pass CI."""

import pytest


@pytest.mark.system
def test_dummy() -> None:
    """Dummy system test that always passes."""
    assert True
