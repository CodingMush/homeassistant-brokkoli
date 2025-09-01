"""Integration tests for the create_plant service."""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.config_entries import ConfigEntry

from custom_components.plant.services import async_setup_services
from homeassistant.const import ATTR_NAME
from custom_components.plant.const import (
    DOMAIN, SERVICE_CREATE_PLANT, ATTR_STRAIN, 
    FLOW_PLANT_INFO, DEVICE_TYPE_PLANT
)


class TestCreatePlantService:
    """Test create_plant service functionality."""

    @pytest.fixture
    def mock_hass(self):
        """Create mock Home Assistant instance."""
        hass = Mock(spec=HomeAssistant)
        hass.data = {DOMAIN: {}}
        hass.states = Mock()
        hass.services = Mock()
        hass.config_entries = Mock()
        # Fix: Make async_entries return an empty list instead of being a plain Mock
        hass.config_entries.async_entries = Mock(return_value=[])
        # Fix: Add config attribute with components
        hass.config = Mock()
        hass.config.components = set()
        # Fix: Add config_dir attribute
        hass.config.config_dir = "/config"
        # Fix: Add bus attribute
        hass.bus = Mock()
        hass.bus.async_listen = Mock()
        return hass

    @pytest.mark.asyncio
    async def test_create_plant_success(self, mock_hass):
        """Test successful plant creation."""
        # Setup service call
        call = Mock(spec=ServiceCall)
        call.data = {
            ATTR_NAME: "Test Plant",
            ATTR_STRAIN: "Test Strain",
            "breeder": "Test Breeder"
        }

        # Setup mock config entry flow
        mock_result = {
            "type": "create_entry",
            "result": Mock(entry_id="test_entry_id")
        }
        mock_hass.config_entries.flow.async_init = AsyncMock(return_value=mock_result)

        # Setup services
        await async_setup_services(mock_hass)

        # Call the service
        service_func = None
        for call_args in mock_hass.services.async_register.call_args_list:
            if call_args[0][1] == SERVICE_CREATE_PLANT:
                service_func = call_args[0][2]
                break

        assert service_func is not None, "create_plant service not found"
        
        response = await service_func(call)
        
        # Verify config entry flow was called
        mock_hass.config_entries.flow.async_init.assert_called_once()
        assert response["entity_id"] == "test_entry_id"

    @pytest.mark.asyncio
    async def test_create_plant_missing_name(self, mock_hass):
        """Test create_plant with missing name."""
        call = Mock(spec=ServiceCall)
        call.data = {
            ATTR_STRAIN: "Test Strain"
        }

        # Setup services
        await async_setup_services(mock_hass)

        # Find the service function
        service_func = None
        for call_args in mock_hass.services.async_register.call_args_list:
            if call_args[0][1] == SERVICE_CREATE_PLANT:
                service_func = call_args[0][2]
                break

        # Call the service and expect HomeAssistantError
        with pytest.raises(HomeAssistantError, match="Plant name is required"):
            await service_func(call)

    @pytest.mark.asyncio
    async def test_create_plant_missing_strain(self, mock_hass):
        """Test create_plant with missing strain."""
        call = Mock(spec=ServiceCall)
        call.data = {
            ATTR_NAME: "Test Plant"
        }

        # Setup services
        await async_setup_services(mock_hass)

        # Find the service function
        service_func = None
        for call_args in mock_hass.services.async_register.call_args_list:
            if call_args[0][1] == SERVICE_CREATE_PLANT:
                service_func = call_args[0][2]
                break

        # Call the service and expect HomeAssistantError
        with pytest.raises(HomeAssistantError, match="Plant strain is required"):
            await service_func(call)

    @pytest.mark.asyncio
    async def test_create_plant_invalid_sensor(self, mock_hass):
        """Test create_plant with invalid sensor entity."""
        call = Mock(spec=ServiceCall)
        call.data = {
            ATTR_NAME: "Test Plant",
            ATTR_STRAIN: "Test Strain",
            "temperature_sensor": "invalid_sensor"
        }

        # Setup services
        await async_setup_services(mock_hass)

        # Find the service function
        service_func = None
        for call_args in mock_hass.services.async_register.call_args_list:
            if call_args[0][1] == SERVICE_CREATE_PLANT:
                service_func = call_args[0][2]
                break

        # Call the service and expect HomeAssistantError
        with pytest.raises(HomeAssistantError, match="Invalid sensor entity ID"):
            await service_func(call)