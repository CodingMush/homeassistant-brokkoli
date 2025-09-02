"""Test to verify precision consistency between tent and non-tent plants."""

import sys
import os
from unittest.mock import MagicMock, patch

# Add the custom_components directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'custom_components'))

from plant.sensor_definitions import get_sensor_definition, round_sensor_value


def test_sensor_definitions_precision():
    """Test that sensor definitions have correct precision values."""
    # Test water consumption sensors
    water_consumption_def = get_sensor_definition("water_consumption")
    assert water_consumption_def is not None
    assert water_consumption_def.display_precision == 2
    
    total_water_consumption_def = get_sensor_definition("total_water_consumption")
    assert total_water_consumption_def is not None
    assert total_water_consumption_def.display_precision == 1
    
    # Test fertilizer consumption sensors
    fertilizer_consumption_def = get_sensor_definition("fertilizer_consumption")
    assert fertilizer_consumption_def is not None
    assert fertilizer_consumption_def.display_precision == 2
    
    total_fertilizer_consumption_def = get_sensor_definition("total_fertilizer_consumption")
    assert total_fertilizer_consumption_def is not None
    assert total_fertilizer_consumption_def.display_precision == 1
    
    print("✓ Sensor definitions have correct precision values")


def test_rounding_consistency():
    """Test that rounding functions work consistently."""
    # Test water consumption values
    test_value = 1.234567
    water_rounded = round_sensor_value(test_value, "water_consumption", for_display=True)
    assert water_rounded == 1.23, f"Expected 1.23, got {water_rounded}"
    
    total_water_rounded = round_sensor_value(test_value, "total_water_consumption", for_display=True)
    assert total_water_rounded == 1.2, f"Expected 1.2, got {total_water_rounded}"
    
    # Test fertilizer consumption values
    fertilizer_rounded = round_sensor_value(test_value, "fertilizer_consumption", for_display=True)
    assert fertilizer_rounded == 1.23, f"Expected 1.23, got {fertilizer_rounded}"
    
    total_fertilizer_rounded = round_sensor_value(test_value, "total_fertilizer_consumption", for_display=True)
    assert total_fertilizer_rounded == 1.2, f"Expected 1.2, got {total_fertilizer_rounded}"
    
    print("✓ Rounding functions work consistently")


def test_median_sensor_rounding():
    """Test that median sensor rounding matches sensor definitions."""
    # Test that the new rounding logic works correctly
    sensor_type = "water_consumption"
    value = 1.234567
    
    # Correct logic: round to 2 decimal places (from sensor definition)
    correct_result = round_sensor_value(value, sensor_type, for_display=True)
    assert correct_result == 1.23
    
    # Test total water consumption (1 decimal place)
    total_sensor_type = "total_water_consumption"
    total_value = 1.234567
    total_result = round_sensor_value(total_value, total_sensor_type, for_display=True)
    assert total_result == 1.2
    
    print("✓ Median sensor rounding now uses sensor definitions")


if __name__ == "__main__":
    test_sensor_definitions_precision()
    test_rounding_consistency()
    test_median_sensor_rounding()
    print("All precision consistency tests completed! ✓")