#!/usr/bin/env python3
"""
Simple verification script for the virtual sensor fix.
This script verifies that the VirtualSensor class returns the correct values.
"""

class MockHomeAssistant:
    """Mock Home Assistant class for testing."""
    pass

class MockConfigEntry:
    """Mock ConfigEntry class for testing."""
    def __init__(self):
        self.entry_id = "test_entry_id"
        self.data = {}

class MockPlantDevice:
    """Mock PlantDevice class for testing."""
    def __init__(self):
        self.entity_id = "plant.test_plant"
        self.uses_virtual_sensors = True
        self._config = None

# Mock constants
STATE_UNKNOWN = "unknown"
STATE_UNAVAILABLE = "unavailable"

# Import the VirtualSensor class
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'plant'))

from sensor import VirtualSensor

def test_virtual_sensor_fix():
    """Test that VirtualSensor returns default state instead of STATE_UNKNOWN."""
    print("Testing VirtualSensor fix...")
    
    # Create mock objects
    hass = MockHomeAssistant()
    config = MockConfigEntry()
    plant_device = MockPlantDevice()
    
    # Create a virtual sensor
    virtual_sensor = VirtualSensor(
        hass=hass,
        config=config,
        plantdevice=plant_device,
        sensor_type="temperature",
        reading_name="Temperature",
        icon="mdi:thermometer",
        unit="°C",
        device_class="temperature"
    )
    
    # Test 1: Virtual sensor without reference should return default state (0)
    virtual_sensor._reference_entity_id = None
    state = virtual_sensor.state
    print(f"Virtual sensor without reference returns: {state} (type: {type(state)})")
    
    # Check if it's a numeric value (0) instead of a string ("unknown")
    if isinstance(state, (int, float)) and state == 0:
        print("✓ PASS: Virtual sensor correctly returns default state (0) when no reference")
    else:
        print("✗ FAIL: Virtual sensor should return default state (0) when no reference")
        return False
    
    # Test 2: Virtual sensor with reference should return actual value
    virtual_sensor._reference_entity_id = "sensor.test_temperature"
    virtual_sensor._attr_native_value = 25.5
    state = virtual_sensor.state
    print(f"Virtual sensor with reference returns: {state} (type: {type(state)})")
    
    if state == 25.5:
        print("✓ PASS: Virtual sensor correctly returns actual value when reference exists")
    else:
        print("✗ FAIL: Virtual sensor should return actual value when reference exists")
        return False
    
    print("\n✓ All tests passed! The fix is working correctly.")
    return True

if __name__ == "__main__":
    test_virtual_sensor_fix()