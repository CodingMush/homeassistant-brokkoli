"""Test for Plant-Tent integration."""

import pytest
from unittest.mock import Mock, patch
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from custom_components.plant import PlantDevice
from custom_components.plant.tent import Tent


def test_plant_assign_tent():
    """Test assigning a tent to a plant."""
    # Create mock objects
    hass = Mock(spec=HomeAssistant)
    config = Mock(spec=ConfigEntry)
    
    # Set up config data
    config.data = {
        "plant_info": {
            "name": "Test Plant",
            "device_type": "plant"
        }
    }
    config.options = {}
    config.entry_id = "test_entry_id"
    
    # Create plant device
    with patch('custom_components.plant.PlantDevice._get_next_id'):
        plant = PlantDevice(hass, config)
    
    # Create mock tent
    tent_config = Mock(spec=ConfigEntry)
    tent_config.data = {
        "tent_id": "test_tent",
        "name": "Test Tent",
        "sensors": ["sensor.temperature", "sensor.humidity"]
    }
    tent = Tent(hass, tent_config)
    
    # Mock the replace_sensors method
    plant.replace_sensors = Mock()
    
    # Assign tent to plant
    plant.assign_tent(tent)
    
    # Verify the assignment
    assert plant.get_assigned_tent() == tent
    assert plant.get_tent_id() == "test_tent"
    plant.replace_sensors.assert_called_once_with(["sensor.temperature", "sensor.humidity"])


def test_plant_change_tent():
    """Test changing the tent assigned to a plant."""
    # Create mock objects
    hass = Mock(spec=HomeAssistant)
    config = Mock(spec=ConfigEntry)
    
    # Set up config data
    config.data = {
        "plant_info": {
            "name": "Test Plant",
            "device_type": "plant"
        }
    }
    config.options = {}
    config.entry_id = "test_entry_id"
    
    # Create plant device
    with patch('custom_components.plant.PlantDevice._get_next_id'):
        plant = PlantDevice(hass, config)
    
    # Create mock tents
    tent1_config = Mock(spec=ConfigEntry)
    tent1_config.data = {
        "tent_id": "test_tent_1",
        "name": "Test Tent 1",
        "sensors": ["sensor.temperature", "sensor.humidity"]
    }
    tent1 = Tent(hass, tent1_config)
    
    tent2_config = Mock(spec=ConfigEntry)
    tent2_config.data = {
        "tent_id": "test_tent_2",
        "name": "Test Tent 2",
        "sensors": ["sensor.light", "sensor.soil_moisture"]
    }
    tent2 = Tent(hass, tent2_config)
    
    # Mock the replace_sensors method
    plant.replace_sensors = Mock()
    
    # Assign first tent
    plant.assign_tent(tent1)
    assert plant.get_assigned_tent() == tent1
    assert plant.get_tent_id() == "test_tent_1"
    plant.replace_sensors.assert_called_once_with(["sensor.temperature", "sensor.humidity"])
    
    # Reset mock for second call
    plant.replace_sensors.reset_mock()
    
    # Change to second tent
    plant.change_tent(tent2)
    assert plant.get_assigned_tent() == tent2
    assert plant.get_tent_id() == "test_tent_2"
    plant.replace_sensors.assert_called_once_with(["sensor.light", "sensor.soil_moisture"])


if __name__ == "__main__":
    pytest.main([__file__])