"""Tests for the tent integration fixes."""

import sys
import os
from unittest.mock import patch, MagicMock

# Add the custom_components directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'custom_components'))

from plant.tent_integration import TentIntegration, TentInfo
from plant.sensor import PlantCurrentStatus


def test_tent_integration_initialization():
    """Test TentIntegration initialization."""
    # Create mock hass
    mock_hass = MagicMock()
    
    # Create tent integration
    tent_integration = TentIntegration(mock_hass)
    
    # Verify initialization
    assert tent_integration is not None
    assert tent_integration._tents == {}


def test_tent_info_initialization():
    """Test TentInfo initialization."""
    # Create tent info
    tent_info_data = {
        "name": "Test Tent",
        "sensors": {
            "temperature": "sensor.tent_temperature",
            "humidity": "sensor.tent_humidity"
        },
        "controls": {
            "light": "switch.tent_light"
        }
    }
    
    tent_info = TentInfo("tent_1", tent_info_data)
    
    # Verify initialization
    assert tent_info.tent_id == "tent_1"
    assert tent_info.name == "Test Tent"
    assert tent_info.sensors == {
        "temperature": "sensor.tent_temperature",
        "humidity": "sensor.tent_humidity"
    }
    assert tent_info.controls == {
        "light": "switch.tent_light"
    }
    assert tent_info.plants == set()


def test_tent_integration_add_and_get_tent():
    """Test adding and getting tents."""
    # Create mock hass
    mock_hass = MagicMock()
    
    # Create tent integration
    tent_integration = TentIntegration(mock_hass)
    
    # Add a tent
    tent_info_data = {
        "name": "Test Tent",
        "sensors": {
            "temperature": "sensor.tent_temperature"
        }
    }
    
    tent_integration.add_tent("tent_1", tent_info_data)
    
    # Get the tent
    tent = tent_integration.get_tent("tent_1")
    
    # Verify
    assert tent is not None
    assert tent.tent_id == "tent_1"
    assert tent.name == "Test Tent"


def test_tent_plant_assignment():
    """Test assigning plants to tents."""
    # Create mock hass
    mock_hass = MagicMock()
    
    # Create tent integration
    tent_integration = TentIntegration(mock_hass)
    
    # Add a tent
    tent_info_data = {
        "name": "Test Tent",
        "sensors": {
            "temperature": "sensor.tent_temperature"
        }
    }
    
    tent_integration.add_tent("tent_1", tent_info_data)
    
    # Assign a plant to the tent
    tent_integration.assign_plant_to_tent("plant.test_plant", "tent_1")
    
    # Get tent for plant
    tent_id = tent_integration.get_tent_for_plant("plant.test_plant")
    
    # Verify
    assert tent_id == "tent_1"


def test_plant_current_status_get_effective_sensor():
    """Test PlantCurrentStatus get_effective_sensor method."""
    # Create mock objects
    mock_hass = MagicMock()
    mock_config = MagicMock()
    mock_config.entry_id = "test_entry_id"
    mock_plant = MagicMock()
    mock_plant.entity_id = "plant.test_plant"
    mock_plant.name = "Test Plant"
    
    # Create a test sensor class
    class TestSensor(PlantCurrentStatus):
        def __init__(self, hass, config, plantdevice):
            self._attr_name = f"{plantdevice.name} Test"
            super().__init__(hass, config, plantdevice)
    
    # Create sensor
    sensor = TestSensor(mock_hass, mock_config, mock_plant)
    sensor._sensor_type = "temperature"
    
    # Test with external sensor set
    sensor._external_sensor = "sensor.external_temperature"
    effective_sensor = sensor.get_effective_sensor()
    assert effective_sensor == "sensor.external_temperature"
    
    # Test with no external sensor and not in tent
    sensor._external_sensor = None
    with patch('plant.sensor.is_plant_in_tent', return_value=False):
        effective_sensor = sensor.get_effective_sensor()
        assert effective_sensor is None


if __name__ == "__main__":
    test_tent_integration_initialization()
    test_tent_info_initialization()
    test_tent_integration_add_and_get_tent()
    test_tent_plant_assignment()
    test_plant_current_status_get_effective_sensor()
    print("All tent integration tests passed! ✓")