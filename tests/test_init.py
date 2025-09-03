"""Test the plant integration."""

import pytest
from unittest.mock import patch, MagicMock
from homeassistant.const import STATE_OK, STATE_PROBLEM, STATE_UNKNOWN, STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntryState
from custom_components.plant import (
    PlantDevice,
)
from custom_components.plant.const import (
    DOMAIN,
    DEVICE_TYPE_PLANT,
    DEVICE_TYPE_CYCLE,
)


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    return MagicMock()


@pytest.fixture
def mock_config_entry():
    """Create a mock config entry."""
    config_entry = MagicMock()
    config_entry.data = {
        "plant_info": {
            "name": "Test Plant",
            "device_type": DEVICE_TYPE_PLANT,
        }
    }
    config_entry.entry_id = "test_entry_id"
    config_entry.options = {}
    return config_entry


def test_plant_device_initialization(mock_hass, mock_config_entry):
    """Test PlantDevice initialization."""
    # Create a PlantDevice instance
    plant_device = PlantDevice(mock_hass, mock_config_entry)
    
    # Check that attributes are initialized correctly
    assert plant_device.name == "Test Plant"
    assert plant_device.device_type == DEVICE_TYPE_PLANT
    assert plant_device.state is None


def test_plant_device_properties(mock_hass, mock_config_entry):
    """Test PlantDevice properties."""
    plant_device = PlantDevice(mock_hass, mock_config_entry)
    
    # Test device_info property
    device_info = plant_device.device_info
    assert "identifiers" in device_info
    assert "name" in device_info
    
    # Test icon property
    assert plant_device.icon is not None


def test_plant_device_state_handling(mock_hass, mock_config_entry):
    """Test PlantDevice state handling."""
    plant_device = PlantDevice(mock_hass, mock_config_entry)
    
    # Initially state should be None
    assert plant_device.state is None
    
    # Test setting state
    plant_device._attr_state = STATE_OK
    assert plant_device.state == STATE_OK


def test_plant_device_with_cycle_type(mock_hass):
    """Test PlantDevice initialization with cycle type."""
    config_entry = MagicMock()
    config_entry.data = {
        "plant_info": {
            "name": "Test Cycle",
            "device_type": DEVICE_TYPE_CYCLE,
        }
    }
    config_entry.entry_id = "test_cycle_entry_id"
    config_entry.options = {}
    
    plant_device = PlantDevice(mock_hass, config_entry)
    
    assert plant_device.name == "Test Cycle"
    assert plant_device.device_type == DEVICE_TYPE_CYCLE