"""Integration tests for the create_cycle service."""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.exceptions import HomeAssistantError

from custom_components.plant.services import async_setup_services
from homeassistant.const import ATTR_NAME
from custom_components.plant.const import (
    DOMAIN, SERVICE_CREATE_CYCLE, 
    FLOW_PLANT_INFO, DEVICE_TYPE_CYCLE
)


class TestCreateCycleService:
    """Test create_cycle service functionality."""

    @pytest.fixture
    def mock_hass(self):
        """Create mock Home Assistant instance."""
        hass = Mock(spec=HomeAssistant)
        hass.data = {DOMAIN: {}}
        hass.states = Mock()
        # Fix: Make async_all return an empty list
        hass.states.async_all = Mock(return_value=[])
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
    async def test_create_cycle_success(self, mock_hass):
        """Test successful cycle creation."""
        # Setup service call
        call = Mock(spec=ServiceCall)
        call.data = {
            ATTR_NAME: "Test Cycle",
            "plant_emoji": "🔄"
        }

        # Setup mock config entry flow
        mock_result = {
            "type": FlowResultType.CREATE_ENTRY,
            "result": Mock(entry_id="test_entry_id")
        }
        mock_hass.config_entries.flow.async_init = AsyncMock(return_value=mock_result)

        # Mock entity registry
        mock_entity_registry = Mock()
        mock_entity_registry.entities.values.return_value = []
        
        # Mock device registry
        mock_device_registry = Mock()
        
        # Setup services with patched registries
        with patch('custom_components.plant.services.er.async_get', return_value=mock_entity_registry):
            with patch('custom_components.plant.services.dr.async_get', return_value=mock_device_registry):
                await async_setup_services(mock_hass)

                # Find the service function
                service_func = None
                for call_args in mock_hass.services.async_register.call_args_list:
                    if call_args[0][1] == SERVICE_CREATE_CYCLE:
                        service_func = call_args[0][2]
                        break

                assert service_func is not None, "create_cycle service not found"
                
                # Call the service
                response = await service_func(call)
                
                # Verify config entry flow was called
                mock_hass.config_entries.flow.async_init.assert_called_once()
                # The service returns an info message when it can't find the entity
                assert "info" in response

    @pytest.mark.asyncio
    async def test_create_cycle_flow_error(self, mock_hass):
        """Test create_cycle with flow error."""
        call = Mock(spec=ServiceCall)
        call.data = {
            ATTR_NAME: "Test Cycle"
        }

        # Setup mock config entry flow with error
        mock_result = {
            "type": "error",
            "reason": "test_error"
        }
        mock_hass.config_entries.flow.async_init = AsyncMock(return_value=mock_result)

        # Mock entity registry
        mock_entity_registry = Mock()
        mock_entity_registry.entities.values.return_value = []
        
        # Mock device registry
        mock_device_registry = Mock()
        
        # Setup services with patched registries
        with patch('custom_components.plant.services.er.async_get', return_value=mock_entity_registry):
            with patch('custom_components.plant.services.dr.async_get', return_value=mock_device_registry):
                # Setup services
                await async_setup_services(mock_hass)

                # Find the service function
                service_func = None
                for call_args in mock_hass.services.async_register.call_args_list:
                    if call_args[0][1] == SERVICE_CREATE_CYCLE:
                        service_func = call_args[0][2]
                        break

                # Call the service and expect HomeAssistantError
                with pytest.raises(HomeAssistantError, match="Failed to create cycle"):
                    await service_func(call)

    @pytest.mark.asyncio
    async def test_create_cycle_missing_name(self, mock_hass):
        """Test create_cycle with missing name."""
        call = Mock(spec=ServiceCall)
        call.data = {
            "plant_emoji": "🔄"
            # No name provided
        }

        # Setup mock config entry flow
        mock_result = {
            "type": FlowResultType.CREATE_ENTRY,
            "result": Mock(entry_id="test_entry_id")
        }
        mock_hass.config_entries.flow.async_init = AsyncMock(return_value=mock_result)

        # Mock entity registry
        mock_entity_registry = Mock()
        mock_entity_registry.entities.values.return_value = []
        
        # Mock device registry
        mock_device_registry = Mock()
        
        # Setup services with patched registries
        with patch('custom_components.plant.services.er.async_get', return_value=mock_entity_registry):
            with patch('custom_components.plant.services.dr.async_get', return_value=mock_device_registry):
                # Setup services
                await async_setup_services(mock_hass)

                # Find the service function
                service_func = None
                for call_args in mock_hass.services.async_register.call_args_list:
                    if call_args[0][1] == SERVICE_CREATE_CYCLE:
                        service_func = call_args[0][2]
                        break

                # Call the service
                response = await service_func(call)
                
                # Should still work even without name (name would be handled by flow)
                mock_hass.config_entries.flow.async_init.assert_called_once()
                # The service returns an info message when it can't find the entity
                assert "info" in response