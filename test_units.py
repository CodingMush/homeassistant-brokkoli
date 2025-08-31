#!/usr/bin/env python3
"""
Test script to verify unit consistency fixes.
"""

# Test the pH unit fix
def test_ph_unit():
    """Test that pH sensors have unit=None"""
    # Import the sensor definition
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'plant'))
    
    from sensor_definitions import SENSOR_DEFINITIONS
    
    ph_definition = SENSOR_DEFINITIONS["ph"]
    print(f"pH sensor unit: {repr(ph_definition.unit_of_measurement)}")
    
    if ph_definition.unit_of_measurement is None:
        print("✓ PASS: pH sensor correctly has unit=None")
        return True
    else:
        print(f"✗ FAIL: pH sensor should have unit=None but has {repr(ph_definition.unit_of_measurement)}")
        return False

# Test the conductivity unit fix
def test_conductivity_unit():
    """Test that conductivity sensors use micro sign (µ) not Greek mu (μ)"""
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'plant'))
    
    from const import UNIT_CONDUCTIVITY
    
    print(f"Conductivity unit: {repr(UNIT_CONDUCTIVITY)}")
    print(f"First character code: {ord(UNIT_CONDUCTIVITY[0])}")
    
    # Micro sign (µ) has character code 181
    # Greek mu (μ) has character code 956
    if ord(UNIT_CONDUCTIVITY[0]) == 181:  # Micro sign
        print("✓ PASS: Conductivity unit correctly uses micro sign (µ)")
        return True
    elif ord(UNIT_CONDUCTIVITY[0]) == 956:  # Greek mu
        print("✗ FAIL: Conductivity unit incorrectly uses Greek mu (μ)")
        return False
    else:
        print(f"? UNKNOWN: Conductivity unit uses unexpected character with code {ord(UNIT_CONDUCTIVITY[0])}")
        return False

if __name__ == "__main__":
    print("Testing unit consistency fixes...")
    print()
    
    ph_result = test_ph_unit()
    print()
    
    conductivity_result = test_conductivity_unit()
    print()
    
    if ph_result and conductivity_result:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed!")
        sys.exit(1)