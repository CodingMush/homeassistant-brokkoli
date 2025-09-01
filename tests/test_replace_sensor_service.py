"""Integration tests for the replace_sensor service."""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from custom_components.plant.services import async_setup_services
from custom_components.plant.const import DOMAIN, SERVICE_REPLACE_SENSOR


class TestReplaceSensorService:
    """Test replace_sensor service functionality."""

    @pytest.fixture
    def mock_hass(self):
        """Create mock Home Assistant instance."""
        hass = Mock(spec=HomeAssistant)
        hass.data = {DOMAIN: {}}
        hass.states = Mock()
        hass.services = Mock()
        return hass

    @pytest.mark.asyncio
    async def test_replace_sensor_success(self, mock_hass):
        """Test successful sensor replacement."""
        # Setup mock meter entity
        mock_meter = Mock()
        mock_meter.entity_id = "sensor.test_meter"
        mock_meter.replace_external_sensor = Mock()

        # Setup hass.data with meter
        mock_hass.data[DOMAIN] = {
            "test_entry": {
                "sensors": [mock_meter]
            }
        }

        # Setup mock states
        mock_hass.states.get.return_value = mock_meter

        # Setup service call
        call = Mock(spec=ServiceCall)
        call.data = {
            "meter_entity": "sensor.test_meter",
            "new_sensor": "sensor.new_sensor"
        }

        # Setup mock for new sensor
        mock_new_sensor = Mock()
        mock_new_sensor.entity_id = "sensor.new_sensor"
        mock_hass.states.get.side_effect = [mock_meter, mock_new_sensor]

        # Setup services
        await async_setup_services(mock_hass)

        # Find the service function
        service_func = None
        for call_args in mock_hass.services.async_register.call_args_list:
            if call_args[0][1] == SERVICE_REPLACE_SENSOR:
                service_func = call_args[0][2]
                break

        assert service_func is not None, "replace_sensor service not found"

        # Call the service
        await service_func(call)

        # Verify sensor replacement was called
        mock_meter.replace_external_sensor.assert_called_once_with("sensor.new_sensor")

    @pytest.mark.asyncio
    async def test_replace_sensor_no_meter_entity(self, mock_hass):
        """Test replace_sensor with no meter entity specified."""
        call = Mock(spec=ServiceCall)
        call.data = {
            "new_sensor": "sensor.new_sensor"
        }

        # Setup services
        await async_setup_services(mock_hass)

        # Find the service function
        service_func = None
        for call_args in mock_hass.services.async_register.call_args_list:
            if call_args[0][1] == SERVICE_REPLACE_SENSOR:
                service_func = call_args[0][2]
                break

        # Call the service and expect HomeAssistantError
        with pytest.raises(HomeAssistantError, match="No meter entity specified"):
            await service_func(call)

    @pytest.mark.asyncio
    async def test_replace_sensor_invalid_meter(self, mock_hass):
        """Test replace_sensor with invalid meter entity."""
        call = Mock(spec=ServiceCall)
        call.data = {
            "meter_entity": "sensor.invalid_meter",
            "new_sensor": "sensor.new_sensor"
        }

        # Setup hass.data without the meter
        mock_hass.data[DOMAIN] = {
            "test_entry": {
                "sensors": []
            }
        }

        # Setup services
        await async_setup_services(mock_hass)

        # Find the service function
        service_func = None
        for call_args in mock_hass.services.async_register.call_args_list:
            if call_args[0][1] == SERVICE_REPLACE_SENSOR:
                service_func = call_args[0][2]
                break

        # Call the service and expect HomeAssistantError
        with pytest.raises(HomeAssistantError, match="Entity sensor.invalid_meter not found"):
            await service_func(call)

    @pytest.mark.asyncio
    async def test_replace_sensor_invalid_new_sensor(self, mock_hass):
        """Test replace_sensor with invalid new sensor entity."""
        # Setup mock meter entity
        mock_meter = Mock()
        mock_meter.entity_id = "sensor.test_meter"

        # Setup hass.data with meter
        mock_hass.data[DOMAIN] = {
            "test_entry": {
                "sensors": [mock_meter]
            }
        }

        # Setup mock states
        mock_hass.states.get.return_value = mock_meter

        call = Mock(spec=ServiceCall)
        call.data = {
            "meter_entity": "sensor.test_meter",
            "new_sensor": "invalid_entity"
        }

        # Setup services
        await async_setup_services(mock_hass)

        # Find the service function
        service_func = None
        for call_args in mock_hass.services.async_register.call_args_list:
            if call_args[0][1] == SERVICE_REPLACE_SENSOR:
                service_func = call_args[0][2]
                break

        # Call the service and expect HomeAssistantError
        with pytest.raises(HomeAssistantError, match="invalid_entity is not a valid sensor entity"):
            await service_func(call)

    @pytest.mark.asyncio
    async def test_replace_sensor_new_sensor_not_found(self, mock_hass):
        """Test replace_sensor with new sensor that doesn't exist."""
        # Setup mock meter entity
        mock_meter = Mock()
        mock_meter.entity_id = "sensor.test_meter"

        # Setup hass.data with meter
        mock_hass.data[DOMAIN] = {
            "test_entry": {
                "sensors": [mock_meter]
            }
        }

        # Setup mock states - meter exists but new sensor doesn't
        mock_hass.states.get.side_effect = [mock_meter, None]

        call = Mock(spec=ServiceCall)
        call.data = {
            "meter_entity": "sensor.test_meter",
            "new_sensor": "sensor.nonexistent"
        }

        # Setup services
        await async_setup_services(mock_hass)

        # Find the service function
        service_func = None
        for call_args in mock_hass.services.async_register.call_args_list:
            if call_args[0][1] == SERVICE_REPLACE_SENSOR:
                service_func = call_args[0][2]
                break

        # Call the service and expect HomeAssistantError
        with pytest.raises(HomeAssistantError, match="New sensor entity sensor.nonexistent not found"):
            await service_func(call)