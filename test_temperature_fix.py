#!/usr/bin/env python3
"""
Test script to verify the temperature sensor fix.
"""

class MockHomeAssistant:
    """Mock Home Assistant class for testing."""
    pass

class MockConfigEntry:
    """Mock ConfigEntry class for testing."""
    def __init__(self):
        self.entry_id = "test_entry_id"
        self.data = {
            "plant_info": {
                "temperature_sensor": "sensor.test_temperature"
            }
        }

class MockPlantDevice:
    """Mock PlantDevice class for testing."""
    def __init__(self):
        self.entity_id = "plant.test_plant"
        self.name = "Test Plant"

class MockState:
    """Mock State class for testing."""
    def __init__(self, state, attributes=None):
        self.state = state
        self.attributes = attributes or {}

# Mock constants
STATE_UNKNOWN = "unknown"
STATE_UNAVAILABLE = "unavailable"

def test_temperature_sensor_fix():
    """Test that temperature sensors properly handle non-numeric values."""
    print("Testing temperature sensor fix...")
    
    # Import the PlantCurrentTemperature class
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'plant'))
    
    try:
        from sensor import PlantCurrentTemperature
    except ImportError as e:
        print(f"Could not import required modules: {e}")
        return False
    
    # Create mock objects
    hass = MockHomeAssistant()
    config = MockConfigEntry()
    plant_device = MockPlantDevice()
    
    # Create a temperature sensor
    temperature_sensor = PlantCurrentTemperature(hass, config, plant_device)
    
    # Test 1: Valid numeric value
    print("\nTest 1: Valid numeric value")
    mock_state = MockState("25.5", {"unit_of_measurement": "°C"})
    temperature_sensor.state_changed("sensor.test_temperature", mock_state)
    print(f"Temperature sensor value: {temperature_sensor.native_value} (type: {type(temperature_sensor.native_value)})")
    
    if isinstance(temperature_sensor.native_value, (int, float)) and temperature_sensor.native_value == 25.5:
        print("✓ PASS: Temperature sensor correctly handles valid numeric value")
        test1_result = True
    else:
        print("✗ FAIL: Temperature sensor should handle valid numeric value")
        test1_result = False
    
    # Test 2: Invalid string value (should use default state)
    print("\nTest 2: Invalid string value")
    mock_state = MockState("unknown")
    temperature_sensor.state_changed("sensor.test_temperature", mock_state)
    print(f"Temperature sensor value: {temperature_sensor.native_value} (type: {type(temperature_sensor.native_value)})")
    
    if temperature_sensor.native_value == 0:  # Default state
        print("✓ PASS: Temperature sensor correctly uses default state for invalid value")
        test2_result = True
    else:
        print("✗ FAIL: Temperature sensor should use default state for invalid value")
        test2_result = False
    
    # Test 3: Empty string value (should use default state)
    print("\nTest 3: Empty string value")
    mock_state = MockState("")
    temperature_sensor.state_changed("sensor.test_temperature", mock_state)
    print(f"Temperature sensor value: {temperature_sensor.native_value} (type: {type(temperature_sensor.native_value)})")
    
    if temperature_sensor.native_value == 0:  # Default state
        print("✓ PASS: Temperature sensor correctly uses default state for empty value")
        test3_result = True
    else:
        print("✗ FAIL: Temperature sensor should use default state for empty value")
        test3_result = False
    
    return test1_result and test2_result and test3_result

if __name__ == "__main__":
    result = test_temperature_sensor_fix()
    if result:
        print("\n✓ ALL TESTS PASSED! Temperature sensor fix is working correctly.")
    else:
        print("\n✗ SOME TESTS FAILED! Temperature sensor fix needs more work.")
        exit(1)