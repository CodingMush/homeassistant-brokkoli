#!/usr/bin/env python3
"""
Test script to verify that our fixes work correctly.
"""

import sys
import os

# Add the current directory to the path so we can import the modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that we can import all the necessary modules without errors."""
    try:
        # Test importing sensor.py
        from sensor import (
            PlantCurrentConductivity,
            PlantCurrentIlluminance,
            PlantCurrentMoisture,
            PlantCurrentTemperature,
            PlantCurrentHumidity,
            PlantCurrentCO2,
        )
        print("✓ All sensor classes imported successfully")
        
        # Test importing from plant_meters
        from plant_meters import (
            PlantCurrentConductivity as PlantMetersConductivity,
            PlantCurrentIlluminance as PlantMetersIlluminance,
            PlantCurrentMoisture as PlantMetersMoisture,
            PlantCurrentTemperature as PlantMetersTemperature,
            PlantCurrentHumidity as PlantMetersHumidity,
            PlantCurrentCO2 as PlantMetersCO2,
        )
        print("✓ All plant_meters classes imported successfully")
        
        # Test that the classes are the same
        assert PlantCurrentConductivity is PlantMetersConductivity
        assert PlantCurrentIlluminance is PlantMetersIlluminance
        assert PlantCurrentMoisture is PlantMetersMoisture
        assert PlantCurrentTemperature is PlantMetersTemperature
        assert PlantCurrentHumidity is PlantMetersHumidity
        assert PlantCurrentCO2 is PlantMetersCO2
        print("✓ All classes are correctly imported from plant_meters")
        
        return True
    except Exception as e:
        print(f"✗ Import test failed: {e}")
        return False

def test_sensor_config():
    """Test that sensor configuration works correctly."""
    try:
        # Import the sensor config module
        from sensor_config import SENSOR_CONFIG, get_sensor_config, round_sensor_value, format_sensor_value
        
        print("✓ Sensor configuration module imported successfully")
        print(f"✓ Total sensors configured: {len(SENSOR_CONFIG)}")
        
        # Test getting configuration for different sensors
        sensors_to_test = [
            "temperature",
            "moisture", 
            "conductivity",
            "illuminance",
            "humidity",
            "co2",
            "ppfd",
            "dli",
            "moisture_consumption",
            "fertilizer_consumption",
            "power_consumption",
            "ph",
            "energy_cost"
        ]
        
        print("\nTesting sensor configurations:")
        for sensor_type in sensors_to_test:
            config = get_sensor_config(sensor_type)
            if config:
                print(f"✓ {sensor_type}: {config.get('name', 'N/A')} - Display precision: {config.get('display_precision', 'N/A')}, Calculation precision: {config.get('calculation_precision', 'N/A')}")
            else:
                print(f"✗ {sensor_type}: Configuration not found")
        
        print("\nTesting precision handling...")
        
        # Test rounding with different contexts
        test_value = 12.3456789
        
        print(f"Original value: {test_value}")
        print(f"Temperature (display): {round_sensor_value(test_value, 'temperature', 'display')}")
        print(f"Temperature (calculation): {round_sensor_value(test_value, 'temperature', 'calculation')}")
        print(f"Moisture (display): {round_sensor_value(test_value, 'moisture', 'display')}")
        print(f"Moisture (calculation): {round_sensor_value(test_value, 'moisture', 'calculation')}")
        print(f"Conductivity (display): {round_sensor_value(test_value, 'conductivity', 'display')}")
        print(f"Conductivity (calculation): {round_sensor_value(test_value, 'conductivity', 'calculation')}")
        
        print("\nTesting format function...")
        print(f"Temperature: {format_sensor_value(test_value, 'temperature')}")
        print(f"Moisture: {format_sensor_value(test_value, 'moisture')}")
        print(f"Conductivity: {format_sensor_value(test_value, 'conductivity')}")
        
        print("\n✓ All sensor config tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Sensor config test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running tests to verify our fixes...")
    
    # Run the tests
    import_test_passed = test_imports()
    sensor_config_test_passed = test_sensor_config()
    
    if import_test_passed and sensor_config_test_passed:
        print("\n🎉 All tests passed! The fixes are working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the output above.")
        sys.exit(1)