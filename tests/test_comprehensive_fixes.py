"""Comprehensive tests to verify all fixes for the plant integration issues."""

import sys
import os
import re
from unittest.mock import MagicMock

# Add the custom_components directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'custom_components'))

def test_threshold_classes_keyerror_fix():
    """Test that all threshold classes handle missing 'limits' key correctly."""
    from plant.plant_thresholds import (
        PlantMaxMoisture, PlantMinMoisture, PlantMaxTemperature, PlantMinTemperature,
        PlantMaxConductivity, PlantMinConductivity, PlantMaxHumidity, PlantMinHumidity,
        PlantMaxCO2, PlantMinCO2, PlantMaxWaterConsumption, PlantMinWaterConsumption,
        PlantMaxFertilizerConsumption, PlantMinFertilizerConsumption,
        PlantMaxPowerConsumption, PlantMinPowerConsumption, PlantMaxPh, PlantMinPh,
        PlantMaxDli, PlantMinDli, PlantMaxIlluminance, PlantMinIlluminance
    )
    from plant.const import (
        DEFAULT_MAX_MOISTURE, DEFAULT_MIN_MOISTURE, DEFAULT_MAX_TEMPERATURE, DEFAULT_MIN_TEMPERATURE,
        DEFAULT_MAX_CONDUCTIVITY, DEFAULT_MIN_CONDUCTIVITY, DEFAULT_MAX_HUMIDITY, DEFAULT_MIN_HUMIDITY,
        DEFAULT_MAX_CO2, DEFAULT_MIN_CO2, DEFAULT_MAX_WATER_CONSUMPTION, DEFAULT_MIN_WATER_CONSUMPTION,
        DEFAULT_MAX_FERTILIZER_CONSUMPTION, DEFAULT_MIN_FERTILIZER_CONSUMPTION,
        DEFAULT_MAX_POWER_CONSUMPTION, DEFAULT_MIN_POWER_CONSUMPTION, DEFAULT_MAX_PH, DEFAULT_MIN_PH,
        DEFAULT_MAX_DLI, DEFAULT_MIN_DLI, DEFAULT_MAX_ILLUMINANCE, DEFAULT_MIN_ILLUMINANCE
    )
    
    # Create a mock config entry WITHOUT FLOW_PLANT_LIMITS
    config_entry = MagicMock()
    config_entry.data = {
        "plant_info": {
            "name": "Test Plant",
        }
    }
    config_entry.entry_id = "test_entry_id"
    
    # Create a mock plant device
    plant_device = MagicMock()
    plant_device.name = "Test Plant"
    
    # Test all threshold classes - these should not raise KeyError
    try:
        max_moisture = PlantMaxMoisture(MagicMock(), config_entry, plant_device)
        min_moisture = PlantMinMoisture(MagicMock(), config_entry, plant_device)
        max_temperature = PlantMaxTemperature(MagicMock(), config_entry, plant_device)
        min_temperature = PlantMinTemperature(MagicMock(), config_entry, plant_device)
        max_conductivity = PlantMaxConductivity(MagicMock(), config_entry, plant_device)
        min_conductivity = PlantMinConductivity(MagicMock(), config_entry, plant_device)
        max_humidity = PlantMaxHumidity(MagicMock(), config_entry, plant_device)
        min_humidity = PlantMinHumidity(MagicMock(), config_entry, plant_device)
        max_co2 = PlantMaxCO2(MagicMock(), config_entry, plant_device)
        min_co2 = PlantMinCO2(MagicMock(), config_entry, plant_device)
        max_water_consumption = PlantMaxWaterConsumption(MagicMock(), config_entry, plant_device)
        min_water_consumption = PlantMinWaterConsumption(MagicMock(), config_entry, plant_device)
        max_fertilizer_consumption = PlantMaxFertilizerConsumption(MagicMock(), config_entry, plant_device)
        min_fertilizer_consumption = PlantMinFertilizerConsumption(MagicMock(), config_entry, plant_device)
        max_power_consumption = PlantMaxPowerConsumption(MagicMock(), config_entry, plant_device)
        min_power_consumption = PlantMinPowerConsumption(MagicMock(), config_entry, plant_device)
        max_ph = PlantMaxPh(MagicMock(), config_entry, plant_device)
        min_ph = PlantMinPh(MagicMock(), config_entry, plant_device)
        max_dli = PlantMaxDli(MagicMock(), config_entry, plant_device)
        min_dli = PlantMinDli(MagicMock(), config_entry, plant_device)
        max_illuminance = PlantMaxIlluminance(MagicMock(), config_entry, plant_device)
        min_illuminance = PlantMinIlluminance(MagicMock(), config_entry, plant_device)
        
        # Verify they use default values
        assert max_moisture._attr_native_value == DEFAULT_MAX_MOISTURE
        assert min_moisture._attr_native_value == DEFAULT_MIN_MOISTURE
        assert max_temperature._attr_native_value == DEFAULT_MAX_TEMPERATURE
        assert min_temperature._attr_native_value == DEFAULT_MIN_TEMPERATURE
        assert max_conductivity._attr_native_value == DEFAULT_MAX_CONDUCTIVITY
        assert min_conductivity._attr_native_value == DEFAULT_MIN_CONDUCTIVITY
        assert max_humidity._attr_native_value == DEFAULT_MAX_HUMIDITY
        assert min_humidity._attr_native_value == DEFAULT_MIN_HUMIDITY
        assert max_co2._attr_native_value == DEFAULT_MAX_CO2
        assert min_co2._attr_native_value == DEFAULT_MIN_CO2
        assert max_water_consumption._attr_native_value == DEFAULT_MAX_WATER_CONSUMPTION
        assert min_water_consumption._attr_native_value == DEFAULT_MIN_WATER_CONSUMPTION
        assert max_fertilizer_consumption._attr_native_value == DEFAULT_MAX_FERTILIZER_CONSUMPTION
        assert min_fertilizer_consumption._attr_native_value == DEFAULT_MIN_FERTILIZER_CONSUMPTION
        assert max_power_consumption._attr_native_value == DEFAULT_MAX_POWER_CONSUMPTION
        assert min_power_consumption._attr_native_value == DEFAULT_MIN_POWER_CONSUMPTION
        assert max_ph._attr_native_value == DEFAULT_MAX_PH
        assert min_ph._attr_native_value == DEFAULT_MIN_PH
        assert max_dli._attr_native_value == DEFAULT_MAX_DLI
        assert min_dli._attr_native_value == DEFAULT_MIN_DLI
        assert max_illuminance._attr_native_value == DEFAULT_MAX_ILLUMINANCE
        assert min_illuminance._attr_native_value == DEFAULT_MIN_ILLUMINANCE
        
        print("✓ All threshold classes handle missing 'limits' key correctly")
        return True
    except KeyError as e:
        if "limits" in str(e):
            print(f"✗ Threshold classes still raise KeyError for missing 'limits' key: {e}")
            return False
        else:
            raise
    except Exception as e:
        print(f"✗ Unexpected error in threshold classes test: {e}")
        return False


