"""Test the plant sensor module."""

import pytest
from unittest.mock import patch, MagicMock
from homeassistant.const import STATE_UNKNOWN, STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from custom_components.plant.sensor import (
    PlantCurrentStatus,
)
from custom_components.plant.const import DOMAIN


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    return MagicMock()


@pytest.fixture
def mock_config_entry():
    """Create a mock config entry."""
    config_entry = MagicMock()
    config_entry.entry_id = "test_entry_id"
    return config_entry


@pytest.fixture
def mock_plant_device():
    """Create a mock plant device."""
    plant_device = MagicMock()
    plant_device.unique_id = "test_plant_id"
    plant_device.name = "Test Plant"
    return plant_device


def test_plant_current_status_initialization(mock_hass, mock_config_entry, mock_plant_device):
    """Test PlantCurrentStatus initialization."""
    # Create a PlantCurrentStatus instance
    sensor = PlantCurrentStatus(mock_hass, mock_config_entry, mock_plant_device)
    
    # Check that attributes are initialized correctly
    assert sensor._hass == mock_hass
    assert sensor._config == mock_config_entry
    assert sensor._plant == mock_plant_device
    assert sensor._external_sensor is None


def test_plant_current_status_properties(mock_hass, mock_config_entry, mock_plant_device):
    """Test PlantCurrentStatus properties."""
    sensor = PlantCurrentStatus(mock_hass, mock_config_entry, mock_plant_device)
    
    # Test device_info property
    device_info = sensor.device_info
    assert "identifiers" in device_info
    assert (DOMAIN, mock_plant_device.unique_id) in device_info["identifiers"]
    
    # Test external_sensor property
    assert sensor.external_sensor is None
    
    # Test extra_state_attributes property when no external sensor
    assert sensor.extra_state_attributes is None


def test_plant_current_status_with_external_sensor(mock_hass, mock_config_entry, mock_plant_device):
    """Test PlantCurrentStatus with external sensor."""
    sensor = PlantCurrentStatus(mock_hass, mock_config_entry, mock_plant_device)
    
    # Set an external sensor
    test_sensor_id = "sensor.test_moisture"
    sensor._external_sensor = test_sensor_id
    
    # Test external_sensor property
    assert sensor.external_sensor == test_sensor_id
    
    # Test extra_state_attributes property
    attributes = sensor.extra_state_attributes
    assert attributes is not None
    assert "external_sensor" in attributes
    assert attributes["external_sensor"] == test_sensor_id


def test_plant_current_status_replace_external_sensor(mock_hass, mock_config_entry, mock_plant_device):
    """Test PlantCurrentStatus replace_external_sensor method."""
    sensor = PlantCurrentStatus(mock_hass, mock_config_entry, mock_plant_device)
    
    # Initially no external sensor
    assert sensor.external_sensor is None
    
    # Replace with a new sensor
    new_sensor_id = "sensor.new_moisture"
    sensor.replace_external_sensor(new_sensor_id)
    
    # Check that the external sensor was updated
    assert sensor.external_sensor == new_sensor_id
    
    # Replace with None
    sensor.replace_external_sensor(None)
    assert sensor.external_sensor is None