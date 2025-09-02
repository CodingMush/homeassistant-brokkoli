"""Test to verify the fix for AttributeError: 'PlantCurrentCO2' object has no attribute '_plantdevice'."""

import sys
import os
from unittest.mock import MagicMock, patch

# Add the custom_components directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'custom_components'))

from plant.sensor import PlantCurrentStatus
from plant.tent_integration import is_plant_in_tent


# Create a test class that inherits from PlantCurrentStatus for testing
class TestPlantCurrentStatus(PlantCurrentStatus):
    """Test class for PlantCurrentStatus"""
    
    def __init__(self, hass, config, plantdevice):
        """Initialize the test sensor"""
        self._attr_name = f"{plantdevice.name} Test"
        super().__init__("test", hass, config, plantdevice)


def test_get_effective_sensor_uses_correct_attribute():
    """Test that get_effective_sensor uses the correct plant attribute."""
    # Create mock objects
    mock_hass = MagicMock()
    mock_config = MagicMock()
    mock_config.entry_id = "test_entry_id"
    mock_plant = MagicMock()
    mock_plant.entity_id = "plant.test_plant"
    mock_plant.name = "Test Plant"
    
    # Create sensor
    sensor = TestPlantCurrentStatus(mock_hass, mock_config, mock_plant)
    sensor._sensor_type = "temperature"
    
    # Verify that the sensor has the correct attribute name
    assert hasattr(sensor, '_plant'), "Sensor should have _plant attribute"
    assert not hasattr(sensor, '_plantdevice'), "Sensor should NOT have _plantdevice attribute"
    assert sensor._plant == mock_plant, "Sensor _plant attribute should reference the plant device"
    
    # Test get_effective_sensor method
    sensor._external_sensor = None
    
    # Mock is_plant_in_tent to return False
    with patch('plant.sensor.is_plant_in_tent', return_value=False):
        effective_sensor = sensor.get_effective_sensor()
        assert effective_sensor is None, "Should return None when not in tent and no external sensor"
    
    print("✓ Sensor uses correct plant attribute name")


def test_sensor_inheritance_consistency():
    """Test that sensor classes consistently use the correct plant attribute."""
    # Check that PlantCurrentStatus initializes the correct attribute
    mock_hass = MagicMock()
    mock_config = MagicMock()
    mock_config.entry_id = "test_entry_id"
    mock_plant = MagicMock()
    mock_plant.entity_id = "plant.test_plant"
    mock_plant.name = "Test Plant"
    
    sensor = TestPlantCurrentStatus(mock_hass, mock_config, mock_plant)
    
    # Verify the attribute is set correctly
    assert sensor._plant == mock_plant
    assert not hasattr(sensor, '_plantdevice')
    
    print("✓ Sensor inheritance uses correct plant attribute")


if __name__ == "__main__":
    test_get_effective_sensor_uses_correct_attribute()
    test_sensor_inheritance_consistency()
    print("All sensor attribute tests passed! ✓")