def test_plant_device_ph_attributes():
    """Test that PlantDevice properly initializes pH attributes."""
    from plant import PlantDevice
    
    # Create a mock config entry
    config_entry = MagicMock()
    config_entry.data = {
        "plant_info": {
            "name": "Test Plant",
            "device_type": "plant",
        }
    }
    config_entry.entry_id = "test_entry_id"
    
    # Create the plant device
    plant = PlantDevice(MagicMock(), config_entry)
    
    # Verify that pH attributes are initialized
    assert hasattr(plant, 'max_ph'), "PlantDevice should have max_ph attribute"
    assert hasattr(plant, 'min_ph'), "PlantDevice should have min_ph attribute"
    assert plant.max_ph is None, "max_ph should be initialized to None"
    assert plant.min_ph is None, "min_ph should be initialized to None"
    
    print("✓ PlantDevice pH attributes test passed")
    return True


def test_threshold_entities_property():
    """Test that threshold_entities property works without AttributeError."""
    from plant import PlantDevice
    
    # Create a mock config entry
    config_entry = MagicMock()
    config_entry.data = {
        "plant_info": {
            "name": "Test Plant",
            "device_type": "plant",
        }
    }
    config_entry.entry_id = "test_entry_id"
    
    # Create the plant device
    plant = PlantDevice(MagicMock(), config_entry)
    
    # Access the threshold_entities property - this should not raise AttributeError
    try:
        entities = plant.threshold_entities
        # The property should return a list, even if all entities are None
        assert isinstance(entities, list), "threshold_entities should return a list"
        print("✓ threshold_entities property test passed")
        return True
    except AttributeError as e:
        if "max_ph" in str(e):
            print(f"✗ PlantDevice is missing max_ph attribute: {e}")
            return False
        else:
            raise
    except Exception as e:
        print(f"✗ Unexpected error in threshold_entities test: {e}")
        return False


