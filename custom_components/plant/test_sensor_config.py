#!/usr/bin/env python3
"""
Test script to verify the sensor_config module works correctly.
"""

import sys
import os

# Add the current directory to the path so we can import the module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Try to import the sensor_config module
    from sensor_config import get_sensor_config, round_sensor_value, format_sensor_value
    
    # Test getting a sensor configuration
    temp_config = get_sensor_config("temperature")
    print(f"Temperature config: {temp_config}")
    
    # Test rounding a value
    rounded_value = round_sensor_value(25.123456, "temperature", "calculation")
    print(f"Rounded temperature value (calculation): {rounded_value}")
    
    # Test formatting a value
    formatted_value = format_sensor_value(25.123456, "temperature")
    print(f"Formatted temperature value: {formatted_value}")
    
    print("All tests passed!")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

"""Test script to verify the sensor configuration works correctly."""

import sys
import os

# Add the current directory to the path so we can import the plant module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sensor_config import get_sensor_config, round_sensor_value, format_sensor_value

def test_sensor_config():
    """Test that sensor configuration works correctly."""
    print("Testing sensor configuration...")
    
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
    
    for sensor_type in sensors_to_test:
        config = get_sensor_config(sensor_type)
        if config:
            print(f"✓ {sensor_type}: {config['name']} - Display precision: {config.get('display_precision', 'N/A')}, Calculation precision: {config.get('calculation_precision', 'N/A')}")
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

if __name__ == "__main__":
    test_sensor_config()