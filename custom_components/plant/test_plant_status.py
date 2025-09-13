"""Test for plant status management."""

import pytest
import logging
from unittest.mock import Mock, patch, MagicMock
from datetime import timedelta

from homeassistant.const import STATE_OK, STATE_PROBLEM, STATE_UNKNOWN, STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from custom_components.plant import PlantDevice
from custom_components.plant.const import (
    FLOW_PLANT_INFO,
    ATTR_NAME,
    ATTR_DEVICE_TYPE,
    DEVICE_TYPE_PLANT,
    STATE_LOW,
    STATE_HIGH,
)

_LOGGER = logging.getLogger(__name__)


class TestPlantStatus:
    """Test plant status management."""

    @pytest.fixture
    def hass(self):
        """Fixture for Home Assistant instance."""
        return Mock(spec=HomeAssistant)

    @pytest.fixture
    def config_entry(self):
        """Fixture for config entry."""
        config = Mock(spec=ConfigEntry)
        config.data = {
            FLOW_PLANT_INFO: {
                ATTR_NAME: "Test Plant",
                ATTR_DEVICE_TYPE: DEVICE_TYPE_PLANT,
            }
        }
        config.options = {}
        config.entry_id = "test_entry_id"
        return config

    @pytest.fixture
    def plant_device(self, hass, config_entry):
        """Fixture for plant device."""
        with patch("custom_components.plant.PlantDevice._schedule_regular_updates"):
            plant = PlantDevice(hass, config_entry)
        return plant

    def test_initial_state_unknown(self, plant_device):
        """Test that plant starts with UNKNOWN state."""
        assert plant_device.state == STATE_UNKNOWN

    def test_update_with_no_sensors(self, plant_device):
        """Test update with no sensors configured."""
        plant_device.update()
        assert plant_device.state == STATE_UNKNOWN

    def test_update_with_valid_temperature_sensor(self, plant_device):
        """Test update with valid temperature sensor within range."""
        # Setup mock temperature sensor
        temp_sensor = Mock()
        temp_sensor.state = "25.0"
        plant_device.sensor_temperature = temp_sensor

        # Setup temperature thresholds
        min_temp = Mock()
        min_temp.native_value = "10.0"
        plant_device.min_temperature = min_temp

        max_temp = Mock()
        max_temp.native_value = "30.0"
        plant_device.max_temperature = max_temp

        # Update plant status
        plant_device.update()

        # Verify results
        assert plant_device.state == STATE_OK
        assert plant_device.temperature_status == STATE_OK

    def test_update_with_low_temperature_sensor(self, plant_device):
        """Test update with temperature sensor below minimum."""
        # Setup mock temperature sensor
        temp_sensor = Mock()
        temp_sensor.state = "5.0"  # Below minimum
        plant_device.sensor_temperature = temp_sensor

        # Setup temperature thresholds
        min_temp = Mock()
        min_temp.native_value = "10.0"
        plant_device.min_temperature = min_temp

        max_temp = Mock()
        max_temp.native_value = "30.0"
        plant_device.max_temperature = max_temp

        # Update plant status
        plant_device.update()

        # Verify results
        assert plant_device.state == STATE_PROBLEM
        assert plant_device.temperature_status == STATE_LOW

    def test_update_with_high_temperature_sensor(self, plant_device):
        """Test update with temperature sensor above maximum."""
        # Setup mock temperature sensor
        temp_sensor = Mock()
        temp_sensor.state = "35.0"  # Above maximum
        plant_device.sensor_temperature = temp_sensor

        # Setup temperature thresholds
        min_temp = Mock()
        min_temp.native_value = "10.0"
        plant_device.min_temperature = min_temp

        max_temp = Mock()
        max_temp.native_value = "30.0"
        plant_device.max_temperature = max_temp

        # Update plant status
        plant_device.update()

        # Verify results
        assert plant_device.state == STATE_PROBLEM
        assert plant_device.temperature_status == STATE_HIGH

    def test_update_with_unavailable_temperature_sensor(self, plant_device):
        """Test update with unavailable temperature sensor."""
        # Setup mock temperature sensor
        temp_sensor = Mock()
        temp_sensor.state = STATE_UNAVAILABLE
        plant_device.sensor_temperature = temp_sensor

        # Setup temperature thresholds
        min_temp = Mock()
        min_temp.native_value = "10.0"
        plant_device.min_temperature = min_temp

        max_temp = Mock()
        max_temp.native_value = "30.0"
        plant_device.max_temperature = max_temp

        # Update plant status
        plant_device.update()

        # Verify results
        assert plant_device.state == STATE_UNKNOWN

    def test_update_with_invalid_temperature_value(self, plant_device):
        """Test update with invalid temperature value."""
        # Setup mock temperature sensor
        temp_sensor = Mock()
        temp_sensor.state = "invalid"
        plant_device.sensor_temperature = temp_sensor

        # Setup temperature thresholds
        min_temp = Mock()
        min_temp.native_value = "10.0"
        plant_device.min_temperature = min_temp

        max_temp = Mock()
        max_temp.native_value = "30.0"
        plant_device.max_temperature = max_temp

        # Update plant status
        plant_device.update()

        # Verify results (should remain UNKNOWN due to invalid value)
        assert plant_device.state == STATE_UNKNOWN

    def test_update_with_multiple_sensors_all_ok(self, plant_device):
        """Test update with multiple sensors all within range."""
        # Setup mock temperature sensor
        temp_sensor = Mock()
        temp_sensor.state = "25.0"
        plant_device.sensor_temperature = temp_sensor

        # Setup temperature thresholds
        min_temp = Mock()
        min_temp.native_value = "10.0"
        plant_device.min_temperature = min_temp

        max_temp = Mock()
        max_temp.native_value = "30.0"
        plant_device.max_temperature = max_temp

        # Setup mock humidity sensor
        humidity_sensor = Mock()
        humidity_sensor.state = "50.0"
        plant_device.sensor_humidity = humidity_sensor

        # Setup humidity thresholds
        min_humidity = Mock()
        min_humidity.native_value = "40.0"
        plant_device.min_humidity = min_humidity

        max_humidity = Mock()
        max_humidity.native_value = "60.0"
        plant_device.max_humidity = max_humidity

        # Update plant status
        plant_device.update()

        # Verify results
        assert plant_device.state == STATE_OK
        assert plant_device.temperature_status == STATE_OK
        assert plant_device.humidity_status == STATE_OK

    def test_update_with_multiple_sensors_one_problem(self, plant_device):
        """Test update with multiple sensors where one is problematic."""
        # Setup mock temperature sensor (OK)
        temp_sensor = Mock()
        temp_sensor.state = "25.0"
        plant_device.sensor_temperature = temp_sensor

        # Setup temperature thresholds
        min_temp = Mock()
        min_temp.native_value = "10.0"
        plant_device.min_temperature = min_temp

        max_temp = Mock()
        max_temp.native_value = "30.0"
        plant_device.max_temperature = max_temp

        # Setup mock humidity sensor (Problem - too high)
        humidity_sensor = Mock()
        humidity_sensor.state = "70.0"
        plant_device.sensor_humidity = humidity_sensor

        # Setup humidity thresholds
        min_humidity = Mock()
        min_humidity.native_value = "40.0"
        plant_device.min_humidity = min_humidity

        max_humidity = Mock()
        max_humidity.native_value = "60.0"
        plant_device.max_humidity = max_humidity

        # Update plant status
        plant_device.update()

        # Verify results
        assert plant_device.state == STATE_PROBLEM
        assert plant_device.temperature_status == STATE_OK
        assert plant_device.humidity_status == STATE_HIGH

    def test_update_with_disabled_temperature_trigger(self, plant_device):
        """Test update with temperature trigger disabled."""
        # Setup config to disable temperature trigger
        plant_device._config.options = {"temperature_trigger": False}

        # Setup mock temperature sensor (Problematic value)
        temp_sensor = Mock()
        temp_sensor.state = "5.0"  # Below minimum
        plant_device.sensor_temperature = temp_sensor

        # Setup temperature thresholds
        min_temp = Mock()
        min_temp.native_value = "10.0"
        plant_device.min_temperature = min_temp

        max_temp = Mock()
        max_temp.native_value = "30.0"
        plant_device.max_temperature = max_temp

        # Update plant status
        plant_device.update()

        # Verify results - should be OK because trigger is disabled
        assert plant_device.state == STATE_OK
        assert plant_device.temperature_status == STATE_LOW  # Status still set, but doesn't affect overall state

    def test_update_with_ph_sensor(self, plant_device):
        """Test update with pH sensor."""
        # Setup mock pH sensor
        ph_sensor = Mock()
        ph_sensor.state = "6.5"
        plant_device.sensor_ph = ph_sensor

        # Setup pH thresholds
        min_ph = Mock()
        min_ph.native_value = "5.5"
        plant_device.min_ph = min_ph

        max_ph = Mock()
        max_ph.native_value = "7.5"
        plant_device.max_ph = max_ph

        # Update plant status
        plant_device.update()

        # Verify results
        assert plant_device.state == STATE_OK
        assert plant_device.ph_status == STATE_OK

    def test_update_with_low_ph_sensor(self, plant_device):
        """Test update with pH sensor below minimum."""
        # Setup mock pH sensor
        ph_sensor = Mock()
        ph_sensor.state = "5.0"  # Below minimum
        plant_device.sensor_ph = ph_sensor

        # Setup pH thresholds
        min_ph = Mock()
        min_ph.native_value = "5.5"
        plant_device.min_ph = min_ph

        max_ph = Mock()
        max_ph.native_value = "7.5"
        plant_device.max_ph = max_ph

        # Update plant status
        plant_device.update()

        # Verify results
        assert plant_device.state == STATE_PROBLEM
        assert plant_device.ph_status == STATE_LOW

    def test_update_with_high_ph_sensor(self, plant_device):
        """Test update with pH sensor above maximum."""
        # Setup mock pH sensor
        ph_sensor = Mock()
        ph_sensor.state = "8.0"  # Above maximum
        plant_device.sensor_ph = ph_sensor

        # Setup pH thresholds
        min_ph = Mock()
        min_ph.native_value = "5.5"
        plant_device.min_ph = min_ph

        max_ph = Mock()
        max_ph.native_value = "7.5"
        plant_device.max_ph = max_ph

        # Update plant status
        plant_device.update()

        # Verify results
        assert plant_device.state == STATE_PROBLEM
        assert plant_device.ph_status == STATE_HIGH

    def test_update_with_disabled_ph_trigger(self, plant_device):
        """Test update with pH trigger disabled."""
        # Setup config to disable pH trigger
        plant_device._config.options = {"ph_trigger": False}

        # Setup mock pH sensor (Problematic value)
        ph_sensor = Mock()
        ph_sensor.state = "5.0"  # Below minimum
        plant_device.sensor_ph = ph_sensor

        # Setup pH thresholds
        min_ph = Mock()
        min_ph.native_value = "5.5"
        plant_device.min_ph = min_ph

        max_ph = Mock()
        max_ph.native_value = "7.5"
        plant_device.max_ph = max_ph

        # Update plant status
        plant_device.update()

        # Verify results - should be OK because trigger is disabled
        assert plant_device.state == STATE_OK
        assert plant_device.ph_status == STATE_LOW  # Status still set, but doesn't affect overall state

    def test_schedule_regular_updates(self, plant_device, hass):
        """Test that regular updates are scheduled."""
        with patch("custom_components.plant.async_track_time_interval") as mock_track:
            plant_device._schedule_regular_updates()
            
            # Verify that async_track_time_interval was called
            mock_track.assert_called_once()
            
            # Verify the interval is 30 seconds
            args = mock_track.call_args
            assert args[0][2] == timedelta(seconds=30)

if __name__ == "__main__":
    pytest.main([__file__])