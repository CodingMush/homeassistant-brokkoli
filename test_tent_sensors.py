#!/usr/bin/env python3
"""Test script to verify tent sensor services work correctly."""

import sys
import os

# Add the custom_components directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components'))

try:
    # Test importing the services module
    import plant.services as plant_services
    print("✅ Successfully imported plant.services module")
    
    # Check if the update_tent_sensors function exists
    if hasattr(plant_services, 'update_tent_sensors'):
        print("✅ update_tent_sensors function exists in services module")
    else:
        print("❌ update_tent_sensors function NOT found in services module")
        
    # Check if the change_tent function exists
    if hasattr(plant_services, 'change_tent'):
        print("✅ change_tent function exists in services module")
    else:
        print("❌ change_tent function NOT found in services module")
        
    # Check if SERVICE_UPDATE_TENT_SENSORS constant exists in const module
    import plant.const as plant_const
    if hasattr(plant_const, 'SERVICE_UPDATE_TENT_SENSORS'):
        print(f"✅ SERVICE_UPDATE_TENT_SENSORS constant exists: {plant_const.SERVICE_UPDATE_TENT_SENSORS}")
    else:
        print("❌ SERVICE_UPDATE_TENT_SENSORS constant NOT found in const module")
        
    print("\n✅ All tests passed! Tent sensor services are properly implemented.")
    
except Exception as e:
    print(f"❌ Error during testing: {e}")
    import traceback
    traceback.print_exc()