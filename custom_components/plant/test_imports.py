#!/usr/bin/env python3
"""
Test script to verify that imports work correctly.
"""

import sys
import os

# Add the current directory to the path so we can import the modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_plant_meters_import():
    """Test that we can import plant_meters without errors."""
    try:
        import plant_meters
        print("✓ plant_meters imported successfully")
        return True
    except Exception as e:
        print(f"✗ plant_meters import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sensor_import():
    """Test that we can import sensor without errors."""
    try:
        import sensor
        print("✓ sensor imported successfully")
        return True
    except Exception as e:
        print(f"✗ sensor import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_import_chain():
    """Test that the import chain works correctly."""
    try:
        # Test importing plant_meters first
        import plant_meters
        print("✓ plant_meters imported successfully")
        
        # Test importing sensor which imports from plant_meters
        import sensor
        print("✓ sensor imported successfully")
        
        # Test that we can access the classes
        from plant_meters import (
            PlantCurrentConductivity,
            PlantCurrentIlluminance,
            PlantCurrentMoisture,
            PlantCurrentTemperature,
            PlantCurrentHumidity,
            PlantCurrentCO2,
        )
        print("✓ All plant_meters classes imported successfully")
        
        # Test that sensor can access them
        from sensor import (
            PlantCurrentConductivity as SensorConductivity,
            PlantCurrentIlluminance as SensorIlluminance,
            PlantCurrentMoisture as SensorMoisture,
            PlantCurrentTemperature as SensorTemperature,
            PlantCurrentHumidity as SensorHumidity,
            PlantCurrentCO2 as SensorCO2,
        )
        print("✓ All sensor classes imported successfully")
        
        # Verify they're the same classes
        assert PlantCurrentConductivity is SensorConductivity
        assert PlantCurrentIlluminance is SensorIlluminance
        assert PlantCurrentMoisture is SensorMoisture
        assert PlantCurrentTemperature is SensorTemperature
        assert PlantCurrentHumidity is SensorHumidity
        assert PlantCurrentCO2 is SensorCO2
        print("✓ All classes are correctly imported and identical")
        
        return True
    except Exception as e:
        print(f"✗ Import chain test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running import tests...")
    
    # Run the tests
    plant_meters_test = test_plant_meters_import()
    sensor_test = test_sensor_import()
    import_chain_test = test_import_chain()
    
    if plant_meters_test and sensor_test and import_chain_test:
        print("\n🎉 All import tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some import tests failed.")
        sys.exit(1)