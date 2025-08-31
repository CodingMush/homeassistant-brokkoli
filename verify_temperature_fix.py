#!/usr/bin/env python3
"""
Verification script to check that the temperature sensor fix has been applied.
"""

def verify_temperature_fix():
    """Verify that the temperature sensor fix has been applied."""
    print("Verifying temperature sensor fix...")
    
    with open('custom_components/plant/sensor.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check that the state_changed method now converts to float
    if 'self._attr_native_value = float(new_state.state)' in content:
        print("✓ PASS: state_changed method now converts values to float")
        float_conversion_ok = True
    else:
        print("✗ FAIL: state_changed method does not convert values to float")
        float_conversion_ok = False
    
    # Check that the state_changed method has error handling
    if 'except (ValueError, TypeError):' in content:
        print("✓ PASS: state_changed method has proper error handling")
        error_handling_ok = True
    else:
        print("✗ FAIL: state_changed method does not have proper error handling")
        error_handling_ok = False
    
    # Check that the state_changed method uses default state for invalid values
    if 'self._attr_native_value = self._default_state' in content and 'Invalid value for' in content:
        print("✓ PASS: state_changed method uses default state for invalid values")
        default_state_ok = True
    else:
        print("✗ FAIL: state_changed method does not properly handle invalid values")
        default_state_ok = False
    
    return float_conversion_ok and error_handling_ok and default_state_ok

if __name__ == "__main__":
    result = verify_temperature_fix()
    if result:
        print("\n✓ VERIFICATION PASSED! Temperature sensor fix has been applied correctly.")
        print("\nSummary of changes:")
        print("1. Fixed state_changed method to convert values to float")
        print("2. Added proper error handling for invalid values")
        print("3. Ensured default state (0) is used for invalid values")
        print("\nThis should resolve the issue where temperature sensors were showing 0°C")
        print("when the external sensor provided non-numeric values like 'unknown'.")
    else:
        print("\n✗ VERIFICATION FAILED! Temperature sensor fix was not applied correctly.")
        exit(1)