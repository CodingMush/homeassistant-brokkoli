#!/usr/bin/env python3
"""
Verification script for virtual sensor unit fixes.
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

def test_virtual_sensor_units():
    """Test that virtual sensors have correct units."""
    print("Testing virtual sensor units...")
    
    # Import the VirtualSensor class
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'plant'))
    
    try:
        from sensor import VirtualSensor, VirtualSensorManager
        from const import UNIT_CONDUCTIVITY, READING_PH, READING_CONDUCTIVITY, ICON_PH, ICON_CONDUCTIVITY
    except ImportError as e:
        print(f"Could not import required modules: {e}")
        return False
    
    # Create mock objects
    hass = MockHomeAssistant()
    config = MockConfigEntry()
    plant_device = MockPlantDevice()
    
    # Test pH virtual sensor
    print("\nTesting pH virtual sensor...")
    ph_virtual_sensor = VirtualSensor(
        hass=hass,
        config=config,
        plantdevice=plant_device,
        sensor_type="ph",
        reading_name=READING_PH,
        icon=ICON_PH,
        unit=None,  # Should be None for pH
        device_class="ph"
    )
    
    print(f"pH virtual sensor unit: {repr(ph_virtual_sensor._attr_native_unit_of_measurement)}")
    if ph_virtual_sensor._attr_native_unit_of_measurement is None:
        print("✓ PASS: pH virtual sensor correctly has unit=None")
        ph_result = True
    else:
        print(f"✗ FAIL: pH virtual sensor should have unit=None but has {repr(ph_virtual_sensor._attr_native_unit_of_measurement)}")
        ph_result = False
    
    # Test conductivity virtual sensor
    print("\nTesting conductivity virtual sensor...")
    conductivity_virtual_sensor = VirtualSensor(
        hass=hass,
        config=config,
        plantdevice=plant_device,
        sensor_type="conductivity",
        reading_name=READING_CONDUCTIVITY,
        icon=ICON_CONDUCTIVITY,
        unit=UNIT_CONDUCTIVITY,  # Should use the fixed UNIT_CONDUCTIVITY
        device_class="conductivity"
    )
    
    print(f"Conductivity virtual sensor unit: {repr(conductivity_virtual_sensor._attr_native_unit_of_measurement)}")
    if conductivity_virtual_sensor._attr_native_unit_of_measurement == UNIT_CONDUCTIVITY:
        print(f"✓ PASS: Conductivity virtual sensor correctly has unit={repr(UNIT_CONDUCTIVITY)}")
        # Check that it uses micro sign (µ) not Greek mu (μ)
        if ord(UNIT_CONDUCTIVITY[0]) == 181:  # Micro sign
            print("✓ PASS: UNIT_CONDUCTIVITY correctly uses micro sign (µ)")
            conductivity_result = True
        else:
            print(f"✗ FAIL: UNIT_CONDUCTIVITY uses incorrect character")
            conductivity_result = False
    else:
        print(f"✗ FAIL: Conductivity virtual sensor should have unit={repr(UNIT_CONDUCTIVITY)} but has {repr(conductivity_virtual_sensor._attr_native_unit_of_measurement)}")
        conductivity_result = False
    
    return ph_result and conductivity_result

if __name__ == "__main__":
    result = test_virtual_sensor_units()
    if result:
        print("\n✓ All virtual sensor unit tests passed!")
    else:
        print("\n✗ Some virtual sensor unit tests failed!")
        exit(1)