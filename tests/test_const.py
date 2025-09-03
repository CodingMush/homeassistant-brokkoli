"""Test for const.py."""

import pytest
from custom_components.plant.const import (
    READING_DLI,
    READING_PPFD,
    READING_MOISTURE_CONSUMPTION,
    READING_FERTILIZER_CONSUMPTION,
    UNIT_PPFD,
    UNIT_DLI,
    ICON_PPFD,
    ICON_DLI,
    ICON_CO2,
    ICON_WATER_CONSUMPTION,
    ICON_FERTILIZER_CONSUMPTION,
    ICON_POWER_CONSUMPTION,
)


def test_required_constants():
    """Test that all required constants are defined."""
    # Test that critical constants are defined
    assert READING_DLI is not None
    assert READING_PPFD is not None
    assert READING_MOISTURE_CONSUMPTION is not None
    assert READING_FERTILIZER_CONSUMPTION is not None
    
    # Test that units are defined
    assert UNIT_PPFD is not None
    assert UNIT_DLI is not None
    
    # Test that icons are defined
    assert ICON_PPFD is not None
    assert ICON_DLI is not None
    assert ICON_CO2 is not None
    assert ICON_WATER_CONSUMPTION is not None
    assert ICON_FERTILIZER_CONSUMPTION is not None
    assert ICON_POWER_CONSUMPTION is not None


def test_constant_values():
    """Test that constants have expected values."""
    # Test some specific values
    assert isinstance(READING_DLI, str)
    assert isinstance(READING_PPFD, str)
    assert isinstance(UNIT_PPFD, str)
    assert isinstance(UNIT_DLI, str)
    assert isinstance(ICON_PPFD, str)
    assert isinstance(ICON_DLI, str)