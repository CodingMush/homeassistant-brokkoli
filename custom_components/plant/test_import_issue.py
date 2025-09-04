#!/usr/bin/env python3
"""
Test script to reproduce the import issue.
"""

import sys
import os

# Add the current directory to the path so we can import the modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that we can import all the necessary modules without errors."""
    try:
        print("Testing import of plant_meters...")
        import plant_meters
        print("✓ plant_meters imported successfully")
        
        print("Testing import of sensor...")
        import sensor
        print("✓ sensor imported successfully")
        
        print("Testing import of select...")
        import select
        print("✓ select imported successfully")
        
        return True
    except Exception as e:
        print(f"✗ Import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running import test to reproduce the issue...")
    
    # Run the test
    test_passed = test_imports()
    
    if test_passed:
        print("\n🎉 Import test passed!")
        sys.exit(0)
    else:
        print("\n❌ Import test failed.")
        sys.exit(1)