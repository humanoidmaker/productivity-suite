"""Shared test fixtures."""
import pytest


@pytest.fixture
def sample_cell_data():
    """Sample cell data for formula evaluation tests."""
    return {
        "A1": 10, "A2": 20, "A3": 30,
        "B1": 1, "B2": 2, "B3": 3,
        "C1": "hello", "C2": "world",
        "D1": True, "D2": False,
    }
