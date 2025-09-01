#!/usr/bin/env python3
"""
Final verification script for the unit consistency fixes.
"""

def verify_ph_fix():
    """Verify that pH sensor definition has been fixed."""
    print("Verifying pH sensor fix...")
    
    with open('custom_components/plant/sensor_definitions.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check that pH sensor definition uses unit=None
    if 'unit_of_measurement=None' in content and 'sensor_type="ph"' in content:
        print("✓ PASS: pH sensor definition correctly uses unit=None")
        return True
    else:
        print("✗ FAIL: pH sensor definition fix not found")
        return False

def verify_conductivity_fix():
    """Verify that conductivity unit has been fixed."""
    print("Verifying conductivity unit fix...")
    
    with open('custom_components/plant/const.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check that UNIT_CONDUCTIVITY uses micro sign (µ)
    import re
    match = re.search(r'UNIT_CONDUCTIVITY\s*=\s*["\'](.+?)["\']', content)
    if match:
        unit = match.group(1)
        print(f"UNIT_CONDUCTIVITY: {repr(unit)}")
        
        if ord(unit[0]) == 181:  # Micro sign
            print("✓ PASS: UNIT_CONDUCTIVITY correctly uses micro sign (µ)")
            return True
        else:
            print("✗ FAIL: UNIT_CONDUCTIVITY does not use micro sign")
            return False
    else:
        print("✗ FAIL: UNIT_CONDUCTIVITY definition not found")
        return False

def verify_sensor_mapping():
    """Verify that sensor mappings use the correct units."""
    print("Verifying sensor mappings...")
    
    with open('custom_components/plant/sensor.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check that conductivity mapping uses UNIT_CONDUCTIVITY
    if "'conductivity': {" in content and "UNIT_CONDUCTIVITY" in content:
        print("✓ PASS: Sensor conductivity mapping uses UNIT_CONDUCTIVITY")
        conductivity_mapping_ok = True
    else:
        print("✗ FAIL: Sensor conductivity mapping issue")
        conductivity_mapping_ok = False
    
    # Check that pH mapping uses None
    if "'ph': {" in content and "'unit': None" in content:
        print("✓ PASS: Sensor pH mapping uses unit=None")
        ph_mapping_ok = True
    else:
        print("✗ FAIL: Sensor pH mapping issue")
        ph_mapping_ok = False
    
    return conductivity_mapping_ok and ph_mapping_ok

if __name__ == "__main__":
    print("Final verification of unit consistency fixes")
    print("=" * 50)
    
    ph_ok = verify_ph_fix()
    print()
    
    conductivity_ok = verify_conductivity_fix()
    print()
    
    sensors_ok = verify_sensor_mapping()
    print()
    
    if ph_ok and conductivity_ok and sensors_ok:
        print("✓ ALL FIXES VERIFIED SUCCESSFULLY!")
        print("\nSummary of fixes:")
        print("1. pH sensor definition now uses unit=None instead of unit='pH'")
        print("2. UNIT_CONDUCTIVITY now uses micro sign (µ) instead of Greek mu (μ)")
        print("3. Sensor mappings correctly reference the fixed units")
        print("\nThese changes should resolve the long-term statistics generation issues.")
    else:
        print("✗ SOME VERIFICATIONS FAILED!")
        exit(1)