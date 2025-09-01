"""Integration tests for the add_conductivity service."""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from homeassistant.core import HomeAssistant, ServiceCall

from custom_components.plant.services import async_setup_services
from custom_components.plant.const import DOMAIN, SERVICE_ADD_CONDUCTIVITY, DEVICE_TYPE_PLANT


class TestAddConductivityService:
    """Test add_conductivity service functionality."""

    @pytest.fixture
    def mock_hass(self):
        """Create mock Home Assistant instance."""
        hass = Mock(spec=HomeAssistant)
        hass.data = {DOMAIN: {}}
        hass.states = Mock()
        hass.services = Mock()
        return hass

    @pytest.fixture
    def mock_plant_device(self):
        """Create mock plant device with conductivity functionality."""
        device = Mock()
        device.entity_id = "plant.test_plant"
        device.device_type = DEVICE_TYPE_PLANT
        
        # Mock conductivity sensor with async method
        mock_sensor = Mock()
        mock_sensor.set_manual_value = AsyncMock()
        mock_sensor.async_write_ha_state = Mock()
        device.sensor_conductivity = mock_sensor
        
        return device

    @pytest.mark.asyncio
    async def test_add_conductivity_success(self, mock_hass, mock_plant_device):
        """Test successful conductivity addition."""
        # Setup service call
        call = Mock(spec=ServiceCall)
        call.data = {
            "entity_id": "plant.test_plant",
            "value_us_cm": 1200.5
        }

        # Setup hass.data with plant
        mock_hass.data[DOMAIN] = {
            "test_entry_id": {
                "plant": mock_plant_device
            }
        }

        # Setup services
        await async_setup_services(mock_hass)

        # Find the service function
        service_func = None
        for call_args in mock_hass.services.async_register.call_args_list:
            if call_args[0][1] == SERVICE_ADD_CONDUCTIVITY:
                service_func = call_args[0][2]
                break

        assert service_func is not None, "add_conductivity service not found"
        
        # Call the service
        await service_func(call)
        
        # Verify conductivity sensor was updated
        mock_plant_device.sensor_conductivity.set_manual_value.assert_called_once_with(1200.5)

    @pytest.mark.asyncio
    async def test_add_conductivity_no_value(self, mock_hass, mock_plant_device):
        """Test add_conductivity with no value specified."""
        call = Mock(spec=ServiceCall)
        call.data = {
            "entity_id": "plant.test_plant"
            # No value_us_cm specified
        }

        # Setup hass.data with plant
        mock_hass.data[DOMAIN] = {
            "test_entry_id": {
                "plant": mock_plant_device
            }
        }

        # Setup services
        await async_setup_services(mock_hass)

        # Find the service function
        service_func = None
        for call_args in mock_hass.services.async_register.call_args_list:
            if call_args[0][1] == SERVICE_ADD_CONDUCTIVITY:
                service_func = call_args[0][2]
                break

        # Call the service - should return early without error
        await service_func(call)
        
        # Verify no updates were made
        mock_plant_device.sensor_conductivity.set_manual_value.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_conductivity_plant_not_found(self, mock_hass):
        """Test add_conductivity with non-existent plant."""
        call = Mock(spec=ServiceCall)
        call.data = {
            "entity_id": "plant.nonexistent_plant",
            "value_us_cm": 1200.5
        }

        # Setup empty hass.data
        mock_hass.data[DOMAIN] = {}

        # Setup services
        await async_setup_services(mock_hass)

        # Find the service function
        service_func = None
        for call_args in mock_hass.services.async_register.call_args_list:
            if call_args[0][1] == SERVICE_ADD_CONDUCTIVITY:
                service_func = call_args[0][2]
                break

        # Call the service - should return early without error
        await service_func(call)

    @pytest.mark.asyncio
    async def test_add_conductivity_no_sensor(self, mock_hass):
        """Test add_conductivity with plant that has no conductivity sensor."""
        call = Mock(spec=ServiceCall)
        call.data = {
            "entity_id": "plant.test_plant",
            "value_us_cm": 1200.5
        }

        # Create plant device without conductivity sensor
        mock_plant_device = Mock()
        mock_plant_device.entity_id = "plant.test_plant"
        mock_plant_device.device_type = DEVICE_TYPE_PLANT
        mock_plant_device.sensor_conductivity = None

        # Setup hass.data with plant
        mock_hass.data[DOMAIN] = {
            "test_entry_id": {
                "plant": mock_plant_device
            }
        }

        # Setup services
        await async_setup_services(mock_hass)

        # Find the service function
        service_func = None
        for call_args in mock_hass.services.async_register.call_args_list:
            if call_args[0][1] == SERVICE_ADD_CONDUCTIVITY:
                service_func = call_args[0][2]
                break

        # Call the service - should return early without error
        await service_func(call)