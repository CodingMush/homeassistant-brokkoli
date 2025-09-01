"""Integration tests for the remove_plant service."""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
import homeassistant.helpers.device_registry as dr

from custom_components.plant.services import async_setup_services
from custom_components.plant.const import DOMAIN, SERVICE_REMOVE_PLANT, DEVICE_TYPE_PLANT


class TestRemovePlantService:
    """Test remove_plant service functionality."""

    @pytest.fixture
    def mock_hass(self):
        """Create mock Home Assistant instance."""
        hass = Mock(spec=HomeAssistant)
        hass.data = {DOMAIN: {}}
        hass.states = Mock()
        hass.services = Mock()
        hass.config_entries = Mock()
        return hass

    @pytest.fixture
    def mock_plant_device(self):
        """Create mock plant device."""
        device = Mock()
        device.entity_id = "plant.test_plant"
        device.device_type = DEVICE_TYPE_PLANT
        device.unique_id = "test_unique_id"
        return device

    @pytest.mark.asyncio
    async def test_remove_plant_success(self, mock_hass, mock_plant_device):
        """Test successful plant removal."""
        # Setup service call
        call = Mock(spec=ServiceCall)
        call.data = {
            "plant_entity": "plant.test_plant"
        }

        # Setup hass.data with plant
        mock_hass.data[DOMAIN] = {
            "test_entry_id": {
                "plant": mock_plant_device
            }
        }

        # Setup mock device registry
        mock_device_registry = Mock()
        mock_device = Mock()
        mock_device.identifiers = {(DOMAIN, "test_unique_id")}
        mock_device.via_device_id = None
        mock_device_registry.async_get_device.return_value = mock_device
        mock_device_registry.devices.values.return_value = []
        
        with patch('custom_components.plant.services.dr.async_get', return_value=mock_device_registry):
            # Setup config entries mock
            mock_hass.config_entries.async_remove = AsyncMock()
            
            # Setup services
            await async_setup_services(mock_hass)

            # Find the service function
            service_func = None
            for call_args in mock_hass.services.async_register.call_args_list:
                if call_args[0][1] == SERVICE_REMOVE_PLANT:
                    service_func = call_args[0][2]
                    break

            assert service_func is not None, "remove_plant service not found"
            
            # Call the service
            result = await service_func(call)
            
            # Verify config entry removal was called
            mock_hass.config_entries.async_remove.assert_called_once_with("test_entry_id")
            assert result is True

    @pytest.mark.asyncio
    async def test_remove_plant_not_found(self, mock_hass):
        """Test remove_plant with non-existent plant."""
        call = Mock(spec=ServiceCall)
        call.data = {
            "plant_entity": "plant.nonexistent_plant"
        }

        # Setup empty hass.data
        mock_hass.data[DOMAIN] = {}

        # Setup services
        await async_setup_services(mock_hass)

        # Find the service function
        service_func = None
        for call_args in mock_hass.services.async_register.call_args_list:
            if call_args[0][1] == SERVICE_REMOVE_PLANT:
                service_func = call_args[0][2]
                break

        # Call the service and expect HomeAssistantError
        with pytest.raises(HomeAssistantError, match="Plant entity plant.nonexistent_plant not found"):
            await service_func(call)

    @pytest.mark.asyncio
    async def test_remove_plant_missing_entity(self, mock_hass):
        """Test remove_plant with missing plant entity."""
        call = Mock(spec=ServiceCall)
        call.data = {}

        # Setup services
        await async_setup_services(mock_hass)

        # Find the service function
        service_func = None
        for call_args in mock_hass.services.async_register.call_args_list:
            if call_args[0][1] == SERVICE_REMOVE_PLANT:
                service_func = call_args[0][2]
                break

        # Call the service and expect HomeAssistantError
        with pytest.raises(HomeAssistantError, match="No plant entity specified"):
            await service_func(call)