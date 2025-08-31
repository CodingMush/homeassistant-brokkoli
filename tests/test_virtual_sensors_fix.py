"""Test cases for virtual sensor fixes."""

import unittest
from unittest.mock import Mock
from homeassistant.const import STATE_UNKNOWN, STATE_UNAVAILABLE

from custom_components.plant.sensor import VirtualSensor, VirtualSensorManager
from custom_components.plant.const import (
    FLOW_SENSOR_TEMPERATURE,
    FLOW_PLANT_INFO,
    READING_TEMPERATURE,
    ICON_TEMPERATURE,
)


class TestVirtualSensorsFix(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.hass = Mock()
        self.config_entry = Mock()
        self.config_entry.entry_id = "test_entry_id"
        self.config_entry.data = {
            FLOW_PLANT_INFO: {
                FLOW_SENSOR_TEMPERATURE: "sensor.test_temperature"
            }
        }
        self.plant_device = Mock()
        self.plant_device.entity_id = "plant.test_plant"
        self.plant_device.uses_virtual_sensors = True
        self.plant_device.get_virtual_sensor_reference = Mock(return_value=None)
        self.plant_device._config = None

    def test_virtual_sensor_state_without_reference(self):
        """Test that virtual sensor returns default state (0) when no reference is available."""
        # Create virtual sensor
        virtual_sensor = VirtualSensor(
            hass=self.hass,
            config=self.config_entry,
            plantdevice=self.plant_device,
            sensor_type="temperature",
            reading_name=READING_TEMPERATURE,
            icon=ICON_TEMPERATURE,
            unit="°C",
            device_class="temperature"
        )
        
        # Mock the update_virtual_reference to return no reference
        virtual_sensor._reference_entity_id = None
        
        # Check that state returns default state (0) instead of STATE_UNKNOWN
        self.assertEqual(virtual_sensor.state, 0)

    def test_virtual_sensor_with_reference(self):
        """Test that virtual sensor works correctly with a reference."""
        # Create virtual sensor
        virtual_sensor = VirtualSensor(
            hass=self.hass,
            config=self.config_entry,
            plantdevice=self.plant_device,
            sensor_type="temperature",
            reading_name=READING_TEMPERATURE,
            icon=ICON_TEMPERATURE,
            unit="°C",
            device_class="temperature"
        )
        
        # Mock the update_virtual_reference to return a reference
        virtual_sensor._reference_entity_id = "sensor.test_temperature"
        virtual_sensor._attr_native_value = 25.5
        
        # Check that state returns the actual value
        self.assertEqual(virtual_sensor.state, 25.5)

    def test_virtual_sensor_manager_create_sensors(self):
        """Test that virtual sensor manager creates sensors correctly."""
        # Create virtual sensor manager
        manager = VirtualSensorManager(self.hass)
        
        # Create virtual sensors
        virtual_sensors = manager.create_virtual_sensors_for_plant(self.plant_device, self.config_entry)
        
        # Check that sensors were created
        self.assertGreater(len(virtual_sensors), 0)
        self.assertIn("temperature", virtual_sensors)
        self.assertIsInstance(virtual_sensors["temperature"], VirtualSensor)

    def test_plant_device_get_virtual_sensor_reference_standalone(self):
        """Test that plant device correctly gets virtual sensor reference for standalone plants."""
        # Set up plant device for standalone virtual sensors
        self.plant_device._use_virtual_sensors = True
        self.plant_device._tent_assignment = None
        self.plant_device._plant_info = {
            FLOW_SENSOR_TEMPERATURE: "sensor.standalone_temperature"
        }
        
        # Test getting reference for temperature sensor
        reference = self.plant_device.get_virtual_sensor_reference("temperature")
        
        # Should return the direct sensor assignment
        self.assertEqual(reference, "sensor.standalone_temperature")

    def test_plant_device_get_virtual_sensor_reference_no_reference(self):
        """Test that plant device returns None when no reference is available."""
        # Set up plant device with no references
        self.plant_device._use_virtual_sensors = True
        self.plant_device._tent_assignment = None
        self.plant_device._plant_info = {}
        
        # Test getting reference for temperature sensor
        reference = self.plant_device.get_virtual_sensor_reference("temperature")
        
        # Should return None
        self.assertIsNone(reference)


if __name__ == '__main__':
    unittest.main()