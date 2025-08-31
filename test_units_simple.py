#!/usr/bin/env python3
"""
Simple test script to verify unit consistency fixes by reading files directly.
"""

def test_ph_unit():
    """Test that pH sensor definition has unit=None"""
    with open('custom_components/plant/sensor_definitions.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Look for the pH sensor definition
    if 'unit_of_measurement=None' in content and 'sensor_type="ph"' in content:
        print("✓ PASS: pH sensor definition correctly has unit=None")
        return True
    elif 'unit_of_measurement="pH"' in content and 'sensor_type="ph"' in content:
        print("✗ FAIL: pH sensor definition still has unit='pH'")
        return False
    else:
        print("? UNKNOWN: Could not find pH sensor definition")
        return False

def test_conductivity_unit():
    """Test that conductivity unit uses micro sign (µ) not Greek mu (μ)"""
    with open('custom_components/plant/const.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Look for UNIT_CONDUCTIVITY definition
    import re
    match = re.search(r'UNIT_CONDUCTIVITY\s*=\s*["\'](.+?)["\']', content)
    if match:
        unit = match.group(1)
        print(f"Conductivity unit: {repr(unit)}")
        print(f"First character code: {ord(unit[0])}")
        
        # Micro sign (µ) has character code 181
        # Greek mu (μ) has character code 956
        if ord(unit[0]) == 181:  # Micro sign
            print("✓ PASS: Conductivity unit correctly uses micro sign (µ)")
            return True
        elif ord(unit[0]) == 956:  # Greek mu
            print("✗ FAIL: Conductivity unit incorrectly uses Greek mu (μ)")
            return False
        else:
            print(f"? UNKNOWN: Conductivity unit uses unexpected character with code {ord(unit[0])}")
            return False
    else:
        print("? UNKNOWN: Could not find UNIT_CONDUCTIVITY definition")
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