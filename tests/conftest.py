"""Fixtures for plant integration tests."""

import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def mock_hass():
    """Mock Home Assistant object."""
    with patch('homeassistant.core.HomeAssistant') as mock_hass_class:
        mock_hass_instance = MagicMock()
        mock_hass_class.return_value = mock_hass_instance
        yield mock_hass_instance


@pytest.fixture
def mock_config_entry():
    """Mock config entry."""
    mock_entry = MagicMock()
    mock_entry.data = {
        "plant_info": {
            "name": "Test Plant",
            "device_type": "plant",
        }
    }
    mock_entry.entry_id = "test_entry_id"
    return mock_entry