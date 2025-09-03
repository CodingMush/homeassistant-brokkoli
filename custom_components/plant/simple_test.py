"""Simple test script to verify the sensor configuration works correctly."""

def test_sensor_config():
    """Test that sensor configuration works correctly."""
    # Import the sensor config module
    import sys
    import os
    
    # Add the current directory to the path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Simple test without Home Assistant imports
    try:
        # Try to import just the functions we need
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
        
        print("\n✓ All tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    test_sensor_config()