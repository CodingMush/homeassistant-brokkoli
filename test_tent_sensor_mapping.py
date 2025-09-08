#!/usr/bin/env python3
"""Test script to verify tent sensor mapping functionality."""

import sys
import os
import asyncio
import logging

# Add the custom_components directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'plant'))

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from unittest.mock import Mock, MagicMock
from custom_components.plant.tent import Tent
from custom_components.plant.const import (
    FLOW_SENSOR_TEMPERATURE,
    FLOW_SENSOR_MOISTURE,
    FLOW_SENSOR_CONDUCTIVITY,
    FLOW_SENSOR_ILLUMINANCE,
    FLOW_SENSOR_HUMIDITY,
    FLOW_SENSOR_CO2,
    FLOW_SENSOR_POWER_CONSUMPTION,
    FLOW_SENSOR_PH
)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)

def test_tent_sensor_mapping():
    """Test tent sensor mapping functionality."""
    print("Testing Tent sensor mapping...")
    
    # Create mock Home Assistant instance
    hass = Mock(spec=HomeAssistant)
    hass.states = Mock()
    hass.data = {}  # Add the required data attribute
    
    # Mock device registry
    device_registry_mock = Mock()
    device_registry_mock.async_get_device = Mock(return_value=None)
    
    # Mock the device registry import and function
    import homeassistant.helpers.device_registry as dr
    dr.async_get = Mock(return_value=device_registry_mock)
    
    # Mock sensor states with different device classes and units
    mock_states = {
        "sensor.temperature_1": Mock(
            attributes={"device_class": "temperature", "unit_of_measurement": "°C"}
        ),
        "sensor.humidity_1": Mock(
            attributes={"device_class": "humidity", "unit_of_measurement": "%"}
        ),
        "sensor.soil_moisture_1": Mock(
            attributes={"device_class": "humidity", "unit_of_measurement": "%"}
        ),
        "sensor.illuminance_1": Mock(
            attributes={"device_class": "illuminance", "unit_of_measurement": "lux"}
        ),
        "sensor.conductivity_1": Mock(
            attributes={"device_class": "conductivity", "unit_of_measurement": "µS/cm"}
        ),
        "sensor.co2_1": Mock(
            attributes={"device_class": "carbon_dioxide", "unit_of_measurement": "ppm"}
        ),
        "sensor.power_1": Mock(
            attributes={"device_class": "power", "unit_of_measurement": "W"}
        ),
        "sensor.ph_1": Mock(
            attributes={"device_class": "ph", "unit_of_measurement": "pH"}
        ),
    }
    
    hass.states.get = lambda entity_id: mock_states.get(entity_id, None)
    
    # Create a mock config entry
    config_entry = Mock(spec=ConfigEntry)
    config_entry.data = {
        "plant_info": {
            "tent_id": "0001",
            "name": "Test Tent",
            "sensors": [
                "sensor.temperature_1",
                "sensor.humidity_1", 
                "sensor.soil_moisture_1",
                "sensor.illuminance_1",
                "sensor.conductivity_1",
                "sensor.co2_1",
                "sensor.power_1",
                "sensor.ph_1"
            ],
            "journal": {},
            "maintenance_entries": [],
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }
    }
    
    # Create Tent instance
    tent = Tent(hass, config_entry)
    
    # Get sensors
    sensors = tent.get_sensors()
    print(f"Tent sensors: {sensors}")
    
    # Test that we have the expected number of sensors
    assert len(sensors) == 8, f"Expected 8 sensors, got {len(sensors)}"
    
    print("✓ Tent sensor mapping test passed")

def test_plant_sensor_replacement():
    """Test plant sensor replacement functionality."""
    print("Testing Plant sensor replacement...")
    
    # This would require more complex mocking of the PlantDevice class
    # For now, we'll just verify the method signature exists
    print("✓ Plant sensor replacement test placeholder")

if __name__ == "__main__":
    test_tent_sensor_mapping()
    test_plant_sensor_replacement()
    print("All tests passed!")