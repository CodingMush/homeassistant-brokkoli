"""Integration tests for the add_ph service."""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from homeassistant.core import HomeAssistant, ServiceCall

from custom_components.plant.services import async_setup_services
from custom_components.plant.const import DOMAIN, SERVICE_ADD_PH, DEVICE_TYPE_PLANT


class TestAddPhService:
    """Test add_ph service functionality."""

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
        """Create mock plant device with pH functionality."""
        device = Mock()
        device.entity_id = "plant.test_plant"
        device.device_type = DEVICE_TYPE_PLANT
        
        # Mock pH sensor with async method
        mock_sensor = Mock()
        mock_sensor.async_write_ha_state = AsyncMock()
        mock_sensor.set_manual_value = AsyncMock()
        device.sensor_ph = mock_sensor
        device.ph = mock_sensor  # Alternative attribute name
        
        return device

    @pytest.mark.asyncio
    async def test_add_ph_success(self, mock_hass, mock_plant_device):
        """Test successful pH addition."""
        # Setup service call
        call = Mock(spec=ServiceCall)
        call.data = {
            "entity_id": "plant.test_plant",
            "value": 6.5
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
            if call_args[0][1] == SERVICE_ADD_PH:
                service_func = call_args[0][2]
                break

        assert service_func is not None, "add_ph service not found"
        
        # Call the service
        await service_func(call)
        
        # Verify pH sensor was updated
        mock_plant_device.sensor_ph.set_manual_value.assert_called_once_with(6.5)

    @pytest.mark.asyncio
    async def test_add_ph_success_alternative_attribute(self, mock_hass):
        """Test successful pH addition using alternative attribute name."""
        # Setup service call
        call = Mock(spec=ServiceCall)
        call.data = {
            "entity_id": "plant.test_plant",
            "value": 6.5
        }

        # Create plant device with pH sensor in alternative attribute
        mock_plant_device = Mock()
        mock_plant_device.entity_id = "plant.test_plant"
        mock_plant_device.device_type = DEVICE_TYPE_PLANT
        mock_plant_device.sensor_ph = None  # No sensor_ph attribute
        
        # Mock pH sensor in alternative attribute with async method
        mock_sensor = Mock()
        mock_sensor.async_write_ha_state = AsyncMock()
        mock_sensor.set_manual_value = AsyncMock()
        mock_plant_device.ph = mock_sensor

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
            if call_args[0][1] == SERVICE_ADD_PH:
                service_func = call_args[0][2]
                break

        # Call the service
        await service_func(call)
        
        # Verify pH sensor was updated
        mock_plant_device.ph.set_manual_value.assert_called_once_with(6.5)

    @pytest.mark.asyncio
    async def test_add_ph_no_value(self, mock_hass, mock_plant_device):
        """Test add_ph with no value specified."""
        call = Mock(spec=ServiceCall)
        call.data = {
            "entity_id": "plant.test_plant"
            # No value specified
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
            if call_args[0][1] == SERVICE_ADD_PH:
                service_func = call_args[0][2]
                break

        # Call the service - should return early without error
        await service_func(call)
        
        # Verify no updates were made
        mock_plant_device.sensor_ph.set_manual_value.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_ph_plant_not_found(self, mock_hass):
        """Test add_ph with non-existent plant."""
        call = Mock(spec=ServiceCall)
        call.data = {
            "entity_id": "plant.nonexistent_plant",
            "value": 6.5
        }

        # Setup empty hass.data
        mock_hass.data[DOMAIN] = {}

        # Setup services
        await async_setup_services(mock_hass)

        # Find the service function
        service_func = None
        for call_args in mock_hass.services.async_register.call_args_list:
            if call_args[0][1] == SERVICE_ADD_PH:
                service_func = call_args[0][2]
                break

        # Call the service - should return early without error
        await service_func(call)

    @pytest.mark.asyncio
    async def test_add_ph_no_sensor(self, mock_hass):
        """Test add_ph with plant that has no pH sensor."""
        call = Mock(spec=ServiceCall)
        call.data = {
            "entity_id": "plant.test_plant",
            "value": 6.5
        }

        # Create plant device without pH sensor
        mock_plant_device = Mock()
        mock_plant_device.entity_id = "plant.test_plant"
        mock_plant_device.device_type = DEVICE_TYPE_PLANT
        mock_plant_device.sensor_ph = None
        mock_plant_device.ph = None  # No alternative attribute either

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
            if call_args[0][1] == SERVICE_ADD_PH:
                service_func = call_args[0][2]
                break

        # Call the service - should return early without error
        await service_func(call)