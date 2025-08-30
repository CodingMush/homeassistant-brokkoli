"""Test cases for virtual sensor fixes."""

import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from homeassistant.const import STATE_UNKNOWN, STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from custom_components.plant.sensor import VirtualSensor, VirtualSensorManager
from custom_components.plant.const import (
    FLOW_SENSOR_TEMPERATURE,
    FLOW_PLANT_INFO,
    READING_TEMPERATURE,
    ICON_TEMPERATURE,
)


@pytest.fixture
def hass():
    """Fixture for Home Assistant instance."""
    return Mock(spec=HomeAssistant)


@pytest.fixture
def config_entry():
    """Fixture for config entry."""
    entry = Mock(spec=ConfigEntry)
    entry.entry_id = "test_entry_id"
    entry.data = {
        FLOW_PLANT_INFO: {
            FLOW_SENSOR_TEMPERATURE: "sensor.test_temperature"
        }
    }
    return entry


@pytest.fixture
def plant_device():
    """Fixture for plant device."""
    plant = Mock()
    plant.entity_id = "plant.test_plant"
    plant.uses_virtual_sensors = True
    plant.get_virtual_sensor_reference = Mock(return_value=None)
    plant._config = None
    return plant


def test_virtual_sensor_state_without_reference(hass, config_entry, plant_device):
    """Test that virtual sensor returns STATE_UNKNOWN when no reference is available."""
    # Create virtual sensor
    virtual_sensor = VirtualSensor(
        hass=hass,
        config=config_entry,
        plantdevice=plant_device,
        sensor_type="temperature",
        reading_name=READING_TEMPERATURE,
        icon=ICON_TEMPERATURE,
        unit="°C",
        device_class="temperature"
    )
    
    # Mock the update_virtual_reference to return no reference
    virtual_sensor._reference_entity_id = None
    
    # Check that state returns STATE_UNKNOWN instead of STATE_UNAVAILABLE
    assert virtual_sensor.state == STATE_UNKNOWN


def test_virtual_sensor_with_reference(hass, config_entry, plant_device):
    """Test that virtual sensor works correctly with a reference."""
    # Create virtual sensor
    virtual_sensor = VirtualSensor(
        hass=hass,
        config=config_entry,
        plantdevice=plant_device,
        sensor_type="temperature",
        reading_name=READING_TEMPERATURE,
        icon=ICON_TEMPERATURE,
        unit="°C",
        device_class="temperature"
    )
    
    # Mock the update_virtual_reference to return a reference
    virtual_sensor._reference_entity_id = "sensor.test_temperature"
    virtual_sensor._attr_native_value = 25.5
    
    # Check that state returns the actual value
    assert virtual_sensor.state == 25.5


def test_virtual_sensor_manager_create_sensors(hass, config_entry, plant_device):
    """Test that virtual sensor manager creates sensors correctly."""
    # Create virtual sensor manager
    manager = VirtualSensorManager(hass)
    
    # Create virtual sensors
    virtual_sensors = manager.create_virtual_sensors_for_plant(plant_device, config_entry)
    
    # Check that sensors were created
    assert len(virtual_sensors) > 0
    assert "temperature" in virtual_sensors
    assert isinstance(virtual_sensors["temperature"], VirtualSensor)


def test_plant_device_get_virtual_sensor_reference_standalone(plant_device):
    """Test that plant device correctly gets virtual sensor reference for standalone plants."""
    # Set up plant device for standalone virtual sensors
    plant_device._use_virtual_sensors = True
    plant_device._tent_assignment = None
    plant_device._plant_info = {
        FLOW_SENSOR_TEMPERATURE: "sensor.standalone_temperature"
    }
    
    # Test getting reference for temperature sensor
    reference = plant_device.get_virtual_sensor_reference("temperature")
    
    # Should return the direct sensor assignment
    assert reference == "sensor.standalone_temperature"


def test_plant_device_get_virtual_sensor_reference_no_reference(plant_device):
    """Test that plant device returns None when no reference is available."""
    # Set up plant device with no references
    plant_device._use_virtual_sensors = True
    plant_device._tent_assignment = None
    plant_device._plant_info = {}
    
    # Test getting reference for temperature sensor
    reference = plant_device.get_virtual_sensor_reference("temperature")
    
    # Should return None
    assert reference is None