def test_sensor_attribute_references():
    """Test that sensor files use the correct plant attribute name."""
    
    # Check sensor.py
    with open(os.path.join(os.path.dirname(__file__), '..', 'custom_components', 'plant', 'sensor.py'), 'r') as f:
        sensor_content = f.read()
    
    # Check that we no longer have references to _plantdevice
    plantdevice_matches = re.findall(r'self\._plantdevice', sensor_content)
    if len(plantdevice_matches) > 0:
        print(f"✗ Found {len(plantdevice_matches)} references to _plantdevice in sensor.py")
        return False
    
    # Check that we have references to _plant
    plant_matches = re.findall(r'self\._plant', sensor_content)
    if len(plant_matches) == 0:
        print("✗ Should have references to _plant in sensor.py")
        return False
    
    print("✓ sensor.py uses correct plant attribute name")
    
    # Check plant_meters.py
    with open(os.path.join(os.path.dirname(__file__), '..', 'custom_components', 'plant', 'plant_meters.py'), 'r') as f:
        meters_content = f.read()
    
    # Check that we no longer have references to _plantdevice
    plantdevice_matches = re.findall(r'self\._plantdevice', meters_content)
    if len(plantdevice_matches) > 0:
        print(f"✗ Found {len(plantdevice_matches)} references to _plantdevice in plant_meters.py")
        return False
    
    # Check that we have references to _plant
    plant_matches = re.findall(r'self\._plant', meters_content)
    if len(plant_matches) == 0:
        print("✗ Should have references to _plant in plant_meters.py")
        return False
    
    print("✓ plant_meters.py uses correct plant attribute name")
    return True


def test_update_method_null_checks():
    """Test that the update method has proper null checks for threshold entities."""
    from plant import PlantDevice
    
    # Create a mock config entry
    config_entry = MagicMock()
    config_entry.data = {
        "plant_info": {
            "name": "Test Plant",
            "device_type": "plant",  # Test with plant device type
        }
    }
    config_entry.entry_id = "test_entry_id"
    
    # Create the plant device
    mock_hass = MagicMock()
    plant = PlantDevice(mock_hass, config_entry)
    
    # Set up mock sensors
    plant.sensor_moisture = MagicMock()
    plant.sensor_moisture.state = "45.0"
    
    # Leave threshold entities as None (this simulates the tent scenario)
    plant.min_moisture = None
    plant.max_moisture = None
    
    # This should not raise AttributeError
    try:
        plant.update()
        print("✓ Plant update method handles None threshold entities correctly")
        return True
    except AttributeError as e:
        if "state" in str(e):
            print(f"✗ Plant update method still raises AttributeError for None threshold entities: {e}")
            return False
        else:
            raise
    except Exception as e:
        print(f"✗ Unexpected error in plant update test: {e}")
        return False


def test_cycle_update_method_null_checks():
    """Test that the cycle update method has proper null checks for threshold entities."""
    from plant import PlantDevice
    
    # Create a mock config entry
    config_entry = MagicMock()
    config_entry.data = {
        "plant_info": {
            "name": "Test Cycle",
            "device_type": "cycle",  # Test with cycle device type
        }
    }
    config_entry.entry_id = "test_entry_id"
    
    # Create the plant device
    mock_hass = MagicMock()
    plant = PlantDevice(mock_hass, config_entry)
    
    # Set up mock sensors and median sensors
    plant.sensor_temperature = MagicMock()
    plant._median_sensors = {"temperature": "22.5"}
    
    # Leave threshold entities as None (this simulates the tent scenario)
    plant.min_temperature = None
    plant.max_temperature = None
    
    # This should not raise AttributeError
    try:
        plant.update()
        print("✓ Cycle update method handles None threshold entities correctly")
        return True
    except AttributeError as e:
        if "state" in str(e):
            print(f"✗ Cycle update method still raises AttributeError for None threshold entities: {e}")
            return False
        else:
            raise
    except Exception as e:
        print(f"✗ Unexpected error in cycle update test: {e}")
        return False


def run_all_tests():
    """Run all tests and report results."""
    print("Running comprehensive tests for plant integration fixes...\n")
    
    tests = [
        test_threshold_classes_keyerror_fix,
        test_plant_device_ph_attributes,
        test_threshold_entities_property,
        test_sensor_attribute_references,
        test_update_method_null_checks,
        test_cycle_update_method_null_checks,
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
    
    print(f"\nTest Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! The fixes are working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please review the implementation.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)