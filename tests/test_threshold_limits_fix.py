"""Test to verify the fix for KeyError: 'limits' in threshold classes."""

import sys
import os
from unittest.mock import MagicMock

# Add the custom_components directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'custom_components'))

from plant.plant_thresholds import PlantMaxMoisture, PlantMinMoisture, PlantMaxTemperature, PlantMinTemperature
from plant.const import DEFAULT_MAX_MOISTURE, DEFAULT_MIN_MOISTURE, DEFAULT_MAX_TEMPERATURE, DEFAULT_MIN_TEMPERATURE


def test_threshold_limits_with_missing_key():
    """Test that threshold classes handle missing FLOW_PLANT_LIMITS key."""
    # Create a mock config entry WITHOUT FLOW_PLANT_LIMITS
    config_entry = MagicMock()
    config_entry.data = {
        "plant_info": {
            "name": "Test Plant",
        }
    }
    config_entry.entry_id = "test_entry_id"
    
    # Create a mock plant device
    plant_device = MagicMock()
    plant_device.name = "Test Plant"
    
    # These should not raise KeyError: 'limits'
    try:
        max_moisture = PlantMaxMoisture(MagicMock(), config_entry, plant_device)
        min_moisture = PlantMinMoisture(MagicMock(), config_entry, plant_device)
        max_temperature = PlantMaxTemperature(MagicMock(), config_entry, plant_device)
        min_temperature = PlantMinTemperature(MagicMock(), config_entry, plant_device)
        
        # Verify they use default values
        assert max_moisture._attr_native_value == DEFAULT_MAX_MOISTURE
        assert min_moisture._attr_native_value == DEFAULT_MIN_MOISTURE
        assert max_temperature._attr_native_value == DEFAULT_MAX_TEMPERATURE
        assert min_temperature._attr_native_value == DEFAULT_MIN_TEMPERATURE
        
        print("✓ Threshold classes handle missing 'limits' key correctly")
    except KeyError as e:
        if "limits" in str(e):
            raise AssertionError("Threshold classes still raise KeyError for missing 'limits' key") from e
        else:
            raise


def test_threshold_limits_with_empty_limits():
    """Test that threshold classes handle empty FLOW_PLANT_LIMITS dict."""
    # Create a mock config entry WITH empty FLOW_PLANT_LIMITS
    config_entry = MagicMock()
    config_entry.data = {
        "plant_info": {
            "name": "Test Plant",
            "limits": {}  # Empty limits dict
        }
    }
    config_entry.entry_id = "test_entry_id"
    
    # Create a mock plant device
    plant_device = MagicMock()
    plant_device.name = "Test Plant"
    
    # These should not raise KeyError and should use default values
    try:
        max_moisture = PlantMaxMoisture(MagicMock(), config_entry, plant_device)
        min_moisture = PlantMinMoisture(MagicMock(), config_entry, plant_device)
        
        # Verify they use default values
        assert max_moisture._attr_native_value == DEFAULT_MAX_MOISTURE
        assert min_moisture._attr_native_value == DEFAULT_MIN_MOISTURE
        
        print("✓ Threshold classes handle empty 'limits' dict correctly")
    except KeyError as e:
        if "limits" in str(e):
            raise AssertionError("Threshold classes still raise KeyError for empty 'limits' dict") from e
        else:
            raise


if __name__ == "__main__":
    test_threshold_limits_with_missing_key()
    test_threshold_limits_with_empty_limits()
    print("All threshold limits tests passed! ✓")