"""Test the precision configuration for the plant integration."""

import sys
import os

def test_precision_configuration():
    """Test that precision configuration works correctly."""
    try:
        # Add the custom_components directory to the path
        plant_path = os.path.join(os.path.dirname(__file__), '..', 'custom_components', 'plant')
        sys.path.insert(0, plant_path)
        
        # Import the sensor_config module directly
        import sensor_config
        
        # Test that sensor definitions include precision settings
        temp_def = sensor_config.get_sensor_definition("temperature")
        assert temp_def is not None, "Temperature sensor definition not found"
        assert "display_precision" in temp_def, "Temperature sensor missing display_precision"
        assert "calculation_precision" in temp_def, "Temperature sensor missing calculation_precision"
        assert temp_def["display_precision"] == 1, "Temperature display precision should be 1"
        assert temp_def["calculation_precision"] == 2, "Temperature calculation precision should be 2"
        
        moisture_def = sensor_config.get_sensor_definition("moisture")
        assert moisture_def is not None, "Moisture sensor definition not found"
        assert "display_precision" in moisture_def, "Moisture sensor missing display_precision"
        assert moisture_def["display_precision"] == 0, "Moisture display precision should be 0"
        
        # Test rounding functions
        # Temperature should round to 1 decimal place for display
        temp_value = sensor_config.round_sensor_value(20.567, "temperature", for_display=True)
        assert temp_value == 20.6, f"Expected 20.6, got {temp_value}"
        
        # Temperature should round to 2 decimal places for calculation
        temp_calc_value = sensor_config.round_sensor_value(20.567, "temperature", for_display=False)
        assert temp_calc_value == 20.57, f"Expected 20.57, got {temp_calc_value}"
        
        # Moisture should round to whole numbers for display
        moisture_value = sensor_config.round_sensor_value(45.8, "moisture", for_display=True)
        assert moisture_value == 46, f"Expected 46, got {moisture_value}"
        
        # Water consumption should round to 2 decimal places for display
        water_value = sensor_config.round_sensor_value(1.2345, "water_consumption", for_display=True)
        assert water_value == 1.23, f"Expected 1.23, got {water_value}"
        
        # Test precision getter functions
        temp_display_precision = sensor_config.get_display_precision("temperature")
        assert temp_display_precision == 1, f"Expected temperature display precision 1, got {temp_display_precision}"
        
        moisture_calc_precision = sensor_config.get_calculation_precision("moisture")
        assert moisture_calc_precision == 1, f"Expected moisture calculation precision 1, got {moisture_calc_precision}"
        
        print("[PASS] All precision configuration tests passed!")
        return True
        
    except Exception as e:
        print(f"[FAIL] Precision configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_precision_configuration()
    sys.exit(0 if success else 1)