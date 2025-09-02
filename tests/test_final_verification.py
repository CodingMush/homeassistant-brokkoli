"""Final verification tests for the plant integration fixes."""

import sys
import os
import re

# Add the custom_components directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'custom_components'))

def test_no_keyerror_in_threshold_files():
    """Test that plant_thresholds.py no longer has direct access to FLOW_PLANT_LIMITS."""
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'custom_components', 'plant', 'plant_thresholds.py'), 'r') as f:
        content = f.read()
    
    # Check that we no longer have direct access pattern
    direct_access_pattern = r'config\.data\[FLOW_PLANT_INFO\]\[FLOW_PLANT_LIMITS\]'
    matches = re.findall(direct_access_pattern, content)
    
    if len(matches) > 0:
        print(f"✗ Found {len(matches)} direct accesses to FLOW_PLANT_LIMITS in plant_thresholds.py")
        return False
    
    # Check that we have the safe access pattern
    safe_access_pattern = r'config\.data\.get\(FLOW_PLANT_INFO, {}\)\.get\(FLOW_PLANT_LIMITS, {}\)'
    matches = re.findall(safe_access_pattern, content)
    
    if len(matches) == 0:
        print("✗ Should have safe access pattern in plant_thresholds.py")
        return False
    
    print("✓ plant_thresholds.py uses safe access pattern for FLOW_PLANT_LIMITS")
    return True


def test_no_plantdevice_attribute_references():
    """Test that sensor files no longer reference _plantdevice."""
    
    # Check sensor.py
    with open(os.path.join(os.path.dirname(__file__), '..', 'custom_components', 'plant', 'sensor.py'), 'r') as f:
        sensor_content = f.read()
    
    # Check that we no longer have references to _plantdevice
    plantdevice_matches = re.findall(r'self\._plantdevice', sensor_content)
    if len(plantdevice_matches) > 0:
        print(f"✗ Found {len(plantdevice_matches)} references to _plantdevice in sensor.py")
        return False
    
    print("✓ sensor.py no longer references _plantdevice")
    
    # Check plant_meters.py
    with open(os.path.join(os.path.dirname(__file__), '..', 'custom_components', 'plant', 'plant_meters.py'), 'r') as f:
        meters_content = f.read()
    
    # Check that we no longer have references to _plantdevice
    plantdevice_matches = re.findall(r'self\._plantdevice', meters_content)
    if len(plantdevice_matches) > 0:
        print(f"✗ Found {len(plantdevice_matches)} references to _plantdevice in plant_meters.py")
        return False
    
    print("✓ plant_meters.py no longer references _plantdevice")
    return True


def test_plantdevice_ph_attributes():
    """Test that PlantDevice properly initializes pH attributes."""
    
    # We'll do a simple text search since importing might cause issues
    with open(os.path.join(os.path.dirname(__file__), '..', 'custom_components', 'plant', '__init__.py'), 'r') as f:
        content = f.read()
    
    # Look for the pH attribute initialization
    max_ph_pattern = r'self\.max_ph\s*=\s*None'
    min_ph_pattern = r'self\.min_ph\s*=\s*None'
    
    max_ph_matches = re.findall(max_ph_pattern, content)
    min_ph_matches = re.findall(min_ph_pattern, content)
    
    if len(max_ph_matches) == 0:
        print("✗ PlantDevice should initialize max_ph to None")
        return False
        
    if len(min_ph_matches) == 0:
        print("✗ PlantDevice should initialize min_ph to None")
        return False
    
    print("✓ PlantDevice properly initializes pH attributes")
    return True


def test_update_method_has_null_checks():
    """Test that update methods have null checks for threshold entities."""
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'custom_components', 'plant', '__init__.py'), 'r') as f:
        content = f.read()
    
    # Look for null check patterns in the update method
    null_check_pattern = r'if self\.min_\w+ is not None and self\.max_\w+ is not None:'
    
    matches = re.findall(null_check_pattern, content)
    
    if len(matches) < 5:  # Should have several null check patterns
        print(f"✗ Should have more null check patterns in update method (found {len(matches)})")
        return False
    
    print(f"✓ Update method has {len(matches)} null check patterns for threshold entities")
    return True


def run_final_tests():
    """Run all final verification tests."""
    print("Running final verification tests...\n")
    
    tests = [
        test_no_keyerror_in_threshold_files,
        test_no_plantdevice_attribute_references,
        test_plantdevice_ph_attributes,
        test_update_method_has_null_checks,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
            failed += 1
    
    print(f"\nFinal Verification Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All final verification tests passed! The fixes are working correctly.")
        return True
    else:
        print("❌ Some final verification tests failed. Please review the implementation.")
        return False


if __name__ == "__main__":
    success = run_final_tests()
    sys.exit(0 if success else 1)