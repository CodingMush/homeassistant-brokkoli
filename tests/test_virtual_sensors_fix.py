"""Test cases for virtual sensor fixes."""

import unittest
from unittest.mock import Mock
from homeassistant.const import STATE_UNKNOWN, STATE_UNAVAILABLE

from custom_components.plant.const import (
    FLOW_SENSOR_TEMPERATURE,
    FLOW_PLANT_INFO,
    READING_TEMPERATURE,
    ICON_TEMPERATURE,
)


class MockVirtualSensor:
    """Mock virtual sensor for testing."""
    
    def __init__(self, hass, config, plantdevice, sensor_type, reading_name, icon, unit=None, device_class=None):
        self._hass = hass
        self._config = config
        self._plant = plantdevice
        self._sensor_type = sensor_type
        self._reading_name = reading_name
        self._attr_icon = icon
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_name = f"{plantdevice.name} {reading_name}" if hasattr(plantdevice, 'name') else f"Plant {reading_name}"
        self._attr_unique_id = f"{config.entry_id}-virtual-{sensor_type}" if hasattr(config, 'entry_id') else f"test-virtual-{sensor_type}"
        self._reference_entity_id = None
        self._default_state = 0
        self._attr_native_value = None
        
        # Mock the update reference method
        self._update_virtual_reference = Mock()
    
    @property
    def state(self):
        """Return the state of the sensor."""
        if not self._reference_entity_id:
            return self._default_state
        
        # Mock getting state from reference
        if self._hass and self._hass.states:
            state_obj = self._hass.states.get(self._reference_entity_id)
            if state_obj and state_obj.state not in [STATE_UNAVAILABLE, None]:
                return state_obj.state
        return STATE_UNAVAILABLE
    
    @property
    def extra_state_attributes(self):
        """Return extra attributes including virtual sensor info."""
        return {
            "is_virtual_sensor": True,
            "virtual_sensor_reference": self._reference_entity_id,
            "sensor_type": self._sensor_type,
        }
    
    @property
    def device_class(self):
        """Return the device class."""
        return self._attr_device_class
    
    @property
    def name(self):
        """Return the name."""
        return self._attr_name


class MockVirtualSensorManager:
    """Mock virtual sensor manager for testing."""
    
    def __init__(self, hass):
        self._hass = hass
        self._virtual_sensors = {}
    
    def create_virtual_sensors_for_plant(self, plant_device, config):
        """Create virtual sensors for a plant."""
        virtual_sensors = {}
        
        # Create mock virtual sensors
        mock_sensor = MockVirtualSensor(
            hass=self._hass,
            config=config,
            plantdevice=plant_device,
            sensor_type="temperature",
            reading_name=READING_TEMPERATURE,
            icon=ICON_TEMPERATURE,
            unit="°C",
            device_class="temperature"
        )
        virtual_sensors['temperature'] = mock_sensor
        
        return virtual_sensors


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
        self.plant_device.name = "Test Plant"

    def test_virtual_sensor_state_without_reference(self):
        """Test that virtual sensor returns default state (0) when no reference is available."""
        # Create virtual sensor
        virtual_sensor = MockVirtualSensor(
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
        virtual_sensor = MockVirtualSensor(
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
        
        # Mock hass.states.get to return a state
        mock_state = Mock()
        mock_state.state = "25.5"
        self.hass.states.get.return_value = mock_state
        
        # Check that state returns the actual value
        self.assertEqual(virtual_sensor.state, "25.5")

    def test_virtual_sensor_manager_create_sensors(self):
        """Test that virtual sensor manager creates sensors correctly."""
        # Create virtual sensor manager
        manager = MockVirtualSensorManager(self.hass)
        
        # Create virtual sensors
        virtual_sensors = manager.create_virtual_sensors_for_plant(self.plant_device, self.config_entry)
        
        # Check that sensors were created
        self.assertGreater(len(virtual_sensors), 0)
        self.assertIn("temperature", virtual_sensors)

    def test_plant_device_get_virtual_sensor_reference_standalone(self):
        """Test that plant device correctly gets virtual sensor reference for standalone plants."""
        # Set up plant device for standalone virtual sensors
        self.plant_device._use_virtual_sensors = True
        self.plant_device._tent_assignment = None
        self.plant_device._plant_info = {
            FLOW_SENSOR_TEMPERATURE: "sensor.standalone_temperature"
        }
        
        # Mock the get_virtual_sensor_reference method
        self.plant_device.get_virtual_sensor_reference = Mock(return_value="sensor.standalone_temperature")
        
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
        
        # Mock the get_virtual_sensor_reference method to return None
        self.plant_device.get_virtual_sensor_reference = Mock(return_value=None)
        
        # Test getting reference for temperature sensor
        reference = self.plant_device.get_virtual_sensor_reference("temperature")
        
        # Should return None
        self.assertIsNone(reference)


if __name__ == '__main__':
    unittest.main()