#!/usr/bin/env python3
"""Simple verification script for the plant integration."""

import sys
import os

# Add the custom_components directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    # Test importing the main module
    try:
        import custom_components.plant
        print("[PASS] custom_components.plant imported successfully")
    except Exception as e:
        print(f"[FAIL] Failed to import custom_components.plant: {e}")
        return False
    
    # Test importing const module
    try:
        import custom_components.plant.const
        print("[PASS] custom_components.plant.const imported successfully")
    except Exception as e:
        print(f"[FAIL] Failed to import custom_components.plant.const: {e}")
        return False
    
    # Test importing sensor module
    try:
        import custom_components.plant.sensor
        print("[PASS] custom_components.plant.sensor imported successfully")
    except Exception as e:
        print(f"[FAIL] Failed to import custom_components.plant.sensor: {e}")
        return False
    
    # Test importing the PlantDevice class
    try:
        from custom_components.plant import PlantDevice
        print("[PASS] PlantDevice class imported successfully")
    except Exception as e:
        print(f"[FAIL] Failed to import PlantDevice class: {e}")
        return False
        
    return True


def test_constants():
    """Test that critical constants are defined."""
    print("\nTesting constants...")
    
    try:
        from custom_components.plant.const import (
            READING_DLI,
            READING_PPFD,
            READING_MOISTURE_CONSUMPTION,
            READING_FERTILIZER_CONSUMPTION,
            UNIT_PPFD,
            UNIT_DLI,
            ICON_PPFD,
            ICON_DLI,
            ICON_CO2,
            ICON_WATER_CONSUMPTION,
            ICON_FERTILIZER_CONSUMPTION,
            ICON_POWER_CONSUMPTION,
        )
        
        # Verify all constants are defined and are strings
        assert isinstance(READING_DLI, str), f"READING_DLI should be a string, got {type(READING_DLI)}"
        print(f"[PASS] READING_DLI: {READING_DLI}")
        
        assert isinstance(READING_PPFD, str), f"READING_PPFD should be a string, got {type(READING_PPFD)}"
        print(f"[PASS] READING_PPFD: {READING_PPFD}")
        
        assert isinstance(READING_MOISTURE_CONSUMPTION, str), f"READING_MOISTURE_CONSUMPTION should be a string, got {type(READING_MOISTURE_CONSUMPTION)}"
        print(f"[PASS] READING_MOISTURE_CONSUMPTION: {READING_MOISTURE_CONSUMPTION}")
        
        assert isinstance(READING_FERTILIZER_CONSUMPTION, str), f"READING_FERTILIZER_CONSUMPTION should be a string, got {type(READING_FERTILIZER_CONSUMPTION)}"
        print(f"[PASS] READING_FERTILIZER_CONSUMPTION: {READING_FERTILIZER_CONSUMPTION}")
        
        assert isinstance(UNIT_PPFD, str), f"UNIT_PPFD should be a string, got {type(UNIT_PPFD)}"
        print(f"[PASS] UNIT_PPFD: {UNIT_PPFD}")
        
        assert isinstance(UNIT_DLI, str), f"UNIT_DLI should be a string, got {type(UNIT_DLI)}"
        print(f"[PASS] UNIT_DLI: {UNIT_DLI}")
        
        assert isinstance(ICON_PPFD, str), f"ICON_PPFD should be a string, got {type(ICON_PPFD)}"
        print(f"[PASS] ICON_PPFD: {ICON_PPFD}")
        
        assert isinstance(ICON_DLI, str), f"ICON_DLI should be a string, got {type(ICON_DLI)}"
        print(f"[PASS] ICON_DLI: {ICON_DLI}")
        
        assert isinstance(ICON_CO2, str), f"ICON_CO2 should be a string, got {type(ICON_CO2)}"
        print(f"[PASS] ICON_CO2: {ICON_CO2}")
        
        assert isinstance(ICON_WATER_CONSUMPTION, str), f"ICON_WATER_CONSUMPTION should be a string, got {type(ICON_WATER_CONSUMPTION)}"
        print(f"[PASS] ICON_WATER_CONSUMPTION: {ICON_WATER_CONSUMPTION}")
        
        assert isinstance(ICON_FERTILIZER_CONSUMPTION, str), f"ICON_FERTILIZER_CONSUMPTION should be a string, got {type(ICON_FERTILIZER_CONSUMPTION)}"
        print(f"[PASS] ICON_FERTILIZER_CONSUMPTION: {ICON_FERTILIZER_CONSUMPTION}")
        
        assert isinstance(ICON_POWER_CONSUMPTION, str), f"ICON_POWER_CONSUMPTION should be a string, got {type(ICON_POWER_CONSUMPTION)}"
        print(f"[PASS] ICON_POWER_CONSUMPTION: {ICON_POWER_CONSUMPTION}")
        
        print("[PASS] All constants are properly defined")
        return True
        
    except Exception as e:
        print(f"[FAIL] Error testing constants: {e}")
        return False


def main():
    """Main verification function."""
    print("Verifying Brokkoli Plant Integration...")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n[ERROR] Import verification failed!")
        return 1
    
    # Test constants
    if not test_constants():
        print("\n[ERROR] Constant verification failed!")
        return 1
    
    print("\n[SUCCESS] All verifications passed!")
    print("The Brokkoli Plant Integration is ready for use.")
    return 0


if __name__ == "__main__":
    sys.exit(main())