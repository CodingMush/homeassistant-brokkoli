"""Integration tests for the remove_cycle service."""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from custom_components.plant.services import async_setup_services
from custom_components.plant.const import DOMAIN, SERVICE_REMOVE_CYCLE, DEVICE_TYPE_CYCLE


class TestRemoveCycleService:
    """Test remove_cycle service functionality."""

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
    def mock_cycle_device(self):
        """Create mock cycle device."""
        device = Mock()
        device.entity_id = "cycle.test_cycle"
        device.device_type = DEVICE_TYPE_CYCLE
        return device

    @pytest.mark.asyncio
    async def test_remove_cycle_success(self, mock_hass, mock_cycle_device):
        """Test successful cycle removal."""
        # Setup service call
        call = Mock(spec=ServiceCall)
        call.data = {
            "cycle_entity": "cycle.test_cycle"
        }

        # Setup hass.data with cycle
        mock_hass.data[DOMAIN] = {
            "test_entry_id": {
                "plant": mock_cycle_device
            }
        }

        # Setup config entries mock
        mock_hass.config_entries.async_remove = AsyncMock()

        # Setup services
        await async_setup_services(mock_hass)

        # Find the service function
        service_func = None
        for call_args in mock_hass.services.async_register.call_args_list:
            if call_args[0][1] == SERVICE_REMOVE_CYCLE:
                service_func = call_args[0][2]
                break

        assert service_func is not None, "remove_cycle service not found"

        # Call the service
        result = await service_func(call)

        # Verify config entry removal was called
        mock_hass.config_entries.async_remove.assert_called_once_with("test_entry_id")

    @pytest.mark.asyncio
    async def test_remove_cycle_not_found(self, mock_hass):
        """Test remove_cycle with non-existent cycle."""
        call = Mock(spec=ServiceCall)
        call.data = {
            "cycle_entity": "cycle.nonexistent_cycle"
        }

        # Setup empty hass.data
        mock_hass.data[DOMAIN] = {}

        # Setup services
        await async_setup_services(mock_hass)

        # Find the service function
        service_func = None
        for call_args in mock_hass.services.async_register.call_args_list:
            if call_args[0][1] == SERVICE_REMOVE_CYCLE:
                service_func = call_args[0][2]
                break

        # Call the service - should return False
        result = await service_func(call)
        assert result is False

    @pytest.mark.asyncio
    async def test_remove_cycle_missing_entity(self, mock_hass):
        """Test remove_cycle with missing cycle entity."""
        call = Mock(spec=ServiceCall)
        call.data = {}

        # Setup services
        await async_setup_services(mock_hass)

        # Find the service function
        service_func = None
        for call_args in mock_hass.services.async_register.call_args_list:
            if call_args[0][1] == SERVICE_REMOVE_CYCLE:
                service_func = call_args[0][2]
                break

        # Call the service - should return False
        result = await service_func(call)
        assert result is False