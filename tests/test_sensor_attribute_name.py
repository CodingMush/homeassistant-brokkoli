"""Simple test to verify the sensor attribute name fix."""

import sys
import os
import re

# Add the custom_components directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'custom_components'))

def test_sensor_attribute_references():
    """Test that sensor files use the correct plant attribute name."""
    
    # Check sensor.py
    with open(os.path.join(os.path.dirname(__file__), '..', 'custom_components', 'plant', 'sensor.py'), 'r') as f:
        sensor_content = f.read()
    
    # Check that we no longer have references to _plantdevice
    plantdevice_matches = re.findall(r'self\._plantdevice', sensor_content)
    assert len(plantdevice_matches) == 0, f"Found {len(plantdevice_matches)} references to _plantdevice in sensor.py"
    
    # Check that we have references to _plant
    plant_matches = re.findall(r'self\._plant', sensor_content)
    assert len(plant_matches) > 0, "Should have references to _plant in sensor.py"
    
    print("✓ sensor.py uses correct plant attribute name")
    
    # Check plant_meters.py
    with open(os.path.join(os.path.dirname(__file__), '..', 'custom_components', 'plant', 'plant_meters.py'), 'r') as f:
        meters_content = f.read()
    
    # Check that we no longer have references to _plantdevice
    plantdevice_matches = re.findall(r'self\._plantdevice', meters_content)
    assert len(plantdevice_matches) == 0, f"Found {len(plantdevice_matches)} references to _plantdevice in plant_meters.py"
    
    # Check that we have references to _plant
    plant_matches = re.findall(r'self\._plant', meters_content)
    assert len(plant_matches) > 0, "Should have references to _plant in plant_meters.py"
    
    print("✓ plant_meters.py uses correct plant attribute name")


if __name__ == "__main__":
    test_sensor_attribute_references()
    print("All sensor attribute name tests passed! ✓")